"""Tiny self-contained visual helpers for the static HTML report.

No plotting library and no CDN: every "chart" is inline CSS/HTML (colored
divs and table cells). This keeps each weekly report a small, self-contained
file that opens offline by double-click — the C7 "static self-contained HTML"
intent, achieved without inlining a ~3.5 MB plotly.js into every week. Plotly
/ Quarto stays an upgrade path (recorded in the decision-log amendment).

One fixed visual language: a diverging score scale (low = red, mid = grey,
high = green), chosen toward color-blind legibility by keeping the extremes
distinct in luminance as well as hue.
"""

from __future__ import annotations


def _lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def score_color(score: float | None) -> str:
    """Map a 0-100 score to a hex color: 0 red -> 50 grey -> 100 green."""
    if score is None:
        return "#eeeeee"
    s = max(0.0, min(100.0, float(score)))
    # anchor colors (luminance-separated for color-blind legibility)
    low = (178, 24, 43)     # red
    mid = (222, 222, 222)   # grey
    high = (27, 120, 55)    # green
    if s <= 50:
        t = s / 50.0
        rgb = tuple(_lerp(low[i], mid[i], t) for i in range(3))
    else:
        t = (s - 50) / 50.0
        rgb = tuple(_lerp(mid[i], high[i], t) for i in range(3))
    return "#%02x%02x%02x" % tuple(int(round(c)) for c in rgb)


def text_on(color_hex: str) -> str:
    """Pick black/white text for contrast against a background hex color."""
    r = int(color_hex[1:3], 16)
    g = int(color_hex[3:5], 16)
    b = int(color_hex[5:7], 16)
    luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
    return "#000000" if luminance > 0.6 else "#ffffff"


def gauge_html(value: float, *, vmin: float = 0, vmax: float = 100) -> str:
    """A horizontal 0-100 track with a marker at `value`, colored by score."""
    pct = max(0.0, min(100.0, (value - vmin) / (vmax - vmin) * 100))
    color = score_color(value)
    return (
        f'<div class="gauge"><div class="gauge-fill" style="width:{pct:.1f}%;'
        f'background:{color}"></div>'
        f'<div class="gauge-marker" style="left:{pct:.1f}%"></div></div>'
    )


def _pts(values, w, h, pad=2):
    """Normalize a value series to SVG polyline points within (w,h)."""
    vals = [v for v in values if v is not None]
    if len(vals) < 2:
        return None, min(vals) if vals else None, max(vals) if vals else None
    lo, hi = min(vals), max(vals)
    span = (hi - lo) or 1.0
    n = len(values)
    step = (w - 2 * pad) / (n - 1)
    pts = []
    for i, v in enumerate(values):
        if v is None:
            continue
        x = pad + i * step
        y = h - pad - (v - lo) / span * (h - 2 * pad)
        pts.append(f"{x:.1f},{y:.1f}")
    return " ".join(pts), lo, hi


def sparkline_svg(values, *, w: int = 130, h: int = 26, color: str = "#3f6fb0") -> str:
    """A minimal inline-SVG sparkline (no axes). Last point dotted."""
    pts, lo, hi = _pts(values, w, h)
    if not pts:
        return '<span class="spark-na">—</span>'
    last = pts.split(" ")[-1]
    lx, ly = last.split(",")
    return (
        f'<svg class="spark" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
        f'preserveAspectRatio="none" role="img">'
        f'<polyline fill="none" stroke="{color}" stroke-width="1.4" points="{pts}"/>'
        f'<circle cx="{lx}" cy="{ly}" r="1.9" fill="{color}"/></svg>'
    )


def regime_map_svg(points, *, w: int = 320, h: int = 240) -> str:
    """2D regime map: X = growth tilt, Y = inflation/commodities tilt, in
    [-1,+1]. Draws quadrant axes, a 26-week trail (faded->bold), and labels the
    current point. `points` = ordered list of (x, y) oldest..newest."""
    pad = 26
    def sx(x): return pad + (x + 1) / 2 * (w - 2 * pad)
    def sy(y): return (h - pad) - (y + 1) / 2 * (h - 2 * pad)
    parts = [
        f'<svg class="regime-map" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img">',
        f'<line x1="{sx(0):.1f}" y1="{pad}" x2="{sx(0):.1f}" y2="{h-pad}" class="rm-axis"/>',
        f'<line x1="{pad}" y1="{sy(0):.1f}" x2="{w-pad}" y2="{sy(0):.1f}" class="rm-axis"/>',
        f'<text x="{w-pad}" y="{sy(0)-4:.1f}" class="rm-lab" text-anchor="end">growth +</text>',
        f'<text x="{sx(0)+4:.1f}" y="{pad+8}" class="rm-lab">inflation +</text>',
    ]
    pts = [p for p in points if p is not None]
    if len(pts) >= 2:
        poly = " ".join(f"{sx(x):.1f},{sy(y):.1f}" for x, y in pts)
        parts.append(f'<polyline fill="none" stroke="#8aa0c0" stroke-width="1.3" points="{poly}"/>')
    for i, (x, y) in enumerate(pts):
        if i == len(pts) - 1:
            parts.append(f'<circle cx="{sx(x):.1f}" cy="{sy(y):.1f}" r="4.5" class="rm-now"/>')
        else:
            op = 0.15 + 0.5 * (i / max(1, len(pts) - 1))
            parts.append(f'<circle cx="{sx(x):.1f}" cy="{sy(y):.1f}" r="2" fill="#8aa0c0" opacity="{op:.2f}"/>')
    parts.append("</svg>")
    return "".join(parts)


def tilt_bar_html(value: float) -> str:
    """A [-1,+1] tilt bar: center line, fill left (neg) or right (pos)."""
    v = max(-1.0, min(1.0, value))
    half = abs(v) * 50.0
    side = "left" if v < 0 else "right"
    color = score_color(50 + v * 50)
    fill = (
        f'<div class="tilt-fill" style="{side}:50%;width:{half:.1f}%;'
        f'background:{color}"></div>'
    )
    return f'<div class="tilt"><div class="tilt-center"></div>{fill}</div>'
