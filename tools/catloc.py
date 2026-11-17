#!/usr/bin/env python3
"""catloc - tools for the EU4 Catalan translation mod.

The mod overrides the English slot: Catalan text lives in
localisation/replace/ca_<name>_l_english.yml and contains ONLY translated
entries, so anything untranslated falls back to vanilla English.

Workflow:
    python3 tools/catloc.py progress            # how much is done
    python3 tools/catloc.py todo text -n 300    # -> tools/work/text.todo.yml
    (translate the values in the todo file)
    python3 tools/catloc.py merge tools/work/text.todo.yml
    python3 tools/catloc.py validate            # check every Catalan file
    python3 tools/catloc.py stale               # entries whose English changed in a patch

The game folder is auto-detected; override with --game or EU4_GAME_DIR.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import json
import os
import re
import sys
import time
from dataclasses import dataclass
from pathlib import Path

MOD_DIR = Path(__file__).resolve().parent.parent
REPLACE_DIR = MOD_DIR / "localisation" / "replace"
WORK_DIR = MOD_DIR / "tools" / "work"
HASH_FILE = MOD_DIR / "tools" / "source_hashes.json"
PROGRESS_FILE = MOD_DIR / "PROGRESS.md"
PREFIX = "ca_"
SUFFIX = "_l_english.yml"
OWN_KEY_PREFIX = "CA_"  # keys that only exist in this mod (grammar helper strings)
PROV_KEY_RX = re.compile(r"^PROV\d+$")
TAG_RX = re.compile(r"^\s*([A-Z][A-Z0-9]{2})\s*=", re.M)
NAME_KEY_RX = re.compile(r"^[A-Z][A-Z0-9]{2}$")
HEADER = "l_english:"
BOM = "\ufeff"

GAME_CANDIDATES = [
    "/mnt/c/Program Files (x86)/Steam/steamapps/common/Europa Universalis IV",
    "C:/Program Files (x86)/Steam/steamapps/common/Europa Universalis IV",
    "/mnt/c/Program Files/Steam/steamapps/common/Europa Universalis IV",
    os.path.expanduser("~/.local/share/Steam/steamapps/common/Europa Universalis IV"),
]

ENTRY_RX = re.compile(r'^\s*([^\s:#"]+):(\d*)\s*"(.*)"\s*(#.*)?$')

# Tokens the game interprets; a translation must keep them intact.
TOKEN_RULES = [
    # (name, regex, severity)
    ("variable", re.compile(r"\$[^$\s\"]+\$"), "error"),        # $WHO$, $NAME|Y$
    ("scope", re.compile(r"\[[^\[\]\"]+\]"), "error"),          # [Root.GetName]
    ("icon", re.compile(r"£[^£\s]+£"), "error"),               # £adm£
    ("flag", re.compile(r"@[A-Z0-9]{3}\b"), "error"),           # @SWE
    ("colour", re.compile(r"§[^!]"), "error"),                  # §Y §G ...
    ("colour-end", re.compile(r"§!"), "error"),
    ("currency", re.compile(r"¤"), "error"),
    ("newline", re.compile(r"\\n"), "warning"),
]


@dataclass
class Entry:
    key: str
    version: str
    value: str
    line: int


@dataclass
class LocFile:
    path: Path
    entries: dict[str, Entry]
    order: list[str]
    problems: list[tuple[int, str, str]]  # (line, severity, message)


# (file, entries, translated entries, stale, words, translated words)
ProgressRow = tuple[str, int, int, int, int, int]


class Args(argparse.Namespace):
    """Typed view of the parsed command line (union of all subcommands' options)."""

    game: str | None = None
    cmd: str = ""
    file: str | None = None
    all: bool = False
    sort: str = "name"
    limit: int = 0
    out: str | None = None
    force: bool = False
    include_empty: bool = False
    no_es: bool = False
    todo: str = ""
    quiet: bool = False
    unknown: bool = False
    write: bool = False


# ---------------------------------------------------------------- I/O

def parse_file(path: Path) -> LocFile:
    problems: list[tuple[int, str, str]] = []
    raw = path.read_bytes()
    if not raw.startswith(b"\xef\xbb\xbf"):
        problems.append((1, "error", "file must be UTF-8 with BOM"))
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError as e:
        problems.append((1, "error", f"not valid UTF-8: {e}"))
        return LocFile(path, {}, [], problems)

    entries: dict[str, Entry] = {}
    order: list[str] = []
    seen_header = False
    for n, line in enumerate(text.splitlines(), 1):
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        if not seen_header:
            if s != HEADER:
                problems.append((n, "error", f"first non-comment line must be '{HEADER}', got {s[:40]!r}"))
            seen_header = True
            continue
        m = ENTRY_RX.match(line)
        if not m:
            problems.append((n, "error", f"unparseable line: {line[:80]!r}"))
            continue
        key, ver, val = m.group(1), m.group(2), m.group(3)
        if key in entries:
            problems.append((n, "error", f"duplicate key {key} (also line {entries[key].line})"))
            continue
        entries[key] = Entry(key, ver or "0", val, n)
        order.append(key)
    if not seen_header:
        problems.append((1, "error", f"missing '{HEADER}' header"))
    return LocFile(path, entries, order, problems)


def write_file(path: Path, entries: list[Entry], comments: dict[str, list[str]] | None = None,
               preamble: list[str] | None = None) -> None:
    out = [BOM + HEADER]
    out += preamble or []
    for e in entries:
        for c in (comments or {}).get(e.key, []):
            out.append(f" # {c}")
        out.append(f' {e.key}:{e.version} "{e.value}"')
    path.parent.mkdir(parents=True, exist_ok=True)
    _ = path.write_text("\n".join(out) + "\n", encoding="utf-8", newline="\n")


def find_game(arg: str | None) -> Path:
    for c in [arg, os.environ.get("EU4_GAME_DIR"), *GAME_CANDIDATES]:
        if c and (Path(c) / "localisation").is_dir():
            return Path(c)
    sys.exit("EU4 game folder not found; pass --game or set EU4_GAME_DIR")


class Vanilla:
    """All English localisation of the installed game."""

    def __init__(self, game: Path):
        self.game: Path = game
        self._spanish: dict[str, str] | None = None
        self.files: dict[str, LocFile] = {}     # base name -> file
        self.index: dict[str, tuple[str, Entry]] = {}  # key -> (base name, entry)
        for p in sorted((game / "localisation").glob("*" + SUFFIX)):
            base = p.name[: -len(SUFFIX)]
            lf = parse_file(p)
            self.files[base] = lf
            for k in lf.order:
                self.index[k] = (base, lf.entries[k])

    def spanish(self) -> dict[str, str]:
        """Official Spanish text by key (reference only; English is the source of truth)."""
        if self._spanish is None:
            self._spanish = {}
            for p in (self.game / "localisation").glob("*_l_spanish.yml"):
                for k, e in parse_file(p).entries.items():
                    self._spanish[k] = e.value
        return self._spanish

    def country_tags(self) -> list[str]:
        """Country tags (common/country_tags) plus name-override keys (XXX + XXX_ADJ), sorted."""
        tags: set[str] = set()
        for p in (self.game / "common" / "country_tags").glob("*.txt"):
            text = p.read_text(encoding="cp1252", errors="replace")
            tags.update(m.group(1) for m in TAG_RX.finditer(re.sub(r"#.*", "", text)))
        tags.update(k for k in self.index if NAME_KEY_RX.match(k) and k + "_ADJ" in self.index)
        return sorted(t for t in tags if t in self.index)

    def name_keys(self) -> set[str]:
        """Country names/adjectives and province names: maintained in glossary/*.tsv, not via todo."""
        keys = {k for t in self.country_tags() for k in (t, t + "_ADJ")}
        return keys | {k for k in self.index if PROV_KEY_RX.match(k)}

    def resolve(self, name: str) -> str:
        base = name
        for s in (SUFFIX, ".yml"):
            if base.endswith(s):
                base = base[: -len(s)]
        if base not in self.files:
            close = [b for b in self.files if name.lower() in b.lower()]
            sys.exit(f"unknown vanilla file {name!r}" + (f"; did you mean: {', '.join(close[:8])}" if close else ""))
        return base


def ca_path(base: str) -> Path:
    return REPLACE_DIR / f"{PREFIX}{base}{SUFFIX}"


def load_translations() -> dict[Path, LocFile]:
    return {p: parse_file(p) for p in sorted(REPLACE_DIR.glob("*" + SUFFIX))}


def src_hash(value: str) -> str:
    return hashlib.sha1(value.encode("utf-8")).hexdigest()[:12]


def load_hashes() -> dict[str, str]:
    return json.loads(HASH_FILE.read_text(encoding="utf-8")) if HASH_FILE.exists() else {}


def save_hashes(h: dict[str, str]) -> None:
    _ = HASH_FILE.write_text(json.dumps(dict(sorted(h.items())), ensure_ascii=False, indent=0) + "\n",
                         encoding="utf-8")


def words(s: str) -> int:
    return len(re.findall(r"[A-Za-z]+", re.sub(r"\$[^$]*\$|\[[^\]]*\]|§.|£[^£]*£", " ", s)))


# ---------------------------------------------------------------- checks

# Catalan grammar helpers (see glossary/guia_estil.md §6), defined in customizable_localization/.
CA_PARTICLE_RX = re.compile(r"\[[^\[\]\"]+\.GetCa(?:El|De|A|Per)(?:Prov)?(?:Cap)?\]")
CA_ADJ_RX = re.compile(r"(\[[^\[\]\"]+\.)GetCaAdj(?:FS|MP|FP)\]")


def normalise_ca(ca: str) -> str:
    """Strip Catalan-only helpers so token checks compare like with like."""
    return CA_ADJ_RX.sub(r"\1GetAdjective]", CA_PARTICLE_RX.sub("", ca))


def check_entry(en: str, ca: str) -> list[tuple[str, str]]:
    """Compare a translation against its English source. Returns (severity, message)."""
    out: list[tuple[str, str]] = []
    raw_ca, ca = ca, normalise_ca(ca)
    for name, rx, sev in TOKEN_RULES:
        a, b = collections.Counter(rx.findall(en)), collections.Counter(rx.findall(ca))
        if a != b:
            missing, extra = list((a - b).elements()), list((b - a).elements())
            detail = "; ".join(x for x in [
                f"missing {' '.join(missing)}" if missing else "",
                f"unexpected {' '.join(extra)}" if extra else ""] if x)
            out.append((sev, f"{name} mismatch: {detail}"))
    ca = raw_ca
    bad = sorted({c for c in ca if not cp1252_ok(c) and c not in en})
    if bad:
        out.append(("error", f"characters the game font cannot show: {' '.join(bad)}"))
    if en.strip() and not ca.strip():
        out.append(("warning", "empty translation"))
    if en != en.strip() or ca != ca.strip():
        if (en[:1].isspace(), en[-1:].isspace()) != (ca[:1].isspace(), ca[-1:].isspace()):
            out.append(("warning", "leading/trailing spaces differ from English"))
    return out


def cp1252_ok(c: str) -> bool:
    try:
        _ = c.encode("cp1252")
        return True
    except UnicodeEncodeError:
        return False


# ---------------------------------------------------------------- commands

def compute_progress(van: Vanilla) -> tuple[list[ProgressRow], collections.Counter[str]]:
    """Per vanilla file: (file, entries, translated, stale, words, translated words), plus totals."""
    hashes = load_hashes()
    done = {k for lf in load_translations().values() for k in lf.entries}
    rows: list[ProgressRow] = []
    tot: collections.Counter[str] = collections.Counter()
    for base, lf in van.files.items():
        n = len(lf.order)
        w = sum(words(lf.entries[k].value) for k in lf.order)
        t = [k for k in lf.order if k in done]
        stale = sum(1 for k in t if k in hashes and hashes[k] != src_hash(lf.entries[k].value))
        tw = sum(words(lf.entries[k].value) for k in t)
        rows.append((base, n, len(t), stale, w, tw))
        tot.update(n=n, t=len(t), s=stale, w=w, tw=tw)
    return rows, tot


def pct(part: int, whole: int) -> float:
    return 100 * part / whole if whole else 100.0


def write_progress_md(van: Vanilla) -> None:
    """Regenerate PROGRESS.md (called by merge and by catnames build)."""
    rows, tot = compute_progress(van)
    rows.sort(key=lambda r: (-r[4], r[0]))
    total = pct(tot["tw"], tot["w"])
    started = [r for r in rows if r[2]]
    out = [
        "# Translation progress",
        "",
        "Generated by `tools/catloc.py`; updated automatically on every `merge` and `catnames.py build`.",
        "Percentages count words of the English source.",
        "",
        f"**Total: {total:.2f}%**",
        "",
        f"- Words: {tot['tw']:,} / {tot['w']:,}",
        f"- Entries: {tot['t']:,} / {tot['n']:,}",
        f"- Files started: {len(started)} / {len(rows)} ({sum(1 for r in rows if r[5] >= r[4])} complete)",
        f"- Stale (English changed since translated): {tot['s']}",
        "",
        "## Files",
        "",
        "Sorted by size. Run `python3 tools/catloc.py todo <file>` to translate one.",
        "",
        "| File | % | Words | Entries | Stale |",
        "|---|---:|---:|---:|---:|",
    ]
    for base, n, t, s, w, tw in rows:
        p = pct(tw, w)
        out.append(f"| `{base}` | {p:.1f}% | {tw:,} / {w:,} | {t:,} / {n:,} | {s or ''} |")
    _ = PROGRESS_FILE.write_text("\n".join(out) + "\n", encoding="utf-8", newline="\n")


def cmd_progress(args: Args, van: Vanilla) -> int:
    if args.write:
        write_progress_md(van)
        print(f"wrote {PROGRESS_FILE.relative_to(MOD_DIR).as_posix()}")
        return 0
    rows, tot = compute_progress(van)
    if args.file:
        rows = [r for r in rows if r[0] == van.resolve(args.file)]
    elif not args.all:
        rows = [r for r in rows if r[2]] or rows[:0]
    if args.sort == "name":
        rows.sort(key=lambda r: r[0])
    elif args.sort == "size":
        rows.sort(key=lambda r: -r[4])
    else:
        rows.sort(key=lambda r: -(r[5] / r[4] if r[4] else 0.0))
    if rows:
        print(f"{'file':<40} {'entries':>14} {'words':>16} {'stale':>6}")
        for base, n, t, s, w, tw in rows:
            print(f"{base:<40} {t:>6}/{n:<7} {tw:>7}/{w:<7} {s:>6}  {pct(tw, w):5.1f}%")
        print()
    print(f"TOTAL: {tot['t']}/{tot['n']} entries, {tot['tw']}/{tot['w']} words "
          + f"({pct(tot['tw'], tot['w']):.2f}%), {tot['s']} stale")
    if not args.all and not args.file:
        print("(use --all to list every file, --sort size to see the biggest ones)")
    return 0


def cmd_todo(args: Args, van: Vanilla) -> int:
    if not args.file:  # required by argparse; narrows the type
        sys.exit("todo needs a vanilla file name")
    base = van.resolve(args.file)
    out = Path(args.out) if args.out else WORK_DIR / f"{base}.todo.yml"
    if out.exists() and not args.force:
        sys.exit(f"{out} already exists (unmerged work?). Merge it first or use --force to overwrite.")
    src = van.files[base]
    existing = parse_file(ca_path(base)).entries if ca_path(base).exists() else {}
    others = {k for p, lf in load_translations().items() if p != ca_path(base) for k in lf.entries}
    hashes = load_hashes()
    es = {} if args.no_es else van.spanish()
    names = van.name_keys()
    picked: list[Entry] = []
    comments: collections.defaultdict[str, list[str]] = collections.defaultdict(list)
    for k in src.order:
        e = src.entries[k]
        if k in others or k in names:
            continue
        if k in existing:
            if not (k in hashes and hashes[k] != src_hash(e.value)):
                continue
            comments[k].append(f'STALE - English changed. Previous Catalan: "{existing[k].value}"')
        if not args.include_empty and not e.value.strip():
            continue
        if es.get(k, e.value) != e.value:
            comments[k].append(f'ES: "{es[k]}"')
        picked.append(Entry(k, e.version, e.value, 0))
        if args.limit and len(picked) >= args.limit:
            break
    if not picked:
        print(f"nothing left to translate in {base}")
        return 0
    write_file(out, picked, comments, preamble=[
        f" # catloc todo for '{base}' ({len(picked)} entries).",
        " # Replace each English value with Catalan. Keep keys, :N, $VARS$, [Scopes], §X..§!, £icons£, \\n.",
        " # '# ES:' lines are the official Spanish text, for reference only. Its Spanish-only",
        " # helpers ([Root.GetElLaDir]...) must NOT be copied; use the GetCa... helpers instead.",
        " # Then run: python3 tools/catloc.py merge " + out.relative_to(MOD_DIR).as_posix(),
    ])
    print(f"wrote {len(picked)} entries ({sum(words(e.value) for e in picked)} words) to {out}")
    return 0


LOCK_DIR = MOD_DIR / "tools" / ".merge.lock"


def cmd_merge(args: Args, van: Vanilla) -> int:
    """Serialise merges (they rewrite shared files) with an atomic lock directory."""
    for _ in range(600):
        try:
            LOCK_DIR.mkdir()
            break
        except FileExistsError:
            time.sleep(0.5)
    else:
        sys.exit(f"could not get {LOCK_DIR} after 5 minutes; delete it if no merge is running")
    try:
        return merge_locked(args, van)
    finally:
        LOCK_DIR.rmdir()


def merge_locked(args: Args, van: Vanilla) -> int:
    path = Path(args.todo)
    todo = parse_file(path)
    for ln, sev, msg in todo.problems:
        print(f"{path}:{ln}: {sev}: {msg}")
    if any(sev == "error" for _, sev, _ in todo.problems):
        return 1
    hashes = load_hashes()
    by_base: dict[str, list[Entry]] = collections.defaultdict(list)
    left: list[Entry] = []
    skipped = failed = 0
    for k in todo.order:
        e = todo.entries[k]
        if k not in van.index:
            print(f"{path}:{e.line}: error: {k} does not exist in the game; dropped")
            failed += 1
            continue
        base, src = van.index[k]
        if e.value == src.value and not args.all:
            left.append(e)
            skipped += 1
            continue
        probs = check_entry(src.value, e.value)
        errs = [m for s, m in probs if s == "error"]
        for s, m in probs:
            print(f"{path}:{e.line}: {s}: {k}: {m}")
        if errs and not args.force:
            left.append(e)
            failed += 1
            continue
        by_base[base].append(Entry(k, src.version, e.value, 0))
    merged = 0
    for base, new in by_base.items():
        target = ca_path(base)
        cur = parse_file(target).entries if target.exists() else {}
        for e in new:
            cur[e.key] = e
            hashes[e.key] = src_hash(van.index[e.key][1].value)
        order = [k for k in van.files[base].order if k in cur] + [k for k in cur if k not in van.files[base].entries]
        write_file(target, [cur[k] for k in order])
        merged += len(new)
    save_hashes(hashes)
    write_progress_md(van)
    if left:
        write_file(path, left, preamble=[" # Entries not merged yet (unchanged from English or with errors)."])
    else:
        path.unlink()
    print(f"merged {merged}, unchanged-from-English {skipped}, errors {failed}; "
          + (f"{len(left)} left in {path}" if left else f"removed {path}"))
    if skipped:
        print("  (if an entry should stay identical to English, run merge again with --all)")
    return 1 if failed else 0


def cmd_validate(args: Args, van: Vanilla) -> int:
    errors = warnings = 0
    first_seen: dict[str, Path] = {}

    def report(p: Path, ln: int, sev: str, msg: str):
        nonlocal errors, warnings
        if sev == "error":
            errors += 1
        else:
            warnings += 1
            if args.quiet:
                return
        print(f"{p.relative_to(MOD_DIR).as_posix()}:{ln}: {sev}: {msg}")

    stray = [p for p in REPLACE_DIR.rglob("*") if p.is_file() and not p.name.endswith(SUFFIX)]
    for p in stray:
        report(p, 0, "warning", f"ignored by the game (name must end in {SUFFIX})")
    for p, lf in load_translations().items():
        for ln, sev, msg in lf.problems:
            report(p, ln, sev, msg)
        for k in lf.order:
            e = lf.entries[k]
            if k in first_seen:
                report(p, e.line, "error", f"{k} also defined in {first_seen[k].name}")
                continue
            first_seen[k] = p
            if k not in van.index:
                if not k.startswith(OWN_KEY_PREFIX):
                    report(p, e.line, "warning", f"{k} no longer exists in the game")
                continue
            src = van.index[k][1]
            if e.version != src.version:
                report(p, e.line, "warning", f"{k}: version :{e.version} differs from game :{src.version}")
            for sev, msg in check_entry(src.value, e.value):
                report(p, e.line, sev, f"{k}: {msg}")
    print(f"{len(first_seen)} translated entries checked: {errors} errors, {warnings} warnings")
    return 1 if errors else 0


def cmd_stale(args: Args, van: Vanilla) -> int:
    hashes = load_hashes()
    n = 0
    for p, lf in load_translations().items():
        for k in lf.order:
            if k.startswith(OWN_KEY_PREFIX):
                continue
            if k not in van.index:
                print(f"REMOVED  {p.name}: {k}")
                n += 1
            elif k not in hashes:
                if args.unknown:
                    print(f"UNKNOWN  {p.name}: {k} (no source hash; run 'rehash')")
            elif hashes[k] != src_hash(van.index[k][1].value):
                print(f"CHANGED  {p.name}: {k}\n    EN now: {van.index[k][1].value}\n    CA:     {lf.entries[k].value}")
                n += 1
    print(f"{n} stale entries" + ("; 'todo <file>' includes CHANGED ones automatically" if n else ""))
    return 0


def cmd_rehash(args: Args, van: Vanilla) -> int:
    hashes = load_hashes()
    added = 0
    for lf in load_translations().values():
        for k in lf.order:
            if k in van.index and (args.force or k not in hashes):
                hashes[k] = src_hash(van.index[k][1].value)
                added += 1
    save_hashes(hashes)
    print(f"recorded source hashes for {added} entries")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    _ = ap.add_argument("--game", help="EU4 install folder")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("progress", help="show translation progress")
    _ = p.add_argument("file", nargs="?", help="only this vanilla file (e.g. text)")
    _ = p.add_argument("--all", action="store_true", help="list every file, not only started ones")
    _ = p.add_argument("--sort", choices=["name", "size", "pct"], default="name")
    _ = p.add_argument("--write", action="store_true", help="regenerate PROGRESS.md instead of printing")

    p = sub.add_parser("todo", help="export untranslated/stale entries of a vanilla file")
    _ = p.add_argument("file", help="vanilla file base name, e.g. text or EU4")
    _ = p.add_argument("-n", "--limit", type=int, default=0, help="max entries (0 = all)")
    _ = p.add_argument("-o", "--out", help="output path (default tools/work/<file>.todo.yml)")
    _ = p.add_argument("--force", action="store_true", help="overwrite an existing todo file")
    _ = p.add_argument("--include-empty", action="store_true", help="include entries whose English is empty")
    _ = p.add_argument("--no-es", action="store_true", help="don't add the official Spanish text as reference comments")

    p = sub.add_parser("merge", help="validate a translated todo file and merge it into the mod")
    _ = p.add_argument("todo")
    _ = p.add_argument("--all", action="store_true", help="also merge entries left identical to English")
    _ = p.add_argument("--force", action="store_true", help="merge entries even if they have errors")

    p = sub.add_parser("validate", help="check all Catalan files")
    _ = p.add_argument("-q", "--quiet", action="store_true", help="hide warnings")

    p = sub.add_parser("stale", help="list translations whose English source changed or was removed")
    _ = p.add_argument("--unknown", action="store_true", help="also list entries without a recorded hash")

    p = sub.add_parser("rehash", help="record current English hashes for hand-made translations")
    _ = p.add_argument("--force", action="store_true", help="overwrite existing hashes too (marks all as up to date)")

    args = ap.parse_args(namespace=Args())
    van = Vanilla(find_game(args.game))
    return {"progress": cmd_progress, "todo": cmd_todo, "merge": cmd_merge, "validate": cmd_validate,
            "stale": cmd_stale, "rehash": cmd_rehash}[args.cmd](args, van)


if __name__ == "__main__":
    sys.exit(main())
