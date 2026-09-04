"""수집 파일 파서.

두 가지 입력 형태를 지원:
1. markdown 표  ( | 순위 | 선수명 | 지표1 | 지표2 | ... | )  ← 사용자가 올리는 리포트
2. FotMob 리더보드 raw 붙여넣기 (선수당 4개 markdown 링크)  ← 나중에 raw 를 받을 경우

값 정제: **굵게**, 단위(회/개/명), %, 쉼표, 공백 제거 → float.
"""

from __future__ import annotations

import re
from pathlib import Path

_NUM = re.compile(r"-?\d+(?:\.\d+)?")
_FOTMOB_LINK = re.compile(r"\[([^\]]*)\]\(https?://[^)]*?/players/(\d+)/([a-z0-9-]+)\)")


def to_num(cell: str):
    """표 셀 문자열 → float 또는 None."""
    if cell is None:
        return None
    s = cell.replace("**", "").strip()
    if s in ("", "-", "—", "N/A", "n/a"):
        return None
    m = _NUM.search(s.replace(",", ""))
    return float(m.group()) if m else None


def parse_md_table(path: str | Path) -> list[dict[str, str]]:
    """파일에서 가장 큰 markdown 표를 찾아 [{헤더: 원본셀, ...}] 리스트로."""
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    blocks: list[list[str]] = []
    cur: list[str] = []
    for ln in lines:
        if ln.lstrip().startswith("|"):
            cur.append(ln.strip())
        elif cur:
            blocks.append(cur)
            cur = []
    if cur:
        blocks.append(cur)
    if not blocks:
        return []

    block = max(blocks, key=len)

    def cells(row: str) -> list[str]:
        return [c.strip() for c in row.strip().strip("|").split("|")]

    header = cells(block[0])
    rows = []
    for row in block[1:]:
        c = cells(row)
        if set("".join(c)) <= set(":- "):   # |:---|:---| 구분선
            continue
        if len(c) != len(header):
            continue
        rows.append(dict(zip(header, c)))
    return rows


def parse_fotmob_leaderboard(text: str) -> list[dict]:
    """FotMob 리더보드 raw (선수당 링크 4개) → [{rank, fotmob_id, slug, name, value, secondary_*}]."""
    tok = [(m.group(1).strip(), m.group(2), m.group(3)) for m in _FOTMOB_LINK.finditer(text)]
    out, i = [], 0
    while i + 3 < len(tok):
        (rank_l, pid, slug), (name_l, p2, _), (sec_l, p3, _), (val_l, p4, _) = tok[i:i + 4]
        if not (pid == p2 == p3 == p4):
            i += 1
            continue
        sec = sec_l.split(":", 1)
        out.append({
            "rank": int(_NUM.search(rank_l).group()) if _NUM.search(rank_l) else None,
            "fotmob_id": pid, "slug": slug, "name": name_l,
            "value": to_num(val_l),
            "secondary_label": sec[0].strip() if len(sec) == 2 else "",
            "secondary_value": to_num(sec[1]) if len(sec) == 2 else None,
        })
        i += 4
    return out


def name_column(row: dict[str, str]) -> str | None:
    for k in row:
        if "선수" in k or k.lower() in ("name", "player"):
            return row[k].replace("**", "").strip()
    return None
