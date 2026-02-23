---
module_id: SENTIMENT_POSITIONING
scope: module
tags: [sentiment, positioning, equity, macro]
version: 0.1
source: seminar_pdf
cadence: weekly
---

## Purpose
Capture *crowd behavior* via surveys + transactional proxies, using **extremes-only** logic to inform risk budget and tilts.

## Indicators (MVP-active)
- sentiment_aaii_sentiment_survey
  - Source link in PDF: AAII sentiment.xls (p23)
- sentiment_naaim_exposure_index
  - Source link in PDF: NAAIM exposure index (p27)
- sentiment_cnn_fear_greed_index
  - External composite (0–100). **Do NOT rebuild components internally.** (p33–p35)
- sentiment_cboe_put_call_ratio_pcratcbo
  - Source link in PDF: StockCharts !PCRATCBO (p37)

## Scoring Defaults (0–100)
- Extreme detection (recommended):
  - Use **percentiles** (5y default) or z-score (5y) to flag extremes.
  - Only act on *extreme states*; mid-range is low signal.
- Directionality:
  - Primarily **contrarian at extremes** (fear → bullish bias; greed → caution).

## Rules (operational, compact)
- RULE: Extremes are what matter
  - If: sentiment is not extreme (mid-range)
  - Then: score_adjustment = 0 (low actionability)
  - Page refs: p35

- RULE: Fear & Greed extreme fear → contrarian bullish bias
  - If: Fear & Greed near 0 (“extreme fear”)
  - Then: increase risk budget / reduce defensiveness (incremental)
  - Page refs: p35
  - Failure modes: fear can persist in crises; confirm with liquidity + rates modules.

- RULE: Fear & Greed extreme greed → caution (tops hard)
  - If: Fear & Greed near 100 (“extreme greed”)
  - Then: reduce incremental risk adds; tighten stops; avoid aggressive leverage
  - Page refs: p35
  - Failure modes: momentum can persist; avoid premature full de-risk.

- RULE: Put/Call is contrarian; explicit threshold
  - If: Put/Call ratio is high → crowd bearish
  - Then: contrarian bullish bias
  - Special: Put/Call > 1.1 = “good signal value”
  - Page refs: p36–p37
  - Failure modes: can spike and stay elevated; use confirmation and stagger entries.

- RULE: AAII (survey) — extremes matter
  - If: AAII bullish/bearish readings at historical extremes
  - Then: contrarian interpretation
  - Page refs: p22–p23
  - Failure modes: structural shifts in participation; treat as “soft” signal unless confirmed.

- RULE: NAAIM (manager exposure) — positioning extremes
  - If: NAAIM exposure is very low → fear/low risk taking
  - Then: contrarian bullish bias
  - If: NAAIM exposure is very high → crowded long
  - Then: caution / lower confidence
  - Page refs: p26–p27
  - Failure modes: managers can stay risk-on in trends; confirm with trend/regime module.

## Confidence Heuristic (module-level)
Increase confidence when **2+ indicators agree** at extremes:
- (Fear&Greed extreme fear) AND (Put/Call > 1.1) AND/OR (NAAIM very low)
Decrease confidence when signals conflict or are non-extreme.

## Contradictions to Watch (trigger investigation)
- Fear&Greed = extreme fear, but Put/Call is low (no fear in options) → investigate data timing/source mismatch.
- AAII extreme bearish, but NAAIM very high exposure → “survey fear vs professional risk-on”; check market regime/trend.
- Sentiment extreme fear while yield curve inverted + liquidity tightening → sentiment may be “right”; reduce contrarian aggressiveness.

## Implementation Notes (IPOS-friendly)
- Store only the composite Fear&Greed value externally (0–100).
- Compute “extreme flags” via percentiles (5y) to keep rules simple and stable.
- Log the contradiction triggers as structured events for weekly review.

## DOC_MAP (Autonomous) — Seminar PDF → IPOS Extraction Queue
**PDF:** `/mnt/data/onvista Aktien-Intensiv-Seminar 11-2025.pdf`  
**Chunk analyzed:** pages **57–80** (1-based)

