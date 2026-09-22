#!/usr/bin/env python3
"""Render the scraped contribution JSON as the classic 53-week x 7-day
calendar of rounded boxes. Reveals once with a diagonal slide-down (CSS
keyframes that play on load and freeze -- no looping glow), plus a
Less -> More legend and a stats footer.
"""
import json
import math
from datetime import datetime, timedelta
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "contributions.json"
OUT_PATH = Path(__file__).resolve().parent.parent / "contrib-heatmap.svg"

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]
#          none      ->                                          neon top end

CELL = 12
GAP = 3
PAD_X = 28
PAD_TOP = 46
PAD_BOTTOM = 56
LABEL_W = 28
BG = "#0d1117"
BORDER = "#30363d"
TEXT_COLOR = "#c9d1d9"
MUTED = "#8b949e"

MONTH_NAMES = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
WEEKDAY_LABELS = {1: "Lun", 3: "Mié", 5: "Vie"}  # weekday row (Sun=0) -> label


def level_for(count: int) -> int:
    if count <= 0:
        return 0
    if count <= 2:
        return 1
    if count <= 5:
        return 2
    if count <= 9:
        return 3
    if count <= 14:
        return 4
    return 5


def build_grid(days: list[dict]):
    by_date = {d["date"]: d["count"] for d in days}
    first = datetime.strptime(days[0]["date"], "%Y-%m-%d").date()
    last = datetime.strptime(days[-1]["date"], "%Y-%m-%d").date()
    start = first - timedelta(days=(first.isoweekday() % 7))
    total = (last - start).days + 1
    weeks = math.ceil(total / 7)

    grid = [[0] * 7 for _ in range(weeks)]
    month_starts: dict[int, int] = {}
    seen_months: set[tuple[int, int]] = set()
    cursor = start
    for i in range(weeks * 7):
        w, d = divmod(i, 7)
        grid[w][d] = by_date.get(cursor.strftime("%Y-%m-%d"), 0)
        month_key = (cursor.year, cursor.month)
        if cursor.day <= 7 and month_key not in seen_months:
            month_starts[w] = cursor.month
            seen_months.add(month_key)
        cursor += timedelta(days=1)
    return grid, weeks, month_starts, start


def build_svg(data: dict) -> str:
    days = data["days"]
    stats = data.get("stats", {})
    grid, weeks, month_starts, start = build_grid(days)

    grid_w = weeks * (CELL + GAP) - GAP
    grid_h = 7 * (CELL + GAP) - GAP
    width = LABEL_W + PAD_X + grid_w + PAD_X
    height = PAD_TOP + grid_h + PAD_BOTTOM

    style_rules = []
    cells = []
    for w in range(weeks):
        for d in range(7):
            count = grid[w][d]
            level = level_for(count)
            x = LABEL_W + PAD_X + w * (CELL + GAP)
            y = PAD_TOP + d * (CELL + GAP)
            delay = (w + d) * 0.012
            cls = f"c{w}_{d}"
            cell_date = (start + timedelta(days=w * 7 + d)).strftime("%d/%m/%Y")
            style_rules.append(
                f".{cls}{{animation:reveal .5s cubic-bezier(.25,.1,.25,1) {delay:.3f}s both;}}"
            )
            cells.append(
                f'<rect class="{cls}" x="{x}" y="{y}" width="{CELL}" height="{CELL}" '
                f'rx="3" fill="{PALETTE[level]}"><title>{count} contribuciones el {cell_date}</title></rect>'
            )

    month_labels = [
        f'<text x="{LABEL_W + PAD_X + w * (CELL + GAP)}" y="{PAD_TOP - 12}" '
        f'fill="{MUTED}" font-size="11">{MONTH_NAMES[month - 1]}</text>'
        for w, month in month_starts.items()
    ]

    weekday_labels = [
        f'<text x="0" y="{PAD_TOP + row * (CELL + GAP) + CELL - 2}" fill="{MUTED}" '
        f'font-size="10">{label}</text>'
        for row, label in WEEKDAY_LABELS.items()
    ]

    legend_x = width - PAD_X - (len(PALETTE) * (CELL + 3)) - 60
    legend_y = height - 24
    legend = [f'<text x="{legend_x - 46}" y="{legend_y + 10}" fill="{MUTED}" font-size="11">Less</text>']
    for i, color in enumerate(PALETTE):
        legend.append(
            f'<rect x="{legend_x + i * (CELL + 3)}" y="{legend_y}" width="{CELL}" height="{CELL}" '
            f'rx="3" fill="{color}"/>'
        )
    legend.append(
        f'<text x="{legend_x + len(PALETTE) * (CELL + 3) + 6}" y="{legend_y + 10}" '
        f'fill="{MUTED}" font-size="11">More</text>'
    )

    total = stats.get("total", sum(d["count"] for d in days))
    streak = stats.get("current_streak", 0)
    longest = stats.get("longest_streak", 0)
    footer = (
        f'<text x="{LABEL_W + PAD_X}" y="{legend_y + 10}" fill="{TEXT_COLOR}" font-size="12">'
        f"{total:,} contribuciones en el último año · racha actual: {streak}d · "
        f"racha más larga: {longest}d</text>"
    )

    svg = [
        f'<svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" '
        f'font-family="Consolas, \'SF Mono\', Menlo, monospace">',
        "<style>@keyframes reveal{from{opacity:0;transform:translate(0,-6px);}"
        "to{opacity:1;transform:translate(0,0);}}" + "".join(style_rules) + "</style>",
        f'<rect x="0" y="0" width="{width}" height="{height}" rx="14" fill="{BG}" stroke="{BORDER}"/>',
        "".join(month_labels),
        "".join(weekday_labels),
        "".join(cells),
        "".join(legend),
        footer,
        "</svg>",
    ]
    return "".join(svg)


def main() -> None:
    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    svg = build_svg(data)
    OUT_PATH.write_text(svg, encoding="utf-8")
    print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
