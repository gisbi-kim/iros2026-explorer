# IROS 2026 Paper Explorer

Self-contained explorer for all 1,933 papers in the IROS 2026 Paper & Author Index.

Live site: <https://gisbi-kim.github.io/iros2026-explorer/>

Features include title/author/affiliation/keyword search, day and session filters,
topic and country summaries, sortable results, and shareable filter URLs.

## Build

Save the official IROS 2026 Paper & Author Index HTML, then run:

```bash
python scripts/parse_iros_index.py "path/to/Paper & Author Index _ IROS 2026.html"
python scripts/build_html.py
```

The generated standalone page is `output/iros2026_explorer.html`.

## Source

- <https://2026.ieee-iros.org/program/paper-index/>
