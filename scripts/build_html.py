"""Build a self-contained IROS 2026 explorer HTML — Apple Developer Docs style."""
from __future__ import annotations
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent
JSON_PATH = ROOT / "output" / "papers.json"
OUT = ROOT / "output" / "iros2026_explorer.html"

sys.path.insert(0, str(SCRIPT_DIR))
from dump_affiliations import COUNTRY_HINTS as _RAW_HINTS  # noqa

# Fold the special HK-Macau bucket into the China entry for the embedded JS.
_HINTS_FOR_JS = []
_china_idx = None
for name, hints in _RAW_HINTS:
    if name == "China-HK-Macau":
        # Append into the existing China block; if missing, create one.
        if _china_idx is None:
            _HINTS_FOR_JS.append(["China", list(hints)])
            _china_idx = len(_HINTS_FOR_JS) - 1
        else:
            _HINTS_FOR_JS[_china_idx][1].extend(hints)
    else:
        _HINTS_FOR_JS.append([name, list(hints)])
        if name == "China":
            _china_idx = len(_HINTS_FOR_JS) - 1
country_hints_json = json.dumps(_HINTS_FOR_JS, ensure_ascii=False, separators=(",", ":"))

data = json.loads(JSON_PATH.read_text(encoding="utf-8"))
papers_json = json.dumps(data["papers"], ensure_ascii=False, separators=(",", ":"))

# Authoritative LLM-built affiliation -> country lookup table (preferred).
# Falls back to country_overrides.json (older partial table) and finally to
# regex hints inside the JS.
TABLE_PATH = ROOT / "classification" / "aff_country_table.json"
OVERRIDES_PATH = ROOT / "classification" / "country_overrides.json"
INSTITUTION_ALIASES_PATH = ROOT / "classification" / "aff_institution_aliases.json"
INSTITUTION_MULTIMAP_PATH = ROOT / "classification" / "aff_institution_multimap.json"
INSTITUTION_COUNTRY_PATH = ROOT / "classification" / "aff_institution_country_table.json"
INSTITUTION_SITE_COUNTRY_PATH = ROOT / "classification" / "aff_institution_site_country_overrides.json"
INSTITUTION_PARENT_ORG_PATH = ROOT / "classification" / "aff_institution_parent_org.json"
overrides_data: dict[str, str] = {}
if OVERRIDES_PATH.exists():
    overrides_data.update(json.loads(OVERRIDES_PATH.read_text(encoding="utf-8")))
if TABLE_PATH.exists():
    # Authoritative table wins over older partial overrides.
    overrides_data.update(json.loads(TABLE_PATH.read_text(encoding="utf-8")))
# Defensive: fold HK / Macau / Unknown.
for k, v in list(overrides_data.items()):
    if v in ("Hong Kong", "Macau"):
        overrides_data[k] = "China"
    elif v == "Unknown":
        del overrides_data[k]
country_overrides_json = json.dumps(overrides_data, ensure_ascii=False, separators=(",", ":"))

institution_aliases_data = {}
if INSTITUTION_ALIASES_PATH.exists():
    institution_aliases_data = json.loads(INSTITUTION_ALIASES_PATH.read_text(encoding="utf-8"))
institution_aliases_json = json.dumps(institution_aliases_data, ensure_ascii=False, separators=(",", ":"))

institution_multimap_data = {}
if INSTITUTION_MULTIMAP_PATH.exists():
    institution_multimap_data = json.loads(INSTITUTION_MULTIMAP_PATH.read_text(encoding="utf-8"))
institution_multimap_json = json.dumps(institution_multimap_data, ensure_ascii=False, separators=(",", ":"))

institution_country_data = {}
if INSTITUTION_COUNTRY_PATH.exists():
    institution_country_data = json.loads(INSTITUTION_COUNTRY_PATH.read_text(encoding="utf-8"))
institution_country_json = json.dumps(institution_country_data, ensure_ascii=False, separators=(",", ":"))

institution_site_country_data = {}
if INSTITUTION_SITE_COUNTRY_PATH.exists():
    institution_site_country_data = json.loads(INSTITUTION_SITE_COUNTRY_PATH.read_text(encoding="utf-8"))
institution_site_country_json = json.dumps(institution_site_country_data, ensure_ascii=False, separators=(",", ":"))

institution_parent_org_data = {}
if INSTITUTION_PARENT_ORG_PATH.exists():
    institution_parent_org_data = json.loads(INSTITUTION_PARENT_ORG_PATH.read_text(encoding="utf-8"))
institution_parent_org_json = json.dumps(institution_parent_org_data, ensure_ascii=False, separators=(",", ":"))

# Pre-computed top-K similar-paper lookup (SPECTER2 embeddings, see scripts/embed_papers.py).
# Optional: if the file is missing the explorer simply omits the "Similar papers" section.
SIMILAR_PATH = ROOT / "classification" / "similar_papers.json"
if SIMILAR_PATH.exists():
    similar_data = json.loads(SIMILAR_PATH.read_text(encoding="utf-8"))
else:
    similar_data = {}
similar_json = json.dumps(similar_data, ensure_ascii=False, separators=(",", ":"))

