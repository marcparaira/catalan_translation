#!/usr/bin/env python3
"""catnames - country/province names and the Catalan grammar helpers.

Names are maintained in two tables instead of todo files:
    glossary/paisos.tsv      tag, en, en_adj, ca, article, adj_ms, adj_fs, adj_mp, adj_fp, de, notes
    glossary/provincies.tsv  id, en, ca, article, de, notes

Commands:
    python3 tools/catnames.py init    # create/refresh the tables from the game (keeps Catalan columns)
    python3 tools/catnames.py build   # generate the mod files from the tables

`build` writes (do not edit these by hand):
    localisation/replace/ca_00_names_l_english.yml     names, adjectives, helper strings
    customizable_localization/ca_helpers.txt           GetCaEl/De/A/Per[Prov][Cap], GetCaAdjFS/MP/FP
    common/scripted_triggers/ca_loc_triggers.txt       country/province groups used by the helpers

Columns:
    article  '', el, la, l', els, les   (article the name takes in Catalan; never put it in `ca`)
    de       '' = automatic (d' before a vowel or h+vowel), or force "de" / "d'"
"""
from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

import catloc
from catloc import MOD_DIR, Entry, Vanilla, find_game, load_hashes, save_hashes, src_hash, write_file

GLOSSARY = MOD_DIR / "glossary"
COUNTRY_TSV = GLOSSARY / "paisos.tsv"
PROVINCE_TSV = GLOSSARY / "provincies.tsv"
NAMES_YML = catloc.REPLACE_DIR / f"{catloc.PREFIX}00_names{catloc.SUFFIX}"
HELPERS_TXT = MOD_DIR / "customizable_localization" / "ca_helpers.txt"
TRIGGERS_TXT = MOD_DIR / "common" / "scripted_triggers" / "ca_loc_triggers.txt"

COUNTRY_COLS = ["tag", "en", "en_adj", "ca", "article", "adj_ms", "adj_fs", "adj_mp", "adj_fp", "de", "notes"]
PROVINCE_COLS = ["id", "en", "ca", "article", "de", "notes"]
CA_COLS = {"ca", "article", "adj_ms", "adj_fs", "adj_mp", "adj_fp", "de", "notes"}

Row = dict[str, str]

# Name form -> particle per helper. "£" swallows the following space (same trick as the French loc).
FORMS: dict[str, dict[str, str]] = {
    "0": {"El": "£", "De": "de", "A": "a", "Per": "per"},
    "d": {"El": "£", "De": "d'£", "A": "a", "Per": "per"},
    "el": {"El": "el", "De": "del", "A": "al", "Per": "pel"},
    "la": {"El": "la", "De": "de la", "A": "a la", "Per": "per la"},
    "l": {"El": "l'£", "De": "de l'£", "A": "a l'£", "Per": "per l'£"},
    "els": {"El": "els", "De": "dels", "A": "als", "Per": "pels"},
    "les": {"El": "les", "De": "de les", "A": "a les", "Per": "per les"},
}
ARTICLE_FORM = {"el": "el", "la": "la", "l'": "l", "els": "els", "les": "les"}
ADJ_FORMS = ["FS", "MP", "FP"]
VOWELS = "aeiouàèéíïòóúüAEIOUÀÈÉÍÏÒÓÚÜ"


# ---------------------------------------------------------------- tables

def read_tsv(path: Path, cols: list[str]) -> list[Row]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f, delimiter="\t"))
    return [{c: (r.get(c) or "").strip() for c in cols} for r in rows]


