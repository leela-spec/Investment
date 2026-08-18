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
    """Map a 0-100 score to a CVD-SAFE diverging hex: 0 red -> 50 grey -> 100
    blue (ColorBrewer RdBu). Red↔green FAILs the palette validator (deuteranope
    ΔE 2.5); red↔blue PASSes light & dark (ΔE 21/17). Low = risk-off/weak,
    high = supportive/strong."""
    if score is None:
        return "#eeeeee"
    s = max(0.0, min(100.0, float(score)))
    low = (178, 24, 43)     # red  #b2182b
    mid = (230, 230, 230)   # neutral grey
    high = (33, 102, 172)   # blue #2166ac
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
    """A bullet gauge: a 0-100 track with faint qualitative zone dividers at
    20/50/80, a score-colored measure fill, and a marker at `value`."""
    pct = max(0.0, min(100.0, (value - vmin) / (vmax - vmin) * 100))
    color = score_color(value)
    ticks = "".join(
        f'<div class="gauge-tick" style="left:{t}%"></div>' for t in (20, 50, 80)
    )
    return (
        f'<div class="gauge">{ticks}'
        f'<div class="gauge-fill" style="width:{pct:.1f}%;background:{color}"></div>'
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


_MONTHS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun",
           "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")

# Macro quadrants (growth × inflation) — interpretive anchors. Keys match the
# ``macro_quadrants`` glossary section so the report can explain each one.
QUADRANTS = (
    ("Reflation", 0.52, 0.58),     # growth+ inflation+
    ("Stagflation", -0.52, 0.58),  # growth- inflation+
    ("Goldilocks", 0.52, -0.62),   # growth+ inflation-
    ("Deflation", -0.52, -0.62),   # growth- inflation-
)


def _mon(d) -> str:
    return _MONTHS[d.month - 1]


def _short_date(d) -> str:
    return f"{_MONTHS[d.month - 1]} {d.day}"


