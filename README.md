# IROS 2026 Paper Explorer

Self-contained explorer for all 1,933 papers in the IROS 2026 Paper & Author Index.

Live site: <https://gisbi-kim.github.io/iros2026-explorer/>

Features include title/author/affiliation/keyword search, day and session filters,
topic and country summaries, submission and acceptance context, sortable results,
and shareable filter URLs. The explorer shows 500 papers per page by default. A PI / Lab Radar adds a curated 100-PI APRL-relevance watchlist (three/two/one stars indicate research fit, not PI or lab quality),
per-PI program metrics, automatically derived themes, keyword distributions,
coauthor networks, overlap signals, and representative-paper shortcuts.

## Counting scope

- IROS 2026 acceptance decisions reported 4,348 contributed-paper submissions,
  with 1,585 accepted (36% rounded; 36.45% from the published counts).
- The official final Paper & Author Index contains 1,933 program papers. This is
  a broader presentation-program count that can include eligible IEEE RAS/IES
  journal papers as well as final program changes; it is not the numerator used
  for the contributed-paper acceptance rate.

## Build

Save the official IROS 2026 Paper & Author Index HTML, then run:

```bash
python scripts/parse_iros_index.py "path/to/Paper & Author Index _ IROS 2026.html"
python scripts/build_html.py
powershell -ExecutionPolicy Bypass -File scripts/build_analysis.ps1
```

The generated standalone page is `output/iros2026_explorer.html`.

## Analysis

- Analysis index: <https://gisbi-kim.github.io/iros2026-explorer/output/analysis/>
- VLM/VLA research landscape review: <https://gisbi-kim.github.io/iros2026-explorer/output/iros2026_vlm_vla_landscape_review.html>
- Vision-Language Navigation research landscape: <https://gisbi-kim.github.io/iros2026-explorer/output/iros_2026_vln_landscape.html>
- Robot reasoning papers analysis: <https://gisbi-kim.github.io/iros2026-explorer/output/iros2026_reasoning_papers_analysis.html>

## Source

- <https://2026.ieee-iros.org/program/paper_index/>