def write_tsv(path: Path, cols: list[str], rows: list[Row]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, delimiter="\t", lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def refresh(path: Path, cols: list[str], id_col: str, fresh: list[Row]) -> tuple[int, int, int]:
    """Merge game data into a table, keeping the Catalan columns. Returns (added, changed, removed)."""
    old = {r[id_col]: r for r in read_tsv(path, cols)}
    added = changed = 0
    out: list[Row] = []
    for r in fresh:
        prev = old.pop(r[id_col], None)
        if prev is None:
            added += 1
        else:
            if any(prev[c] != r[c] for c in cols if c not in CA_COLS):
                changed += 1
            r.update({c: prev[c] for c in cols if c in CA_COLS})
        out.append(r)
    for r in old.values():  # no longer in the game: keep the work, flag it
        if "REMOVED" not in r["notes"]:
            r["notes"] = ("REMOVED from game. " + r["notes"]).strip()
        out.append(r)
    write_tsv(path, cols, out)
    return added, changed, len(old)


def cmd_init(van: Vanilla) -> int:
    countries: list[Row] = []
    for t in van.country_tags():
        adj = van.index.get(t + "_ADJ")
        countries.append({c: "" for c in COUNTRY_COLS} | {
            "tag": t, "en": van.index[t][1].value, "en_adj": adj[1].value if adj else ""})
    provinces: list[Row] = []
    for k in sorted((k for k in van.index if catloc.PROV_KEY_RX.match(k)), key=lambda k: int(k[4:])):
        provinces.append({c: "" for c in PROVINCE_COLS} | {"id": k[4:], "en": van.index[k][1].value})
    for path, cols, idc, rows in ((COUNTRY_TSV, COUNTRY_COLS, "tag", countries),
                                  (PROVINCE_TSV, PROVINCE_COLS, "id", provinces)):
        a, c, r = refresh(path, cols, idc, rows)
        print(f"{path.relative_to(MOD_DIR).as_posix()}: {len(rows)} rows ({a} new, {c} English changed, {r} removed)")
    return 0


# ---------------------------------------------------------------- build

def elides(name: str) -> bool:
    """Catalan 'de' -> "d'" before a vowel or h+vowel, except i/u + vowel (semiconsonant)."""
    s = name.lstrip("\"'«")
    if s[:1] in "hH":
        s = s[1:]
    if not s or s[0] not in VOWELS:
        return False
    return not (s[0] in "iIuU" and s[1:2] != "" and s[1] in VOWELS)


def de_form(name: str, override: str, where: str, problems: list[str]) -> str:
    if override in ("", "auto"):
        return "d" if elides(name) else "0"
    if override in ("d'", "d"):
        return "d"
    if override == "de":
        return "0"
    problems.append(f"{where}: invalid 'de' value {override!r} (use '', de or d')")
    return "0"


def check_text(value: str, where: str, problems: list[str]) -> None:
    bad = sorted({ch for ch in value if not catloc.cp1252_ok(ch)})
    if bad:
        problems.append(f"{where}: characters the game font cannot show: {' '.join(bad)}")
    if '"' in value:
        problems.append(f"{where}: double quotes are not allowed in names")


def name_form(r: Row, where: str, problems: list[str]) -> str:
    """Grammatical form of a country/province name: a key of FORMS."""
    art = r["article"]
    if art:
        if art not in ARTICLE_FORM:
            problems.append(f"{where}: invalid article {art!r} (use el, la, l', els, les)")
            return "0"
        return ARTICLE_FORM[art]
    if re.match(r"(?i)^(el|la|els|les)\s|^l'", r["ca"]):
        problems.append(f"warning: {where}: name starts with an article ({r['ca']}); "
                        + "if it isn't part of a foreign name, move it to the 'article' column")
    return de_form(r["ca"] or r["en"], r["de"], where, problems)


def or_block(lines: list[str], indent: str = "\t") -> str:
    if not lines:
        return f"{indent}always = no"
    body = "\n".join(f"{indent}\t{x}" for x in lines)
    return f"{indent}OR = {{\n{body}\n{indent}}}"


def cap(s: str) -> str:
    return s[:1].upper() + s[1:]


def cmd_build(van: Vanilla) -> int:
    countries = read_tsv(COUNTRY_TSV, COUNTRY_COLS)
    provinces = read_tsv(PROVINCE_TSV, PROVINCE_COLS)
    if not countries or not provinces:
        sys.exit("tables missing; run 'python3 tools/catnames.py init' first")
    problems: list[str] = []
    entries: list[Entry] = []
    hashes = load_hashes()

    def emit(key: str, value: str) -> None:
        src = van.index.get(key)
        entries.append(Entry(key, src[1].version if src else "0", value, 0))
        if src:
            hashes[key] = src_hash(src[1].value)

    # --- countries
    groups: dict[str, list[str]] = {f: [] for f in FORMS}
    with_adj: list[str] = []
    for r in countries:
        t = r["tag"]
        if "REMOVED" in r["notes"] or t not in van.index:
            continue
        where = f"paisos.tsv {t}"
        groups[name_form(r, where, problems)].append(t)
        if r["ca"]:
            check_text(r["ca"], where, problems)
            emit(t, r["ca"])
        adjs = [r["adj_ms"], r["adj_fs"], r["adj_mp"], r["adj_fp"]]
        if any(adjs):
            if not all(adjs):
                problems.append(f"{where}: fill all four adjective forms (or none)")
                continue
            for a in adjs:
                check_text(a, where, problems)
            emit(t + "_ADJ", r["adj_ms"])
            for form, a in zip(ADJ_FORMS, adjs[1:]):
                emit(f"CA_ADJ_{form}_{t}", a)
            with_adj.append(t)

    # --- provinces
    pgroups: dict[str, list[str]] = {f: [] for f in FORMS}
    for r in provinces:
        pid = r["id"]
        if "REMOVED" in r["notes"] or f"PROV{pid}" not in van.index:
            continue
        where = f"provincies.tsv {pid}"
        if r["ca"]:
            check_text(r["ca"], where, problems)
            emit(f"PROV{pid}", r["ca"])
        pgroups[name_form(r, where, problems)].append(pid)

    if problems:
        print("\n".join(problems))
    errors = [p for p in problems if not p.startswith("warning:")]
    if errors:
        print(f"{len(errors)} errors; nothing written")
        return 1

    # --- helper strings
    for form, parts in FORMS.items():
        for helper, text in parts.items():
            emit(f"CA_P_{form}_{helper}", text)
            emit(f"CA_P_{form}_{helper}_CAP", cap(text))
    emit("CA_ADJ_FALLBACK", "[This.GetAdjective]")

    write_file(NAMES_YML, entries, preamble=[
        " # GENERATED by tools/catnames.py from glossary/paisos.tsv and glossary/provincies.tsv.",
        " # Do not edit: change the tables and run 'python3 tools/catnames.py build'."])
    save_hashes(hashes)

    # --- scripted triggers
    trig = ["# GENERATED by tools/catnames.py - do not edit.", ""]
    for kind, cond, grp in (("country", "tag", groups), ("province", "province_id", pgroups)):
        for form in FORMS:
            if form != "0":
                items = [f"{cond} = {x}" for x in grp[form]]
                trig += [f"caloc_{kind}_{form} = {{", or_block(items), "}", ""]
        trig += [f"caloc_{kind}_0 = {{", "\tNOT = {", "\t\tOR = {"]
        trig += [f"\t\t\tcaloc_{kind}_{f} = yes" for f in FORMS if f != "0"]
        trig += ["\t\t}", "\t}", "}", ""]
    trig += ["caloc_country_has_adj = {", or_block([f"tag = {t}" for t in with_adj]), "}", ""]
    write_ascii(TRIGGERS_TXT, trig)

    # --- defined_text helpers
    out = ["# GENERATED by tools/catnames.py - do not edit.",
           "# Catalan grammar helpers; see glossary/guia_estil.md section 6.", ""]
    for kind, scope_suffix in (("country", ""), ("province", "Prov")):
        for helper in ("El", "De", "A", "Per"):
            for suffix in ("", "_CAP"):
                name = f"GetCa{helper}{scope_suffix}{'Cap' if suffix else ''}"
                out += ["defined_text = {", f"\tname = {name}", "\trandom = no"]
                for form in FORMS:
                    out += ["\ttext = {", f"\t\tlocalisation_key = CA_P_{form}_{helper}{suffix}",
                            f"\t\ttrigger = {{ caloc_{kind}_{form} = yes }}", "\t}"]
                out += ["}", ""]
    for form in ADJ_FORMS:
        out += [f"defined_text = {{", f"\tname = GetCaAdj{form}", "\trandom = no"]
        for t in with_adj:
            out += ["\ttext = {", f"\t\tlocalisation_key = CA_ADJ_{form}_{t}", f"\t\ttrigger = {{ tag = {t} }}", "\t}"]
        out += ["\ttext = {", "\t\tlocalisation_key = CA_ADJ_FALLBACK",
                "\t\ttrigger = { NOT = { caloc_country_has_adj = yes } }", "\t}", "}", ""]
    write_ascii(HELPERS_TXT, out)

    named = sum(1 for r in countries if r["ca"])
    pnamed = sum(1 for r in provinces if r["ca"])
    print(f"countries: {named}/{len(countries)} named, {len(with_adj)} with adjectives")
    print(f"provinces: {pnamed}/{len(provinces)} named")
    for p in (NAMES_YML, TRIGGERS_TXT, HELPERS_TXT):
        print(f"wrote {p.relative_to(MOD_DIR).as_posix()}")
    return 0


def write_ascii(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    _ = path.write_text("\n".join(lines) + "\n", encoding="ascii", newline="\n")


class Args(argparse.Namespace):
    action: str = ""
    game: str | None = None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    _ = ap.add_argument("action", choices=["init", "build"])
    _ = ap.add_argument("--game", help="EU4 install folder")
    args = ap.parse_args(namespace=Args())
    van = Vanilla(find_game(args.game))
    return cmd_init(van) if args.action == "init" else cmd_build(van)


if __name__ == "__main__":
    sys.exit(main())
