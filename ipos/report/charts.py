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