def regime_map_svg(points, *, w: int = 400, h: int = 320) -> str:
    """2D regime map: X = growth tilt, Y = inflation/commodities tilt, in
    [-1,+1].

    ``points`` = ordered ``(week_date, x, y)`` oldest..newest. Draws the
    quadrant axes, the trail (older half muted, recent half accented and
    arrow-headed so direction of travel is unambiguous), a larger dot plus
    month label at each month boundary, and start/now callouts. Every point
    carries a ``<title>`` so hovering gives the week and its coordinates.

    Previously this drew an unlabelled 1.3px polyline with 2px dots at 15-65%
    opacity, which was effectively invisible — the path was there but unreadable.
    """
    pad = 34
    def sx(x): return pad + (x + 1) / 2 * (w - 2 * pad)
    def sy(y): return (h - pad) - (y + 1) / 2 * (h - 2 * pad)

    parts = [
        f'<svg class="regime-map" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img">',
        '<defs><marker id="rm-arrow" viewBox="0 0 10 10" refX="8" refY="5" '
        'markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
        '<path d="M 0 0 L 10 5 L 0 10 z" class="rm-arrowhead"/></marker></defs>',
    ]
    for lab, qx, qy in QUADRANTS:
        parts.append(
            f'<text x="{sx(qx):.1f}" y="{sy(qy):.1f}" class="rm-quad" '
            f'text-anchor="middle">{lab}<title>{lab} quadrant</title></text>'
        )
    parts += [
        f'<line x1="{sx(0):.1f}" y1="{pad}" x2="{sx(0):.1f}" y2="{h-pad}" class="rm-axis"/>',
        f'<line x1="{pad}" y1="{sy(0):.1f}" x2="{w-pad}" y2="{sy(0):.1f}" class="rm-axis"/>',
        f'<text x="{w-pad}" y="{sy(0)-6:.1f}" class="rm-lab" text-anchor="end">growth tilt →</text>',
        f'<text x="{sx(0)+6:.1f}" y="{pad+2:.1f}" class="rm-lab">inflation tilt ↑</text>',
    ]

    pts = [p for p in points if p is not None]
    if not pts:
        parts.append(
            f'<text x="{w/2:.0f}" y="{h/2:.0f}" class="rm-lab" text-anchor="middle">'
            "no history yet — run ipos-replay</text></svg>"
        )
        return "".join(parts)

    xy = [(sx(x), sy(y)) for _d, x, y in pts]
    if len(xy) >= 2:
        half = len(xy) // 2
        older = " ".join(f"{x:.1f},{y:.1f}" for x, y in xy[:half + 1])
        recent = " ".join(f"{x:.1f},{y:.1f}" for x, y in xy[half:])
        parts.append(f'<polyline fill="none" class="rm-trail-old" points="{older}"/>')
        parts.append(
            f'<polyline fill="none" class="rm-trail-new" points="{recent}" '
            'marker-end="url(#rm-arrow)"/>'
        )

    last_month = None
    for i, ((d, x, y), (px, py)) in enumerate(zip(pts, xy)):
        is_last = i == len(pts) - 1
        new_month = _mon(d) != last_month
        last_month = _mon(d)
        title = f"{d.isoformat()} — growth {x:+.2f}, inflation {y:+.2f}"
        if is_last:
            parts.append(
                f'<circle cx="{px:.1f}" cy="{py:.1f}" r="5.5" class="rm-now">'
                f"<title>{title} (current week)</title></circle>"
            )
        else:
            cls = "rm-dot-month" if new_month else "rm-dot"
            parts.append(
                f'<circle cx="{px:.1f}" cy="{py:.1f}" r="{3.2 if new_month else 2}" '
                f'class="{cls}"><title>{title}</title></circle>'
            )
            if new_month:
                parts.append(
                    f'<text x="{px+6:.1f}" y="{py-5:.1f}" class="rm-tick">{_mon(d)}</text>'
                )
    # start / now callouts
    parts.append(
        f'<text x="{xy[0][0]+7:.1f}" y="{xy[0][1]+13:.1f}" class="rm-tick">'
        f"start {_short_date(pts[0][0])}</text>"
    )
    if len(pts) > 1:
        parts.append(
            f'<text x="{xy[-1][0]-9:.1f}" y="{xy[-1][1]+17:.1f}" class="rm-nowlab" '
            f'text-anchor="end">now · {_short_date(pts[-1][0])}</text>'
        )
    parts.append("</svg>")
    return "".join(parts)


REGIME_RAMP = {
    "TRENDY": "var(--rg-trendy)",
    "MOMENTUM": "var(--rg-momentum)",
    "CHOPPY": "var(--rg-choppy)",
    "UNCERTAIN": "var(--rg-uncertain)",
}


def regime_ribbon_svg(history, *, cell: int = 16, h: int = 22) -> str:
    """One cell per week, coloured by regime label, oldest → newest, with a
    tick at every label change and month labels underneath.

    ``history`` = ordered ``(week_date, label, confidence, risk_scaler)``. The
    colours are an *ordinal* one-hue ramp keyed to how much risk each regime
    allows (TRENDY 1.00 → UNCERTAIN 0.40), not a categorical palette — the
    sequence is meaningful, so the encoding is too."""
    rows = [r for r in history if r is not None]
    if not rows:
        return '<span class="spark-na">no regime history yet — run ipos-replay</span>'
    gap = 2
    top = 0
    w = len(rows) * (cell + gap)
    parts = [
        f'<svg class="ribbon" width="{w}" height="{h + 16}" '
        f'viewBox="0 0 {w} {h + 16}" role="img">'
    ]
    last_month = None
    for i, (d, label, conf, scaler) in enumerate(rows):
        x = i * (cell + gap)
        fill = REGIME_RAMP.get(label, "var(--rg-uncertain)")
        conf_txt = f", conf {conf:.0f}" if conf is not None else ""
        parts.append(
            f'<rect x="{x}" y="{top}" width="{cell}" height="{h}" rx="2" fill="{fill}">'
            f"<title>{d.isoformat()} — {label or 'n/a'}{conf_txt}, risk ×{scaler}</title></rect>"
        )
        if _mon(d) != last_month:
            parts.append(
                f'<text x="{x}" y="{h + 12}" class="rm-tick">{_mon(d)}</text>'
            )
            last_month = _mon(d)
    for i in range(1, len(rows)):
        if rows[i][1] != rows[i - 1][1]:
            x = i * (cell + gap) - 1
            parts.append(
                f'<line x1="{x}" y1="{top - 2}" x2="{x}" y2="{top + h + 2}" '
                'class="ribbon-flip"/>'
            )
    parts.append("</svg>")
    return "".join(parts)