HTML = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>IROS 2026 · Paper Explorer</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
<style>
  :root {
    --bg: #ffffff;
    --bg-alt: #f5f5f7;
    --bg-soft: #fafafa;
    --panel: #ffffff;
    --border: #d2d2d7;
    --border-soft: #e5e5ea;
    --text: #1d1d1f;
    --text-2: #424245;
    --muted: #6e6e73;
    --muted-2: #86868b;
    --accent: #0066cc;
    --accent-hover: #0058b0;
    --accent-soft: rgba(0,102,204,0.08);
    --green: #248a3d;
    --orange: #b25000;
    --purple: #6e3ad6;
    --pink: #c0185c;
    --yellow: #8a6d00;
    --shadow: 0 1px 3px rgba(0,0,0,0.04), 0 1px 2px rgba(0,0,0,0.06);
    --shadow-lg: 0 4px 16px rgba(0,0,0,0.06), 0 2px 4px rgba(0,0,0,0.04);
    --font: -apple-system, BlinkMacSystemFont, "SF Pro Text", "SF Pro Display",
            "Segoe UI", "Pretendard", "Noto Sans KR", system-ui, sans-serif;
  }
  * { box-sizing: border-box; }
  html, body { margin: 0; padding: 0; background: var(--bg); color: var(--text);
    font-family: var(--font); -webkit-font-smoothing: antialiased;
    font-size: 15px; line-height: 1.47; max-width:100%; overflow-x:clip; }
  a { color: var(--accent); text-decoration: none; }
  a:hover { text-decoration: underline; }

  /* Top bar */
  .topbar {
    position: sticky; top: 0; z-index: 50;
    background: rgba(255,255,255,0.85);
    backdrop-filter: saturate(180%) blur(20px);
    -webkit-backdrop-filter: saturate(180%) blur(20px);
    border-bottom: 1px solid var(--border-soft);
    height: 52px;
  }
  .topbar .inner {
    max-width: 1440px; margin: 0 auto; padding: 0 24px;
    height: 100%; display: flex; align-items: center; gap: 18px;
  }
  .brand { font-weight: 600; font-size: 17px; letter-spacing: -0.02em;
           color: inherit; text-decoration: none; cursor: pointer;
           user-select: none; transition: opacity 0.15s; }
  .brand:hover { opacity: 0.7; }
  .brand .dot { color: var(--accent); }
  .topbar .meta { color: var(--muted); font-size: 13px; }
  .topbar .right { margin-left: auto; display: flex; gap: 8px; align-items: center; }
  .stat-pill {
    font-size: 12px; color: var(--muted-2); padding: 4px 10px; border-radius: 999px;
    background: var(--bg-alt); border: 1px solid var(--border-soft);
    font-variant-numeric: tabular-nums;
  }
  .stat-pill b { color: var(--text); font-weight: 600; }
  .stat-pill.accent { background: var(--accent-soft); border-color: rgba(0,102,204,0.18); color: var(--accent); }
  .stat-pill.accent b { color: var(--accent); }
  .source-link { font-weight: 600; white-space: nowrap; }
  .source-link:hover { text-decoration: none; background: rgba(0,102,204,0.14); }
  @media (max-width: 980px) { .topbar .right .stat-pill { display: none; } .topbar .right .stat-pill.accent { display: inline-block; } }
  @media (max-width: 600px) { .topbar .inner { padding:0 12px; gap:8px; } .topbar .meta { display:none; } .brand { font-size:15px; } }

  /* Layout */
  .layout {
    max-width: 1440px; margin: 0 auto; padding: 0 24px;
    display: grid; grid-template-columns: 240px minmax(0, 1fr); gap: 32px;
    align-items: start;
  }
  @media (max-width: 1200px) { .layout { grid-template-columns: 200px minmax(0, 1fr); gap: 24px; } }
  @media (max-width: 980px)  { .layout { grid-template-columns: 168px minmax(0, 1fr); gap:16px; padding: 0 12px; } }
  @media (max-width: 640px)  { .layout { grid-template-columns: 1fr; padding: 0 12px; } }
  @media (max-width: 600px)  { .layout { padding: 0 12px; } main { padding-top: 14px; } }

  /* Sidebar */
  aside.sidebar {
    position: sticky; top: 64px;
    padding: 28px 0;
    max-height: calc(100vh - 64px);
    overflow-y: auto;
  }
  @media (max-width: 640px) {
    aside.sidebar {
      position:sticky; top:52px; z-index:45; max-height:none;
      display:flex; gap:4px; overflow-x:auto; overflow-y:hidden;
      padding:8px 0; background:rgba(255,255,255,.94);
      border-bottom:1px solid var(--border-soft);
      backdrop-filter:blur(14px); -webkit-backdrop-filter:blur(14px);
    }
    .sidebar h4 { display:none; }
  }
  .sidebar h4 {
    font-size: 11px; text-transform: uppercase; letter-spacing: 0.06em;
    color: var(--muted); margin: 18px 0 6px; font-weight: 600;
  }
  /* Tabs (for country chart) */
  .card-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 10px; }
  .tabs { display: inline-flex; background: var(--bg-alt); border: 1px solid var(--border-soft);
    border-radius: 8px; padding: 2px; }
  .tabs .tab {
    background: transparent; border: 0; padding: 5px 11px;
    font-size: 12px; color: var(--muted); border-radius: 6px; cursor: pointer;
    font-family: var(--font); font-weight: 500;
  }
  .tabs .tab:hover { color: var(--text); }
  .tabs .tab.active { background: var(--bg); color: var(--text); box-shadow: var(--shadow); }
  /* Abstract panel inside paper card */
  .paper .title { cursor: pointer; }
  .paper .abstract {
    margin-top: 10px; padding: 12px 14px;
    background: var(--bg-soft); border-left: 3px solid var(--accent);
    border-radius: 0 8px 8px 0;
    font-size: 13.5px; color: var(--text-2); line-height: 1.6;
    display: none;
  }
  .paper.open .abstract { display: block; }
  .paper .abstract .kw-row { margin-bottom: 8px; display: flex; flex-wrap: wrap; gap: 6px; align-items: center; }
  .paper .abstract .kw-row .label { font-size: 11px; font-weight: 600; color: var(--muted);
    text-transform: uppercase; letter-spacing: 0.06em; margin-right: 4px; }
  .paper .abstract .kw {
    display: inline-block; padding: 2px 9px; border-radius: 999px; font-size: 11.5px;
    background: var(--bg); border: 1px solid var(--border-soft); color: var(--text-2);
    cursor: pointer;
  }
  .paper .abstract .kw:hover { border-color: var(--accent); color: var(--accent); }
  .paper .abstract .ab-text { white-space: normal; }
  .paper .abstract .empty { color: var(--muted); font-style: italic; }
  /* Similar papers section (SPECTER2) */
  .paper .abstract .similar-row { margin-top: 14px; padding-top: 12px;
    border-top: 1px dashed var(--border-soft); }
  .paper .abstract .similar-row .label { font-size: 11px; font-weight: 600;
    color: var(--muted); text-transform: uppercase; letter-spacing: 0.06em;
    display: block; margin-bottom: 8px; }
  .paper .abstract .similar-row .label .sim-meta { color: var(--muted-2);
    font-weight: 500; text-transform: none; letter-spacing: 0; }
  .paper .abstract .similar-list { display: flex; flex-direction: column; gap: 4px; }
  .paper .abstract .similar-item { all: unset; display: grid;
    grid-template-columns: 44px 1fr; gap: 10px; align-items: center;
    padding: 6px 10px; border-radius: 6px; cursor: pointer;
    border: 1px solid transparent; transition: background 0.1s, border-color 0.1s; }
  .paper .abstract .similar-item:hover { background: var(--accent-soft);
    border-color: rgba(0,102,204,0.20); }
  .paper .abstract .similar-item .sim-score { font-size: 12px; font-weight: 700;
    color: var(--accent); text-align: right; font-variant-numeric: tabular-nums; }
  .paper .abstract .similar-item .sim-text { display: flex; flex-direction: column;
    gap: 2px; min-width: 0; }
  .paper .abstract .similar-item .sim-title { font-size: 13px; color: var(--text);
    overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .paper .abstract .similar-item .sim-tags { font-size: 11px; color: var(--muted); }
  .paper .expand-hint { font-size: 11px; color: var(--muted-2); margin-left: 6px; }
  .paper.open .expand-hint::after { content: "▾"; }
  .paper:not(.open) .expand-hint::after { content: "▸"; }
  .sidebar h4:first-child { margin-top: 0; }
  .sidebar a {
    display: block; padding: 6px 10px; margin: 1px 0;
    color: var(--text-2); border-radius: 6px;
    font-size: 14px; line-height: 1.4;
    border-left: 2px solid transparent;
  }
  .sidebar a:hover { background: var(--bg-alt); text-decoration: none; color: var(--text); }
  .sidebar a.active { color: var(--accent); border-left-color: var(--accent); background: var(--accent-soft); }
  @media (max-width: 640px) {
    .sidebar a { flex:0 0 auto; border-left:0; border-bottom:2px solid transparent; padding:6px 9px; }
    .sidebar a.active { border-left-color:transparent; border-bottom-color:var(--accent); }
  }

  /* Main */
  main { padding: 28px 0 80px; min-width: 0; }
  .eyebrow { font-size: 12px; letter-spacing: 0.10em; text-transform: uppercase; color: var(--muted); font-weight: 600; }
  h1 { font-size: 40px; font-weight: 700; letter-spacing: -0.025em; margin: 6px 0 8px; }
  .lede { font-size: 19px; color: var(--text-2); max-width: 760px; margin: 0 0 28px; line-height: 1.45; }
  h2 { font-size: 24px; font-weight: 600; letter-spacing: -0.015em; margin: 0 0 4px; }
  h2 .pill {
    display: inline-block; vertical-align: middle; margin-left: 8px;
    font-size: 11px; font-weight: 600; padding: 2px 8px; border-radius: 999px;
    background: var(--accent-soft); color: var(--accent); letter-spacing: 0.02em;
    text-transform: uppercase;
  }
  .section-sub { color: var(--muted); font-size: 14px; margin: 4px 0 16px; }

  section { scroll-margin-top: 64px; padding: 28px 0; border-top: 1px solid var(--border-soft); }
  section:first-of-type { border-top: 0; padding-top: 0; }

  /* KPIs */
  .kpis { display: grid; grid-template-columns: repeat(6, minmax(0, 1fr)); gap: 12px; margin: 18px 0 8px; }
  @media (max-width: 1300px) { .kpis { grid-template-columns: repeat(3, minmax(0, 1fr)); } }
  @media (max-width: 700px)  { .kpis { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
  @media (max-width: 420px)  { .kpis { grid-template-columns: 1fr; } }
  .kpi {
    background: var(--bg-soft); border: 1px solid var(--border-soft);
    border-radius: 12px; padding: 14px 16px; position: relative;
  }
  .kpi.official { background: linear-gradient(135deg, #f5f9ff 0%, #eef3fb 100%);
    border-color: rgba(0,102,204,0.20); }
  .kpi.parsed::after { content: "PARSED"; position: absolute; top: 8px; right: 10px;
    font-size: 9px; font-weight: 700; letter-spacing: 0.08em;
    color: var(--muted-2); }
  .kpi.official::after { content: "OFFICIAL"; position: absolute; top: 8px; right: 10px;
    font-size: 9px; font-weight: 700; letter-spacing: 0.08em; color: var(--accent); }
  .kpi .v { font-size: 24px; font-weight: 600; letter-spacing: -0.02em; line-height: 1.1; }
  .kpi.official .v { color: var(--accent); }
  .kpi .l { font-size: 12px; color: var(--muted); margin-top: 4px; letter-spacing: 0.01em; }
  .kpi .e { font-size: 14px; margin-right: 4px; }
  .kpi .note { font-size: 10.5px; color: var(--muted-2); margin-top: 4px; line-height: 1.35; letter-spacing: 0; }

  /* Conference stats hero */
  .stats-hero {
    background: linear-gradient(135deg, #f8f9fc 0%, #eef3fb 60%, #ecf0fb 100%);
    border: 1px solid var(--border-soft); border-radius: 16px;
    padding: 24px 28px; margin-top: 8px;
  }
  .stats-grid {
    display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 12px;
  }
  .stats-grid.submission-grid { grid-template-columns: repeat(4, minmax(0, 1fr)); }
  @media (max-width: 1100px) { .stats-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); } }
  @media (max-width: 1100px) { .stats-grid.submission-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
  @media (max-width: 700px)  { .stats-grid, .stats-grid.submission-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
  @media (max-width: 420px)  { .stats-grid, .stats-grid.submission-grid { grid-template-columns: 1fr; } }
  .stat {
    background: rgba(255,255,255,0.78); border: 1px solid rgba(255,255,255,0.7);
    border-radius: 12px; padding: 16px 18px;
    box-shadow: var(--shadow);
  }
  .stat .v { font-size: 32px; font-weight: 700; letter-spacing: -0.025em; line-height: 1; color: var(--text); }
  .stat .v.accent { color: var(--accent); }
  .stat .v.green { color: var(--green); }
  .stat .l { font-size: 12px; color: var(--muted); margin-top: 6px; letter-spacing: 0.02em; }
  .stat .desc { font-size: 13px; color: var(--text-2); margin-top: 4px; line-height: 1.4; }
  .accept-bar { margin-top: 16px; }
  .accept-bar .row { display: flex; align-items: center; gap: 10px; font-size: 13px; color: var(--text-2); }
  .accept-bar .track {
    flex: 1; height: 8px; background: rgba(0,0,0,0.06);
    border-radius: 999px; overflow: hidden;
  }
  .accept-bar .fill { height: 100%; background: linear-gradient(90deg, #0066cc, #34c759); border-radius: 999px; }
  .scope-note {
    margin-top: 16px; padding: 14px 16px; border-radius: 12px;
    background: rgba(255,255,255,0.72); border: 1px solid rgba(0,102,204,0.14);
    color: var(--text-2); font-size: 13px; line-height: 1.55;
  }
  .scope-note strong { color: var(--text); }
  .footnote { color: var(--muted); font-size: 12px; margin-top: 14px; line-height: 1.5; }

  /* Two-column block */
  .two-col   { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1fr); gap: 16px; }
  .three-col { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1fr) minmax(0, 1fr); gap: 16px; }
  @media (max-width: 1100px) { .three-col { grid-template-columns: minmax(0, 1fr) minmax(0, 1fr); } }
  @media (max-width: 980px)  { .two-col, .three-col { grid-template-columns: 1fr; } }

  /* Cards */
  .card {
    background: var(--panel); border: 1px solid var(--border-soft);
    border-radius: 14px; padding: 18px 20px;
    transition: box-shadow 0.15s ease, border-color 0.15s ease;
  }
  .card:hover { box-shadow: var(--shadow); }
  .card h3 {
    font-size: 13px; color: var(--muted); margin: 0 0 10px;
    text-transform: uppercase; letter-spacing: 0.08em; font-weight: 600;
  }
  /* Info tooltip on chart titles */
  .info-tip {
    display: inline-flex; align-items: center; justify-content: center;
    width: 14px; height: 14px; margin-left: 6px;
    border-radius: 50%; background: var(--bg-alt); color: var(--muted);
    font-size: 9px; font-weight: 700; cursor: help;
    border: 1px solid var(--border-soft);
    text-transform: none; letter-spacing: 0; vertical-align: middle;
    position: relative;
  }
  .info-tip:hover { background: var(--accent); color: #fff; border-color: var(--accent); }
  .info-tip::after {
    content: attr(data-tip);
    position: absolute; bottom: calc(100% + 8px); left: 50%; transform: translateX(-50%);
    background: #1d1d1f; color: #fff;
    padding: 10px 12px; border-radius: 8px;
    font-size: 12px; font-weight: 500; line-height: 1.5; letter-spacing: 0;
    white-space: pre-line; width: 290px; text-align: left;
    text-transform: none;
    box-shadow: 0 4px 16px rgba(0,0,0,0.18);
    opacity: 0; visibility: hidden; pointer-events: none;
    transition: opacity 0.12s ease, visibility 0.12s ease;
    z-index: 100;
  }
  .info-tip::before {
    content: ""; position: absolute; bottom: calc(100% + 2px); left: 50%; transform: translateX(-50%);
    border: 6px solid transparent; border-top-color: #1d1d1f;
    opacity: 0; visibility: hidden; transition: opacity 0.12s ease, visibility 0.12s ease;
    z-index: 100;
  }
  .info-tip:hover::after, .info-tip:hover::before { opacity: 1; visibility: visible; }
  .info-tip.right::after { left: auto; right: 0; transform: none; }
  .info-tip.right::before { left: auto; right: 4px; transform: none; }
  .chart-box { position: relative; height: 320px; }
  .chart-box.tall { height: 460px; }
  .chart-box.xtall { height: 720px; }
  .chart-box.short { height: 240px; }

  /* Day / format stat tiles (single 6-col grid, multiple rows align cleanly) */
  .stat-grid { display: grid; grid-template-columns: repeat(6, minmax(0, 1fr)); gap: 8px; }
  .stat-grid .day-tile.row-format { grid-column: span 3; }
  .stat-grid .day-tile.row-day    { grid-column: span 2; }
  .stat-grid .day-tile.row-df     { grid-column: span 1; }
  @media (max-width: 900px) {
    .stat-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
    .stat-grid .day-tile.row-format,
    .stat-grid .day-tile.row-day,
    .stat-grid .day-tile.row-df { grid-column: span 1; }
  }
  .day-tile {
    flex: 1; display: flex; align-items: center; gap: 12px;
    padding: 12px 16px; border-radius: 10px;
    background: var(--bg-soft); border: 1px solid var(--border-soft);
    cursor: pointer; transition: background 0.1s ease, border-color 0.1s ease, transform 0.08s ease;
    text-align: left; font-family: var(--font);
  }
  .day-tile:hover { background: #fff; border-color: var(--border); transform: translateY(-1px); }
  .day-tile.matched { box-shadow: 0 0 0 2px rgba(255,196,0,0.55); border-color: rgba(180,120,0,0.6); background: rgba(255,196,0,0.10); }
  .day-tile.compact { padding: 9px 12px; gap: 8px; }
  .day-tile.compact .d { font-size: 10px; padding: 3px 8px; }
  .day-tile.compact .n { font-size: 17px; }
  .day-tile.compact .l { font-size: 10px; }
  .day-tile .d { font-size: 11px; font-weight: 600; letter-spacing: 0.08em;
    text-transform: uppercase; color: #fff; padding: 4px 10px; border-radius: 999px; white-space: nowrap; }
  .day-tile.mon        .d { background: var(--green); }
  .day-tile.tue        .d { background: #2563eb; }
  .day-tile.wed        .d { background: var(--purple); }
  .day-tile.oral       .d { background: var(--orange); }
  .day-tile.interactive .d { background: #008080; }
  .day-tile .n { font-size: 22px; font-weight: 600; letter-spacing: -0.02em; line-height: 1.1; }
  .day-tile .l { font-size: 11px; color: var(--muted); }
  .day-tile .info { margin-left: auto; }
  .day-tile.label-only { background: transparent; border: 0; flex: 0 0 auto; padding: 0 4px; cursor: default; }
  .day-tile.label-only:hover { transform: none; background: transparent; }
  /* Trend cards */
  .trend-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; }
  @media (max-width: 1100px) { .trend-grid { grid-template-columns: repeat(3, 1fr); } }
  @media (max-width: 700px) { .trend-grid { grid-template-columns: repeat(2, 1fr); } }
  .trend {
    background: var(--bg); border: 1px solid var(--border-soft);
    border-radius: 12px; padding: 14px 16px;
    cursor: pointer; transition: all 0.12s ease;
    position: relative;
  }
  .trend:hover { border-color: var(--accent); box-shadow: var(--shadow); transform: translateY(-1px); }
  .trend .t { font-size: 13px; color: var(--text-2); font-weight: 500; }
  .trend .n { font-size: 26px; font-weight: 700; letter-spacing: -0.02em; line-height: 1.1; margin-top: 6px; }
  .trend .pct { font-size: 12px; color: var(--green); margin-top: 2px; font-weight: 500; }
  .trend.rank-1 { background: linear-gradient(135deg, #fff, #fff2e6); }
  .trend.rank-2 { background: linear-gradient(135deg, #fff, #f0f6ff); }
  .trend.rank-3 { background: linear-gradient(135deg, #fff, #f3f0ff); }

  /* Search toolbar */
  .toolbar {
    display: grid; gap: 10px;
    background: var(--bg-soft); border: 1px solid var(--border-soft);
    border-radius: 12px; padding: 12px 14px;
  }
  .toolbar-row { display: flex; gap: 8px; flex-wrap: wrap; align-items: center; }
  .toolbar-row + .toolbar-row { padding-top: 10px; border-top: 1px solid var(--border-soft); }
  .toolbar-row.view-row { gap: 10px; }
  .toolbar input[type=text], .toolbar select {
    background: var(--bg); color: var(--text);
    border: 1px solid var(--border); border-radius: 8px;
    padding: 9px 12px; font-size: 14px; outline: none;
    font-family: var(--font);
  }
  .search-group { display: flex; gap: 8px; width: 100%; min-width: 0; }
  .search-group input[type=text] { min-width: 0; flex: 1; }
  .search-group select { flex: 0 0 auto; }
  .filter-row select { flex: 1 1 150px; min-width: 140px; }
  .filter-row #affFilter { flex-basis: 230px; }
  .view-row #sortFilter { flex: 1 1 260px; min-width: 220px; }
  .view-row #pageSizeFilter { flex: 0 1 130px; }
  .toolbar input[type=text]::placeholder { color: var(--muted-2); }
  .toolbar input[type=text]:focus, .toolbar select:focus {
    border-color: var(--accent); box-shadow: 0 0 0 4px var(--accent-soft);
  }
  @media (max-width: 760px) {
    .toolbar-row, .search-group { min-width:0; max-width:100%; }
    .search-group { flex-wrap: wrap; }
    .search-group input[type=text] { flex-basis: 100%; }
    .toolbar input[type=text], .toolbar select { width:100%; max-width:100%; }
    .filter-row select, .view-row #sortFilter, .view-row #pageSizeFilter { flex: 1 1 100%; min-width: 0; }
  }
  .toolbar .count { color: var(--muted); font-size: 13px; margin-left: auto; }
  @media (max-width: 760px) { .toolbar .count { margin-left:0; } }
  .btn-clear {
    background: var(--bg); color: var(--text); border: 1px solid var(--border);
    border-radius: 8px; padding: 8px 12px; font-size: 13px; cursor: pointer;
    font-family: var(--font); font-weight: 500;
  }
  .btn-clear:hover { background: var(--bg-alt); }
  #clearFilters {
    background: rgba(255,55,95,0.08);
    color: #b42346;
    border-color: rgba(255,55,95,0.28);
  }
  #clearFilters:hover {
    background: rgba(255,55,95,0.15);
    border-color: rgba(255,55,95,0.42);
  }
  .active-filters { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 10px; }
  .active-chip {
    display: inline-flex; align-items: center; gap: 6px;
    background: var(--accent-soft); color: var(--accent);
    border: 1px solid rgba(0,102,204,0.2);
    border-radius: 999px; padding: 3px 10px; font-size: 12px;
    cursor: pointer; transition: background 0.1s ease;
  }
  .active-chip:hover { background: rgba(0,102,204,0.16); }
  .active-chip .x { font-size: 14px; line-height: 1; opacity: 0.65; }

  /* Chips */
  .chip {
    display: inline-block; padding: 2px 9px; border-radius: 999px;
    font-size: 11px; font-weight: 600; letter-spacing: 0.02em;
    background: var(--accent-soft); color: var(--accent);
    border: 1px solid rgba(0,102,204,0.15);
  }
  .chip.mon { background: rgba(36,138,61,0.10); color: var(--green); border-color: rgba(36,138,61,0.25); }
  .chip.tue { background: rgba(37,99,235,0.10); color: #1d4ed8; border-color: rgba(37,99,235,0.25); }
  .chip.wed { background: rgba(110,58,214,0.10); color: var(--purple); border-color: rgba(110,58,214,0.25); }
  .chip.tag { background: rgba(192,24,92,0.07); color: var(--pink); border-color: rgba(192,24,92,0.20); }
  .chip.oral        { background: rgba(178,80,0,0.10);  color: var(--orange); border-color: rgba(178,80,0,0.28); }
  .chip.interactive { background: rgba(0,128,128,0.10); color: #008080;       border-color: rgba(0,128,128,0.30); }
  .chip.latebreak   { background: rgba(110,170,30,0.12);color: #4a7000;       border-color: rgba(110,170,30,0.35); }
  .chip.kw  { background: rgba(0,102,204,0.07); color: var(--accent); border-color: rgba(0,102,204,0.22); }
  .chip.clickable { cursor: pointer; transition: background 0.1s ease, transform 0.08s ease; }
  .chip.clickable:hover { transform: translateY(-1px); }
  .chip.tag.clickable:hover { background: rgba(192,24,92,0.14); border-color: rgba(192,24,92,0.4); }
  .chip.kw.clickable:hover  { background: rgba(0,102,204,0.14); border-color: rgba(0,102,204,0.45); }
  .chip.mon.clickable:hover { background: rgba(36,138,61,0.18); border-color: rgba(36,138,61,0.4); }
  .chip.tue.clickable:hover { background: rgba(37,99,235,0.18); border-color: rgba(37,99,235,0.4); }
  .chip.wed.clickable:hover { background: rgba(110,58,214,0.18); border-color: rgba(110,58,214,0.4); }

  /* Paper list */
  .papers { display: grid; gap: 10px; margin-top: 14px; }
  .paper {
    background: var(--panel); border: 1px solid var(--border-soft);
    border-radius: 12px; padding: 14px 16px;
    transition: border-color 0.12s ease, box-shadow 0.12s ease;
  }
  .paper:hover { border-color: var(--border); box-shadow: var(--shadow); }
  .paper .meta { display: flex; gap: 8px; flex-wrap: wrap; align-items: center;
    font-size: 12px; color: var(--muted); margin-bottom: 6px; }
  .paper .meta .dot { color: var(--border); }
  .paper .title { font-size: 15.5px; font-weight: 600; line-height: 1.38;
    color: var(--text); }
  .paper .authors { font-size: 13px; color: var(--text-2); margin-top: 8px; line-height: 1.55; }
  .paper .authors b { color: var(--text); font-weight: 600; }
  .paper .authors b.clickable, .paper .authors .aff.clickable {
    cursor: pointer; transition: color 0.1s ease, background 0.1s ease;
    border-radius: 3px; padding: 0 2px;
  }
  .paper .authors b.clickable:hover { color: var(--accent); background: var(--accent-soft); }
  .paper .authors .aff.clickable:hover { color: var(--accent); background: var(--accent-soft); }
  .paper .authors .aff { color: var(--muted); }
  .paper .authors .sep { color: var(--border); margin: 0 4px; }
  .paper mark { background: rgba(255,196,0,0.32); color: var(--text); padding: 0 2px; border-radius: 3px; }
  /* Active-filter highlight: applied to chips / aff spans / day chips when
     they match the currently active country/aff/topic/day filter. */
  .paper .chip.matched,
  .paper .aff.matched,
  .paper .authors b.matched {
    background: rgba(255,196,0,0.42) !important;
    color: var(--text) !important;
    border-color: rgba(180,120,0,0.6) !important;
    box-shadow: 0 0 0 1px rgba(255,196,0,0.55);
  }

  .pager { display: flex; gap: 6px; justify-content: center; margin-top: 18px; align-items: center; }
  .pager button {
    background: var(--panel); color: var(--text); border: 1px solid var(--border);
    border-radius: 8px; padding: 7px 14px; font-size: 13px; cursor: pointer;
    font-family: var(--font); font-weight: 500;
  }
  .pager button:hover:not(:disabled) { background: var(--bg-alt); }
  .pager button:disabled { opacity: 0.4; cursor: default; }
  .pager .info { color: var(--muted); font-size: 13px; padding: 6px 10px; }

  /* Method note */
  .note {
    background: var(--bg-soft); border-left: 3px solid var(--accent);
    padding: 12px 16px; border-radius: 0 8px 8px 0;
    font-size: 13px; color: var(--text-2); margin-top: 14px;
  }
  .note b { color: var(--text); }

  footer { color: var(--muted); font-size: 12px; text-align: center;
    padding: 32px 0; border-top: 1px solid var(--border-soft); margin-top: 40px; }
  footer .credit { color: var(--text-2); font-weight: 600; margin-bottom: 6px; }

  /* Country × Topic heatmap */
  .heatmap { display: grid; gap: 2px; font-size: 11px; min-width: 760px;
             grid-template-columns: 130px repeat(var(--cols, 20), minmax(28px, 1fr)); }
  .heatmap .corner { grid-column: 1; }
  .heatmap .colhead { writing-mode: vertical-rl; transform: rotate(180deg);
                      padding: 6px 2px; text-align: left; color: var(--text-2);
                      font-size: 10.5px; line-height: 1.1; cursor: pointer;
                      white-space: nowrap; user-select: none;
                      border-bottom: 1px solid var(--border-soft); }
  .heatmap .colhead:hover { color: var(--accent); }
  .heatmap .rowhead { padding: 6px 10px 6px 4px; text-align: right;
                      color: var(--text); font-weight: 500; cursor: pointer;
                      white-space: nowrap; user-select: none;
                      border-right: 1px solid var(--border-soft); font-size: 11.5px; }
  .heatmap .rowhead:hover { color: var(--accent); }
  .heatmap .cell { aspect-ratio: 1 / 1; min-height: 28px; border-radius: 3px;
                   display: flex; align-items: center; justify-content: center;
                   color: var(--text); font-size: 9.5px; font-weight: 600;
                   cursor: pointer; transition: outline 0.1s, transform 0.08s;
                   outline: 1px solid transparent; }
  .heatmap .cell:hover { outline: 2px solid var(--accent); transform: scale(1.08); z-index: 2; }
  .heatmap .cell.empty { background: var(--bg-alt); color: var(--muted-2); }
  .heatmap .cell .v { pointer-events: none; }
  /* Use white text on darker cells (intensity > 0.55) */
  .heatmap .cell.dark { color: #fff; }

  /* PI / Lab radar */
  .lab-toolbar { display:flex; gap:12px; flex-wrap:wrap; align-items:center; margin:16px 0 12px; }
  .lab-toolbar input {
    flex:1 1 260px; min-width:0; height:42px; padding:0 13px;
    appearance:none; border:1px solid var(--border); border-radius:10px;
    background:var(--panel); color:var(--text); font:inherit; font-size:13px;
    box-shadow:0 1px 2px rgba(0,0,0,.03); transition:.15s ease;
  }
  .lab-toolbar input::placeholder { color:var(--muted-2); }
  .lab-toolbar input:focus { outline:3px solid rgba(0,102,204,.16); border-color:var(--accent); }
  .lab-tabs {
    display:inline-flex; gap:3px; flex-wrap:wrap; padding:4px;
    background:var(--bg-alt); border:1px solid var(--border-soft); border-radius:12px;
  }
  .lab-tabs .tab {
    appearance:none; border:1px solid transparent; border-radius:8px;
    background:transparent; color:var(--text-2); padding:9px 12px;
    font:inherit; font-size:12px; line-height:1.2; font-weight:650;
    white-space:nowrap; cursor:pointer; transition:background .15s ease,color .15s ease,box-shadow .15s ease,transform .15s ease;
  }
  .lab-tabs .tab:hover { color:var(--accent); background:rgba(255,255,255,.78); }
  .lab-tabs .tab:active { transform:translateY(1px); }
  .lab-tabs .tab.active {
    color:#fff; background:var(--accent); border-color:var(--accent);
    box-shadow:0 2px 8px rgba(0,102,204,.24);
  }
  .lab-tabs .tab:focus-visible { outline:3px solid rgba(0,102,204,.22); outline-offset:2px; }
  @media (max-width:760px) {
    .lab-tabs { width:100%; }
    .lab-tabs .tab { flex:1 1 100%; }
    .lab-toolbar input { flex-basis:100%; }
  }
  .lab-grid { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:12px; }
  @media (max-width:900px) { .lab-grid { grid-template-columns:1fr; } }
  .lab-card { min-width:0; width:100%; overflow:hidden; text-align:left; cursor:pointer; background:var(--panel); border:1px solid var(--border-soft); border-radius:14px; padding:16px; color:var(--text); transition:.15s ease; }
  .lab-card:hover, .lab-card.selected { border-color:var(--accent); box-shadow:var(--shadow); transform:translateY(-1px); }
  .lab-card-head { display:flex; justify-content:space-between; gap:12px; align-items:flex-start; }
  .lab-name { font-size:16px; font-weight:700; letter-spacing:-.01em; }
  .lab-aff { color:var(--muted); font-size:12px; margin-top:3px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; max-width:360px; }
  .tier-badge { flex:0 0 auto; border-radius:999px; padding:3px 8px; font-size:11px; font-weight:700; }
  .tier-S { color:#8a3d00; background:#fff0df; } .tier-A { color:#0066cc; background:var(--accent-soft); } .tier-B { color:#5b5b60; background:var(--bg-alt); }
  .tier-badge .stars { letter-spacing:1px; font-size:12px; }
  .lab-metrics-mini { display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:6px; margin:12px 0; }
  @media (max-width:520px) { .lab-card-head { flex-wrap:wrap; } .lab-metrics-mini { grid-template-columns:repeat(2,minmax(0,1fr)); } }
  .lab-metric-mini { background:var(--bg-soft); border-radius:8px; padding:8px; }
  .lab-metric-mini b { display:block; font-size:17px; } .lab-metric-mini span { display:block; color:var(--muted); font-size:10px; margin-top:2px; }
  .lab-line { color:var(--text-2); font-size:12px; line-height:1.45; margin-top:7px; }
  .lab-line strong { color:var(--muted); font-size:10px; letter-spacing:.05em; text-transform:uppercase; margin-right:5px; }
  .lab-rep { margin-top:5px; color:var(--muted); font-size:11px; line-height:1.4; overflow-wrap:anywhere; }
  .lab-detail { margin-top:18px; border:1px solid rgba(0,102,204,.24); background:linear-gradient(135deg,#fbfdff,#f5f9ff); border-radius:16px; padding:22px; }
  .lab-detail[hidden] { display:none; }
  .lab-detail-head { display:flex; align-items:flex-start; justify-content:space-between; gap:16px; }
  @media (max-width:600px) { .lab-detail { padding:16px; } .lab-detail-head { flex-wrap:wrap; } .lab-detail-head .btn-clear { width:100%; } }
  .lab-detail h3 { margin:0; color:var(--text); font-size:22px; text-transform:none; letter-spacing:-.015em; }
  .lab-kpis { display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:10px; margin:16px 0; }
  @media (max-width:650px) { .lab-kpis { grid-template-columns:repeat(2,minmax(0,1fr)); } }
  .lab-kpi { background:rgba(255,255,255,.85); border:1px solid var(--border-soft); border-radius:10px; padding:12px; }
  .lab-kpi b { font-size:24px; display:block; } .lab-kpi span { color:var(--muted); font-size:11px; }
  .lab-detail-grid { display:grid; grid-template-columns:minmax(0,1fr) minmax(0,1fr); gap:14px; }
  @media (max-width:850px) { .lab-detail-grid { grid-template-columns:1fr; } }
  .lab-panel { background:rgba(255,255,255,.82); border:1px solid var(--border-soft); border-radius:12px; padding:15px; min-width:0; }
  .lab-panel h4 { margin:0 0 10px; font-size:12px; color:var(--muted); text-transform:uppercase; letter-spacing:.07em; }
  .theme-chips { display:flex; gap:6px; flex-wrap:wrap; }
  .theme-chip { border-radius:999px; background:var(--accent-soft); color:var(--accent); padding:5px 9px; font-size:12px; font-weight:600; }
  .kw-bars { display:grid; gap:7px; }
  .kw-bar-row { display:grid; grid-template-columns:minmax(90px,1.4fr) 2fr 28px; gap:8px; align-items:center; font-size:11px; }
  .kw-bar-row .track { height:7px; background:var(--bg-alt); border-radius:999px; overflow:hidden; }
  .kw-bar-row .fill { height:100%; background:var(--accent); border-radius:999px; }
  .coauthor-net { width:100%; height:270px; display:block; }
  .coauthor-net .edge { stroke:#c8d8ea; stroke-width:1.5; }
  .coauthor-net .node { fill:#fff; stroke:var(--accent); stroke-width:1.5; }
  .coauthor-net .pi-node { fill:var(--accent); stroke:var(--accent); }
  .coauthor-net text { font-size:10px; fill:var(--text-2); text-anchor:middle; }
  .coauthor-net .pi-label { fill:#fff; font-weight:700; }
  .lab-papers { display:grid; gap:8px; margin-top:14px; }
  .lab-paper { background:#fff; border:1px solid var(--border-soft); border-radius:10px; padding:11px 12px; cursor:pointer; }
  .lab-paper:hover { border-color:var(--accent); }
  .lab-paper.rep { border-left:3px solid var(--accent); }
  .lab-paper .meta { color:var(--muted); font-size:11px; margin-bottom:4px; }
  .lab-paper .t { font-size:13px; font-weight:600; line-height:1.4; }
  .overlap-high { color:var(--green); } .overlap-medium { color:var(--accent); } .overlap-expand { color:var(--purple); }
</style>
</head>
<body>

<div class="topbar">
  <div class="inner">
    <a class="brand" id="brandHome" href="#overview" title="Reset filters and return to home">IROS 2026<span class="dot"> · </span>Paper Explorer</a>
    <div class="meta">Pittsburgh, USA · September 28–30 paper program</div>
    <div class="right">
      <span class="stat-pill"><b>1,933</b> papers</span>
      <span class="stat-pill"><b>3</b> program days</span>
      <a class="stat-pill accent source-link" href="https://2026.ieee-iros.org/program/paper_index/" target="_blank" rel="noopener" aria-label="Open the official IROS 2026 Paper and Author Index">Official source ↗</a>
    </div>
  </div>
</div>

<div class="layout">

  <aside class="sidebar">
    <h4>Overview</h4>
    <a href="#overview" class="active">Introduction</a>
    <a href="#submissions">Submissions &amp; acceptance</a>
    <a href="#stats">Conference statistics</a>
    <h4>Trends</h4>
    <a href="#kw-trends">Author keywords</a>
    <a href="#trends">Hot topics</a>
    <h4>EDA</h4>
    <a href="#eda-aff">Top institutions</a>
    <a href="#eda-country">Institution region</a>
    <a href="#eda-heatmap">Country × Topic</a>
    <a href="#eda-misc">Day · authors</a>
    <h4>Research Radar</h4>
    <a href="#lab-radar">PI / Lab Radar</a>
    <h4>Search</h4>
    <a href="#search">Find papers</a>
  </aside>

  <main>

    <section id="overview">
      <div class="eyebrow">2026 IEEE/RSJ IROS · International Conference on Intelligent Robots and Systems</div>
      <h1>Paper Explorer</h1>
      <p class="lede">Search and explore all <span id="lede-count">…</span> indexed papers across Monday · Tuesday · Wednesday — with authors, affiliations, keywords, sessions, and topic-level trend infographics.</p>
      <div class="kpis" id="kpis"></div>
    </section>

    <section id="submissions">
      <h2>Submissions &amp; acceptance <span class="pill">Contributed papers</span></h2>
      <div class="section-sub">The acceptance figures and the final program index measure different populations.</div>
      <div class="stats-hero">
        <div class="stats-grid submission-grid">
          <div class="stat">
            <div class="v">4,348</div>
            <div class="l">SUBMISSIONS</div>
            <div class="desc">Contributed papers received</div>
          </div>
          <div class="stat">
            <div class="v accent">1,585</div>
            <div class="l">ACCEPTED</div>
            <div class="desc">Accepted contributed papers</div>
          </div>
          <div class="stat">
            <div class="v green">36%</div>
            <div class="l">ACCEPTANCE RATE</div>
            <div class="desc">Official rounded rate (36.45% exact)</div>
          </div>
          <div class="stat">
            <div class="v">1,933</div>
            <div class="l">PROGRAM INDEX</div>
            <div class="desc">All papers in the final Paper &amp; Author Index</div>
          </div>
        </div>
        <div class="accept-bar">
          <div class="row"><span>Accepted contributed papers</span><div class="track"><div class="fill" style="width:36.45%"></div></div><b>1,585 / 4,348</b></div>
        </div>
        <div class="scope-note"><strong>Why does the program list 1,933 papers?</strong> The 1,585 figure covers only papers submitted directly as IROS contributed papers. The final technical program can additionally include eligible IEEE RAS/IES journal papers presented at IROS, together with final program changes. The difference of 348 is therefore a <strong>net difference between two scopes</strong>, not by itself an exact count of journal papers.</div>
        <div class="footnote">Sources: IROS 2026 acceptance decision letters issued June 17, 2026; <a href="https://2026.ieee-iros.org/program/paper_index/" target="_blank" rel="noopener">official Paper &amp; Author Index</a>; <a href="https://www.ieee-ras.org/publications/ieee-robotics-and-automation-letters/" target="_blank" rel="noopener">IEEE RAS journal conference-presentation policy</a>.</div>
      </div>
    </section>

    <section id="stats">
      <h2>Index coverage <span class="pill">Official program</span></h2>
      <div class="section-sub">Coverage parsed from the official IROS 2026 Paper &amp; Author Index.</div>
      <div class="stats-hero">
        <div class="stats-grid">
          <div class="stat">
            <div class="v">1,933</div>
            <div class="l">PAPERS</div>
            <div class="desc">Unique indexed paper numbers</div>
          </div>
          <div class="stat">
            <div class="v accent">1,311</div>
            <div class="l">LIGHTNING TALKS</div>
            <div class="desc">Papers in lightning-talk sessions</div>
          </div>
          <div class="stat">
            <div class="v green">579</div>
            <div class="l">FOCUSED SESSIONS</div>
            <div class="desc">Papers in focused sessions</div>
          </div>
          <div class="stat">
            <div class="v">32</div>
            <div class="l">AWARD CANDIDATES</div>
            <div class="desc">Papers in award-candidate sessions</div>
          </div>
          <div class="stat">
            <div class="v">11</div>
            <div class="l">SPECIAL SESSIONS</div>
            <div class="desc">Papers in special sessions</div>
          </div>
        </div>
        <div class="footnote" id="parsed-footnote"></div>
      </div>
    </section>

    <section id="kw-trends">
      <h2>Author-declared keywords<span class="info-tip" data-tip="Keywords assigned by the paper authors themselves at submission time, drawn from PaperPlaza's controlled vocabulary (~150 categories).&#10;&#10;Each paper typically declares 2–3 keywords, so the same paper appears under multiple bars. Click a bar to filter the paper list below.">i</span></h2>
      <div class="section-sub"><b>Ground-truth tagging</b> — assigned by the authors themselves at submission, from PaperPlaza's controlled vocabulary of ~150 categories. Each paper declares 2–3 keywords. More accurate (and more granular) than the regex-based Hot topics below. Click a bar to filter.</div>
      <div class="card" style="margin-top:8px">
        <div class="card-header">
          <h3 style="margin:0">Top keywords</h3>
          <div class="tabs">
            <button class="tab active" data-kwview="30">Top 30</button>
            <button class="tab" data-kwview="60">Top 60</button>
            <button class="tab" data-kwview="all">All</button>
          </div>
        </div>
        <div class="chart-box" id="kwBarBox" style="height:auto;min-height:780px"><canvas id="kwBar"></canvas></div>
      </div>
    </section>

    <section id="trends">
      <h2>Hot topics<span class="info-tip" data-tip="Each paper title is matched against 32 hand-curated regex patterns (keywords + their plurals / variants). The taxonomy is NOT learned from the data.&#10;&#10;Multi-label: a paper can match several topics simultaneously, so percentages can sum above 100%.">i</span></h2>
      <div class="section-sub"><b>Auto-tagged</b> from paper titles only via 32 hand-curated regex patterns — a coarse view of the broad themes at the conference. Multi-label: a paper can match several topics, so percentages can sum above 100%. ~22% of papers (~641) match no topic at all — partly niche subjects the taxonomy doesn't cover (e.g. formal methods, KAN, novel sensors), but also papers whose title phrasing the naive regex simply failed to catch. For granular and accurate tagging use the <a href="#kw-trends">author-declared keywords above</a>.</div>
      <div class="card" style="margin-top:8px"><div class="chart-box xtall"><canvas id="topicBar"></canvas></div></div>
    </section>

    <section id="eda-aff">
      <h2>Institutions · Regions</h2>
      <div class="section-sub">Counting rule: each paper contributes at most +1 per canonical institution and at most +1 per canonical institution region. Raw affiliation strings are first normalized through the institution alias / multimap layer. Bar / doughnut color is keyed to the region's overall rank, so the same region appears in the same color across both charts. Hover the <span style="display:inline-block;width:13px;height:13px;border-radius:50%;background:var(--bg-alt);color:var(--muted);font-size:9px;font-weight:700;line-height:13px;text-align:center;border:1px solid var(--border-soft);vertical-align:middle">i</span> next to a chart title for full details.</div>
      <div class="two-col" style="margin-top:8px">
        <div class="card">
          <h3>Top 20 institutions<span class="info-tip" data-tip="Counting method: per-paper unique canonical institution.&#10;Each paper contributes at most +1 to a given institution after alias canonicalization and exact multimap splitting.&#10;&#10;Example: a paper with 4 Tsinghua authors + 1 MIT author counts as Tsinghua +1, MIT +1.&#10;&#10;Bar color = the institution's inferred region, matching the chart on the right.">i</span></h3>
          <div class="chart-box tall"><canvas id="affChart"></canvas></div>
        </div>
        <div id="eda-country" class="card">
          <div class="card-header">
            <h3 style="margin:0">Institution region<span class="info-tip" data-tip="Counting method: per-paper unique canonical institution region.&#10;Each paper contributes at most +1 to a given region, regardless of how many of its authors use institutions from that region.&#10;&#10;A paper with co-authors from China + USA counts as China +1, USA +1 — interpret as 'papers with at least one institution from this region'.&#10;&#10;Region is inferred after institution canonicalization; unmatched entries fall into 'Other' (excluded from this chart).">i</span></h3>
            <div class="tabs">
              <button class="tab active" data-view="donut">Top 15 · Doughnut</button>
              <button class="tab" data-view="bar15">Top 15 · Bar</button>
            </div>
          </div>
          <div class="chart-box tall" id="countryDonutBox"><canvas id="countryDonut"></canvas></div>
          <div class="chart-box tall" id="countryBarBox" style="display:none"><canvas id="countryBar"></canvas></div>
        </div>
      </div>
    </section>

    <section id="eda-heatmap">
      <div class="card-header" style="align-items:flex-end">
        <h2 style="margin:0">Country × Topic<span class="info-tip" data-tip="Heatmap of papers across countries (rows) and topics (columns).&#10;&#10;A paper with co-authors from China + USA on a 'Manipulation' topic counts +1 for both China×Manipulation AND USA×Manipulation. Multi-label: a paper can also belong to several topics.&#10;&#10;Modes:&#10; Row %: each row sums to ~100% — shows what each country specializes in.&#10; Col %: each column sums to ~100% — shows which countries dominate each topic.&#10; Absolute: raw counts, dynamic range compressed via square-root scaling.&#10;&#10;Click any cell to drill down.">i</span></h2>
        <div class="tabs">
          <button class="tab active" data-heatview="row">Row %</button>
          <button class="tab" data-heatview="col">Col %</button>
          <button class="tab" data-heatview="abs">Absolute</button>
        </div>
      </div>
      <div class="section-sub">Top 15 countries × Top 20 auto-tagged topics. Click a cell to filter the paper list. Click a row/column label to apply that filter alone.</div>
      <div class="card" style="margin-top:8px;overflow-x:auto">
        <div id="heatmapGrid" class="heatmap"></div>
      </div>
    </section>

    <section id="eda-misc">
      <h2>Day · authors</h2>
      <div class="section-sub">Papers per day · authors per paper distribution.</div>
      <div class="card" style="margin-top:8px">
        <div class="stat-grid" id="statGrid"></div>
        <div style="margin-top:18px;border-top:1px solid var(--border-soft);padding-top:14px">
          <h3 style="margin:0 0 8px">Authors per paper<span class="info-tip" data-tip="Distribution of the number of authors per paper. The mean is around 5.2 authors per paper across the conference.">i</span></h3>
          <div class="chart-box short"><canvas id="authorsChart"></canvas></div>
        </div>
      </div>
    </section>

    <section id="lab-radar">
      <h2>PI / Lab Radar <span class="pill">100 recommended PIs</span></h2>
      <div class="section-sub">Switch from papers to research programs. <strong>★★★ / ★★ / ★ indicates APRL relevance only</strong>—how closely each group's indexed IROS 2026 work connects to APRL's radar priorities: 3D perception, persistent mapping/localization, navigation, embodied AI/VLA, multi-robot systems, and physical intelligence. It is not an evaluation or ranking of the PI or lab. Last-author is a useful but imperfect PI proxy.</div>
      <div class="lab-toolbar">
        <div class="lab-tabs" id="labTierTabs">
          <button class="tab active" data-labtier="S">★★★ · closest (20)</button>
          <button class="tab" data-labtier="A">★★ · adjacent (30)</button>
          <button class="tab" data-labtier="B">★ · broader radar (50)</button>
          <button class="tab" data-labtier="all">All 100</button>
        </div>
        <input type="text" id="labSearch" placeholder="Search PI, affiliation, theme, or paper title…" aria-label="Search recommended PIs" />
      </div>
      <div class="footnote" id="labCount"></div>
      <div class="lab-grid" id="labGrid"></div>
      <div class="lab-detail" id="labDetail" hidden></div>
    </section>

    <section id="search">
      <h2>Find papers</h2>
      <div class="section-sub">Searches across titles, authors, raw affiliations, canonical institutions, rooms, sessions, topics, and author-declared keywords. Use up to three search conditions with AND / OR.</div>
      <div class="toolbar">
        <div class="toolbar-row search-row">
          <div class="search-group" role="group" aria-label="Search conditions">
            <input type="text" id="q" placeholder="Search 1: gaussian splatting" autocomplete="off"/>
            <select id="searchMode" title="Combine search conditions">
              <option value="and" selected>AND</option>
              <option value="or">OR</option>
            </select>
            <input type="text" id="q2" placeholder="Search 2" autocomplete="off"/>
            <input type="text" id="q3" placeholder="Search 3" autocomplete="off"/>
          </div>
        </div>
        <div class="toolbar-row filter-row">
          <select id="dayFilter">
            <option value="">All days</option>
            <option value="Monday">Monday</option>
            <option value="Tuesday">Tuesday</option>
            <option value="Wednesday">Wednesday</option>
          </select>
          <select id="sessionTypeFilter">
            <option value="">All formats</option>
            <option value="Lightning Talks">Lightning Talks</option>
            <option value="Focused Sessions">Focused Sessions</option>
            <option value="Award Candidates">Award Candidates</option>
            <option value="Special Sessions">Special Sessions</option>
          </select>
          <select id="topicFilter">
            <option value="">All topics</option>
          </select>
          <select id="countryFilter">
            <option value="">Institution region</option>
          </select>
          <select id="affFilter">
            <option value="">All institutions</option>
          </select>
        </div>
        <div class="toolbar-row view-row">
          <select id="sortFilter" title="Sort the filtered results">
            <option value="default" selected>Sort: Program order</option>
            <option value="shuffle">Sort: Shuffle</option>
            <option value="title-asc">Title A → Z</option>
            <option value="title-desc">Title Z → A</option>
            <option value="authors-desc"># Authors (most first)</option>
            <option value="authors-asc"># Authors (fewest first)</option>
            <option value="affs-desc"># Institutions (most first)</option>
            <option value="affs-asc"># Institutions (fewest first)</option>
            <option value="countries-desc"># Regions (most first)</option>
            <option value="countries-asc"># Regions (fewest first)</option>
            <option value="keywords-desc"># Keywords (most first)</option>
            <option value="keywords-asc"># Keywords (fewest first)</option>
            <option value="title-len-desc">Title length (long first)</option>
            <option value="title-len-asc">Title length (short first)</option>
          </select>
          <button id="shuffleResults" class="btn-clear" title="Shuffle the current result list">Shuffle</button>
          <select id="pageSizeFilter" title="Results per page">
            <option value="50">50 / page</option>
            <option value="100">100 / page</option>
            <option value="250">250 / page</option>
            <option value="500" selected>500 / page</option>
            <option value="1000">1000 / page</option>
            <option value="2000">2000 / page</option>
          </select>
          <button id="clearFilters" class="btn-clear" title="Clear all filters">Clear</button>
          <span class="count" id="count"></span>
        </div>
      </div>
      <div id="activeFilters" class="active-filters"></div>
      <div class="papers" id="papers"></div>
      <div class="pager" id="pager"></div>
    </section>

    <footer>
      <div class="credit">Made by <a href="https://aprl.dgist.ac.kr" target="_blank" rel="noopener">Giseop Kim</a></div>
      Source: official IROS 2026 Paper &amp; Author Index. Generated <span id="genDate"></span>.
    </footer>

  </main>
</div>

<script id="papers-data" type="application/json">__PAPERS_JSON__</script>
<script id="similar-data" type="application/json">__SIMILAR_JSON__</script>
<script>
const ALL_PAPERS = JSON.parse(document.getElementById('papers-data').textContent);
const PAPERS = ALL_PAPERS;
// SPECTER2-based pre-computed top-K similar papers per paper code.
const SIMILAR_PAPERS = (() => {
  const el = document.getElementById('similar-data');
  try { return el ? JSON.parse(el.textContent) : {}; } catch (_) { return {}; }
})();
const PAPER_BY_CODE = new Map(PAPERS.map(p => [p.code, p]));
function normalizeSearchText(s) {
  return String(s || "").toLowerCase().replace(/\s+/g, " ").trim();
}

// Hong Kong / Macau folded into China per requirement.
const COUNTRY_HINTS = __COUNTRY_HINTS_JSON__;
// Exact-match overrides for affiliations that were verified (by parallel
// classification agents). When a paper's affiliation string matches a key here
// EXACTLY, that country wins over the regex hints below.
const COUNTRY_OVERRIDES = __COUNTRY_OVERRIDES_JSON__;
const INSTITUTION_ALIASES_RAW = __INSTITUTION_ALIASES_JSON__;
const INSTITUTION_MULTIMAP_RAW = __INSTITUTION_MULTIMAP_JSON__;
const INSTITUTION_COUNTRIES = __INSTITUTION_COUNTRIES_JSON__;
const SITE_COUNTRY_OVERRIDES_RAW = __INSTITUTION_SITE_COUNTRY_OVERRIDES_JSON__;
const PARENT_ORG = __INSTITUTION_PARENT_ORG_JSON__;

function normalizeAffiliationText(text) {
  let normalized = String(text || "");
  if (typeof normalized.normalize === "function") normalized = normalized.normalize("NFKC");
  normalized = normalized
    .replace(/\uFF0C/g, ",")
    .replace(/\uFF1B/g, ";")
    .replace(/\uFF06/g, "&")
    .replace(/\s+/g, " ")
    .trim()
    .replace(/,+$/g, "")
    .trim();
  return normalized;
}
function normalizedLookupMap(obj) {
  const out = Object.create(null);
  for (const [k, v] of Object.entries(obj || {})) out[normalizeAffiliationText(k)] = v;
  return out;
}
const INSTITUTION_ALIASES = normalizedLookupMap(INSTITUTION_ALIASES_RAW);
const INSTITUTION_MULTIMAP = normalizedLookupMap(INSTITUTION_MULTIMAP_RAW);
const SITE_COUNTRY_OVERRIDES = normalizedLookupMap(SITE_COUNTRY_OVERRIDES_RAW);

function canonicalizeAffiliation(rawAff) {
  const normalized = normalizeAffiliationText(rawAff);
  if (Object.prototype.hasOwnProperty.call(INSTITUTION_MULTIMAP, normalized)) {
    return [...INSTITUTION_MULTIMAP[normalized]];
  }
  if (Object.prototype.hasOwnProperty.call(INSTITUTION_ALIASES, normalized)) {
    return [INSTITUTION_ALIASES[normalized]];
  }
  return [normalized];
}
function canonicalizePaperAffiliations(rawAffs) {
  const institutions = new Set();
  for (const rawAff of rawAffs) {
    for (const institution of canonicalizeAffiliation(rawAff)) institutions.add(institution);
  }
  return Array.from(institutions).sort((a, b) => a.localeCompare(b));
}
function countryForRawText(text) {
  if (Object.prototype.hasOwnProperty.call(COUNTRY_OVERRIDES, text)) {
    return COUNTRY_OVERRIDES[text];
  }
  const lower = String(text || "").toLowerCase();
  for (const [c, hints] of COUNTRY_HINTS) {
    for (const h of hints) if (lower.indexOf(h.toLowerCase()) !== -1) return c;
  }
  return "Other";
}
function countryForCanonical(rawAff, institution) {
  const rawNormalized = normalizeAffiliationText(rawAff);
  if (Object.prototype.hasOwnProperty.call(SITE_COUNTRY_OVERRIDES, rawNormalized)) {
    return SITE_COUNTRY_OVERRIDES[rawNormalized];
  }
  if (Object.prototype.hasOwnProperty.call(SITE_COUNTRY_OVERRIDES, institution)) {
    return SITE_COUNTRY_OVERRIDES[institution];
  }
  if (Object.prototype.hasOwnProperty.call(INSTITUTION_COUNTRIES, institution)) {
    return INSTITUTION_COUNTRIES[institution];
  }
  const parentMeta = PARENT_ORG[institution];
  if (parentMeta && parentMeta.institution_country) return parentMeta.institution_country;
  return countryForRawText(rawAff || institution);
}
function countryForInstitution(institution) {
  return countryForCanonical(institution, institution);
}
function countriesForAffiliation(rawAff) {
  return Array.from(new Set(canonicalizeAffiliation(rawAff).map(inst => countryForCanonical(rawAff, inst))));
}
function countryFor(aff) {
  return countriesForAffiliation(aff)[0] || "Other";
}

// Hand-curated topic taxonomy. Multi-label: a paper can match several topics.
// Patterns are kept loose enough to catch plurals (s?), -ing/-ed/-tion forms (\w*),
// and a few common compound forms.
const TOPICS = [
  ["LLM / VLM",
    /\b(llms?|vlms?|large.{0,5}language.{0,5}models?|vision.?language|gpts?|chatgpt|claude|llama|gemini|mllms?|foundation models?)\b/i],
  ["Diffusion",
    /\b(diffusion|score.?based|denoising|latent diffusion)\b/i],
  ["Gaussian Splatting",
    /\b(gaussian splat(?:ting)?|3dgs|2dgs|4dgs|neural radiance|nerfs?)\b/i],
  ["Reinforcement Learning",
    /\b(reinforcement learning|\brl\b|q.?learning|policy gradient|actor.?critic|ppo|dqn|sac)\b/i],
  ["Imitation / BC",
    /\b(imitation learning|behaviou?ral cloning|behavior cloning|\bbc\b|teleoperat\w*|demonstrat\w*)\b/i],
  ["Manipulation",
    /\b(manipulat\w*|grasps?|grasping|pick.?and.?place|in.?hand|dexterous|peg.?in.?hole|assembl\w+|dual.?arm|grippers?)\b/i],
  ["Humanoid",
    /\b(humanoids?|biped\w*|whole.?body|loco.?manipulat\w*|legged|quadrupeds?)\b/i],
  ["Autonomous Driving",
    /\b(autonomous driving|self.?driving|\bav\b|\badas\b|driving|lanes?|traffic|intersection|highway|vehicles?)\b/i],
  ["UAV / Drone",
    /\b(uavs?|drones?|quadrotors?|aerial|multirotors?|mavs?|fixed.?wing|tilt.?rotor|monocopter\w*|helicopter\w*)\b/i],
  ["Multi-robot / Swarm",
    /\b(multi.?robots?|multi.?agents?|swarm\w*|cooperat\w+|decentrali[sz]ed|formation)\b/i],
  ["SLAM / Localization",
    /\b(slam|odometr\w+|loop closures?|relocali[sz]ations?|place recognitions?|pose graphs?|localizations?|localis\w+|positionings?|state estimation\w*)\b/i],
  ["Mapping / Perception 3D",
    /\b(occupancy|mapping|\b3d\b|point clouds?|voxels?|tsdf|reconstruction\w*|depth estimations?)\b/i],
  ["Object Detection / Tracking",
    /\b(detections?|trackings?|\bmots?\b|segment\w*|pose estimations?|\b6d\b|6.?dof)\b/i],
  ["Tactile / Force",
    /\b(tactile|haptics?|force.?feedback|gelsight|skin sensors?|f\/t sensors?)\b/i],
  ["Soft Robotics",
    /\b(soft robots?|soft robotics?|soft\s+(?:growing|hands?|grippers?|actuators?|skins?|sensors?)|origami|pneumatic|inflatable|continuum robots?|tendon.?driven|jamming|growing robots?)\b/i],
  ["Medical / Surgical",
    /\b(surgical|medical|laparosc\w*|endoscop\w*|catheters?|patients?|nurse|dental|drug delivery|tumor|biops\w+)\b/i],
  ["Wearable / Exoskeleton",
    /\b(exoskeletons?|wearable robots?|orthos(?:is|es)|prosthes(?:is|es)|prosthetics?|gait\s+(?:assist|train)|rehabilitation|wearable sensors?|powered orthos|hand orthos|lower.?limb)\b/i],
  ["Underwater / Marine",
    /\b(underwater|auvs?|uuvs?|marine|submarine|oceans?|aquatic)\b/i],
  ["Agricultural",
    /\b(agricultur\w*|farms?|crops?|orchards?|harvest\w*|greenhouse|weeds?|fruits?|plant phenotyp\w*)\b/i],
  ["Safety / MPC",
    /\b(\bmpcs?\b|model predictive|control barriers?|\bsafety\b|safe.?(?:learning|control)|robust control|reachab\w+)\b/i],
  ["Force / Compliance",
    /\b(impedance|admittance|compliance control|compliant control|force.?(?:control|aware|feedback|guided|tracking)|stiffness control|hybrid force)\b/i],
  ["Visual Servoing",
    /\b(visual servo\w*|image.?based visual|position.?based visual|\bIBVS\b|\bPBVS\b)\b/i],
  ["Classical Control",
    /\b(adaptive control|optimal control|nonlinear control|sliding mode|backstepping|\bLQR\b|\bLQG\b|\bPID\b|H.?infinity|feedback linearization|gain scheduling|lyapunov\w*)\b/i],
  ["Planning",
    /\b(planning|trajectory optim\w*|\brrt\b|sampling.?based|motion planning|task and motion|tamp|navigation)\b/i],
  ["Sim-to-Real",
    /\b(sim.?to.?real|domain randomi[sz]ation|sim2real|real.?to.?sim)\b/i],
  ["Neural Fields",
    /\b(neural fields?|implicit representation|signed distance|\bsdf\b|occupancy networks?)\b/i],
  ["Event Camera",
    /\b(event cameras?|event.?based|\bdvs\b|dynamic vision)\b/i],
  ["Human-Robot",
    /\b(human.?(?:robot|aware)|hri|teleoperat\w*|shared autonomy|collaborative robots?|cobots?|social|crowd|pedestrian)\b/i],
  ["Aerial Manipulation",
    /\b(aerial manipulat\w*|aerial grasp\w*|flying grippers?|aerial transport|cable.?suspended.{0,30}(?:aerial|drone|uav|quadrotor)|drone.{0,20}(?:manipulat|grasp))\b/i],
  ["Knowledge Distillation",
    /\b(knowledge distillation|\bdistillation\b|distill\w+|teacher.{0,5}students?|student models?)\b/i],
  ["Active Learning",
    /\b(active learning|query strateg\w+|uncertainty sampling|active selection)\b/i],
  ["Bio-inspired",
    /\b(bio.?inspired|biomimetic|biologically.?inspired|nature.?inspired|insect.?inspired|fish.?inspired|bird.?inspired|samara|inspired by)\b/i],
];
function topicsForTitle(title) {
  const tags = [];
  for (const [name, re] of TOPICS) if (re.test(title)) tags.push(name);
  return tags;
}

function sessionTypeOf(p) {
  return p.session_type || "Session";
}

PAPERS.forEach(p => {
  p.tags = topicsForTitle(p.title);
  p.rawAffs = Array.from(new Set(p.authors.map(a => a.aff)));
  p.institutions = canonicalizePaperAffiliations(p.rawAffs);
  // Keep p.affs as the existing UI/filter field, now backed by canonical institutions.
  p.affs = p.institutions;
  p.countries = Array.from(new Set(p.rawAffs.flatMap(countriesForAffiliation)));
  p.keywords = p.keywords || [];
  p.abstract = p.abstract || "";
  p.sessionType = sessionTypeOf(p);
  p._search = normalizeSearchText(
    p.code.toLowerCase() + " " +
    p.title.toLowerCase() + " " +
    p.authors.map(a => a.name + " " + a.aff).join(" ").toLowerCase() +
    " " + p.institutions.join(" ").toLowerCase() +
    " " + p.tags.join(" ").toLowerCase() +
    " " + p.keywords.join(" ").toLowerCase() +
    " " + p.abstract.toLowerCase() +
    " " + (p.session_title || "").toLowerCase() +
    " " + (p.sessionType || "").toLowerCase() +
    " " + (p.room || "").toLowerCase()
  );
});

const N = PAPERS.length;
const uniqAuthors = new Set();
const affCount = new Map();
const countryCount = new Map();
const topicCount = new Map();
const kwCount = new Map();
const dayCount = new Map();
const authorsPerPaper = new Map();
for (const p of PAPERS) {
  dayCount.set(p.day, (dayCount.get(p.day) || 0) + 1);
  authorsPerPaper.set(p.authors.length, (authorsPerPaper.get(p.authors.length) || 0) + 1);
  for (const a of p.authors) uniqAuthors.add(a.name + "|" + a.aff);
  for (const aff of p.affs) affCount.set(aff, (affCount.get(aff) || 0) + 1);
  for (const c of p.countries) countryCount.set(c, (countryCount.get(c) || 0) + 1);
  for (const t of p.tags) topicCount.set(t, (topicCount.get(t) || 0) + 1);
  const seenKw = new Set();
  for (const kw of (p.keywords || [])) {
    if (seenKw.has(kw)) continue;
    seenKw.add(kw);
    kwCount.set(kw, (kwCount.get(kw) || 0) + 1);
  }
}
const uniqAffs = affCount.size;
const uniqCountries = Array.from(countryCount.keys()).filter(c => c !== "Other").length;
const totalAuthorSlots = PAPERS.reduce((s,p)=> s + p.authors.length, 0);

// Curated research radar. Three/two/one stars reflect APRL relevance—not PI/lab quality—while
// every metric/theme below is derived live from the official program data.
const LAB_TIERS = {
  S: [
    "Valada, Abhinav","Hutter, Marco","Xiao, Xuesu","Ma, Jun","She, Yu",
    "Huang, Guoquan (Paul)","Myung, Hyun","Kim, Ayoung","Civera, Javier","Scherer, Sebastian",
    "Seita, Daniel","Wang, Xiaolong","Li, Jiaoyang","Loianno, Giuseppe","Zhou, Boyu",
    "Gao, Fei","How, Jonathan","Ames, Aaron","Okada, Kei","Yuan, Wenzhen"
  ],
  A: [
    "Parasuraman, Ramviyas","Sukhatme, Gaurav","Su, Hao","Atanasov, Nikolay","Ghaffari, Maani",
    "Krishna, Madhava","Scaramuzza, Davide","Stachniss, Cyrill","Kaess, Michael","Carlone, Luca",
    "Burgard, Wolfram","Bennewitz, Maren","Leutenegger, Stefan","Cadena, Cesar","Milford, Michael J",
    "Leonard, John","Martín-Martín, Roberto","Fox, Dieter","Agrawal, Pulkit","Srinivasa, Siddhartha",
    "Kumar, Vijay","Xie, Lihua","Zhou, Lifeng","Yazicioglu, Yasin","Manocha, Dinesh",
    "Schwager, Mac","Tokekar, Pratap","Belta, Calin","Kavraki, Lydia","Alexis, Kostas"
  ],
  B: [
    "Malik, Jitendra","Kaelbling, Leslie","Tellex, Stefanie","Nikolaidis, Stefanos","Abbeel, Pieter",
    "Ramanan, Deva","Zhu, Jun-Yan","Jayaraman, Dinesh","Kroemer, Oliver","Pappas, George J.",
    "Agha-mohammadi, Ali-akbar","Martinez, Sonia","Kawaharazuka, Kento","Knoll, Alois","Yip, Michael C.",
    "Ren, Hongliang","Rus, Daniela","Laschi, Cecilia","Tomizuka, Masayoshi","Pucci, Daniele",
    "Katzschmann, Robert Kevin","Park, Jaeheung","Kim, H. Jin","Chung, Soon-Jo","Kum, Dongsuk",
    "Choi, Sungjoon","Akbari Hamed, Kaveh","Stuart, Hannah","Majidi, Carmel","Zhang, Fumin",
    "Yang, Kailun","Ogata, Tetsuya","Liu, Changliu","Choset, Howie","Min, Byung-Cheol",
    "Sartoretti, Guillaume Adrien","Vidal-Calleja, Teresa A.","Berenson, Dmitry","Saska, Martin","Shim, David Hyunchul",
    "Wang, Ziran","Lin, Ming C.","Liu, Yong","Qin, Tong","Harada, Kensuke",
    "Zhang, Shiqi","Vasudevan, Ram","Ichnowski, Jeffrey","Qian, Feifei","Oh, Jean"
  ]
};
const LAB_PI_BY_NAME = new Map(Object.entries(LAB_TIERS).flatMap(([tier,names]) => names.map(name => [name,{name,tier}])));
const LAB_STARS = {S:"★★★",A:"★★",B:"★"};
const OVERLAP_AXES = [
  ["SLAM / localization", /\b(slam|locali[sz]|odometr|state estimation|place recognition|loop closure|vio|lio)\b/i, 3],
  ["3D / mapping", /\b(3d|4d|mapping|point cloud|gaussian|depth|reconstruction|occupancy|scene graph)\b/i, 3],
  ["navigation / planning", /\b(navigation|planning|traversability|trajectory|exploration|path finding)\b/i, 2],
  ["embodied AI / VLA", /\b(vision.language|vla|vlm|llm|embodied|world model|foundation model)\b/i, 2],
  ["multi-robot / aerial", /\b(multi.robot|multi.agent|swarm|uav|aerial|drone|quadrotor)\b/i, 1.5],
  ["physical intelligence", /\b(manipulation|tactile|humanoid|locomotion|dexterous|control)\b/i, 1]
];

// Populate dynamic counts
document.getElementById("lede-count").textContent = N.toLocaleString();
const _byDay = (() => { const m = new Map(); for (const p of PAPERS) m.set(p.day, (m.get(p.day)||0)+1); return m; })();
const _ledeFootnote = `<b>Parsed on this page: ${N.toLocaleString()} papers</b> (Mon ${(_byDay.get("Monday")||0).toLocaleString()} · Tue ${(_byDay.get("Tuesday")||0).toLocaleString()} · Wed ${(_byDay.get("Wednesday")||0).toLocaleString()}). Every indexed paper has a title and author list; author affiliations are joined from the official Author Index.`;
document.getElementById("parsed-footnote").innerHTML = _ledeFootnote;

document.getElementById("kpis").innerHTML = [
  ["📄", N.toLocaleString(),               "Indexed papers",     "official", ""],
  ["👥", uniqAuthors.size.toLocaleString(), "Author rows",        "parsed", "Unique (name, affiliation) pairs"],
  ["🏛️", uniqAffs.toLocaleString(),         "Institutions",       "parsed", "After affiliation canonicalization"],
  ["🔑", kwCount.size.toLocaleString(),     "Keywords",           "parsed", "Unique author-declared keywords"],
  ["📅", "3",                              "Program days",        "official", "Monday through Wednesday"],
  ["🧭", "4",                              "Session formats",     "official", "Lightning, focused, award, and special"],
].map(([e,v,l,t,note]) => `<div class="kpi ${t}"><div class="v"><span class="e">${e}</span>${v}</div><div class="l">${l}</div>${note?`<div class="note">${note}</div>`:""}</div>`).join("");

const sortedTopics = Array.from(topicCount.entries()).sort((a,b)=>b[1]-a[1]);
const topicSel = document.getElementById("topicFilter");
sortedTopics.forEach(([name]) => {
  const o = document.createElement("option");
  o.value = name; o.textContent = name;
  topicSel.appendChild(o);
});

Chart.defaults.color = "#424245";
Chart.defaults.borderColor = "rgba(0,0,0,0.06)";
Chart.defaults.font.family = '-apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI", "Pretendard", "Noto Sans KR", system-ui, sans-serif';

const ACCENT = "#0066cc";
const PALETTE = ["#0066cc","#34c759","#ff9f0a","#bf5af2","#ff375f","#5ac8fa","#ffd60a","#ac8e68","#30b0c7","#8e8e93","#ff6482","#a2845e","#64d2ff","#ffcc02","#85c5e0"];

// Country ranking shared between country charts and institution chart
const sortedCountries = Array.from(countryCount.entries()).filter(([c])=>c!=="Other").sort((a,b)=>b[1]-a[1]);
const top15Country = sortedCountries.slice(0,15);
const colorForRank = i => PALETTE[i % PALETTE.length];
const countryRank = new Map(sortedCountries.map(([name], i) => [name, i]));
const colorForCountry = name => {
  const r = countryRank.get(name);
  return r == null ? "#c7c7cc" : colorForRank(r);
};

const top20Aff = Array.from(affCount.entries()).sort((a,b)=>b[1]-a[1]).slice(0,20);
// Resolve a representative country per canonical institution.
const affCountry = new Map();
for (const [institution] of top20Aff) affCountry.set(institution, countryForInstitution(institution));

new Chart(document.getElementById("affChart"), {
  type: "bar",
  data: {
    labels: top20Aff.map(x => `${x[0]} | ${affCountry.get(x[0]) || "—"}`),
    datasets: [{
      data: top20Aff.map(x => x[1]),
      backgroundColor: top20Aff.map(x => colorForCountry(affCountry.get(x[0]) || "")),
      hoverBorderColor: "#1d1d1f",
      hoverBorderWidth: 2,
      borderColor: "transparent", borderWidth: 0,
      borderRadius: 4,
    }],
  },
  options: {
    indexAxis: "y", maintainAspectRatio: false,
    onHover: (e, els) => { e.native.target.style.cursor = els.length ? "pointer" : "default"; },
    onClick: (e, els, chart) => {
      if (!els.length) return;
      const aff = top20Aff[els[0].index][0];
      filterByAffiliation(aff);
    },
    plugins: {
      legend: { display: false },
      tooltip: { backgroundColor: "#1d1d1f", padding: 10, cornerRadius: 8,
        callbacks: {
          title: ctx => ctx[0].label.split(" | ")[0],
          label: ctx => {
            const country = ctx.label.split(" | ")[1] || "—";
            return ` ${country} · ${ctx.parsed.x} papers — click to filter`;
          },
        } },
    },
    scales: {
      y: { ticks: { font: { size: 11 }, autoSkip: false }, grid: { display: false }, border: { display: false } },
      x: { grid: { color: "rgba(0,0,0,0.05)" }, border: { display: false } },
    },
  },
});

// (sortedCountries / top15Country / colorForRank declared above)

new Chart(document.getElementById("countryDonut"), {
  type: "doughnut",
  data: { labels: top15Country.map(x=>`${x[0]} (${x[1]})`), datasets: [{ data: top15Country.map(x=>x[1]), backgroundColor: top15Country.map((_, i) => colorForRank(i)), borderColor: "#fff", borderWidth: 2, hoverBorderColor: "#1d1d1f", hoverBorderWidth: 3 }] },
  options: {
    maintainAspectRatio: false, cutout: "55%",
    onHover: (e, els) => { e.native.target.style.cursor = els.length ? "pointer" : "default"; },
    onClick: (e, els, chart) => {
      if (!els.length) return;
      const country = top15Country[els[0].index][0];
      filterByCountry(country);
    },
    plugins: {
      legend: { position: "right", labels: { boxWidth: 10, font: { size: 11 }, padding: 6 } },
      tooltip: { backgroundColor: "#1d1d1f", padding: 10, cornerRadius: 8,
        callbacks: { label: ctx => {
          const total = ctx.dataset.data.reduce((s,v)=>s+v,0);
          const pct = (ctx.parsed / total * 100).toFixed(1);
          return ` ${ctx.label.replace(/\s+\(\d+\)$/,"")}: ${ctx.parsed} (${pct}%) — click to filter`;
        } } },
    },
  },
});

new Chart(document.getElementById("countryBar"), {
  type: "bar",
  data: { labels: top15Country.map(x=>x[0]), datasets: [{ data: top15Country.map(x=>x[1]), backgroundColor: top15Country.map((_, i) => colorForRank(i)), borderRadius: 4, hoverBorderColor: "#1d1d1f", hoverBorderWidth: 2, borderColor: "transparent", borderWidth: 0 }] },
  options: {
    indexAxis: "y", maintainAspectRatio: false,
    onHover: (e, els) => { e.native.target.style.cursor = els.length ? "pointer" : "default"; },
    onClick: (e, els, chart) => {
      if (!els.length) return;
      const country = top15Country[els[0].index][0];
      filterByCountry(country);
    },
    plugins: {
      legend: { display: false },
      tooltip: { backgroundColor: "#1d1d1f", padding: 10, cornerRadius: 8,
        callbacks: { label: ctx => ` ${ctx.parsed.x} papers — click to filter` } },
    },
    scales: {
      y: { ticks: { font: { size: 11 }, autoSkip: false }, grid: { display: false }, border: { display: false } },
      x: { grid: { color: "rgba(0,0,0,0.05)" }, border: { display: false } },
    },
  },
});

document.querySelectorAll("#eda-country .tab").forEach(btn => {
  btn.addEventListener("click", () => {
    document.querySelectorAll("#eda-country .tab").forEach(b => b.classList.toggle("active", b === btn));
    const view = btn.dataset.view;
    document.getElementById("countryDonutBox").style.display = view === "donut" ? "block" : "none";
    document.getElementById("countryBarBox").style.display = view === "bar15" ? "block" : "none";
  });
});

// Hot topics — horizontal bar chart (full taxonomy), click to filter, hover highlights.
// Color matches the pink topic chip on each paper card.
const TOPIC_COLOR = "#c0185c"; // var(--pink)
const allTopics = sortedTopics; // already sorted desc
// Lock the y-axis (label gutter) width so the two horizontal bar charts
// (Hot topics + Author keywords) line up vertically below each other.
// Responsive: shrink on narrow viewports so labels still get a reasonable share.
function computeGutter() {
  const w = window.innerWidth;
  if (w < 600) return 130;
  if (w < 900) return 180;
  if (w < 1200) return 230;
  return 280;
}
let Y_AXIS_GUTTER = computeGutter();
const lockGutter = scale => { scale.width = Y_AXIS_GUTTER; };

// Re-fit charts when the viewport changes — Chart.js handles canvas sizing
// natively, but we have to re-run afterFit + force a re-render so the new
// gutter takes effect across both charts.
let _resizeRAF = null;
window.addEventListener("resize", () => {
  if (_resizeRAF) cancelAnimationFrame(_resizeRAF);
  _resizeRAF = requestAnimationFrame(() => {
    const newG = computeGutter();
    if (newG !== Y_AXIS_GUTTER) {
      Y_AXIS_GUTTER = newG;
      const tb = Chart.getChart("topicBar"); if (tb) tb.update();
      const kb = Chart.getChart("kwBar");    if (kb) kb.update();
    }
  });
});
new Chart(document.getElementById("topicBar"), {
  type: "bar",
  data: {
    labels: allTopics.map(x => x[0]),
    datasets: [{
      data: allTopics.map(x => x[1]),
      backgroundColor: TOPIC_COLOR,
      hoverBackgroundColor: TOPIC_COLOR,
      borderColor: "transparent",
      hoverBorderColor: "#1d1d1f",
      borderWidth: 0,
      hoverBorderWidth: 2,
      borderRadius: 3,
    }],
  },
  options: {
    indexAxis: "y", maintainAspectRatio: false,
    onHover: (e, els) => { e.native.target.style.cursor = els.length ? "pointer" : "default"; },
    onClick: (e, els, chart) => {
      if (!els.length) return;
      const idx = els[0].index;
      const topicName = chart.data.labels[idx];
      document.getElementById("topicFilter").value = topicName;
      document.getElementById("q").value = "";
      document.getElementById("dayFilter").value = "";
      applyFilter();
      maybeScrollToSearch();
    },
    plugins: {
      legend: { display: false },
      tooltip: { backgroundColor: "#1d1d1f", padding: 10, cornerRadius: 8,
        callbacks: { label: ctx => {
          const pct = (ctx.parsed.x / N * 100).toFixed(1);
          return ` ${ctx.parsed.x.toLocaleString()} papers (${pct}%) — click to filter`;
        } } },
    },
    scales: {
      y: { afterFit: lockGutter, ticks: { font: { size: 11 }, autoSkip: false }, grid: { display: false }, border: { display: false } },
      x: { grid: { color: "rgba(0,0,0,0.05)" }, border: { display: false } },
    },
  },
});

// === Country × Topic heatmap =================================================
// Build matrix: heatMat[country][topic] = #papers where the country appears in
// p.countries AND the topic appears in p.tags. Multi-label: one paper can
// contribute to many cells.
const heatTopicCount = new Map(); // re-derive in topic-frequency order
for (const p of PAPERS) for (const t of p.tags) heatTopicCount.set(t, (heatTopicCount.get(t)||0)+1);
const heatTopics = Array.from(heatTopicCount.entries()).sort((a,b)=>b[1]-a[1]).slice(0,20).map(x=>x[0]);
const heatCountries = top15Country.map(x => x[0]);  // already sorted desc

const heatMat = {};      // {country: {topic: count}}
const heatRowSum = {};   // {country: int}
const heatColSum = {};   // {topic: int}
let heatGrand = 0;
for (const c of heatCountries) { heatMat[c] = {}; heatRowSum[c] = 0; for (const t of heatTopics) heatMat[c][t] = 0; }
for (const t of heatTopics) heatColSum[t] = 0;
for (const p of PAPERS) {
  const cs = new Set(p.countries.filter(c => heatMat[c]));
  const ts = new Set(p.tags.filter(t => heatColSum.hasOwnProperty(t)));
  for (const c of cs) for (const t of ts) {
    heatMat[c][t]++; heatRowSum[c]++; heatColSum[t]++; heatGrand++;
  }
}

// Renderer. mode: "row" | "col" | "abs"
function renderHeatmap(mode) {
  const grid = document.getElementById("heatmapGrid");
  grid.style.setProperty("--cols", String(heatTopics.length));
  const html = [];
  // Top-left corner
  html.push(`<div class="corner"></div>`);
  // Column headers (topics)
  for (const t of heatTopics) {
    html.push(`<div class="colhead" data-topic="${escapeHTML(t)}" title="Filter topic: ${escapeHTML(t)}">${escapeHTML(t)}</div>`);
  }
  // Rows
  for (const c of heatCountries) {
    html.push(`<div class="rowhead" data-country="${escapeHTML(c)}" title="Filter country: ${escapeHTML(c)}">${escapeHTML(c)}</div>`);
    for (const t of heatTopics) {
      const v = heatMat[c][t];
      let intensity = 0; let pct = 0;
      if (mode === "row") {
        pct = heatRowSum[c] ? v/heatRowSum[c] : 0;
        intensity = Math.min(1, pct / 0.20); // saturate at 20% of any row
      } else if (mode === "col") {
        pct = heatColSum[t] ? v/heatColSum[t] : 0;
        intensity = Math.min(1, pct / 0.45); // saturate at 45% (China-heavy cols)
      } else {
        // sqrt scaling so small values are still visible
        const maxAbs = 250;
        intensity = v ? Math.min(1, Math.sqrt(v) / Math.sqrt(maxAbs)) : 0;
      }
      const empty = v === 0 ? " empty" : "";
      const dark  = intensity > 0.55 ? " dark" : "";
      // background: blend white -> accent (#0066cc)
      // r,g,b lerp from (255,255,255) -> (0,102,204)
      const r = Math.round(255 - intensity * 255);
      const g = Math.round(255 - intensity * 153);
      const b = Math.round(255 - intensity *  51);
      const bg = v === 0 ? "" : ` style="background:rgb(${r},${g},${b})"`;
      const labelText =
        mode === "row" ? (v ? (pct*100).toFixed(0) + "%" : "")
      : mode === "col" ? (v ? (pct*100).toFixed(0) + "%" : "")
      :                  (v ? (v >= 100 ? v : v) : "");
      const rowPctStr = heatRowSum[c] ? (v/heatRowSum[c]*100).toFixed(1) : "0";
      const colPctStr = heatColSum[t] ? (v/heatColSum[t]*100).toFixed(1) : "0";
      const tip = `${c} × ${t}\n${v} papers — ${rowPctStr}% of ${c} · ${colPctStr}% of ${t}\nClick to filter`;
      html.push(`<div class="cell${empty}${dark}" data-country="${escapeHTML(c)}" data-topic="${escapeHTML(t)}" title="${escapeHTML(tip)}"${bg}><span class="v">${labelText}</span></div>`);
    }
  }
  grid.innerHTML = html.join("");
  // Wire interactions
  grid.querySelectorAll(".cell").forEach(el => {
    el.addEventListener("click", () => {
      document.getElementById("countryFilter").value = el.dataset.country;
      document.getElementById("topicFilter").value = el.dataset.topic;
      applyFilter();
      maybeScrollToSearch();
    });
  });
  grid.querySelectorAll(".rowhead").forEach(el => {
    el.addEventListener("click", () => {
      document.getElementById("countryFilter").value = el.dataset.country;
      document.getElementById("topicFilter").value = "";
      applyFilter();
      maybeScrollToSearch();
    });
  });
  grid.querySelectorAll(".colhead").forEach(el => {
    el.addEventListener("click", () => {
      document.getElementById("topicFilter").value = el.dataset.topic;
      document.getElementById("countryFilter").value = "";
      applyFilter();
      maybeScrollToSearch();
    });
  });
}
renderHeatmap("row");
document.querySelectorAll("#eda-heatmap .tab").forEach(btn => {
  btn.addEventListener("click", () => {
    document.querySelectorAll("#eda-heatmap .tab").forEach(b => b.classList.toggle("active", b === btn));
    renderHeatmap(btn.dataset.heatview);
  });
});
// === end heatmap =============================================================

const days = ["Monday","Tuesday","Wednesday"];
const dayClass = { Monday: "mon", Tuesday: "tue", Wednesday: "wed" };

// === Format totals across all days ===
function formatCount(typ, day) {
  let n = 0;
  for (const p of PAPERS) if (p.sessionType === typ && (!day || p.day === day)) n++;
  return n;
}
const lightningAll = formatCount("Lightning Talks");
const focusedAll = formatCount("Focused Sessions");

const tiles = [];
// row 1 — format totals (3 cols each)
tiles.push(`<button type="button" class="day-tile row-format interactive" data-stype="Lightning Talks">
  <span class="d">Lightning</span>
  <div><div class="n">${lightningAll.toLocaleString()}</div><div class="l">papers · all days</div></div>
</button>`);
tiles.push(`<button type="button" class="day-tile row-format oral" data-stype="Focused Sessions">
  <span class="d">Focused</span>
  <div><div class="n">${focusedAll.toLocaleString()}</div><div class="l">papers · all days</div></div>
</button>`);
// row 2 — day totals (2 cols each)
for (const d of days) {
  tiles.push(`<button type="button" class="day-tile row-day ${dayClass[d]}" data-day="${d}">
    <span class="d">${d.slice(0,3)}</span>
    <div><div class="n">${(dayCount.get(d)||0).toLocaleString()}</div><div class="l">papers</div></div>
  </button>`);
}
// row 3 — per-day × per-format (1 col each)
for (const d of days) {
  for (const t of ["Lightning Talks", "Focused Sessions"]) {
    const cnt = formatCount(t, d);
    const tCls = t === "Focused Sessions" ? "oral" : "interactive";
    tiles.push(`<button type="button" class="day-tile row-df compact ${tCls}" data-day="${d}" data-stype="${t}">
      <span class="d">${d.slice(0,3)}·${t === "Lightning Talks" ? "Ltg" : "Foc"}</span>
      <div><div class="n">${cnt.toLocaleString()}</div><div class="l">${t.toLowerCase()}</div></div>
    </button>`);
  }
}
document.getElementById("statGrid").innerHTML = tiles.join("");

// Wire the tiles: clicking a tile sets the filter to that tile's exact (day,
// stype) signature. Clicking the same tile again clears both. Each tile
// represents a specific slice — including the "no day" or "no type" slice —
// so clicking always replaces, never partially carries state over.
function toggleFilters(day, stype) {
  const daySel  = document.getElementById("dayFilter");
  const typeSel = document.getElementById("sessionTypeFilter");
  const tileDay  = day  || "";
  const tileType = stype || "";
  const exactMatch = daySel.value === tileDay && typeSel.value === tileType;
  if (exactMatch) {
    daySel.value  = "";
    typeSel.value = "";
  } else {
    daySel.value  = tileDay;
    typeSel.value = tileType;
  }
  applyFilter();
  maybeScrollToSearch();
}
function refreshTileMatches() {
  const dv = document.getElementById("dayFilter").value;
  const tv = document.getElementById("sessionTypeFilter").value;
  document.querySelectorAll("#statGrid .day-tile").forEach(el => {
    const d = el.dataset.day || "";
    const s = el.dataset.stype || "";
    // A tile is matched only when its (day,stype) signature exactly equals the
    // current filters. Tiles with empty signature never highlight.
    const exact = ((d && dv === d) || (!d && !dv)) && ((s && tv === s) || (!s && !tv));
    el.classList.toggle("matched", exact && (!!dv || !!tv));
  });
}
document.querySelectorAll("#statGrid .day-tile").forEach(el => {
  el.addEventListener("click", () => toggleFilters(el.dataset.day || null, el.dataset.stype || null));
});
// Refresh tile matched-state on every filter change. applyFilter has a built-in
// hook (`onAfterApplyFilter`) which we register here.
onAfterApplyFilter = refreshTileMatches;
refreshTileMatches();

const apBuckets = Array.from(authorsPerPaper.entries()).sort((a,b)=>a[0]-b[0]);
// Helper: pick the column nearest to the click x even if the bar itself is too thin to hit
function pickAuthorBucketIdx(e, chart) {
  const direct = chart.getElementsAtEventForMode(e, "nearest", { intersect: true }, false);
  if (direct.length) return direct[0].index;
  const indexHit = chart.getElementsAtEventForMode(e, "index", { intersect: false, axis: "x" }, false);
  return indexHit.length ? indexHit[0].index : -1;
}
new Chart(document.getElementById("authorsChart"), {
  type: "bar",
  data: { labels: apBuckets.map(x=>x[0]), datasets: [{ data: apBuckets.map(x=>x[1]), backgroundColor: "#5ac8fa", hoverBackgroundColor: "#3aa8d8", hoverBorderColor: "#1d1d1f", hoverBorderWidth: 2, borderColor: "transparent", borderWidth: 0, borderRadius: 3 }] },
  options: {
    maintainAspectRatio: false,
    interaction: { mode: "index", intersect: false, axis: "x" },
    onHover: (e, els, chart) => {
      const idx = pickAuthorBucketIdx(e, chart);
      e.native.target.style.cursor = idx >= 0 ? "pointer" : "default";
    },
    onClick: (e, els, chart) => {
      const idx = pickAuthorBucketIdx(e, chart);
      if (idx < 0) return;
      filterByAuthorCount(apBuckets[idx][0]);
    },
    plugins: { legend: { display: false }, tooltip: { backgroundColor: "#1d1d1f", padding: 10, cornerRadius: 8,
      callbacks: { label: ctx => ` ${ctx.parsed.y.toLocaleString()} papers with ${apBuckets[ctx.dataIndex][0]} authors — click to filter` } } },
    scales: {
      x: { title: { display: true, text: "# authors  (click any column or label below)", font: { size: 11 }, color: "#86868b" }, grid: { display: false }, border: { display: false }, ticks: { font: { size: 11 } } },
      y: { grid: { color: "rgba(0,0,0,0.05)" }, border: { display: false } },
    },
  },
});

// Make the x-axis number labels themselves clickable too.
// Tick labels sit between chartArea.bottom and xAxis.bottom — that whole
// strip should react to clicks/hovers.
(function makeAuthorTicksClickable() {
  const canvas = document.getElementById("authorsChart");
  function inTickStrip(e, chart) {
    const rect = canvas.getBoundingClientRect();
    const localY = e.clientY - rect.top;
    const top = chart.chartArea.bottom;
    const bot = chart.scales.x.bottom + 12; // small buffer past the label baseline
    return localY >= top && localY <= bot;
  }
  function nearestColumnIdx(e, chart) {
    const rect = canvas.getBoundingClientRect();
    const localX = e.clientX - rect.left;
    const xAxis = chart.scales.x;
    let bestIdx = -1, bestDist = Infinity;
    for (let i = 0; i < apBuckets.length; i++) {
      const px = xAxis.getPixelForValue(i);
      const d = Math.abs(px - localX);
      if (d < bestDist) { bestDist = d; bestIdx = i; }
    }
    return bestIdx;
  }
  canvas.addEventListener("click", (e) => {
    const chart = Chart.getChart(canvas);
    if (!chart || !inTickStrip(e, chart)) return;
    const idx = nearestColumnIdx(e, chart);
    if (idx >= 0) filterByAuthorCount(apBuckets[idx][0]);
  });
  canvas.addEventListener("mousemove", (e) => {
    const chart = Chart.getChart(canvas);
    if (!chart) return;
    if (inTickStrip(e, chart)) canvas.style.cursor = "pointer";
  });
})();

// Author-keyword chart with tab switcher (Top 30 / 60 / All)
const sortedKw = Array.from(kwCount.entries()).sort((a,b)=>b[1]-a[1]);
// Lowercase set of all author-declared keywords. Used during render() to detect
// when the user's query is an exact keyword (e.g. set via clicking a kw chip).
const KW_SET = new Set(Array.from(kwCount.keys()).map(s => s.toLowerCase()));
function makeKwChart(limit) {
  const data = limit === "all" ? sortedKw : sortedKw.slice(0, parseInt(limit, 10));
  const canvas = document.getElementById("kwBar");
  const box = document.getElementById("kwBarBox");
  // 22 px per row keeps each label readable
  box.style.height = Math.max(360, data.length * 22 + 40) + "px";
  const old = Chart.getChart("kwBar"); if (old) old.destroy();
  new Chart(canvas, {
    type: "bar",
    data: { labels: data.map(x=>x[0]), datasets: [{ data: data.map(x=>x[1]), backgroundColor: "#0066cc", hoverBorderColor: "#1d1d1f", hoverBorderWidth: 2, borderColor: "transparent", borderWidth: 0, borderRadius: 3 }] },
    options: {
      indexAxis: "y", maintainAspectRatio: false,
      onHover: (e, els) => { e.native.target.style.cursor = els.length ? "pointer" : "default"; },
      onClick: (e, els, chart) => {
        if (!els.length) return;
        const kw = chart.data.labels[els[0].index];
        document.getElementById("q").value = kw;
        document.getElementById("topicFilter").value = "";
        applyFilter();
        maybeScrollToSearch();
      },
      plugins: { legend: { display: false }, tooltip: { backgroundColor: "#1d1d1f", padding: 10, cornerRadius: 8,
        callbacks: { label: ctx => ` ${ctx.parsed.x.toLocaleString()} papers — click to filter` } } },
      scales: {
        y: { afterFit: lockGutter, ticks: { font: { size: 11 }, autoSkip: false }, grid: { display: false }, border: { display: false } },
        x: { grid: { color: "rgba(0,0,0,0.05)" }, border: { display: false } },
      },
    },
  });
}
makeKwChart("30");
document.querySelectorAll("#kw-trends .tab").forEach(btn => {
  btn.addEventListener("click", () => {
    document.querySelectorAll("#kw-trends .tab").forEach(b => b.classList.toggle("active", b === btn));
    makeKwChart(btn.dataset.kwview);
  });
});

// Country and institution filter selects
const countrySel = document.getElementById("countryFilter");
sortedCountries.forEach(([c]) => {
  const o = document.createElement("option");
  o.value = c; o.textContent = c;
  countrySel.appendChild(o);
});
const affSel = document.getElementById("affFilter");
Array.from(affCount.entries()).sort((a,b)=>b[1]-a[1]).slice(0, 100).forEach(([aff, n]) => {
  const o = document.createElement("option");
  o.value = aff; o.textContent = `${aff} (${n})`;
  affSel.appendChild(o);
});

// Search
let PAGE = 50;
let page = 0;
let filtered = PAPERS;
function escapeHTML(s){ return s.replace(/[&<>"']/g, ch => ({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;"}[ch])); }

let activeLabTier = "S";
let selectedLabPI = "";
function paperOverlap(p) {
  const text = [p.title, ...(p.keywords||[]), ...(p.tags||[])].join(" ");
  return OVERLAP_AXES.reduce((score,[_,re,w]) => score + (re.test(text) ? w : 0), 0);
}
function buildLabProfile(name, tier) {
  const papers = PAPERS.filter(p => p.authors.some(a => a.name === name));
  const lastPapers = papers.filter(p => p.authors.length && p.authors[p.authors.length-1].name === name);
  const firstAuthors = new Set(papers.map(p => p.authors[0]?.name).filter(n => n && n !== name));
  const kw = new Map(), tag = new Map(), co = new Map(), aff = new Map(), axes = [];
  for (const p of papers) {
    for (const k of new Set(p.keywords||[])) kw.set(k,(kw.get(k)||0)+1);
    for (const t of new Set(p.tags||[])) tag.set(t,(tag.get(t)||0)+1);
    for (const a of p.authors) {
      if (a.name !== name) co.set(a.name,(co.get(a.name)||0)+1);
      else aff.set(a.aff,(aff.get(a.aff)||0)+1);
    }
  }
  const sortedKw = Array.from(kw.entries()).sort((a,b)=>b[1]-a[1] || a[0].localeCompare(b[0]));
  const sortedTags = Array.from(tag.entries()).sort((a,b)=>b[1]-a[1] || a[0].localeCompare(b[0]));
  const themes = Array.from(new Set([...sortedKw.map(x=>x[0]),...sortedTags.map(x=>x[0])])).slice(0,5);
  for (const [axis,re] of OVERLAP_AXES) {
    const count = papers.filter(p => re.test([p.title,...(p.keywords||[]),...(p.tags||[])].join(" "))).length;
    if (count) axes.push([axis,count]);
  }
  const overlapScore = axes.reduce((sum,[axis,count]) => {
    const weight = OVERLAP_AXES.find(x=>x[0]===axis)?.[2] || 1;
    return sum + Math.min(count,3)*weight;
  },0);
  const overlap = overlapScore >= 10 ? "High" : overlapScore >= 4 ? "Medium" : "Expand";
  const representatives = papers.slice().sort((a,b) =>
    (b.sessionType === "Award Candidates") - (a.sessionType === "Award Candidates") ||
    (b.authors.at(-1)?.name === name) - (a.authors.at(-1)?.name === name) ||
    paperOverlap(b) - paperOverlap(a) || a.paper_number.localeCompare(b.paper_number)
  ).slice(0,3);
  return {
    name,tier,papers,lastPapers,firstAuthors,kw:sortedKw,
    coauthors:Array.from(co.entries()).sort((a,b)=>b[1]-a[1] || a[0].localeCompare(b[0])),
    affiliation:Array.from(aff.entries()).sort((a,b)=>b[1]-a[1])[0]?.[0] || "Affiliation unavailable",
    themes, topicDiversity:kw.size, axes, overlap, overlapScore, representatives
  };
}
const LAB_PROFILES = Array.from(LAB_PI_BY_NAME.values()).map(x => buildLabProfile(x.name,x.tier));
const LAB_PROFILE_BY_NAME = new Map(LAB_PROFILES.map(x => [x.name,x]));

function shortTitle(title, max=88) { return title.length > max ? title.slice(0,max-1).trimEnd()+"…" : title; }
function overlapHTML(profile) {
  const axes = profile.axes.slice(0,3).map(([a,n])=>`${escapeHTML(a)} (${n})`).join(" · ") || "broader APRL radar";
  return `<span class="overlap-${profile.overlap.toLowerCase()}">${profile.overlap}</span> · ${axes}`;
}
function renderLabCards() {
  const q = normalizeSearchText(document.getElementById("labSearch").value);
  const rows = LAB_PROFILES.filter(p => (activeLabTier === "all" || p.tier === activeLabTier) && (!q || normalizeSearchText([
    p.name,p.affiliation,...p.themes,...p.axes.map(x=>x[0]),...p.papers.map(x=>x.title)
  ].join(" ")).includes(q))).sort((a,b)=>b.papers.length-a.papers.length || b.lastPapers.length-a.lastPapers.length || a.name.localeCompare(b.name));
  document.getElementById("labCount").textContent = `${rows.length} PIs shown · topic diversity = unique author-declared keywords · click a card to open the lab view and load all matching papers below`;
  document.getElementById("labGrid").innerHTML = rows.map(p => `<button type="button" class="lab-card${selectedLabPI===p.name?" selected":""}" data-labpi="${escapeHTML(p.name)}">
    <div class="lab-card-head"><div><div class="lab-name">${escapeHTML(p.name)}</div><div class="lab-aff">${escapeHTML(p.affiliation)}</div></div><span class="tier-badge tier-${p.tier}">APRL relevance <span class="stars">${LAB_STARS[p.tier]}</span></span></div>
    <div class="lab-metrics-mini">
      <div class="lab-metric-mini"><b>${p.papers.length}</b><span>IROS26 papers</span></div>
      <div class="lab-metric-mini"><b>${p.lastPapers.length}</b><span>last-author</span></div>
      <div class="lab-metric-mini"><b>${p.firstAuthors.size}</b><span>first authors</span></div>
      <div class="lab-metric-mini"><b>${p.topicDiversity}</b><span>topic diversity</span></div>
    </div>
    <div class="lab-line"><strong>Themes</strong>${escapeHTML(p.themes.slice(0,4).join(" · ") || "Insufficient keyword data")}</div>
    <div class="lab-line"><strong>Your overlap</strong>${overlapHTML(p)}</div>
    <div class="lab-rep"><strong>Start with</strong> ${p.representatives.slice(0,2).map(x=>escapeHTML(shortTitle(x.title,64))).join(" · ")}</div>
  </button>`).join("") || `<div class="card" style="grid-column:1/-1;text-align:center;color:var(--muted)">No recommended PI matches this search.</div>`;
  document.querySelectorAll(".lab-card[data-labpi]").forEach(el => el.addEventListener("click",()=>selectLabPI(el.dataset.labpi)));
}
function coauthorNetworkSVG(profile) {
  const nodes = profile.coauthors.slice(0,8), cx=210, cy=135, radius=96;
  const points = nodes.map((x,i)=>({name:x[0],count:x[1],x:cx+radius*Math.cos(-Math.PI/2+i*2*Math.PI/nodes.length),y:cy+radius*Math.sin(-Math.PI/2+i*2*Math.PI/nodes.length)}));
  const edges = points.map(p=>`<line class="edge" x1="${cx}" y1="${cy}" x2="${p.x.toFixed(1)}" y2="${p.y.toFixed(1)}"/>`).join("");
  const circles = points.map(p=>`<g><circle class="node" cx="${p.x.toFixed(1)}" cy="${p.y.toFixed(1)}" r="${Math.min(18,10+p.count*2)}"/><text x="${p.x.toFixed(1)}" y="${(p.y+27).toFixed(1)}">${escapeHTML(p.name.split(",")[0])} · ${p.count}</text></g>`).join("");
  return `<svg class="coauthor-net" viewBox="0 0 420 270" role="img" aria-label="Top coauthor network for ${escapeHTML(profile.name)}">${edges}${circles}<circle class="pi-node" cx="${cx}" cy="${cy}" r="34"/><text class="pi-label" x="${cx}" y="${cy-2}">${escapeHTML(profile.name.split(",")[0])}</text><text class="pi-label" x="${cx}" y="${cy+12}">PI</text></svg>`;
}
function syncLabPaperSearch(profile, shouldScroll=false) {
  setPrimarySearch(profile.name);
  document.getElementById("searchMode").value = "and";
  document.getElementById("dayFilter").value = "";
  document.getElementById("sessionTypeFilter").value = "";
  document.getElementById("topicFilter").value = "";
  document.getElementById("countryFilter").value = "";
  document.getElementById("affFilter").value = "";
  document.getElementById("sortFilter").value = "default";
  authorCountFilter = null;
  applyFilter();
  if (shouldScroll) maybeScrollToSearch();
}
function selectLabPI(name, shouldScroll=true, syncPaperSearch=true) {
  const p = LAB_PROFILE_BY_NAME.get(name); if (!p) return;
  selectedLabPI = name;
  const maxKw = p.kw[0]?.[1] || 1;
  const summary = p.themes.length
    ? `The indexed program spans ${p.themes.slice(0,-1).join(", ")}${p.themes.length>1?", and ":""}${p.themes.at(-1)}. ${p.lastPapers.length} of ${p.papers.length} papers list this PI last; treat this as a group-program signal, not proof of supervision.`
    : "The program has too little declared-keyword data for a reliable automatic theme summary.";
  const reps = new Set(p.representatives.map(x=>x.code));
  const detail = document.getElementById("labDetail");
  detail.hidden = false;
  detail.innerHTML = `<div class="lab-detail-head"><div><span class="tier-badge tier-${p.tier}">APRL relevance <span class="stars">${LAB_STARS[p.tier]}</span></span><h3>${escapeHTML(p.name)}</h3><div class="lab-aff">${escapeHTML(p.affiliation)}</div></div><button class="btn-clear" id="labToSearch">${p.papers.length} papers loaded below ↓</button></div>
    <div class="lab-kpis">
      <div class="lab-kpi"><b>${p.papers.length}</b><span>Total papers</span></div><div class="lab-kpi"><b>${p.lastPapers.length}</b><span>Last-author papers</span></div>
      <div class="lab-kpi"><b>${p.firstAuthors.size}</b><span>Unique first authors (PI excluded)</span></div><div class="lab-kpi"><b>${p.topicDiversity}</b><span>Topic diversity (unique keywords)</span></div>
    </div>
    <div class="lab-panel" style="margin-bottom:14px"><h4>Automatic research-program summary</h4><div class="theme-chips">${p.themes.map(x=>`<span class="theme-chip">${escapeHTML(x)}</span>`).join("")}</div><p style="font-size:13px;line-height:1.55;margin:12px 0 6px">${escapeHTML(summary)}</p><div class="lab-line"><strong>Your overlap</strong>${overlapHTML(p)}</div></div>
    <div class="lab-detail-grid">
      <div class="lab-panel"><h4>Coauthor network · top 8</h4>${coauthorNetworkSVG(p)}</div>
      <div class="lab-panel"><h4>Keyword distribution</h4><div class="kw-bars">${p.kw.slice(0,10).map(([k,n])=>`<div class="kw-bar-row"><span>${escapeHTML(k)}</span><span class="track"><span class="fill" style="display:block;width:${n/maxKw*100}%"></span></span><b>${n}</b></div>`).join("")}</div></div>
    </div>
    <div class="lab-papers"><h4 style="margin:4px 0 0">All ${p.papers.length} indexed papers · representative picks marked</h4>${p.papers.map(x=>`<div class="lab-paper${reps.has(x.code)?" rep":""}" data-labpaper="${escapeHTML(x.code)}"><div class="meta">${reps.has(x.code)?"REPRESENTATIVE · ":""}${escapeHTML(x.day)} ${escapeHTML(x.time)} · ${escapeHTML(x.sessionType)} · ${escapeHTML(x.code)}</div><div class="t">${escapeHTML(x.title)}</div></div>`).join("")}</div>`;
  document.getElementById("labToSearch").addEventListener("click",()=>syncLabPaperSearch(p,true));
  detail.querySelectorAll("[data-labpaper]").forEach(el=>el.addEventListener("click",()=>jumpToPaper(el.dataset.labpaper)));
  renderLabCards();
  if (syncPaperSearch) syncLabPaperSearch(p,false);
  if (shouldScroll) detail.scrollIntoView({behavior:"smooth",block:"start"});
}
function initLabRadar() {
  const counts = Object.fromEntries(Object.entries(LAB_TIERS).map(([k,v])=>[k,v.length]));
  if (counts.S!==20 || counts.A!==30 || counts.B!==50 || LAB_PROFILE_BY_NAME.size!==100) console.error("APRL relevance inventory mismatch",counts,LAB_PROFILE_BY_NAME.size);
  document.querySelectorAll("[data-labtier]").forEach(btn=>btn.addEventListener("click",()=>{
    activeLabTier=btn.dataset.labtier;
    document.querySelectorAll("[data-labtier]").forEach(x=>x.classList.toggle("active",x===btn));
    renderLabCards();
  }));
  document.getElementById("labSearch").addEventListener("input",renderLabCards);
  renderLabCards();
  selectLabPI("Valada, Abhinav",false,false);
}
// Highlight on plain text only — escapes HTML, then wraps matches with <mark>.
// Pass plain (un-escaped) text in. Returns safe HTML.
function hl(text, terms){
  let out = escapeHTML(text);
  if (!terms || !terms.length) return out;
  for (const t of terms) {
    if (!t) continue;
    const re = new RegExp("(" + t.replace(/[.*+?^${}()|[\]\\]/g,"\\$&") + ")", "gi");
    out = out.replace(re, "<mark>$1</mark>");
  }
  return out;
}
function getSearchConditions() {
  return ["q", "q2", "q3"]
    .map(id => normalizeSearchText(document.getElementById(id).value))
    .filter(Boolean)
    .slice(0, 3);
}
function getSearchTermsForHighlight() {
  return getSearchConditions();
}
function matchesSearchCondition(p, q) {
  return q.length > 0 && p._search.includes(q);
}
function setPrimarySearch(value) {
  document.getElementById("q").value = value;
  document.getElementById("q2").value = "";
  document.getElementById("q3").value = "";
}
function dayChip(day, matched) {
  const cls = day === "Monday" ? "mon" : day === "Tuesday" ? "tue" : "wed";
  return `<span class="chip clickable ${cls}${matched ? " matched" : ""}" data-day="${day}" title="Filter by day: ${day}">${day.slice(0,3)}</span>`;
}
function render() {
  const wrap = document.getElementById("papers");
  const start = page * PAGE;
  const end = Math.min(start + PAGE, filtered.length);
  const searchConditions = getSearchConditions();
  const q = searchConditions.length === 1 ? searchConditions[0] : "";
  // Author-keyword search mode: q exactly matches one of PaperPlaza's
  // author-declared keywords. In that case we skip inline <mark> on
  // title/authors/abstract and instead yellow-highlight the matching kw chip.
  const kwSearchMode = q.length > 0 && KW_SET.has(q);
  const terms = kwSearchMode ? [] : getSearchTermsForHighlight();
  // Active-filter values for visual highlighting on each card
  const fDay     = document.getElementById("dayFilter").value;
  const fTopic   = document.getElementById("topicFilter").value;
  const fCountry = document.getElementById("countryFilter").value;
  const fAff     = document.getElementById("affFilter").value;
  const fType    = document.getElementById("sessionTypeFilter").value;
  const html = [];
  for (let i = start; i < end; i++) {
    const p = filtered[i];
    const tags = p.tags.map(t => {
      const cls = "chip tag clickable" + (fTopic && t === fTopic ? " matched" : "");
      return `<span class="${cls}" data-topic="${escapeHTML(t)}" title="Filter by topic: ${escapeHTML(t)}">${escapeHTML(t)}</span>`;
    }).join("");
    const kwChips = (p.keywords || []).map(k => {
      const cls = "chip kw clickable" + (kwSearchMode && k.toLowerCase() === q ? " matched" : "");
      return `<span class="${cls}" data-kwsearch="${escapeHTML(k)}" title="Search by keyword: ${escapeHTML(k)}">${escapeHTML(k)}</span>`;
    }).join("");
    const authorList = p.authors.map(a => {
      const authorInstitutions = canonicalizeAffiliation(a.aff);
      const authorCountries = new Set(authorInstitutions.map(inst => countryForCanonical(a.aff, inst)));
      const primaryInstitution = authorInstitutions[0] || a.aff;
      const affMatched = (fAff && authorInstitutions.includes(fAff)) || (fCountry && authorCountries.has(fCountry));
      const affCls = "aff clickable" + (affMatched ? " matched" : "");
      return `<b class="clickable" data-author="${escapeHTML(a.name)}" title="Search by author: ${escapeHTML(a.name)}">${hl(a.name, terms)}</b> `
        + `<span class="${affCls}" data-aff="${escapeHTML(primaryInstitution)}" title="Filter by institution: ${escapeHTML(authorInstitutions.join("; "))}">· ${hl(a.aff, terms)}</span>`;
    }).join('<span class="sep">|</span>');
    const kws = (p.keywords || []);
    const kwHTML = kws.length
      ? `<div class="kw-row"><span class="label">Keywords</span>${kws.map(k => `<span class="kw" data-kw="${escapeHTML(k)}">${hl(k, terms)}</span>`).join("")}</div>`
      : "";
    const abText = p.abstract
      ? `<div class="ab-text">${hl(p.abstract, terms)}</div>`
      : `<div class="empty">No abstract available for this paper.</div>`;
    const sim = SIMILAR_PAPERS[p.code] || [];
    const simItems = sim
      .map(s => [s, PAPER_BY_CODE.get(s.code)])
      .filter(([_, t]) => t)
      .slice(0, 5);
    const simHTML = simItems.length
      ? `<div class="similar-row">
           <span class="label">Similar papers <span class="sim-meta">· SPECTER2</span></span>
           <div class="similar-list">${simItems.map(([s, t]) => `
             <button type="button" class="similar-item" data-jump="${escapeHTML(s.code)}" title="Jump to ${escapeHTML(t.code)}">
               <span class="sim-score">${(s.sim*100).toFixed(0)}%</span>
               <span class="sim-text">
                 <span class="sim-title">${escapeHTML(t.title)}</span>
                 <span class="sim-tags">${escapeHTML(t.day.slice(0,3))} · ${escapeHTML(t.code)}${(t.tags||[]).length ? " · " + escapeHTML((t.tags||[]).slice(0,2).join(", ")) : ""}</span>
               </span>
             </button>`).join("")}</div>
         </div>`
      : "";
    const typeCls = p.sessionType === "Focused Sessions" ? "oral" : p.sessionType === "Lightning Talks" ? "interactive" : p.sessionType === "Award Candidates" ? "latebreak" : "tag";
    const typeChip = typeCls
      ? `<span class="chip clickable ${typeCls}${fType && p.sessionType === fType ? " matched" : ""}" data-stype="${escapeHTML(p.sessionType)}" title="Filter by format: ${escapeHTML(p.sessionType)}">${escapeHTML(p.sessionType)}</span>`
      : "";
    html.push(`<div class="paper" data-idx="${i}">
      <div class="meta">
        ${dayChip(p.day, fDay && p.day === fDay)}
        ${typeChip}
        <span>${escapeHTML(p.time)}</span>
        <span class="dot">·</span>
        <span title="Presentation room">Room ${escapeHTML(p.room || "TBA")}</span>
        <span class="dot">·</span>
        <span>${escapeHTML(p.code)}</span>
        <span class="dot">·</span>
        <span>${escapeHTML(p.session_title || "")}</span>
        ${tags}
        ${kwChips}
      </div>
      <div class="title">${hl(p.title, terms)}<span class="expand-hint"></span></div>
      <div class="authors">${authorList}</div>
      <div class="abstract">${kwHTML}${abText}${simHTML}</div>
    </div>`);
  }
  wrap.innerHTML = html.join("") || `<div class="card" style="text-align:center;color:var(--muted)">No results match your search.</div>`;
  // wire up click-to-expand on titles
  wrap.querySelectorAll(".paper").forEach(card => {
    const titleEl = card.querySelector(".title");
    titleEl.addEventListener("click", () => card.classList.toggle("open"));
  });
  // topic chip click → toggle topic filter (set/unset based on matched state)
  wrap.querySelectorAll(".paper .chip.tag[data-topic]").forEach(el => {
    el.addEventListener("click", (e) => {
      e.stopPropagation();
      const sel = document.getElementById("topicFilter");
      sel.value = el.classList.contains("matched") ? "" : el.dataset.topic;
      applyFilter();
      maybeScrollToSearch();
    });
  });
  // author keyword chip click → seed search query with that keyword
  wrap.querySelectorAll(".paper .chip.kw[data-kwsearch]").forEach(el => {
    el.addEventListener("click", (e) => {
      e.stopPropagation();
      setPrimarySearch(el.dataset.kwsearch);
      applyFilter();
      maybeScrollToSearch();
    });
  });
  // Curated PI clicks open the lab-centric view; other authors retain the
  // original paper-search behavior.
  wrap.querySelectorAll(".paper .authors b[data-author]").forEach(el => {
    el.addEventListener("click", (e) => {
      e.stopPropagation();
      if (LAB_PROFILE_BY_NAME.has(el.dataset.author)) {
        selectLabPI(el.dataset.author);
        return;
      }
      setPrimarySearch(el.dataset.author);
      applyFilter();
      maybeScrollToSearch();
    });
  });
  // Raw affiliation click → toggle the corresponding canonical institution.
  // If currently matched because of country filter, remove the country filter.
  wrap.querySelectorAll(".paper .authors .aff[data-aff]").forEach(el => {
    el.addEventListener("click", (e) => {
      e.stopPropagation();
      const aff = el.dataset.aff;
      const affSel = document.getElementById("affFilter");
      const countrySel = document.getElementById("countryFilter");
      if (affSel.value === aff) {
        affSel.value = "";
        applyFilter();
        maybeScrollToSearch();
        return;
      }
      // If the highlight is due to country filter and this aff sits in that country, clear the country filter
      if (countrySel.value && countryFor(aff) === countrySel.value) {
        countrySel.value = "";
        applyFilter();
        maybeScrollToSearch();
        return;
      }
      filterByAffiliation(aff);
    });
  });
  // day chip click → toggle day filter
  wrap.querySelectorAll(".paper .chip[data-day]").forEach(el => {
    el.addEventListener("click", (e) => {
      e.stopPropagation();
      const sel = document.getElementById("dayFilter");
      sel.value = el.classList.contains("matched") ? "" : el.dataset.day;
      applyFilter();
      maybeScrollToSearch();
    });
  });
  // session-type chip click → toggle the IROS session-format filter
  wrap.querySelectorAll(".paper .chip[data-stype]").forEach(el => {
    el.addEventListener("click", (e) => {
      e.stopPropagation();
      const sel = document.getElementById("sessionTypeFilter");
      sel.value = el.classList.contains("matched") ? "" : el.dataset.stype;
      applyFilter();
      maybeScrollToSearch();
    });
  });
  // in-abstract keyword chip → seed search (selector must avoid matching the
  // meta-row .chip.kw, which has data-kwsearch instead of data-kw)
  wrap.querySelectorAll(".paper .abstract .kw[data-kw]").forEach(el => {
    el.addEventListener("click", (e) => {
      e.stopPropagation();
      setPrimarySearch(el.dataset.kw);
      document.getElementById("topicFilter").value = "";
      applyFilter();
      maybeScrollToSearch();
    });
  });
  // similar-paper button click → reset filters and search by paper code
  wrap.querySelectorAll(".paper .similar-item[data-jump]").forEach(el => {
    el.addEventListener("click", (e) => {
      e.stopPropagation();
      e.preventDefault();
      jumpToPaper(el.dataset.jump);
    });
  });
  const totalPages = Math.max(1, Math.ceil(filtered.length / PAGE));
  document.getElementById("pager").innerHTML = `
    <button ${page<=0?"disabled":""} id="prev">← prev</button>
    <span class="info">${page+1} / ${totalPages}</span>
    <button ${page>=totalPages-1?"disabled":""} id="next">next →</button>`;
  document.getElementById("prev").onclick = () => { if (page>0){page--; render(); maybeScrollToSearch();} };
  document.getElementById("next").onclick = () => { if (page<totalPages-1){page++; render(); maybeScrollToSearch();} };
  document.getElementById("count").textContent = `${filtered.length.toLocaleString()} / ${N.toLocaleString()} papers`;
}
let authorCountFilter = null; // null | int
let shuffleSeed = Math.floor(Math.random() * 2147483647);
const DAY_ORDER = { Monday: 0, Tuesday: 1, Wednesday: 2 };
function hashForShuffle(p) {
  const s = String(p.id || p.code || p.title || "") + "|" + shuffleSeed;
  let h = 2166136261;
  for (let i = 0; i < s.length; i++) {
    h ^= s.charCodeAt(i);
    h = Math.imul(h, 16777619);
  }
  return h >>> 0;
}
const SORTERS = {
  "default":        (a, b) => (DAY_ORDER[a.day] - DAY_ORDER[b.day]) || a.time.localeCompare(b.time) || a.code.localeCompare(b.code),
  "shuffle":        (a, b) => hashForShuffle(a) - hashForShuffle(b),
  "title-asc":      (a, b) => a.title.toLowerCase().localeCompare(b.title.toLowerCase()),
  "title-desc":     (a, b) => b.title.toLowerCase().localeCompare(a.title.toLowerCase()),
  "authors-asc":    (a, b) => a.authors.length - b.authors.length,
  "authors-desc":   (a, b) => b.authors.length - a.authors.length,
  "affs-asc":       (a, b) => a.affs.length - b.affs.length,
  "affs-desc":      (a, b) => b.affs.length - a.affs.length,
  "countries-asc":  (a, b) => a.countries.length - b.countries.length,
  "countries-desc": (a, b) => b.countries.length - a.countries.length,
  "keywords-asc":   (a, b) => (a.keywords?.length || 0) - (b.keywords?.length || 0),
  "keywords-desc":  (a, b) => (b.keywords?.length || 0) - (a.keywords?.length || 0),
  "title-len-asc":  (a, b) => a.title.length - b.title.length,
  "title-len-desc": (a, b) => b.title.length - a.title.length,
};

function applyFilter() {
  const searchConditions = getSearchConditions();
  const searchMode = document.getElementById("searchMode").value;
  const day = document.getElementById("dayFilter").value;
  const topic = document.getElementById("topicFilter").value;
  const country = document.getElementById("countryFilter").value;
  const aff = document.getElementById("affFilter").value;
  const sort = document.getElementById("sortFilter").value;
  const sessionType = document.getElementById("sessionTypeFilter").value;
  filtered = PAPERS.filter(p => {
    if (day && p.day !== day) return false;
    if (sessionType && p.sessionType !== sessionType) return false;
    if (topic && !p.tags.includes(topic)) return false;
    if (country && !p.countries.includes(country)) return false;
    if (aff && !p.affs.includes(aff)) return false;
    if (authorCountFilter !== null && p.authors.length !== authorCountFilter) return false;
    if (!searchConditions.length) return true;
    return searchMode === "or"
      ? searchConditions.some(q => matchesSearchCondition(p, q))
      : searchConditions.every(q => matchesSearchCondition(p, q));
  });
  // Stable sort with default tiebreaker
  const cmp = SORTERS[sort] || SORTERS.default;
  if (sort !== "default") {
    filtered = filtered.slice().sort((a, b) => cmp(a, b) || SORTERS.default(a, b));
  }
  page = 0;
  render();
  syncURL();
  renderActiveFilters();
  if (typeof onAfterApplyFilter !== "undefined" && onAfterApplyFilter) onAfterApplyFilter();
}
var onAfterApplyFilter = null; // hooked later by stat-grid wiring

// ----- scroll helper: only jump to results if the search section
//       isn't already comfortably in view. Saves the user's scroll
//       position when they tap a chip inside an already-visible card. -----
function maybeScrollToSearch() {
  const sec = document.getElementById("search");
  if (!sec) return;
  const rect = sec.getBoundingClientRect();
  // If the section header is well below the viewport (more than ~25% down),
  // pull it into view. Otherwise leave the scroll untouched.
  if (rect.top > window.innerHeight * 0.25) {
    sec.scrollIntoView({behavior:"smooth"});
  }
}

// ----- click helpers from charts -----
function filterByCountry(country) {
  document.getElementById("countryFilter").value = country;
  document.getElementById("affFilter").value = "";
  applyFilter();
  maybeScrollToSearch();
}
function filterByAuthorCount(n) {
  authorCountFilter = n;
  applyFilter();
  maybeScrollToSearch();
}
function filterByAffiliation(aff) {
  // If institution isn't in the select (only top 100 are), append it dynamically.
  const sel = document.getElementById("affFilter");
  let found = false;
  for (const opt of sel.options) if (opt.value === aff) { found = true; break; }
  if (!found) {
    const o = document.createElement("option");
    o.value = aff; o.textContent = aff;
    sel.appendChild(o);
  }
  sel.value = aff;
  document.getElementById("countryFilter").value = "";
  applyFilter();
  maybeScrollToSearch();
}

// ----- URL state sync -----
function syncURL() {
  const params = new URLSearchParams();
  const q = document.getElementById("q").value.trim();
  const q2 = document.getElementById("q2").value.trim();
  const q3 = document.getElementById("q3").value.trim();
  const searchMode = document.getElementById("searchMode").value;
  const day = document.getElementById("dayFilter").value;
  const topic = document.getElementById("topicFilter").value;
  const country = document.getElementById("countryFilter").value;
  const aff = document.getElementById("affFilter").value;
  if (q) params.set("q", q);
  if (q2) params.set("q2", q2);
  if (q3) params.set("q3", q3);
  if ((q2 || q3) && searchMode === "or") params.set("qop", "or");
  if (day) params.set("day", day);
  const stype = document.getElementById("sessionTypeFilter").value;
  if (stype) params.set("type", stype);
  if (topic) params.set("topic", topic);
  if (country) params.set("country", country);
  if (aff) params.set("aff", aff);
  if (authorCountFilter !== null) params.set("authors", String(authorCountFilter));
  const sort = document.getElementById("sortFilter").value;
  if (sort && sort !== "default") params.set("sort", sort);
  if (sort === "shuffle") params.set("seed", String(shuffleSeed));
  const qs = params.toString();
  const newURL = window.location.pathname + (qs ? "?" + qs : "") + window.location.hash;
  history.replaceState(null, "", newURL);
}

function loadFromURL() {
  const params = new URLSearchParams(window.location.search);
  if (params.has("q")) document.getElementById("q").value = params.get("q");
  if (params.has("q2")) document.getElementById("q2").value = params.get("q2");
  if (params.has("q3")) document.getElementById("q3").value = params.get("q3");
  if (params.get("qop") === "or") document.getElementById("searchMode").value = "or";
  if (params.has("day")) document.getElementById("dayFilter").value = params.get("day");
  if (params.has("type")) document.getElementById("sessionTypeFilter").value = params.get("type");
  if (params.has("topic")) document.getElementById("topicFilter").value = params.get("topic");
  if (params.has("country")) document.getElementById("countryFilter").value = params.get("country");
  if (params.has("aff")) {
    const sel = document.getElementById("affFilter");
    const v = params.get("aff");
    let found = false;
    for (const o of sel.options) if (o.value === v) { found = true; break; }
    if (!found) {
      const o = document.createElement("option"); o.value = v; o.textContent = v; sel.appendChild(o);
    }
    sel.value = v;
  }
  if (params.has("authors")) {
    const n = parseInt(params.get("authors"), 10);
    if (!isNaN(n)) authorCountFilter = n;
  }
  if (params.has("sort")) {
    const s = params.get("sort");
    const sel = document.getElementById("sortFilter");
    for (const o of sel.options) if (o.value === s) { sel.value = s; break; }
  }
  if (params.has("seed")) {
    const n = parseInt(params.get("seed"), 10);
    if (!isNaN(n)) shuffleSeed = n;
  }
}

function renderActiveFilters() {
  const wrap = document.getElementById("activeFilters");
  if (!wrap) return;
  const items = [];
  const q = document.getElementById("q").value.trim();
  const q2 = document.getElementById("q2").value.trim();
  const q3 = document.getElementById("q3").value.trim();
  const searchMode = document.getElementById("searchMode").value;
  const day = document.getElementById("dayFilter").value;
  const topic = document.getElementById("topicFilter").value;
  const country = document.getElementById("countryFilter").value;
  const aff = document.getElementById("affFilter").value;
  const searches = [q, q2, q3].filter(Boolean);
  if (searches.length) {
    const label = searches.length === 1 ? "search: " + searches[0] : "search (" + searchMode.toUpperCase() + "): " + searches.join(" / ");
    items.push(["q", label, () => {
      document.getElementById("q").value = "";
      document.getElementById("q2").value = "";
      document.getElementById("q3").value = "";
      document.getElementById("searchMode").value = "and";
    }]);
  }
  if (day)     items.push(["day",     day,                  () => { document.getElementById("dayFilter").value = ""; }]);
  const stype = document.getElementById("sessionTypeFilter").value;
  if (stype)   items.push(["type",    stype,                () => { document.getElementById("sessionTypeFilter").value = ""; }]);
  if (topic)   items.push(["topic",   "topic: " + topic,    () => { document.getElementById("topicFilter").value = ""; }]);
  if (country) items.push(["country", country,              () => { document.getElementById("countryFilter").value = ""; }]);
  if (aff)     items.push(["aff",     "institution: " + aff, () => { document.getElementById("affFilter").value = ""; }]);
  if (authorCountFilter !== null) items.push(["authors", `${authorCountFilter} authors`, () => { authorCountFilter = null; }]);
  wrap.innerHTML = items.map(([k,label]) => `<span class="active-chip" data-k="${k}">${escapeHTML(label)}<span class="x">×</span></span>`).join("");
  wrap.querySelectorAll(".active-chip").forEach((el, i) => {
    el.addEventListener("click", () => { items[i][2](); applyFilter(); });
  });
}

document.getElementById("q").addEventListener("input", applyFilter);
document.getElementById("q2").addEventListener("input", applyFilter);
document.getElementById("q3").addEventListener("input", applyFilter);
document.getElementById("searchMode").addEventListener("change", applyFilter);
document.getElementById("dayFilter").addEventListener("change", applyFilter);
document.getElementById("sessionTypeFilter").addEventListener("change", applyFilter);
document.getElementById("topicFilter").addEventListener("change", applyFilter);
document.getElementById("countryFilter").addEventListener("change", applyFilter);
document.getElementById("affFilter").addEventListener("change", applyFilter);
document.getElementById("sortFilter").addEventListener("change", applyFilter);

// Brand click → full reset to initial home state
function resetToHome() {
  document.getElementById("q").value = "";
  document.getElementById("q2").value = "";
  document.getElementById("q3").value = "";
  document.getElementById("searchMode").value = "and";
  document.getElementById("dayFilter").value = "";
  document.getElementById("sessionTypeFilter").value = "";
  document.getElementById("topicFilter").value = "";
  document.getElementById("countryFilter").value = "";
  document.getElementById("affFilter").value = "";
  document.getElementById("sortFilter").value = "default";
  authorCountFilter = null;
  applyFilter();
  history.replaceState(null, "", window.location.pathname);
  window.scrollTo({ top: 0, behavior: "smooth" });
}
document.getElementById("brandHome").addEventListener("click", (e) => {
  e.preventDefault();
  resetToHome();
});

// Jump to a specific paper by code (used by Similar-papers links).
// Resets every filter so the target is always reachable, then searches by
// its code (which is included in p._search) so it appears as the only hit.
function jumpToPaper(code) {
  document.getElementById("q2").value = "";
  document.getElementById("q3").value = "";
  document.getElementById("searchMode").value = "and";
  document.getElementById("dayFilter").value = "";
  document.getElementById("sessionTypeFilter").value = "";
  document.getElementById("topicFilter").value = "";
  document.getElementById("countryFilter").value = "";
  document.getElementById("affFilter").value = "";
  document.getElementById("sortFilter").value = "default";
  authorCountFilter = null;
  document.getElementById("q").value = code;
  applyFilter();
  // applyFilter → render() is synchronous, so the new card is in the DOM now.
  const wrap = document.getElementById("papers");
  const card = wrap?.querySelector(".paper");
  if (card) {
    card.classList.add("open");
    card.scrollIntoView({ behavior: "smooth", block: "start" });
  }
}
document.getElementById("shuffleResults").addEventListener("click", () => {
  shuffleSeed = Math.floor(Math.random() * 2147483647);
  document.getElementById("sortFilter").value = "shuffle";
  applyFilter();
});
document.getElementById("pageSizeFilter").addEventListener("change", (e) => {
  PAGE = parseInt(e.target.value, 10);
  page = 0;
  render();
});
document.getElementById("clearFilters").addEventListener("click", () => {
  document.getElementById("q").value = "";
  document.getElementById("q2").value = "";
  document.getElementById("q3").value = "";
  document.getElementById("searchMode").value = "and";
  document.getElementById("dayFilter").value = "";
  document.getElementById("sessionTypeFilter").value = "";
  document.getElementById("topicFilter").value = "";
  document.getElementById("countryFilter").value = "";
  document.getElementById("affFilter").value = "";
  document.getElementById("sortFilter").value = "default";
  shuffleSeed = Math.floor(Math.random() * 2147483647);
  authorCountFilter = null;
  applyFilter();
});

initLabRadar();
loadFromURL();
applyFilter();

// Sidebar active link tracking
const sectionIds = ["overview","submissions","stats","kw-trends","trends","eda-aff","eda-heatmap","eda-misc","lab-radar","search"];
const navLinks = Array.from(document.querySelectorAll(".sidebar a"));
const observer = new IntersectionObserver((entries) => {
  entries.forEach(en => {
    if (en.isIntersecting) {
      const id = en.target.id;
      navLinks.forEach(a => a.classList.toggle("active", a.getAttribute("href") === "#" + id));
    }
  });
}, { rootMargin: "-40% 0px -55% 0px", threshold: 0 });
sectionIds.forEach(id => { const el = document.getElementById(id); if (el) observer.observe(el); });

document.getElementById("genDate").textContent = new Date().toISOString().slice(0,10);
</script>
</body>
</html>
"""

html_filled = (HTML
    .replace("__PAPERS_JSON__", papers_json)
    .replace("__SIMILAR_JSON__", similar_json)
    .replace("__COUNTRY_HINTS_JSON__", country_hints_json)
    .replace("__COUNTRY_OVERRIDES_JSON__", country_overrides_json)
    .replace("__INSTITUTION_ALIASES_JSON__", institution_aliases_json)
    .replace("__INSTITUTION_MULTIMAP_JSON__", institution_multimap_json)
    .replace("__INSTITUTION_COUNTRIES_JSON__", institution_country_json)
    .replace("__INSTITUTION_SITE_COUNTRY_OVERRIDES_JSON__", institution_site_country_json)
    .replace("__INSTITUTION_PARENT_ORG_JSON__", institution_parent_org_json))
OUT.write_text(html_filled, encoding="utf-8")
print(f"Wrote {OUT} ({OUT.stat().st_size/1024:.0f} KB)")