```json
{
  "chunk": {
    "pages": "57-80",
    "density": "high",
    "topics": [
      "Market conditions",
      "Regime classification",
      "Volatility & momentum",
      "Trend construction",
      "Trend definition"
    ],
    "subtopics": [
      "Market conditions are stable until new impulses",
      "Three conditions: Choppy / Trendy / Momentum",
      "Risk posture if regime is unclear (defensive, small size)",
      "Choppy definition: sideways/range, false breakouts, overlapping highs/lows",
      "Choppy signature: large retracements (80–100%)",
      "Trendy definition: directional movement, higher highs/lows (or lower highs/lows), limited overlap",
      "Momentum definition: high dynamics, rapid ATR expansion, no overlap",
      "Regime-specific playbook: position sizing, entry style, trailing stops, initial stop distance",
      "Trend building blocks: impulse (move) → correction → impulse",
      "Trend exists after 3 swings with visible highs/lows",
      "Uptrend definition (higher lows + higher highs) and continuation condition",
      "Downtrend definition (lower highs + lower lows) and continuation condition"
    ]
  },
  "extract_targets": {
    "indicator_pages": [
      "69",
      "73"
    ],
    "rules_pages": [
      "58-60",
      "65-66",
      "69",
      "73",
      "78-80"
    ],
    "process_pages": [
      "58-59",
      "73",
      "75-76"
    ],
    "low_value_pages": [
      "57",
      "61-64",
      "67-68",
      "70-72",
      "74",
      "77"
    ]
  },
  "likely_modules": [
    {
      "module_id": "MARKET_CONDITIONS",
      "why": "Defines choppy/trendy/momentum regimes and the ‘if unsure, be defensive’ operating rule."
    },
    {
      "module_id": "REGIME_CLASSIFIER_TECH",
      "why": "Operationalizable regime classifier features: overlap, retracement depth, ATR expansion, swing structure."
    },
    {
      "module_id": "TRADE_MANAGEMENT_BY_REGIME",
      "why": "Explicit mapping from regime → position size, entry style, trailing stop method, initial stop distance."
    },
    {
      "module_id": "TREND_STRUCTURE",
      "why": "Formal trend definition (swing-count + higher-high/lower-low logic) for trend regime + trend-break detection."
    }
  ],
  "recommended_next_chunks": [
    {
      "pages": "81-110",
      "why": "Trend sizes (primary/secondary/tertiary), sideways phases, and explicit trend-break definitions — directly usable for regime map/trail + contradictions."
    },
    {
      "pages": "111-135",
      "why": "Bridges into more technical tools/implementation; likely includes more operational rules and indicator definitions."
    }
  ],
  "checkpoint": {
    "pages_done": "57-80",
    "artifacts_written": ["doc_map"],
    "counts": {
      "chunks_mapped": 2
    }
  }
}
## PROCESS_EXTRACT (Autonomous) — `process.jsonl`
**PDF:** `/mnt/data/onvista Aktien-Intensiv-Seminar 11-2025.pdf`  
**Pages:** 57–80 (1-based)  
**Batch cap:** 20 → extracted **13** (high-impact, operationalizable)

```jsonl
{"id":"process_market_conditions_stable_until_new_impulse","topic":"market_conditions","statement":"Market conditions tend to remain stable over time and change mainly when new impulses enter the market.","operationalization":["Compute regime features weekly (e.g., overlap, ATR change, retracement ratio) and apply hysteresis (require N consecutive weeks to switch regimes).","Log regime-change triggers (feature thresholds crossed) for auditability.","Use prior-week regime as default if classifier confidence is low."],"page_refs":["p58"]}
{"id":"process_three_market_conditions_choppy_trendy_momentum","topic":"market_conditions","statement":"Classify the market into three conditions: Choppy, Trendy, Momentum.","operationalization":["Create derived weekly series: market_regime_label ∈ {CHOPPY,TRENDY,MOMENTUM} for each tracked market (e.g., SPX, credit index).","Store regime as categorical + confidence (0–100) in regime aggregates table."],"page_refs":["p59"]}
{"id":"process_if_uncertain_be_defensive_small_positions","topic":"risk_posture","statement":"If you cannot assess market conditions, act defensively and trade small positions.","operationalization":["Add rule: if regime_confidence < threshold => cap risk_budget (e.g., max 40/100) and reduce module weights on tactical signals.","Record a 'regime_uncertain' contradiction flag to force a weekly review note."],"page_refs":["p59"]}
{"id":"process_choppy_definition_range_false_breakouts_high_overlap","topic":"market_conditions","statement":"Choppy markets: sideways/range or weak trend, many false breakouts, highs/lows overlap, large retracements (80–100%).","operationalization":["Define features: overlap_index (share of weeks with overlapping ranges), retracement_ratio (pullback size / impulse size).","Classifier rule-of-thumb: if retracement_ratio in [0.8,1.0] and overlap_index high => CHOPPY.","In CHOPPY regime, downweight breakout signals and tighten risk budget."],"page_refs":["p60"]}
{"id":"process_trendy_definition_directional_hh_hl_or_ll_lh_low_overlap","topic":"market_conditions","statement":"Trendy markets: clear direction with higher highs/higher lows (or lower highs/lower lows) and few overlaps.","operationalization":["Compute swing structure on weekly bars: HH/HL count vs LL/LH count over last K weeks.","Define low overlap condition (overlap_index below threshold) and directional bias (net higher highs vs lower lows).","If directional bias strong and overlap low => TRENDY; increase trend module weight."],"page_refs":["p65","p66"]}
{"id":"process_momentum_definition_high_dynamics_atr_expansion_no_overlap","topic":"market_conditions","statement":"Momentum markets: high dynamics with rapid ATR increase and no overlap of highs/lows; moves can occur with/against the trend direction.","operationalization":["Compute weekly ATR (from daily bars aggregated to week) and atr_change_rate (e.g., 4w ROC of ATR).","Classifier rule-of-thumb: if atr_change_rate high and overlap_index very low => MOMENTUM.","Treat momentum as higher noise: widen stops, reduce position size vs TRENDY, and lower confidence unless confirmed."],"page_refs":["p69"]}
{"id":"process_trade_management_by_regime_position_size","topic":"trade_management","statement":"Position sizing by regime: Choppy = small, Trendy = large, Momentum = medium.","operationalization":["Map regime -> risk_scaler: CHOPPY 0.5x, TRENDY 1.0x, MOMENTUM 0.75x (tunable).","Apply scaler to overall risk budget and to per-module stance magnitudes."],"page_refs":["p73"]}
{"id":"process_trade_management_by_regime_entries","topic":"trade_management","statement":"Entry style by regime: Choppy = avoid trading breakouts; Trendy = retracements and breakouts possible; Momentum = anticipate, do not expect large retracements.","operationalization":["Add playbook rule: if CHOPPY then invalidate/penalize breakout-based signals.","If TRENDY then allow both breakout and pullback entry signals; prefer confirmation.","If MOMENTUM then favor continuation signals; reduce reliance on pullback signals and increase slippage/volatility assumptions."],"page_refs":["p73"]}
{"id":"process_trade_management_by_regime_stops","topic":"trade_management","statement":"Stops by regime: Choppy = none or defensive; Trendy = trailing via relative highs/lows or Supertrend-like; Momentum = initial stop 1–2 ATR; Choppy initial stop far; Trendy initial stop at last swing high/low.","operationalization":["Define stop policy objects per regime (initial_stop_method, trailing_stop_method).","Implement as metadata in Playbook: CHOPPY -> defensive stop + quick exit; TRENDY -> swing-based trailing; MOMENTUM -> ATR-based initial stop (1–2 ATR).","Store chosen stop policy in weekly report for transparency."],"page_refs":["p73"]}
{"id":"process_trend_understanding_enables_position_adds_and_profit_protection","topic":"trend_structure","statement":"Understanding trend mechanics enables adding to trends, trading pullbacks, knowing when to secure profits, and recognizing sideways phases and trend changes early.","operationalization":["Expose trend phase widgets in dashboard: trend strength, pullback depth, and potential trend-break alerts.","Use trend phase to modulate confidence and stance (add-only when phase supports)."],"page_refs":["p76"]}
{"id":"process_trend_definition_requires_three_swings","topic":"trend_structure","statement":"A trend exists when three consecutive movements have produced visible highs/lows (swing points).","operationalization":["Implement swing detection on weekly bars (e.g., pivot highs/lows with a lookback).","Set rule: require ≥3 alternating swings before labeling TRENDY; otherwise treat as CHOPPY/UNCERTAIN."],"page_refs":["p78"]}
{"id":"process_uptrend_definition_min_structure","topic":"trend_structure","statement":"Uptrend: rising highs and rising lows; formed with at least one higher low and two higher highs; continuation requires rising lows which later produce rising highs.","operationalization":["Encode uptrend criteria as boolean features: has_HL>=1 and has_HH>=2 over window K.","Trend continuation alert: if latest low violates prior rising-low sequence => potential trend break."],"page_refs":["p79"]}
{"id":"process_downtrend_definition_min_structure","topic":"trend_structure","statement":"Downtrend: falling highs and falling lows; formed with at least one lower high and two lower lows; continuation requires falling highs which later produce falling lows.","operationalization":["Encode downtrend criteria as boolean features: has_LH>=1 and has_LL>=2 over window K.","Trend continuation alert: if latest high violates prior falling-high sequence => potential trend break."],"page_refs":["p80"]}