HORIZONS = (("1w", "1 week"), ("4w", "1 month"), ("12w", "1 quarter"), ("52w", "1 year"))
_HORIZON_FULL_SCALE = 45.0  # score points that fill the bar


def horizon_strip_svg(deltas: dict, *, label: str = "") -> str:
    """Four small diverging bars — 1w / 1m / 1q / 1y — reading the *shape* of an
    indicator's momentum at a glance. Up (improving score) is the strong pole,
    down the weak pole, height is magnitude clipped at ±45 score points.

    ``deltas`` maps horizon key ("1w", "4w", "12w", "52w") to a score delta or
    None. Exact numbers ride along in each bar's ``<title>``."""
    bw, gap, h = 10, 4, 26
    mid = h / 2
    w = len(HORIZONS) * (bw + gap)
    parts = [
        f'<svg class="hstrip" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img">',
        f'<line x1="0" y1="{mid}" x2="{w - gap}" y2="{mid}" class="hs-base"/>',
    ]
    for i, (key, human) in enumerate(HORIZONS):
        v = deltas.get(key)
        x = i * (bw + gap)
        if v is None:
            parts.append(
                f'<text x="{x + bw/2:.1f}" y="{mid + 3:.1f}" class="hs-na" '
                f'text-anchor="middle">·<title>{label} {human}: no data</title></text>'
            )
            continue
        mag = min(abs(float(v)), _HORIZON_FULL_SCALE) / _HORIZON_FULL_SCALE * (mid - 2)
        up = float(v) > 0
        cls = "hs-flat" if float(v) == 0 else ("hs-up" if up else "hs-down")
        y = mid - mag if up else mid
        parts.append(
            f'<rect x="{x}" y="{y:.1f}" width="{bw}" height="{max(mag, 1.5):.1f}" '
            f'rx="1.5" class="{cls}">'
            f"<title>{label} {human}: {float(v):+.1f} score points</title></rect>"
        )
    parts.append("</svg>")
    return "".join(parts)


def member_strip_svg(members, *, w: int = 300) -> str:
    """Where a module's member indicators sit on the shared 0-100 score scale,
    so an intra-module disagreement reads as physical distance rather than a
    bare spread number. ``members`` = ordered ``(series_id, score)`` ascending.

    This is the answer to "where are these mixed signals?" — the two ends of
    the span are the indicators that disagree."""
    rows = [m for m in members if m is not None]
    if len(rows) < 2:
        return ""
    h, axis = 46, 28
    def X(v): return 4 + v / 100.0 * (w - 8)
    lo, hi = rows[0], rows[-1]
    parts = [
        f'<svg class="mstrip" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img">',
        f'<line x1="{X(0):.1f}" y1="{axis}" x2="{X(100):.1f}" y2="{axis}" class="ms-axis"/>',
    ]
    for t in (0, 25, 50, 75, 100):
        parts.append(
            f'<line x1="{X(t):.1f}" y1="{axis - 4}" x2="{X(t):.1f}" y2="{axis + 4}" class="ms-tick"/>'
            f'<text x="{X(t):.1f}" y="{axis + 15}" class="ms-ticklab" text-anchor="middle">{t}</text>'
        )
    parts.append(
        f'<line x1="{X(lo[1]):.1f}" y1="{axis - 15}" x2="{X(hi[1]):.1f}" y2="{axis - 15}" '
        'class="ms-span"/>'
    )
    parts.append(
        f'<text x="{(X(lo[1]) + X(hi[1])) / 2:.1f}" y="{axis - 19}" class="ms-spanlab" '
        f'text-anchor="middle">{hi[1] - lo[1]:.0f} apart</text>'
    )
    for sid, score in rows:
        parts.append(
            f'<circle cx="{X(score):.1f}" cy="{axis}" r="5" fill="{score_color(score)}" '
            f'class="ms-dot"><title>{sid}: score {score:.1f}</title></circle>'
        )
    parts.append("</svg>")
    return "".join(parts)


