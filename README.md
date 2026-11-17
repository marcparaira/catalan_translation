# Catalan Translation for Europa Universalis IV

Translates EU4 (v1.37.5.0) into Catalan.

EU4 cannot add new languages, so this mod **replaces the English text**: set the game language to English and enable the mod in the launcher. Untranslated text falls back to the original English.

## Structure

```
catalan_translation/
├── descriptor.mod
├── thumbnail.png
├── localisation/replace/   Catalan files: ca_<vanilla_name>_l_english.yml
├── tools/catloc.py         translation helper (Python 3, no dependencies)
└── glossary/               glossary and style guide
```

Catalan files contain only translated entries. They must be UTF-8 **with BOM**, start with `l_english:`, and have one entry per line: ` KEY:0 "text"`.

## Typical use

```sh
# 1. Export the next 300 untranslated entries of a game file (e.g. text, EU4, core)
python3 tools/catloc.py todo text -n 300

# 2. Translate the values in tools/work/text.todo.yml

# 3. Validate and merge into localisation/replace/
python3 tools/catloc.py merge tools/work/text.todo.yml

# 4. Check progress
python3 tools/catloc.py progress
```

Keep the game codes unchanged: `$VARS$`, `[Scopes]`, `§Y…§!` colours, `£icons£`, `@TAG` flags and `\n`. `merge` won't merge an entry if one of these doesn't match.

## Other commands

| Command | Purpose |
|---|---|
| `validate` | Check all Catalan files for errors |
| `progress --all --sort size` | List every game file, biggest first |
| `stale` | After a game update: list translations whose English changed or was removed |
| `rehash` | Mark hand-written translations as up to date |

The game folder is detected automatically; otherwise pass `--game <path>` or set `EU4_GAME_DIR`.

## After a game update

1. Run `python3 tools/catloc.py stale`. A `todo` for a file includes its changed entries automatically.
2. Update `version` and `supported_version` in `descriptor.mod` and `../catalan_translation.mod`.
