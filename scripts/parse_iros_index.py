"""Parse the saved IROS 2026 Paper & Author Index into explorer data."""
from __future__ import annotations

import argparse
import html
import json
import re
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_INPUT = Path.home() / "Downloads" / "Paper & Author Index _ IROS 2026.html"
DEFAULT_OUTPUT = ROOT / "output" / "papers.json"


def embedded_json(page: str, element_id: str):
    match = re.search(
        rf'<script type="application/json" id="{re.escape(element_id)}">(.*?)</script>',
        page,
        flags=re.DOTALL,
    )
    if not match:
        raise ValueError(f"embedded JSON #{element_id} was not found")
    return json.loads(html.unescape(match.group(1)))


def split_values(value: str) -> list[str]:
    return [part.strip() for part in (value or "").split(";") if part.strip()]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", nargs="?", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    page = args.input.read_text(encoding="utf-8")
    paper_rows = embedded_json(page, "pi-data")
    author_rows = embedded_json(page, "ai-data")

    affiliations: dict[tuple[str, str], list[str]] = defaultdict(list)
    for author in author_rows:
        name = (author.get("name") or "").strip()
        affiliation = (author.get("affiliation") or "").strip() or "Unknown affiliation"
        for paper in author.get("papers") or []:
            pn = str(paper.get("pn") or "").strip()
            key = (pn, name)
            if affiliation not in affiliations[key]:
                affiliations[key].append(affiliation)

    papers = []
    unmatched = []
    for row in paper_rows:
        pn = str(row.get("pn") or "").strip()
        p_fields = row.get("p_fields") or {}
        author_names = split_values(row.get("authors") or "")
        authors = []
        for name in author_names:
            affs = affiliations.get((pn, name), [])
            if not affs:
                unmatched.append((pn, name))
            authors.append({"name": name, "aff": " / ".join(affs) if affs else "Unknown affiliation"})

        code = str(p_fields.get("code") or pn)
        time = str(row.get("time") or p_fields.get("b") or "")
        papers.append(
            {
                "id": f"IROS26-{pn}",
                "code": f"{code} · #{pn}" if code != pn else f"#{pn}",
                "paper_number": pn,
                "day": row.get("day") or p_fields.get("day") or "",
                "time": time,
                "session": row.get("sid") or code,
                "session_title": row.get("session") or p_fields.get("tn") or "",
                "session_type": row.get("type") or "Session",
                "room": row.get("room") or p_fields.get("loc") or "",
                "title": row.get("title") or "",
                "authors": authors,
                "keywords": split_values(row.get("keywords") or ""),
                "abstract": "",
            }
        )

    paper_numbers = [paper["paper_number"] for paper in papers]
    if len(papers) != 1933:
        raise ValueError(f"expected 1,933 papers, parsed {len(papers):,}")
    if len(set(paper_numbers)) != len(paper_numbers):
        raise ValueError("duplicate paper numbers found")
    if any(not paper["title"] or not paper["authors"] for paper in papers):
        raise ValueError("paper title or author list is missing")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "papers": papers,
        "n_papers": len(papers),
        "source": "IROS 2026 Paper & Author Index",
        "unmatched_author_affiliations": len(unmatched),
    }
    args.output.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    print(
        f"Wrote {args.output} with {len(papers):,} papers; "
        f"{len(unmatched):,} author-paper affiliations unmatched"
    )


if __name__ == "__main__":
    main()