MIN_PCTILE_HISTORY_WEEKS = 52


def pctile_strip_svg(
    pctile: float | None,
    *,
    history_weeks: int = 0,
    label: str = "",
    w: int = 96,
    h: int = 16,
) -> str:
    """Where an indicator's RAW LEVEL sits in its own rolling history: a 0-100
    track with the interquartile band shaded, a median tick, and a dot at the
    current percentile.

    Deliberately drawn in neutral ink rather than ``score_color``. This is a
    *level* percentile and is NOT direction-adjusted — for an inverted indicator
    (VIXCLS, HY_OAS) a high percentile means a LOW score — so coloring it on the
    risk ramp would assert a good/bad reading the number does not carry. Position
    alone answers the question it exists to answer ("is this reading historically
    extreme?").

    Returns an em dash when the percentile is absent, or when there is too little
    history to mean anything: the underlying rolling window uses min_periods=1,
    so it happily reports a percentile computed from a handful of observations."""
    if pctile is None:
        return '<span class="spark-na" title="no percentile: insufficient history">—</span>'
    if history_weeks and history_weeks < MIN_PCTILE_HISTORY_WEEKS:
        return (
            f'<span class="spark-na" title="{label}: only {history_weeks} weeks of '
            f'history, too few for a percentile">—</span>'
        )
    p = max(0.0, min(100.0, float(pctile)))
    pad = 3
    def X(v): return pad + v / 100.0 * (w - 2 * pad)
    mid = h / 2
    weeks = min(history_weeks, 156) if history_weeks else 156
    return (
        f'<svg class="pstrip" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img">'
        f'<rect x="{pad}" y="{mid - 3:.1f}" width="{w - 2 * pad}" height="6" rx="3" '
        f'class="ps-track"/>'
        f'<rect x="{X(25):.1f}" y="{mid - 3:.1f}" width="{X(75) - X(25):.1f}" height="6" '
        f'class="ps-iqr"/>'
        f'<line x1="{X(50):.1f}" y1="{mid - 5:.1f}" x2="{X(50):.1f}" y2="{mid + 5:.1f}" '
        f'class="ps-median"/>'
        f'<circle cx="{X(p):.1f}" cy="{mid:.1f}" r="3.5" class="ps-dot"/>'
        f"<title>{label}: level sits at the {p:.0f}th percentile of its last "
        f"{weeks} weeks (50 = median; not direction-adjusted)</title></svg>"
    )