## RULE_EXTRACT (Autonomous) — `rules.jsonl`
**PDF:** `/mnt/data/onvista Aktien-Intensiv-Seminar 11-2025.pdf`  
**Pages:** 57–80 (1-based)  
**Batch cap:** 40 → extracted **18** (high-impact, operational)

```jsonl
{"id":"rule_market_conditions_are_stable_until_impulses","scope":"process","applies_to":["MARKET_CONDITIONS"],"if":"operating weekly and interpreting recent price action","then":{"interpretation":"Assume market conditions persist unless a new impulse changes them; avoid overreacting to small fluctuations.","score_adjustment":"n/a","confidence_adjustment":"+0"},"rationale":"Market conditions are relatively stable over time; conditions change when new impulses enter the market.","failure_modes":["Sudden shocks can change regime within days; weekly cadence may lag."],"page_refs":["p58"],"needs_verification":false}
{"id":"rule_three_market_conditions_choppy_trendy_momentum","scope":"process","applies_to":["MARKET_CONDITIONS"],"if":"classifying the market environment","then":{"interpretation":"Use exactly three regime labels: CHOPPY, TRENDY, MOMENTUM.","score_adjustment":"n/a","confidence_adjustment":"n/a"},"rationale":"Seminar explicitly defines three market conditions.","failure_modes":["Edge cases between regimes; needs confidence score."],"page_refs":["p59"],"needs_verification":false}
{"id":"rule_if_regime_unclear_be_defensive_small","scope":"portfolio","applies_to":["MARKET_CONDITIONS"],"if":"you cannot assess market conditions / regime confidence is low","then":{"interpretation":"Be defensive and trade small positions (cap risk budget).","score_adjustment":"-10","confidence_adjustment":"-10"},"rationale":"Seminar: if you cannot judge conditions, be cautious/defensive and trade small positions.","failure_modes":["Can undertrade early trend beginnings; ensure ‘unclear’ threshold is not too strict."],"page_refs":["p59"],"needs_verification":false}
{"id":"rule_choppy_sideways_false_breakouts","scope":"module","applies_to":["MARKET_CONDITIONS"],"if":"market is sideways / no clear moves / many false breakouts","then":{"interpretation":"Classify as CHOPPY and penalize breakout-style signals.","score_adjustment":"-10","confidence_adjustment":"+5"},"rationale":"Choppy: sideways, no clear movements, many false breakouts; can occur in range or weak trend.","failure_modes":["Range breakouts can still work rarely; avoid absolute bans—use penalties."],"page_refs":["p60"],"needs_verification":false}
{"id":"rule_choppy_retracement_80_100_percent","scope":"module","applies_to":["REGIME_CLASSIFIER_TECH"],"if":"retracements are ~80–100% of prior impulse moves","then":{"interpretation":"Strong CHOPPY signature; reduce conviction and position sizing.","score_adjustment":"-15","confidence_adjustment":"+10"},"rationale":"Seminar: choppy markets show large retracements (80–100%) of a move.","failure_modes":["Some mean-reversion phases precede breakouts; watch for impulse expansion."],"page_refs":["p60"],"needs_verification":false}
{"id":"rule_choppy_high_low_overlap","scope":"module","applies_to":["REGIME_CLASSIFIER_TECH"],"if":"highs and lows frequently overlap","then":{"interpretation":"CHOPPY signature (range/overlap); reduce trend-following weight.","score_adjustment":"-10","confidence_adjustment":"+5"},"rationale":"Seminar: highs and lows overlap in choppy markets.","failure_modes":["Overlap can also occur in early trend transitions; pair with retracement/ATR cues."],"page_refs":["p60"],"needs_verification":false}
{"id":"rule_trendy_directional_hh_hl_or_lh_ll","scope":"module","applies_to":["MARKET_CONDITIONS","TREND_STRUCTURE"],"if":"price moves clearly in one direction with higher highs/higher lows (or lower highs/lower lows)","then":{"interpretation":"Classify as TRENDY; allow trend-following signals and larger positions vs choppy.","score_adjustment":"+10","confidence_adjustment":"+5"},"rationale":"Seminar: trendy markets move clearly in one direction with HH/HL (up) or LH/LL (down).","failure_modes":["Trend exhaustion; late-stage trends can look ‘trendy’ but be fragile."],"page_refs":["p65"],"needs_verification":false}
{"id":"rule_trendy_has_few_overlaps","scope":"module","applies_to":["REGIME_CLASSIFIER_TECH"],"if":"only few overlaps of highs and lows","then":{"interpretation":"Supports TRENDY classification; increase trend module weight.","score_adjustment":"+5","confidence_adjustment":"+5"},"rationale":"Seminar: trendy markets have few overlaps of highs/lows.","failure_modes":["Can be true in momentum spikes too; separate TRENDY vs MOMENTUM with ATR cue."],"page_refs":["p65"],"needs_verification":false}
{"id":"rule_momentum_atr_rises_fast_no_overlap","scope":"module","applies_to":["MARKET_CONDITIONS","REGIME_CLASSIFIER_TECH"],"if":"ATR increases quickly and highs/lows do not overlap","then":{"interpretation":"Classify as MOMENTUM; treat as high dynamics (adjust stops/positioning accordingly).","score_adjustment":"+5","confidence_adjustment":"+5"},"rationale":"Seminar: momentum shows high dynamics and rapid ATR increase; no overlap of highs/lows; moves can be with or against the trend.","failure_modes":["Volatility clusters can revert; momentum can flip quickly."],"page_refs":["p69"],"needs_verification":false}
{"id":"rule_trade_by_regime_position_size","scope":"portfolio","applies_to":["TRADE_MANAGEMENT_BY_REGIME"],"if":"regime is CHOPPY / TRENDY / MOMENTUM","then":{"interpretation":"Position sizing guidance: CHOPPY=small, TRENDY=large, MOMENTUM=medium.","score_adjustment":"n/a","confidence_adjustment":"n/a"},"rationale":"Seminar table: position size varies by market condition.","failure_modes":["Account/risk constraints override; translate to scalers (e.g., 0.5x/1.0x/0.75x)."],"page_refs":["p73"],"needs_verification":false}
{"id":"rule_trade_by_regime_trailing_stops","scope":"process","applies_to":["TRADE_MANAGEMENT_BY_REGIME"],"if":"regime is CHOPPY / TRENDY / MOMENTUM","then":{"interpretation":"Trailing stop guidance: CHOPPY=none/defensive; TRENDY=relative highs/lows; MOMENTUM=Supertrend-like.","score_adjustment":"n/a","confidence_adjustment":"n/a"},"rationale":"Seminar table defines trailing stop style by regime.","failure_modes":["Implementation differs across instruments; keep as policy selection rather than numeric stop."],"page_refs":["p73"],"needs_verification":false}
{"id":"rule_trade_by_regime_entries","scope":"process","applies_to":["TRADE_MANAGEMENT_BY_REGIME"],"if":"regime is CHOPPY / TRENDY / MOMENTUM","then":{"interpretation":"Entry guidance: CHOPPY=do not trade breakouts; TRENDY=retracements and breakouts possible; MOMENTUM=anticipate, do not expect large retracements.","score_adjustment":"n/a","confidence_adjustment":"n/a"},"rationale":"Seminar table defines entry approach by regime.","failure_modes":["Even in choppy markets, rare breakouts happen; use ‘penalize’ rather than ‘never’ in automation."],"page_refs":["p73"],"needs_verification":false}
{"id":"rule_trade_by_regime_initial_stop","scope":"process","applies_to":["TRADE_MANAGEMENT_BY_REGIME"],"if":"regime is CHOPPY / TRENDY / MOMENTUM","then":{"interpretation":"Initial stop guidance: CHOPPY=far away; TRENDY=last swing low/high; MOMENTUM=1–2 ATR.","score_adjustment":"n/a","confidence_adjustment":"n/a"},"rationale":"Seminar table defines initial stop placement by regime, including explicit 1–2 ATR for momentum.","failure_modes":["ATR definition and timeframe must be consistent; ‘far away’ needs a policy proxy (e.g., wider ATR multiple)."],"page_refs":["p73"],"needs_verification":false}
{"id":"rule_trend_exists_after_three_consecutive_moves","scope":"module","applies_to":["TREND_STRUCTURE"],"if":"three consecutive moves have produced visible swing highs/lows","then":{"interpretation":"A trend can be declared (vs no-trend).","score_adjustment":"n/a","confidence_adjustment":"+5"},"rationale":"Seminar: a trend exists when three successive movements created visible high/low points.","failure_modes":["Swing detection sensitivity; false swings in noisy markets."],"page_refs":["p78"],"needs_verification":false}
{"id":"rule_uptrend_minimum_structure","scope":"module","applies_to":["TREND_STRUCTURE"],"if":"at least one higher low and two higher highs exist","then":{"interpretation":"Uptrend is formed (structural definition).","score_adjustment":"+5","confidence_adjustment":"+5"},"rationale":"Seminar: uptrend formed with ≥1 higher low and ≥2 higher highs.","failure_modes":["Late-stage trend can meet criteria but be near reversal; pair with momentum/volatility."],"page_refs":["p79"],"needs_verification":false}
{"id":"rule_uptrend_continuation_requires_rising_lows","scope":"module","applies_to":["TREND_STRUCTURE"],"if":"rising lows continue to form","then":{"interpretation":"Uptrend continuation condition; expect higher highs to follow over time.","score_adjustment":"+5","confidence_adjustment":"+5"},"rationale":"Seminar: continuation requires rising lows, which later pull up highs.","failure_modes":["Distribution tops can still print rising lows briefly; watch for failure to make new highs."],"page_refs":["p79"],"needs_verification":false}
{"id":"rule_downtrend_minimum_structure","scope":"module","applies_to":["TREND_STRUCTURE"],"if":"at least one lower high and two lower lows exist","then":{"interpretation":"Downtrend is formed (structural definition).","score_adjustment":"-5","confidence_adjustment":"+5"},"rationale":"Seminar: downtrend formed with ≥1 lower high and ≥2 lower lows.","failure_modes":["Bear market rallies can temporarily break lower-high pattern."],"page_refs":["p80"],"needs_verification":false}
{"id":"rule_downtrend_continuation_requires_falling_highs","scope":"module","applies_to":["TREND_STRUCTURE"],"if":"falling highs continue to form","then":{"interpretation":"Downtrend continuation condition; expect lower lows to follow over time.","score_adjustment":"-5","confidence_adjustment":"+5"},"rationale":"Seminar: continuation requires falling highs, which later lead to falling lows.","failure_modes":["Capitulation lows can end trend abruptly; watch for higher highs."],"page_refs":["p80"],"needs_verification":false}
