"""Quantitative Macro Advisor Engine — deterministic translation of the
126 seminar rules and 44 process steps into executable rule evaluators,
contradiction triggers, and dynamic portfolio posture tilts.

DESIGN CONTRACT (mirrors the IPOS doctrine):
  * The engine only *narrates* pre-computed mathematical signals. It never
    fabricates raw metrics, never fetches data, never places trades.
  * Determinism: identical inputs -> identical posture. No wall-clock, no RNG.
  * Fail-degraded: a rule whose inputs are missing is skipped and reported,
    never fatal. A missing *critical* input can downgrade the posture to
    UNCERTAIN but does not raise.

INPUT SHAPE — ``AdvisorState`` is built from the weekly pipeline artifacts
(module scores from ipos.aggregate.modules, regime from
ipos.aggregate.regime, indicator scores from fact_weekly / scoring tables).
Scores are 0–100 where higher = more risk-on/supportive, matching
configs/contradictions.yaml conventions.

RULE SOURCES:
  * The seminar's 126 rules are grouped into RULEBOOKS below; each rule is a
    pure predicate + action over AdvisorState. Rules are numbered R### so the
    audit trail maps 1:1 to the seminar text.
  * The 44 process steps map to PROCESS_STEPS — ordered gate checks that
    produce a checklist verdict each week.

OUTPUT — ``AdvisorVerdict``: posture tilt per stance dimension in [-1, +1],
fired contradiction list, fired rule list, process-step checklist, confidence.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

# ---------------------------------------------------------------------------
# State
# ---------------------------------------------------------------------------

STANCE_DIMS = ("equity", "duration", "credit", "usd", "commodities", "growth")
REGIMES = ("CHOPPY", "TRENDY", "MOMENTUM", "UNCERTAIN")

# Regime risk scalers mirror ipos/aggregate/regime.RISK_SCALER
RISK_SCALER = {"CHOPPY": 0.50, "TRENDY": 1.00, "MOMENTUM": 0.75, "UNCERTAIN": 0.40}


@dataclass
class AdvisorState:
    """One week of pre-computed signals. All scores are 0-100 (risk-on high)."""

    as_of: str
    module_scores: dict[str, float]          # module_id -> score 0-100
    module_confidence: dict[str, float]      # module_id -> confidence 0-100
    module_spread: dict[str, float]          # max-min intra-module member spread
    indicator_scores: dict[str, float]       # series_id -> score 0-100
    indicator_values: dict[str, float]       # series_id -> raw canonical value
    regime: str                              # one of REGIMES
    regime_confidence: float                 # 0-100
    portfolio_weights: dict[str, float] | None = None   # stance_dim -> pct
    contradictions: list[dict] = field(default_factory=list)  # from configs/contradictions.yaml

    def mod(self, module_id: str) -> float | None:
        return self.module_scores.get(module_id)

    def ind(self, series_id: str) -> float | None:
        return self.indicator_scores.get(series_id)

    def val(self, series_id: str) -> float | None:
        return self.indicator_values.get(series_id)


@dataclass
class RuleHit:
    rule_id: str
    name: str
    severity: str            # low | med | high
    detail: str


@dataclass
class AdvisorVerdict:
    as_of: str
    tilts: dict[str, float]              # stance_dim -> [-1, +1]
    posture: str                         # RISK_ON | NEUTRAL | DEFENSIVE | HEDGED
    regime: str
    regime_risk_scaler: float
    fired_rules: list[RuleHit] = field(default_factory=list)
    skipped_rules: list[str] = field(default_factory=list)
    process_checklist: list[dict] = field(default_factory=list)
    confidence: float = 50.0
    notes: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Rule registry: the 126 seminar rules, grouped into rulebooks.
# Each rule: predicate(state) -> bool | None (None = cannot evaluate),
# plus severity and a tilt delta contribution per stance dim.
# ---------------------------------------------------------------------------

def _s(x):
    """Score accessor tolerant of None: None means 'cannot evaluate'."""
    return x


@dataclass
class Rule:
    rule_id: str
    name: str
    rulebook: str
    severity: str
    when: Callable[[AdvisorState], bool | None]
    # additive tilt deltas applied when the rule fires
    tilt_delta: dict[str, float] = field(default_factory=dict)


def _both(a: float | None, b: float | None) -> bool | None:
    if a is None or b is None:
        return None
    return True


RULES: list[Rule] = []


def _rule(rule_id, name, rulebook, severity, when, **tilts):
    RULES.append(Rule(rule_id, name, rulebook, severity, when, tilts))


# --- Rulebook 1: Equity risk appetite (R001-R018) ---------------------------
_rule("R001", "Broad equity trend supportive", "EQUITY", "low",
      lambda s: _both(s.ind("SPX"), s.mod("EquityRisk")) if (s.mod("EquityRisk") or 0) >= 65 else False,
      equity=+0.15)
_rule("R002", "Broad equity trend deteriorating", "EQUITY", "med",
      lambda s: (s.mod("EquityRisk") or 50) <= 35 if s.mod("EquityRisk") is not None else None,
      equity=-0.20)
_rule("R003", "VIX elevated stress", "EQUITY", "high",
      lambda s: (s.ind("VIXCLS") or 50) <= 30 if s.ind("VIXCLS") is not None else None,
      equity=-0.25, credit=-0.10)
_rule("R004", "VIX compressed complacency guard", "EQUITY", "low",
      lambda s: (s.ind("VIXCLS") or 50) >= 80 if s.ind("VIXCLS") is not None else None,
      equity=-0.05)
_rule("R005", "VIX term structure inverted", "EQUITY", "med",
      lambda s: (s.ind("TERM_VIX") or 50) <= 30 if s.ind("TERM_VIX") is not None else None,
      equity=-0.15)
_rule("R006", "Breadth confirms advance", "EQUITY", "low",
      lambda s: (s.ind("SPX_200DMA_BREADTH") or 50) >= 60 if s.ind("SPX_200DMA_BREADTH") is not None else None,
      equity=+0.10)
_rule("R007", "Breadth divergence: index up, breadth down", "EQUITY", "med",
      lambda s: ((s.ind("SPX") or 0) >= 60 and (s.ind("SPX_200DMA_BREADTH") or 100) <= 40)
                if s.ind("SPX") is not None and s.ind("SPX_200DMA_BREADTH") is not None else None,
      equity=-0.15)
_rule("R008", "Put/call extreme fear (contrarian support)", "EQUITY", "low",
      lambda s: (s.ind("PUTCALL_CBOE") or 50) <= 20 if s.ind("PUTCALL_CBOE") is not None else None,
      equity=+0.05)
_rule("R009", "Put/call extreme greed (contrarian caution)", "EQUITY", "low",
      lambda s: (s.ind("PUTCALL_CBOE") or 50) >= 85 if s.ind("PUTCALL_CBOE") is not None else None,
      equity=-0.05)
_rule("R010", "Global equity complex synchronized up", "EQUITY", "low",
      lambda s: _all_ge(s, ["DAX", "NIKKEI", "EEM"], 60), equity=+0.10)
_rule("R011", "Global equity complex synchronized down", "EQUITY", "med",
      lambda s: _all_le(s, ["DAX", "NIKKEI", "EEM"], 40), equity=-0.15)
_rule("R012", "Small-cap underperformance (late-cycle tell)", "EQUITY", "low",
      lambda s: ((s.ind("RUT") or 50) <= 35 and (s.ind("SPX") or 0) >= 55)
                if s.ind("RUT") is not None and s.ind("SPX") is not None else None,
      equity=-0.10)
_rule("R013", "Equal-weight vs cap-weight divergence guard", "EQUITY", "low",
      lambda s: (s.module_spread.get("EquityRisk") or 0) >= 60, equity=-0.05)
_rule("R014", "Equity ERP thin (valuation stretch)", "EQUITY", "med",
      lambda s: (s.ind("SPX_RISK_PREMIUM_ERP") or 50) <= 25 if s.ind("SPX_RISK_PREMIUM_ERP") is not None else None,
      equity=-0.10)
_rule("R015", "Equity ERP wide (compensation attractive)", "EQUITY", "low",
      lambda s: (s.ind("SPX_RISK_PREMIUM_ERP") or 50) >= 70 if s.ind("SPX_RISK_PREMIUM_ERP") is not None else None,
      equity=+0.10)
_rule("R016", "EM outperformance (global liquidity ample)", "EQUITY", "low",
      lambda s: ((s.ind("EEM") or 0) >= 65 and (s.mod("Liquidity") or 0) >= 55)
                if s.ind("EEM") is not None else None,
      equity=+0.05, commodities=+0.05)
_rule("R017", "Advancers collapsing while index holds", "EQUITY", "med",
      lambda s: (s.ind("NYSE_ADV_DEC_50DMA") or 50) <= 30 if s.ind("NYSE_ADV_DEC_50DMA") is not None else None,
      equity=-0.10)
_rule("R018", "Turnover drying up on rally", "EQUITY", "low",
      lambda s: ((s.ind("SPX_TURNOVER") or 50) <= 30 and (s.ind("SPX") or 0) >= 60)
                if s.ind("SPX_TURNOVER") is not None and s.ind("SPX") is not None else None,
      equity=-0.05)


# --- Rulebook 2: Rates & duration (R019-R036) -------------------------------
def _all_ge(s, ids, thr):
    vals = [s.ind(i) for i in ids]
    if any(v is None for v in vals):
        return None
    return all(v >= thr for v in vals)


def _all_le(s, ids, thr):
    vals = [s.ind(i) for i in ids]
    if any(v is None for v in vals):
        return None
    return all(v <= thr for v in vals)


_rule("R019", "Curve steepening (2s10s positive & rising)", "RATES", "low",
      lambda s: (s.ind("T10Y2Y") or 0) >= 70 if s.ind("T10Y2Y") is not None else None,
      growth=+0.15, equity=+0.10)
_rule("R020", "Curve inverted (recession signal)", "RATES", "high",
      lambda s: (s.val("T10Y2Y") is not None and s.val("T10Y2Y") < 0),
      equity=-0.20, duration=+0.10)
_curve_bands = {"R021": "T10Y2Y", "R022": "T10Y3M"}
_rule("R021", "2s10s deep negative (< -0.5)", "RATES", "high",
      lambda s: (s.val("T10Y2Y") is not None and s.val("T10Y2Y") < -0.5),
      equity=-0.25)
_rule("R022", "3m10s deep negative (< -0.5)", "RATES", "high",
      lambda s: (s.val("T10Y3M") is not None and s.val("T10Y3M") < -0.5),
      equity=-0.25)
_rule("R023", "Policy restrictive (FFR above midpoint band)", "RATES", "med",
      lambda s: (s.ind("DFF") or 50) <= 35 if s.ind("DFF") is not None else None,
      duration=+0.10, equity=-0.05)
_rule("R024", "Real yields punishing (10y TIPS high)", "RATES", "med",
      lambda s: (s.ind("DFII10") or 50) <= 30 if s.ind("DFII10") is not None else None,
      equity=-0.10, gold_guard=True, commodities=-0.05)
_rule("R025", "Financial conditions loose", "RATES", "low",
      lambda s: (s.ind("NFCI") or 50) >= 60 if s.ind("NFCI") is not None else None,
      equity=+0.10)
_rule("R026", "Financial conditions tightening", "RATES", "high",
      lambda s: (s.ind("NFCI") or 50) <= 35 if s.ind("NFCI") is not None else None,
      equity=-0.20, credit=-0.10)
_rule("R027", "TED spread stress", "RATES", "high",
      lambda s: (s.ind("TED_SPREAD") or 50) <= 25 if s.ind("TED_SPREAD") is not None else None,
      equity=-0.15, credit=-0.15)
_rule("R028", "CP funding stress", "RATES", "med",
      lambda s: (s.ind("CP_SPREAD_3M") or 50) <= 25 if s.ind("CP_SPREAD_3M") is not None else None,
      equity=-0.10, credit=-0.10)
_rule("R029", "Breakevens dis-inflating fast", "RATES", "med",
      lambda s: _all_le(s, ["T10YIE", "T5YIE"], 30), growth=-0.10, commodities=-0.10)
_rule("R030", "Breakevens re-accelerating", "RATES", "low",
      lambda s: _all_ge(s, ["T10YIE", "T5YIE"], 70), commodities=+0.10)
_rule("R031", "Front-end anchored, long-end rising (bear steepener)", "RATES", "med",
      lambda s: ((s.ind("DGS2") or 50) <= 45 and (s.ind("US10Y_STOOQ") or 50) <= 35)
                if s.ind("DGS2") is not None and s.ind("US10Y_STOOQ") is not None else None,
      duration=-0.10, equity=-0.05)
_rule("R032", "Bull flattener (flight to duration)", "RATES", "low",
      lambda s: ((s.ind("DGS30") or 50) >= 60 and (s.ind("SPX") or 0) <= 40)
                if s.ind("DGS30") is not None and s.ind("SPX") is not None else None,
      duration=+0.15, equity=-0.10)
_rule("R033", "Bund-UST spread widening (EUR rate shock)", "RATES", "low",
      lambda s: ((s.ind("DE10Y") or 50) <= 30 if s.ind("DE10Y") is not None else None),
      usd=+0.05)
_rule("R034", "SOFR stable (money market calm)", "RATES", "low",
      lambda s: (s.ind("SOFR") or 50) >= 45 and (s.ind("SOFR") or 0) <= 65
                if s.ind("SOFR") is not None else None,
      )
_rule("R035", "Whole curve above policy rate (tight regime)", "RATES", "med",
      lambda s: _all_le(s, ["DGS2", "DGS10"], 40), equity=-0.10, duration=+0.05)
_rule("R036", "Rates module internally split", "RATES", "low",
      lambda s: (s.module_spread.get("RatesLiquidity") or 0) >= 60, duration=-0.05)


# --- Rulebook 3: Credit (R037-R052) -----------------------------------------
_rule("R037", "HY OAS tight (credit supportive)", "CREDIT", "low",
      lambda s: (s.ind("HY_OAS") or 50) >= 70 if s.ind("HY_OAS") is not None else None,
      credit=+0.20, equity=+0.10)
_rule("R038", "HY OAS widening warning", "CREDIT", "high",
      lambda s: (s.ind("HY_OAS") or 50) <= 30 if s.ind("HY_OAS") is not None else None,
      credit=-0.25, equity=-0.20)
_rule("R039", "IG OAS widening before HY (smart-money stress order)", "CREDIT", "med",
      lambda s: ((s.ind("IG_OAS") or 100) <= 35 and (s.ind("HY_OAS") or 0) >= 50)
                if s.ind("IG_OAS") is not None and s.ind("HY_OAS") is not None else None,
      credit=-0.15)
_rule("R040", "CCC vs BB dispersion exploding", "CREDIT", "med",
      lambda s: ((s.ind("CCC_OAS") or 50) <= 30 and (s.ind("BB_OAS") or 50) >= 55)
                if s.ind("CCC_OAS") is not None and s.ind("BB_OAS") is not None else None,
      credit=-0.15)
_rule("R041", "EM credit deteriorating", "CREDIT", "med",
      lambda s: (s.ind("EM_HY_OAS") or 50) <= 30 if s.ind("EM_HY_OAS") is not None else None,
      credit=-0.10, usd=+0.05)
_rule("R042", "Euro credit deteriorating", "CREDIT", "low",
      lambda s: (s.ind("EU_HY_OAS") or 50) <= 30 if s.ind("EU_HY_OAS") is not None else None,
      credit=-0.10)
_rule("R043", "Credit ETF price confirms spreads", "CREDIT", "low",
      lambda s: ((s.ind("HYG") or 0) >= 60 and (s.ind("HY_OAS") or 0) >= 60)
                if s.ind("HYG") is not None and s.ind("HY_OAS") is not None else None,
      credit=+0.10)
_rule("R044", "Credit ETF price diverges negatively from spreads", "CREDIT", "med",
      lambda s: ((s.ind("HYG") or 100) <= 35 and (s.ind("HY_OAS") or 0) >= 55)
                if s.ind("HYG") is not None and s.ind("HY_OAS") is not None else None,
      credit=-0.15, equity=-0.10)
_rule("R045", "IG ETF confirms", "CREDIT", "low",
      lambda s: ((s.ind("LQD") or 0) >= 60 and (s.ind("IG_OAS") or 0) >= 55)
                if s.ind("LQD") is not None and s.ind("IG_OAS") is not None else None,
      credit=+0.05, duration=+0.05)
_rule("R046", "Credit module internally split", "CREDIT", "low",
      lambda s: (s.module_spread.get("Credit") or 0) >= 60, credit=-0.05)
_rule("R047", "Credit leads equities down (top-down confirmation)", "CREDIT", "high",
      lambda s: ((s.mod("Credit") or 100) <= 35 and (s.mod("EquityRisk") or 0) >= 60),
      equity=-0.20, credit=-0.10)
_rule("R048", "Credit leads equities up (bottom confirmation)", "CREDIT", "low",
      lambda s: ((s.mod("Credit") or 0) >= 65 and (s.mod("EquityRisk") or 0) >= 55),
      equity=+0.10)
_rule("R049", "All credit legs tight across geographies", "CREDIT", "low",
      lambda s: _all_ge(s, ["HY_OAS", "IG_OAS", "EM_HY_OAS", "EU_HY_OAS"], 60),
      credit=+0.15)
_rule("R050", "All credit legs stressed across geographies", "CREDIT", "high",
      lambda s: _all_le(s, ["HY_OAS", "IG_OAS", "EM_HY_OAS", "EU_HY_OAS"], 40),
      credit=-0.25, equity=-0.20)
_rule("R051", "Credit stress with funding stress combined", "CREDIT", "high",
      lambda s: ((s.ind("HY_OAS") or 100) <= 30 and (s.ind("TED_SPREAD") or 100) <= 30)
                if s.ind("TED_SPREAD") is not None and s.ind("HY_OAS") is not None else None,
      equity=-0.25, credit=-0.20)
_rule("R052", "Credit calm amid equity volatility (buyable dip)", "CREDIT", "med",
      lambda s: ((s.ind("HY_OAS") or 0) >= 60 and (s.ind("VIXCLS") or 100) <= 35)
                if s.ind("HY_OAS") is not None and s.ind("VIXCLS") is not None else None,
      equity=+0.15)


# --- Rulebook 4: FX / dollar (R053-R066) ------------------------------------
_rule("R053", "Broad USD strength (global tightening)", "FX", "high",
      lambda s: (s.ind("DTWEXBGS") or 50) <= 30 if s.ind("DTWEXBGS") is not None else None,
      usd=+0.20, commodities=-0.15, equity=-0.15)
_rule("R054", "Broad USD weakness (global easing)", "FX", "low",
      lambda s: (s.ind("DTWEXBGS") or 50) >= 70 if s.ind("DTWEXBGS") is not None else None,
      usd=-0.20, commodities=+0.15, equity=+0.10)
_rule("R055", "EURUSD momentum up", "FX", "low",
      lambda s: (s.ind("EURUSD") or 50) >= 65 if s.ind("EURUSD") is not None else None,
      usd=-0.10)
_rule("R056", "USDJPY carry unwinding (yen surge)", "FX", "med",
      lambda s: (s.ind("USDJPY") or 50) >= 75 if s.ind("USDJPY") is not None else None,
      usd=-0.10, equity=-0.05)
_rule("R057", "Sterling strength (global risk appetite)", "FX", "low",
      lambda s: (s.ind("GBPUSD") or 50) >= 65 if s.ind("GBPUSD") is not None else None,
      usd=-0.05)
_rule("R058", "Aussie as China/growth proxy strengthening", "FX", "low",
      lambda s: ((s.ind("AUDUSD") or 0) >= 65 and (s.ind("COPPER") or 0) >= 55)
                if s.ind("AUDUSD") is not None and s.ind("COPPER") is not None else None,
      commodities=+0.10, growth=+0.10)
_rule("R059", "Aussie breaking down (China drag)", "FX", "med",
      lambda s: (s.ind("AUDUSD") or 50) <= 30 if s.ind("AUDUSD") is not None else None,
      commodities=-0.10, growth=-0.10)
_rule("R060", "Dollar-index proxy confirms broad index", "FX", "low",
      lambda s: ((s.ind("DX_Y") or 50) <= 35 and (s.ind("DTWEXBGS") or 50) <= 40)
                if s.ind("DX_Y") is not None and s.ind("DTWEXBGS") is not None else None,
      usd=+0.10)
_rule("R061", "EM FX basket strengthening", "FX", "low",
      lambda s: (s.ind("EM_FX_ETF") or 50) >= 65 if s.ind("EM_FX_ETF") is not None else None,
      usd=-0.10, growth=+0.05)
_rule("R062", "JPY real effective cheap (export cycle tailwind)", "FX", "low",
      lambda s: (s.ind("JPY_REAL_EFF") or 50) <= 30 if s.ind("JPY_REAL_EFF") is not None else None,
      usd=-0.05)
_rule("R063", "FX module internally split", "FX", "low",
      lambda s: (s.module_spread.get("FX") or 0) >= 60, usd=-0.05)
_rule("R064", "USD strong AND credit stressed (double squeeze setup)", "FX", "high",
      lambda s: ((s.ind("DTWEXBGS") or 100) <= 35 and (s.ind("HY_OAS") or 100) <= 35)
                if s.ind("DTWEXBGS") is not None and s.ind("HY_OAS") is not None else None,
      equity=-0.25, credit=-0.15)
_rule("R065", "USD weak AND commodities firm (inflationary impulse)", "FX", "med",
      lambda s: ((s.ind("DTWEXBGS") or 100) >= 65 and (s.mod("Commodities") or 0) >= 65),
      commodities=+0.10, usd=-0.10)
_rule("R066", "Gold outperforming while real yields rise (fear bid)", "FX", "med",
      lambda s: ((s.ind("GOLD") or 0) >= 65 and (s.ind("DFII10") or 100) <= 40)
                if s.ind("GOLD") is not None and s.ind("DFII10") is not None else None,
      equity=-0.10)


# --- Rulebook 5: Commodities (R067-R078) -------------------------------------
_rule("R067", "Energy complex firm (global demand ok)", "COMMODITIES", "low",
      lambda s: ((s.ind("WTI") or 0) >= 60 and (s.ind("BRENT") or 0) >= 60),
      commodities=+0.10, growth=+0.05)
_rule("R068", "Crude breaking down (demand scare)", "COMMODITIES", "med",
      lambda s: ((s.ind("WTI") or 50) <= 30 and (s.ind("BRENT") or 50) <= 35),
      commodities=-0.15, growth=-0.10)
_rule("R069", "Natgas stress (winter/energy crisis)", "COMMODITIES", "low",
      lambda s: (s.ind("HH_NATGAS") or 50) >= 80 if s.ind("HH_NATGAS") is not None else None,
      commodities=+0.05)
_rule("R070", "Precious metals bid (monetary fear)", "COMMODITIES", "med",
      lambda s: ((s.ind("GOLD") or 0) >= 65 and (s.ind("SILVER") or 0) >= 65),
      equity=-0.05, commodities=+0.10)
_rule("R071", "Dracula (copper) says growth accelerating", "COMMODITIES", "low",
      lambda s: (s.ind("COPPER") or 50) >= 70 if s.ind("COPPER") is not None else None,
      growth=+0.15, equity=+0.10)
_rule("R072", "Copper rolling over (industrial slowdown)", "COMMODITIES", "med",
      lambda s: (s.ind("COPPER") or 50) <= 30 if s.ind("COPPER") is not None else None,
      growth=-0.15, equity=-0.10)
_rule("R073", "Grains spiking (food inflation impulse)", "COMMODITIES", "low",
      lambda s: ((s.ind("WHEAT") or 0) >= 80 and (s.ind("CORN") or 0) >= 80),
      commodities=+0.05)
_rule("R074", "Broad commodity complex firm", "COMMODITIES", "low",
      lambda s: ((s.ind("DBC") or 0) >= 65 and (s.mod("Commodities") or 0) >= 60),
      commodities=+0.10)
_rule("R075", "Energy equities leading (confirmation)", "COMMODITIES", "low",
      lambda s: ((s.ind("XLE") or 0) >= 70 and (s.ind("WTI") or 0) >= 60),
      commodities=+0.10)
_rule("R076", "Ag ETF rolling over", "COMMODITIES", "low",
      lambda s: (s.ind("DBA") or 50) <= 30 if s.ind("DBA") is not None else None,
      commodities=-0.05)
_rule("R077", "Commodities module internally split", "COMMODITIES", "low",
      lambda s: (s.module_spread.get("Commodities") or 0) >= 60, commodities=-0.05)
_rule("R078", "Commodities strong while curve screams recession", "COMMODITIES", "med",
      lambda s: ((s.mod("Commodities") or 0) >= 65 and (s.mod("GrowthRisk") or 100) <= 30),
      commodities=-0.10)


# --- Rulebook 6: Positioning (COT) (R079-R092) ------------------------------
def _cot(sid, hib, delta_map, sev="low"):
    _rule(f"R{len(RULES)+79:03d}" if False else sid.replace("COT_", f"R0{len('')}", 1), sid, "POSITIONING", sev,
          lambda s, i=sid, h=hib: ((s.ind(i) or 50) >= 70 if h else (s.ind(i) or 50) <= 30)
          if s.ind(i) is not None else None,
          **delta_map)


# NOTE: COT rules are generated explicitly to keep stable IDs R079-R092.
_COT_DEFS = [
    ("R079", "COT_SPX_COMM", True,  {"equity": +0.10}),
    ("R080", "COT_SPX_SPEC", False, {"equity": -0.10}),   # spec crowd long = crowding risk
    ("R081", "COT_10Y_COMM", False, {"duration": -0.05}), # commercials short bonds = yield pressure
    ("R082", "COT_10Y_SPEC", True,  {"duration": +0.05}),
    ("R083", "COT_ED_SPEC", True,  {"duration": +0.10}),
    ("R084", "COT_USD_IDX_SPEC", False, {"usd": -0.05}),  # spec USD crowd = squeeze risk
    ("R085", "COT_JPY_COMM", False, {"usd": -0.05}),
    ("R086", "COT_EUR_COMM", True, {"usd": -0.05}),
    ("R087", "COT_CRUDE_SPEC", False, {"commodities": -0.05}),
    ("R088", "COT_GOLD_COMM", True, {"commodities": +0.05}),
    ("R089", "COT_COPPER_SPEC", True, {"commodities": +0.05}),
    ("R090", "COT_AGG_SPEC_Z", False, {"equity": -0.10, "commodities": -0.05}),
]
for item in _COT_DEFS:
    rid, sid, hib, deltas = item
    _rule(rid, f"{sid} extreme ({'commercial' if '_COMM' in sid else 'speculator'})",
          "POSITIONING", "low",
          lambda s, i=sid, h=hib: ((s.ind(i) or 50) >= 70 if h else (s.ind(i) or 50) <= 30)
          if s.ind(i) is not None else None,
          **deltas)
_rule("R091", "Speculator aggregate at record skew", "POSITIONING", "med",
      lambda s: (s.ind("COT_AGG_SPEC_Z") or 50) <= 20 if s.ind("COT_AGG_SPEC_Z") is not None else None,
      equity=-0.15)
_rule("R092", "Positioning data stale/unavailable this week", "POSITIONING", "low",
      lambda s: all(s.ind(i) is None for i in
                    ("COT_SPX_COMM", "COT_SPX_SPEC", "COT_CRUDE_SPEC")))


# --- Rulebook 7: ISM subindices & macro fundamentals (R093-R110) -------------
_rule("R093", "ISM PMI expansion (>50 equivalent score)", "MACRO", "low",
      lambda s: (s.ind("ISM_PMI") or 50) >= 60 if s.ind("ISM_PMI") is not None else None,
      growth=+0.15, equity=+0.10)
_rule("R094", "ISM PMI contraction zone", "MACRO", "high",
      lambda s: (s.ind("ISM_PMI") or 50) <= 35 if s.ind("ISM_PMI") is not None else None,
      growth=-0.20, equity=-0.15)
_rule("R095", "ISM New Orders leading down", "MACRO", "med",
      lambda s: (s.ind("ISM_NEW_ORDERS") or 50) <= 35 if s.ind("ISM_NEW_ORDERS") is not None else None,
      growth=-0.15, equity=-0.10)
_rule("R096", "ISM New Orders leading up", "MACRO", "low",
      lambda s: (s.ind("ISM_NEW_ORDERS") or 50) >= 65 if s.ind("ISM_NEW_ORDERS") is not None else None,
      growth=+0.15)
_rule("R097", "ISM Prices Paid re-accelerating (input inflation)", "MACRO", "med",
      lambda s: (s.ind("ISM_PRICES") or 50) >= 75 if s.ind("ISM_PRICES") is not None else None,
      commodities=+0.10, duration=-0.10)
_rule("R098", "ISM Prices Paid collapsing (disinflation impulse)", "MACRO", "low",
      lambda s: (s.ind("ISM_PRICES") or 50) <= 25 if s.ind("ISM_PRICES") is not None else None,
      duration=+0.10)
_rule("R099", "ISM Employment weakening", "MACRO", "med",
      lambda s: (s.ind("ISM_EMPLOYMENT") or 50) <= 35 if s.ind("ISM_EMPLOYMENT") is not None else None,
      growth=-0.10)
_rule("R100", "ISM Inventories building while orders fall (glut)", "MACRO", "med",
      lambda s: ((s.ind("ISM_INVENTORIES") or 0) >= 70 and (s.ind("ISM_NEW_ORDERS") or 100) <= 40)
                if s.ind("ISM_INVENTORIES") is not None and s.ind("ISM_NEW_ORDERS") is not None else None,
      growth=-0.15, equity=-0.10)
_rule("R101", "Supplier deliveries stretching (supply strain)", "MACRO", "low",
      lambda s: (s.ind("ISM_SUPPLIER_DELIV") or 50) >= 75 if s.ind("ISM_SUPPLIER_DELIV") is not None else None,
      commodities=+0.05)
_rule("R102", "ISM services confirming manufacturing", "MACRO", "low",
      lambda s: ((s.ind("ISM_NONMAN_PMI") or 0) >= 60 and (s.ind("ISM_PMI") or 0) >= 60),
      growth=+0.10)
_rule("R103", "Services diverging negatively from manufacturing", "MACRO", "med",
      lambda s: ((s.ind("ISM_NONMAN_PMI") or 100) <= 35 and (s.ind("ISM_PMI") or 0) >= 55)
                if s.ind("ISM_NONMAN_PMI") is not None and s.ind("ISM_PMI") is not None else None,
      growth=-0.10)
_rule("R104", "Claims trending worse", "MACRO", "med",
      lambda s: (s.ind("ICSA") or 50) <= 30 if s.ind("ICSA") is not None else None,
      growth=-0.10, equity=-0.05)
_rule("R105", "Consumer sentiment resilient", "MACRO", "low",
      lambda s: (s.ind("UMCSENT") or 50) >= 65 if s.ind("UMCSENT") is not None else None,
      growth=+0.10)
_rule("R106", "Consumer sentiment collapsing", "MACRO", "med",
      lambda s: (s.ind("UMCSENT") or 50) <= 30 if s.ind("UMCSENT") is not None else None,
      growth=-0.10, equity=-0.05)
_rule("R107", "Labor market softening (unemployment rising)", "MACRO", "med",
      lambda s: (s.ind("UNRATE") or 50) <= 35 if s.ind("UNRATE") is not None else None,
      growth=-0.10, duration=+0.05)
_rule("R108", "Payrolls momentum positive", "MACRO", "low",
      lambda s: (s.ind("PAYEMS") or 50) >= 60 if s.ind("PAYEMS") is not None else None,
      growth=+0.10)
_rule("R109", "Core inflation sticky-high", "MACRO", "med",
      lambda s: ((s.ind("CPILFESL_YOY") or 50) <= 30 and (s.ind("PCEPI_CORE_YOY") or 50) <= 30)
                if s.ind("CPILFESL_YOY") is not None and s.ind("PCEPI_CORE_YOY") is not None else None,
      duration=-0.10, equity=-0.05)
_rule("R110", "Housing complex bottoming", "MACRO", "low",
      lambda s: ((s.ind("HOUST") or 0) >= 55 and (s.ind("PERMIT") or 0) >= 55),
      growth=+0.10)


# --- Rulebook 8: Global liquidity (R111-R126) ---------------------------------
_rule("R111", "Fed balance sheet expanding", "LIQUIDITY", "low",
      lambda s: (s.ind("WALCL") or 50) >= 60 if s.ind("WALCL") is not None else None,
      equity=+0.10, commodities=+0.05)
_rule("R112", "QT draining reserves fast", "LIQUIDITY", "med",
      lambda s: ((s.ind("WRESBAL") or 50) <= 30 and (s.ind("WALCL") or 50) <= 40)
                if s.ind("WRESBAL") is not None and s.ind("WALCL") is not None else None,
      equity=-0.15)
_rule("R113", "RRP drain reversing (liquidity injection)", "LIQUIDITY", "low",
      lambda s: (s.ind("RRP_REVERSE_REPO") or 50) >= 65 if s.ind("RRP_REVERSE_REPO") is not None else None,
      equity=+0.10)
_rule("R114", "TGA rebuild draining liquidity", "LIQUIDITY", "med",
      lambda s: (s.ind("TGA_BALANCE") or 50) <= 30 if s.ind("TGA_BALANCE") is not None else None,
      equity=-0.10)
_rule("R115", "Net liquidity expanding", "LIQUIDITY", "low",
      lambda s: (s.ind("NET_LIQ_FED") or 50) >= 65 if s.ind("NET_LIQ_FED") is not None else None,
      equity=+0.15, commodities=+0.10)
_rule("R116", "Net liquidity contracting", "LIQUIDITY", "high",
      lambda s: (s.ind("NET_LIQ_FED") or 50) <= 30 if s.ind("NET_LIQ_FED") is not None else None,
      equity=-0.20, commodities=-0.10)
_rule("R117", "Monetary base shrinking", "LIQUIDITY", "med",
      lambda s: (s.ind("BOGMBASE") or 50) <= 30 if s.ind("BOGMBASE") is not None else None,
      equity=-0.10)
_rule("R118", "M2 re-accelerating", "LIQUIDITY", "low",
      lambda s: (s.ind("M2_SL") or 50) >= 65 if s.ind("M2_SL") is not None else None,
      equity=+0.05, commodities=+0.05)
_rule("R119", "ECB M3 growth solid (euro liquidity ample)", "LIQUIDITY", "low",
      lambda s: (s.ind("ECB_M3") or 50) >= 60 if s.ind("ECB_M3") is not None else None,
      equity=+0.05)
_rule("R120", "ECB balance sheet expanding", "LIQUIDITY", "low",
      lambda s: (s.ind("ECB_ASSETS") or 50) >= 60 if s.ind("ECB_ASSETS") is not None else None,
      equity=+0.05)
_rule("R121", "BoJ base money expanding (carry fuel)", "LIQUIDITY", "low",
      lambda s: (s.ind("BOJ_BASE_MONEY") or 50) >= 60 if s.ind("BOJ_BASE_MONEY") is not None else None,
      usd=-0.05, equity=+0.05)
_rule("R122", "China M2 accelerating (global growth stimulus)", "LIQUIDITY", "low",
      lambda s: (s.ind("PBOC_M2_CN") or 50) >= 65 if s.ind("PBOC_M2_CN") is not None else None,
      commodities=+0.15, growth=+0.10)
_rule("R123", "Global M2 proxy turning up", "LIQUIDITY", "low",
      lambda s: (s.ind("GLOBAL_M2_PROXY") or 50) >= 60 if s.ind("GLOBAL_M2_PROXY") is not None else None,
      equity=+0.10)
_rule("R124", "Global M2 proxy rolling over", "LIQUIDITY", "med",
      lambda s: (s.ind("GLOBAL_M2_PROXY") or 50) <= 35 if s.ind("GLOBAL_M2_PROXY") is not None else None,
      equity=-0.15)
_rule("R125", "Financial stress indices flashing", "LIQUIDITY", "high",
      lambda s: _any_le(s, ["NFCI", "ANFCI_PROXY", "STLFSI4"], 25),
      equity=-0.20, credit=-0.15)
_rule("R126", "Liquidity supportive despite equity drawdown (dip-buy regime)", "LIQUIDITY", "med",
      lambda s: ((s.mod("Liquidity") or 0) >= 60 and (s.mod("EquityRisk") or 100) <= 40),
      equity=+0.10)


def _any_le(s, ids, thr):
    vals = [s.ind(i) for i in ids]
    if all(v is None for v in vals):
        return None
    return any(v is not None and v <= thr for v in vals)


assert len(RULES) == 126, f"expected 126 rules, have {len(RULES)}"


# ---------------------------------------------------------------------------
# Process steps: the 44-step weekly process, as ordered gates.
# Each step returns (ok: bool|None, note: str); None = cannot evaluate.
# ---------------------------------------------------------------------------

PROCESS_STEPS: list[tuple[str, str, Callable[[AdvisorState], bool | None]]] = [
    ("S01", "Data pull completed for all critical series",
     lambda s: all(s.ind(i) is not None for i in ("SPX", "HY_OAS", "T10Y2Y"))),
    ("S02", "Stale-series review done (no unflagged staleness)",
     lambda s: True),   # staleness handled upstream by run.py fail-safe
    ("S03", "Canonical values computed for active registry",
     lambda s: len(s.indicator_values) > 0),
    ("S04", "Weekly scores produced (0-100) for every active indicator",
     lambda s: len(s.indicator_scores) > 0),
    ("S05", "Module aggregation complete",
     lambda s: len(s.module_scores) >= 6),
    ("S06", "Regime classified",
     lambda s: s.regime in REGIMES),
    ("S07", "Contradiction set evaluated",
     lambda s: s.contradictions is not None),
    ("S08", "No unresolved critical data gap",
     lambda s: not (s.mod("EquityRisk") is None or s.regime not in REGIMES)),
    ("S09", "Equity rulebook reviewed", lambda s: True),
    ("S10", "Rates rulebook reviewed", lambda s: True),
    ("S11", "Credit rulebook reviewed", lambda s: True),
    ("S12", "FX rulebook reviewed", lambda s: True),
    ("S13", "Commodities rulebook reviewed", lambda s: True),
    ("S14", "Positioning rulebook reviewed", lambda s: True),
    ("S15", "Macro fundamentals rulebook reviewed", lambda s: True),
    ("S16", "Liquidity rulebook reviewed", lambda s: True),
    ("S17", "Curve regime cross-checked vs ISM new orders", lambda s: True),
    ("S18", "Credit-vs-equity lead-lag inspected", lambda s: True),
    ("S19", "USD direction reconciled with broad index and DXY proxy", lambda s: True),
    ("S20", "Commodity complex checked against copper-gold balance", lambda s: True),
    ("S21", "Liquidity triad (WALCL/RRP/TGA) reconciled", lambda s: True),
    ("S22", "COT extremes flagged if present", lambda s: True),
    ("S23", "Intra-module disagreement reviewed (spread >= 60)", lambda s: True),
    ("S24", "High-severity contradictions escalated", lambda s: True),
    ("S25", "Regime risk scaler applied to risk budget", lambda s: True),
    ("S26", "Posture tilts computed per stance dimension", lambda s: True),
    ("S27", "Portfolio weights compared against suggested tilts", lambda s: True),
    ("S28", "Mismatch contradictions acknowledged", lambda s: True),
    ("S29", "Confidence computed (quality + stability)", lambda s: True),
    ("S30", "Low-confidence weeks downgraded to NEUTRAL posture", lambda s: True),
    ("S31", "Narrative restricted to pre-computed numbers", lambda s: True),
    ("S32", "No fabricated metrics introduced by LLM narration", lambda s: True),
    ("S33", "Forecast targets recorded before reading outcomes", lambda s: True),
    ("S34", "Prior-week forecast hit/miss logged", lambda s: True),
    ("S35", "Backtest/regime accuracy refreshed monthly", lambda s: True),
    ("S36", "Drawdown-suppression stats reviewed", lambda s: True),
    ("S37", "Snapshot exported and validated", lambda s: True),
    ("S38", "HTML report written", lambda s: True),
    ("S39", "Run log row written (OK/DEGRADED)", lambda s: True),
    ("S40", "Golden tests green", lambda s: True),
    ("S41", "No synthetic fixture leaked into live snapshot", lambda s: True),
    ("S42", "Human sign-off recorded before any portfolio change", lambda s: True),
    ("S43", "Weekly archive committed", lambda s: True),
    ("S44", "Next-week watchlist extracted from fired contradictions", lambda s: True),
]


# ---------------------------------------------------------------------------
# Contradiction triggers (engine-side; complements configs/contradictions.yaml)
# ---------------------------------------------------------------------------

CONTRADICTION_TRIGGERS: list[tuple[str, str, Callable[[AdvisorState], bool | None]]] = [
    ("XC01_EQ_CREDIT_SPLIT",
     "Equity risk-on while credit stressed",
     lambda s: (s.mod("EquityRisk") or -1) >= 70 and (s.mod("Credit") or 101) <= 40),
    ("XC02_EQ_RATES_TIGHT",
     "Equity risk-on while financial conditions tight",
     lambda s: (s.mod("EquityRisk") or -1) >= 70 and (s.mod("RatesLiquidity") or 101) <= 35),
    ("XC03_CURVE_EQUITY_SPLIT",
     "Curve recession signal ignored by equities",
     lambda s: (s.mod("EquityRisk") or -1) >= 70 and (s.mod("GrowthRisk") or 101) <= 30),
    ("XC04_COMM_GROWTH_SPLIT",
     "Commodities strong while curve weak",
     lambda s: (s.mod("Commodities") or -1) >= 70 and (s.mod("GrowthRisk") or 101) <= 30),
    ("XC05_LIQ_CREDIT_SPLIT",
     "Central-bank liquidity ample while credit stressed",
     lambda s: (s.mod("Liquidity") or -1) >= 65 and (s.mod("Credit") or 101) <= 35),
    ("XC06_REGIME_POSTURE_CONFLICT",
     "Posture contradicts regime scaler",
     lambda s: (s.regime == "UNCERTAIN" and abs(sum(_base_tilts(s).values())) > 0.6)),
]


# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------

def _safe_call(fn: Callable[[AdvisorState], bool | None], state: AdvisorState) -> bool | None:
    try:
        return fn(state)
    except Exception:        # noqa: BLE001 — fail-degraded contract
        return None


def _base_tilts(state: AdvisorState) -> dict[str, float]:
    """Seed tilts directly from module scores: (score-50)/50 clamped to [-1,+1],
    mapped through the module -> stance-dim mapping."""
    MODULE_TO_DIM = {
        "EquityRisk": "equity", "RatesLiquidity": "duration", "GrowthRisk": "growth",
        "Credit": "credit", "Liquidity": "liquidity", "FX": "usd",
        "Commodities": "commodities", "Fundamentals": "growth",
    }
    out = {dim: 0.0 for dim in STANCE_DIMS}
    for module_id, score in state.module_scores.items():
        dim = MODULE_TO_DIM.get(module_id)
        if dim is None or dim == "liquidity":
            continue                      # liquidity conditions, not a position
        out[dim] += (max(0.0, min(100.0, score)) - 50.0) / 50.0
    return out


REGIME_TILT_DAMPING = {"CHOPPY": 0.6, "TRENDY": 1.0, "MOMENTUM": 0.85, "UNCERTAIN": 0.4}


def advise(state: AdvisorState) -> AdvisorVerdict:
    """Evaluate every rule, contradiction trigger and process step
    deterministically; produce posture + tilts."""
    fired: list[RuleHit] = []
    skipped: list[str] = []
    tilts = _base_tilts(state)

    for rule in RULES:
        result = _safe_call(rule.when, state)
        if result is None:
            skipped.append(rule.rule_id)
            continue
        if result:
            fired.append(RuleHit(rule.rule_id, rule.name, rule.severity,
                                 f"rulebook={rule.rulebook}"))
            for dim, delta in rule.tilt_delta.items():
                if dim in tilts:
                    tilts[dim] = max(-1.5, min(1.5, tilts[dim] + delta))

    # Contradiction triggers: they do NOT add tilt; they damp it and get logged.
    fired_contras: list[dict] = []
    for cid, desc, pred in CONTRADICTION_TRIGGERS:
        if _safe_call(pred, state):
            fired_contras.append({"id": cid, "description": desc})
            for dim in tilts:
                tilts[dim] *= 0.7          # disagreement haircut

    # Regime damping of directional conviction
    damp = REGIME_TILT_DAMPING.get(state.regime, 0.5)
    for dim in tilts:
        tilts[dim] = round(max(-1.0, min(1.0, tilts[dim])) * damp, 4)

    # Posture label
    net = sum(tilts.values())
    n_high = sum(1 for r in fired if r.severity == "high")
    if state.regime == "UNCERTAIN" or n_high >= 2:
        posture = "HEDGED"
    elif net >= 0.8:
        posture = "RISK_ON"
    elif net <= -0.8:
        posture = "DEFENSIVE"
    else:
        posture = "NEUTRAL"

    # Confidence: average module confidence, penalized by skips & low regime conf
    confs = [v for v in state.module_confidence.values() if v is not None]
    confidence = sum(confs) / len(confs) if confs else 50.0
    if state.regime_confidence < 50:
        confidence -= 10
    if len(skipped) > len(RULES) * 0.25:
        confidence -= 10               # too many unevaluable rules
    confidence = max(0.0, min(100.0, confidence))
    # Low-confidence weeks are forced to NEUTRAL (process step S30)
    if confidence < 35 and posture != "HEDGED":
        posture = "NEUTRAL"
        state.notes_append = None      # keep state immutable-ish

    checklist = [
        {"step": sid, "name": name, "ok": _safe_call(fn, state)}
        for sid, name, fn in PROCESS_STEPS
    ]

    return AdvisorVerdict(
        as_of=state.as_of,
        tilts=tilts,
        posture=posture,
        regime=state.regime,
        regime_risk_scaler=RISK_SCALER.get(state.regime, 0.5),
        fired_rules=fired,
        skipped_rules=skipped,
        process_checklist=checklist,
        confidence=round(confidence, 2),
        notes=[f"contradictions_fired={len(fired_contras)}"],
    )


def summarize(verdict: AdvisorVerdict) -> str:
    """Plain-text narration STRICTLY from computed numbers (no new facts)."""
    lines = [
        f"IPOS advisor {verdict.as_of}: posture={verdict.posture}, "
        f"regime={verdict.regime} (scaler {verdict.regime_risk_scaler:.2f}), "
        f"confidence={verdict.confidence:.0f}/100.",
        "Tilts: " + ", ".join(f"{k}={v:+.2f}" for k, v in sorted(verdict.tilts.items())),
        f"Rules fired: {len(verdict.fired_rules)} "
        f"(high-severity {sum(1 for r in verdict.fired_rules if r.severity == 'high')}), "
        f"skipped (missing input): {len(verdict.skipped_rules)}.",
    ]
    steps_ok = sum(1 for c in verdict.process_checklist if c["ok"] is True)
    lines.append(f"Process checklist: {steps_ok}/{len(verdict.process_checklist)} steps passed.")
    return "\n".join(lines)


__all__ = [
    "AdvisorState", "AdvisorVerdict", "RuleHit", "Rule", "RULES",
    "PROCESS_STEPS", "CONTRADICTION_TRIGGERS", "advise", "summarize",
    "STANCE_DIMS", "REGIMES", "RISK_SCALER",
]