def budget_bridge_svg(
    base: float | None, scaler: float | None, final: float | None, *, w: int = 300
) -> str:
    """Base risk budget -> regime scaler -> headline risk budget, as three bars on
    one shared 0-100 axis.

    The headline number is a product, not a sum (``base x scaler``), so the middle
    row is drawn as the span between the two totals — the points the regime
    removed — rather than as a stacked component. Everything sits on a single
    common scale because that is the only encoding that lets a reader compare the
    two totals accurately."""
    if base is None or final is None:
        return ""
    pad, row, h = 4, 22, 76
    def X(v): return pad + max(0.0, min(100.0, v)) / 100.0 * (w - 2 * pad)
    cut = base - final
    parts = [
        f'<svg class="bridge" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img">'
    ]
    for t in (0, 50, 100):
        parts.append(
            f'<line x1="{X(t):.1f}" y1="6" x2="{X(t):.1f}" y2="{h - 16}" class="br-grid"/>'
        )
    # row 1: base budget
    parts.append(
        f'<rect x="{pad}" y="10" width="{X(base) - pad:.1f}" height="12" rx="3" '
        f'fill="{score_color(base)}" class="br-bar">'
        f"<title>Base risk budget, before the regime scaler: {base:.1f}</title></rect>"
        f'<text x="{X(base) + 5:.1f}" y="20" class="br-lab">base {base:.0f}</text>'
    )
    # row 2: what the scaler removed (or added)
    if abs(cut) < 0.05:
        parts.append(
            f'<text x="{pad}" y="{10 + row + 10}" class="br-lab">'
            f'regime scaler x{scaler if scaler is not None else 1:.2f} — no change'
            f"</text>"
        )
    else:
        x0, x1 = sorted((X(final), X(base)))
        parts.append(
            f'<rect x="{x0:.1f}" y="{10 + row}" width="{max(x1 - x0, 1.5):.1f}" height="12" '
            f'rx="3" class="{"br-cut" if cut > 0 else "br-add"}">'
            f"<title>Regime scaler x{scaler if scaler is not None else 1:.2f} "
            f'{"removed" if cut > 0 else "added"} {abs(cut):.1f} points</title></rect>'
            f'<text x="{x1 + 5:.1f}" y="{10 + row + 10}" class="br-lab">'
            f'x{scaler if scaler is not None else 1:.2f} = {-cut:+.1f}</text>'
        )
    # row 3: headline
    parts.append(
        f'<rect x="{pad}" y="{10 + 2 * row}" width="{X(final) - pad:.1f}" height="12" rx="3" '
        f'fill="{score_color(final)}" class="br-bar">'
        f"<title>Risk budget after the regime scaler: {final:.1f}</title></rect>"
        f'<text x="{X(final) + 5:.1f}" y="{10 + 2 * row + 10}" class="br-lab">'
        f"<tspan class=\"br-strong\">budget {final:.0f}</tspan></text>"
    )
    for t in (0, 50, 100):
        parts.append(
            f'<text x="{X(t):.1f}" y="{h - 4}" class="br-tick" text-anchor="middle">{t}</text>'
        )
    parts.append("</svg>")
    return "".join(parts)


def contribution_bars_svg(contributions, *, w: int = 300, row: int = 17) -> str:
    """Which modules moved the risk budget, and by how much: one diverging bar per
    module on a shared zero axis, ordered by magnitude.

    ``contributions`` = ordered ``(module_id, contribution)`` in score points,
    summing to the week's change in the base budget.

    Deliberately NOT a cumulative waterfall. A waterfall's bars are positioned by
    a running total, which forces the ~0-100 opening balance and the ~±3-point
    contributions onto one axis and squashes the contributions into invisibility.
    The question here is "which module moved it, and which way" — magnitude plus
    polarity per category — so a zero-anchored diverging bar chart is the right
    form, and the totals are stated as text alongside it."""
    rows = [(m, c) for m, c in contributions if c is not None]
    if not rows:
        return ""
    span = max(abs(c) for _, c in rows) or 1.0
    labw, pad = 96, 4
    plot = w - labw - pad
    h = len(rows) * row + 16
    def X(v): return labw + plot / 2 + (v / span) * (plot / 2 - 6)
    zero = X(0)
    parts = [
        f'<svg class="cbars" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img">',
        f'<line x1="{zero:.1f}" y1="4" x2="{zero:.1f}" y2="{len(rows) * row + 2}" '
        f'class="cb-zero"/>',
    ]
    for i, (module, c) in enumerate(rows):
        y = i * row + 4
        x0, x1 = sorted((zero, X(c)))
        parts.append(
            f'<text x="{labw - 6}" y="{y + 9}" class="cb-lab" text-anchor="end">{module}</text>'
            f'<rect x="{x0:.1f}" y="{y}" width="{max(x1 - x0, 1.5):.1f}" height="11" rx="2.5" '
            f'class="{"cb-up" if c > 0 else "cb-down"}">'
            f"<title>{module}: {c:+.2f} score points of the budget change</title></rect>"
        )
    parts.append(
        f'<text x="{zero:.1f}" y="{h - 3}" class="cb-tick" text-anchor="middle">0</text>'
        f'<text x="{labw:.1f}" y="{h - 3}" class="cb-tick">{-span:+.1f}</text>'
        f'<text x="{w - pad}" y="{h - 3}" class="cb-tick" text-anchor="end">{span:+.1f}</text>'
    )
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
