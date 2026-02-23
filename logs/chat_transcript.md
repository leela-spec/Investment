## DOC_MAP (Autonomous) — Seminar PDF → IPOS Extraction Queue
**PDF:** `/mnt/data/onvista Aktien-Intensiv-Seminar 11-2025.pdf`  
**Chunk analyzed:** pages **15–56** (1-based)

```json
{
  "chunk": {
    "pages": "15-56",
    "density": "high",
    "topics": [
      "Market drivers",
      "Liquidity & policy",
      "Sentiment & positioning",
      "Macro fundamentals",
      "Equity flows (buybacks)",
      "Rates (yield curve)"
    ],
    "subtopics": [
      "Three-driver framework (Liquidity/Sentiment/Fundamentals)",
      "Quantitative easing (QE) mechanics",
      "Central bank balance sheet (Fed WALCL link)",
      "Policy/fiscal support vs QE (market impact)",
      "Sentiment definition (survey vs positioning)",
      "AAII sentiment survey (contrarian extremes implied)",
      "NAAIM exposure index (manager positioning)",
      "University of Michigan consumer sentiment/confidence",
      "CNN Fear & Greed composite index",
      "Put/Call ratio (positioning; contrarian extremes implied)",
      "ISM Manufacturing / PMI interpretation (50 threshold explicitly mentioned)",
      "Buybacks: motives, mechanics, effects on EPS/earnings, dividends link",
      "Yield curve basics: steep/flat/inverted; recession signaling",
      "Yield curve interpretation: expectations, policy, risk premia"
    ]
  },
  "extract_targets": {
    "indicator_pages": [
      "15",
      "17-20",
      "23-27",
      "29-35",
      "36-37",
      "39-41",
      "43-50",
      "52-56"
    ],
    "rules_pages": [
      "15",
      "17",
      "22-23",
      "26",
      "29",
      "33",
      "36",
      "39",
      "43-44",
      "52-56"
    ],
    "process_pages": [
      "15",
      "22",
      "39",
      "43-44",
      "52-56"
    ],
    "low_value_pages": [
      "16",
      "21",
      "24",
      "28",
      "38",
      "42",
      "51"
    ]
  },
  "likely_modules": [
    {
      "module_id": "DRIVERS_3FACTOR",
      "why": "Defines the top-level IPOS structure: Liquidity, Sentiment, Fundamentals."
    },
    {
      "module_id": "LIQUIDITY_POLICY",
      "why": "QE + CB balance sheet proxies and policy support mapping to risk-on/off."
    },
    {
      "module_id": "SENTIMENT_POSITIONING",
      "why": "AAII, NAAIM, consumer confidence, Fear&Greed, Put/Call into contrarian scoring."
    },
    {
      "module_id": "MACRO_GROWTH",
      "why": "ISM/PMI growth regime interpretation (explicit 50 threshold)."
    },
    {
      "module_id": "EQUITY_FLOWS_BUYBACKS",
      "why": "Buybacks as equity demand/earnings mechanics; potential risk-on tailwind proxy."
    },
    {
      "module_id": "RATES_YIELD_CURVE",
      "why": "Yield curve shape + inversion as recession risk / risk budget governor."
    }
  ],
  "recommended_next_chunks": [
    {
      "pages": "57-80",
      "why": "Market conditions (choppy vs trendy vs momentum) — likely core regime classifier + contradictions logic."
    },
    {
      "pages": "81-110",
      "why": "Continuation of market conditions + operational trading/process heuristics."
    },
    {
      "pages": "111-135",
      "why": "Bridges into technical/scan logic; likely indicator definitions."
    }
  ],
  "checkpoint": {
    "pages_done": "15-56",
    "artifacts_written": ["doc_map"],
    "counts": {
      "chunks_mapped": 1
    }
  }
}


## INDICATOR_EXTRACT (Autonomous) — `indicators.jsonl`
**PDF:** `/mnt/data/onvista Aktien-Intensiv-Seminar 11-2025.pdf`  
**Pages:** 15–56 (1-based)  
**Batch cap:** 25 → extracted **23**

```jsonl
{"id":"drivers_three_factor_framework","name":"Three drivers framework (Liquidity / Sentiment / Fundamentals + Buybacks)","category":"Process","asset_class":"Cross-Asset","frequency":"weekly","raw_definition":"Top-level framework: 1) Liquidity flows, 2) Sentiment/positioning, 3) Fundamentals; optional 4) Buybacks.","source_hint":"Seminar slide","transforms":["module_scores","overall_risk_budget"],"directionality":"mixed","scoring_method_default":"band","bands_or_thresholds":[{"rule":"Liquidity risk-on & Sentiment risk-on & Fundamentals risk-on => high risk budget","score":80}],"notes":["Use as module structure (not a market series)."],"page_refs":["p15"],"needs_verification":false}
{"id":"liquidity_fed_balance_sheet_total_assets_walcl","name":"Federal Reserve Total Assets (WALCL)","category":"Liquidity","asset_class":"Rates","frequency":"weekly","raw_definition":"Fed balance sheet total assets time series (WALCL).","source_hint":"FRED series WALCL","transforms":["level","1w_change","4w_change","zscore_3y","percentile_5y","roc_12w"],"directionality":"pro_risk","scoring_method_default":"zscore","bands_or_thresholds":[{"rule":"Strong expansion vs history => liquidity tailwind","score":70}],"notes":["Resample to week-end as_of (Fri close)."],"page_refs":["p18"],"needs_verification":false}
{"id":"equity_sp500_index","name":"S&P 500 Index (reference benchmark)","category":"Market","asset_class":"Equity","frequency":"weekly","source_frequency":"daily","raw_definition":"Referenced as equity proxy when discussing QE impact.","source_hint":"Any provider (e.g., Yahoo/FRED/Quandl) — choose local source","transforms":["level","returns_1w","returns_4w","returns_12w","drawdown_52w"],"directionality":"pro_risk","scoring_method_default":"percentile","bands_or_thresholds":[{"rule":"Trend up + drawdown low => supportive backdrop","score":70}],"notes":["Used for context/overlay in charts; not a 'macro indicator' per se."],"page_refs":["p19"],"needs_verification":true}
{"id":"sentiment_aaii_sentiment_survey","name":"AAII Sentiment Survey (Bull/Bear/Neutral; Bull-Bear spread)","category":"Sentiment","asset_class":"Equity","frequency":"weekly","raw_definition":"Weekly AAII member survey: 6-month outlook bull/bear/neutral.","source_hint":"AAII sentiment.xls","transforms":["bull_pct","bear_pct","neutral_pct","bull_bear_spread","zscore_5y","percentile_5y"],"directionality":"contrarian_extremes","scoring_method_default":"percentile","bands_or_thresholds":[{"rule":"Extreme bearishness (high bear_pct / low bull_bear_spread) => contrarian bullish","score":75}],"notes":["Treat extremes as contrarian; verify exact extreme cutoffs during calibration."],"page_refs":["p23"],"needs_verification":false}
{"id":"sentiment_naaim_exposure_index","name":"NAAIM Exposure Index (active manager equity exposure)","category":"Sentiment","asset_class":"Equity","frequency":"weekly","raw_definition":"Weekly average equity exposure reported by active managers (as of Wed close).","source_hint":"NAAIM Exposure Index","transforms":["level","zscore_5y","percentile_5y","extreme_flags"],"directionality":"contrarian_extremes","scoring_method_default":"zscore","bands_or_thresholds":[{"rule":"Very low exposure => contrarian bullish; very high => contrarian caution","score":70}],"notes":["Align to weekly cadence using report date (Wed) mapped to week as_of."],"page_refs":["p26","p27"],"needs_verification":true}
{"id":"macro_consumer_sentiment_university_of_michigan","name":"University of Michigan Consumer Sentiment / Confidence","category":"Fundamentals","asset_class":"Equity","frequency":"weekly","source_frequency":"monthly","raw_definition":"Monthly survey (~500 households) on personal finances + short/long-term economy outlook.","source_hint":"University of Michigan Surveys of Consumers","transforms":["level","yoy_change","zscore_10y","percentile_10y"],"directionality":"mixed","scoring_method_default":"percentile","bands_or_thresholds":[{"rule":"Extremes often contrarian per seminar","score":60}],"notes":["Seminar notes extremes as contrarian; define quantitative extreme bands in playbook."],"page_refs":["p29","p30","p31","p32"],"needs_verification":false}
{"id":"sentiment_cnn_fear_greed_index","name":"CNN Fear & Greed Index (0–100 composite)","category":"Sentiment","asset_class":"Equity","frequency":"weekly","source_frequency":"daily","raw_definition":"Composite of seven equally weighted indicators; 0=extreme fear, 100=extreme greed.","source_hint":"CNN markets Fear & Greed","transforms":["level","1w_change","4w_change","zscore_5y","percentile_5y"],"directionality":"contrarian_extremes","scoring_method_default":"band","bands_or_thresholds":[{"rule":"Very low (fear) => contrarian bullish; very high (greed) => caution","score":70}],"notes":["Composite already 0–100; optionally re-map to risk budget with contrarian banding."],"page_refs":["p33","p34","p35"],"needs_verification":false}
{"id":"sentiment_cnn_fear_greed_component_market_momentum","name":"Fear & Greed component: Market momentum","category":"Sentiment","asset_class":"Equity","frequency":"weekly","source_frequency":"daily","raw_definition":"One of seven components listed in seminar (exact definition per CNN methodology).","source_hint":"CNN methodology","transforms":["level","percentile_5y"],"directionality":"pro_risk","scoring_method_default":"percentile","bands_or_thresholds":[],"notes":["Component definitions not in text extraction; treat as optional; verify exact series construction."],"page_refs":["p33"],"needs_verification":true}
{"id":"sentiment_cnn_fear_greed_component_stock_price_strength","name":"Fear & Greed component: Stock price strength","category":"Sentiment","asset_class":"Equity","frequency":"weekly","source_frequency":"daily","raw_definition":"One of seven components listed in seminar (exact definition per CNN methodology).","source_hint":"CNN methodology","transforms":["level","percentile_5y"],"directionality":"pro_risk","scoring_method_default":"percentile","bands_or_thresholds":[],"notes":["Verify definition and data source."],"page_refs":["p33"],"needs_verification":true}
{"id":"sentiment_cnn_fear_greed_component_stock_price_breadth","name":"Fear & Greed component: Stock price breadth","category":"Sentiment","asset_class":"Equity","frequency":"weekly","source_frequency":"daily","raw_definition":"One of seven components listed in seminar (exact definition per CNN methodology).","source_hint":"CNN methodology","transforms":["level","percentile_5y"],"directionality":"pro_risk","scoring_method_default":"percentile","bands_or_thresholds":[],"notes":["Verify definition and data source."],"page_refs":["p33"],"needs_verification":true}
{"id":"sentiment_cboe_put_call_ratio_pcratcbo","name":"CBOE Put/Call Ratio (e.g., %21PCRATCBO)","category":"Sentiment","asset_class":"Equity","frequency":"weekly","source_frequency":"daily","raw_definition":"Ratio of traded put option volume to call option volume; higher implies negative sentiment.","source_hint":"StockCharts symbol !PCRATCBO (CBOE Put/Call)","transforms":["level","zscore_5y","percentile_5y","extreme_flags"],"directionality":"contrarian_extremes","scoring_method_default":"zscore","bands_or_thresholds":[{"rule":"High put/call (fear) => contrarian bullish; low => contrarian caution","score":70}],"notes":["Seminar states high implies negative sentiment; define contrarian extremes in playbook."],"page_refs":["p36","p37"],"needs_verification":false}
{"id":"positioning_cftc_commitments_of_traders_net_positions","name":"CFTC Commitments of Traders (COT) net positioning (by asset)","category":"Positioning","asset_class":"Cross-Asset","frequency":"weekly","raw_definition":"Positioning proxy mentioned as sentiment via actual transactions (COT reports).","source_hint":"CFTC COT reports (futures positioning)","transforms":["net_long","net_long_pct_oi","zscore_5y","percentile_5y"],"directionality":"mixed","scoring_method_default":"percentile","bands_or_thresholds":[{"rule":"Crowded extremes => reversal risk; use contrarian logic where appropriate","score":60}],"notes":["Implement as a family: e.g., USD, EUR, Gold, Oil, Equities futures."],"page_refs":["p22"],"needs_verification":true}
{"id":"macro_ism_manufacturing_pmi_headline","name":"ISM Manufacturing PMI (headline)","category":"Fundamentals","asset_class":"Equity","frequency":"weekly","source_frequency":"monthly","raw_definition":"ISM Manufacturing/PMI: survey of ~400 purchasing managers; key leading indicator.","source_hint":"ISM (or FRED/TradingView equivalents)","transforms":["level","3m_avg","6m_trend","zscore_10y","percentile_10y"],"directionality":"pro_risk","scoring_method_default":"band","bands_or_thresholds":[{"rule":"ISM > 50 => expanding activity (risk-on tailwind)","score":70},{"rule":"ISM < 50 => contraction risk; often precedes equity drawdowns","score":30}],"notes":["Map to growth regime module; optionally smooth (3m avg)."],"page_refs":["p39","p40","p41"],"needs_verification":false}
{"id":"macro_ism_new_orders","name":"ISM Manufacturing subindex: New Orders (30% weight in headline per seminar)","category":"Fundamentals","asset_class":"Equity","frequency":"weekly","source_frequency":"monthly","raw_definition":"Subcomponent of ISM headline (orders).","source_hint":"ISM","transforms":["level","3m_avg","trend_6m","percentile_10y"],"directionality":"pro_risk","scoring_method_default":"percentile","bands_or_thresholds":[{"rule":"Sustained decline while headline stable => early warning","score":45}],"notes":["Use for contradictions: headline ok but orders weak."],"page_refs":["p39"],"needs_verification":true}
{"id":"macro_ism_production","name":"ISM Manufacturing subindex: Production (25% weight in headline per seminar)","category":"Fundamentals","asset_class":"Equity","frequency":"weekly","source_frequency":"monthly","raw_definition":"Subcomponent of ISM headline (production).","source_hint":"ISM","transforms":["level","3m_avg","trend_6m","percentile_10y"],"directionality":"pro_risk","scoring_method_default":"percentile","bands_or_thresholds":[],"notes":["Useful for growth vs inflation interpretations."],"page_refs":["p39"],"needs_verification":true}
{"id":"macro_ism_employment","name":"ISM Manufacturing subindex: Employment (20% weight in headline per seminar)","category":"Fundamentals","asset_class":"Equity","frequency":"weekly","source_frequency":"monthly","raw_definition":"Subcomponent of ISM headline (employment).","source_hint":"ISM","transforms":["level","3m_avg","trend_6m","percentile_10y"],"directionality":"pro_risk","scoring_method_default":"percentile","bands_or_thresholds":[],"notes":["Bridge to labor market regime; confirm subindex availability in chosen data source."],"page_refs":["p39"],"needs_verification":true}
{"id":"macro_ism_supplier_deliveries","name":"ISM Manufacturing subindex: Supplier Deliveries (15% weight per seminar)","category":"Fundamentals","asset_class":"Equity","frequency":"weekly","source_frequency":"monthly","raw_definition":"Subcomponent of ISM headline (supplier deliveries).","source_hint":"ISM","transforms":["level","3m_avg","percentile_10y"],"directionality":"mixed","scoring_method_default":"percentile","bands_or_thresholds":[],"notes":["Interpretation can flip (delays can mean demand strength or supply constraints); treat carefully."],"page_refs":["p39"],"needs_verification":true}
{"id":"macro_ism_inventories","name":"ISM Manufacturing subindex: Inventories (10% weight per seminar)","category":"Fundamentals","asset_class":"Equity","frequency":"weekly","source_frequency":"monthly","raw_definition":"Subcomponent of ISM headline (inventories).","source_hint":"ISM","transforms":["level","3m_avg","percentile_10y"],"directionality":"mixed","scoring_method_default":"percentile","bands_or_thresholds":[],"notes":["Use in contradictions with orders/production."],"page_refs":["p39"],"needs_verification":true}
{"id":"equity_flows_us_corporate_share_buybacks_total","name":"US Corporate Share Buybacks (aggregate volume)","category":"Equity Flows","asset_class":"Equity","frequency":"weekly","source_frequency":"quarterly","raw_definition":"Seminar highlights buybacks as an increasingly important driver; charts show strong rise since ~2012 and record year 2025.","source_hint":"Chart source not captured in text; likely S&P Dow Jones Indices / Bloomberg / FactSet / Yardeni etc.","transforms":["level","yoy_change","zscore_10y","percentile_10y"],"directionality":"pro_risk","scoring_method_default":"percentile","bands_or_thresholds":[{"rule":"Rising buybacks => demand tailwind; collapsing buybacks => risk-off signal","score":65}],"notes":["Needs source selection + series definition; treat as module input not standalone timing tool."],"page_refs":["p15","p43","p45","p48","p49"],"needs_verification":true}
{"id":"equity_flows_us_buybacks_plus_dividends","name":"US Shareholder Payouts: Buybacks + Dividends (aggregate)","category":"Equity Flows","asset_class":"Equity","frequency":"weekly","source_frequency":"quarterly","raw_definition":"Chart referenced: buybacks and dividends; notable drop in Q2 2020.","source_hint":"Chart source not captured in text extraction","transforms":["level","yoy_change","percentile_10y"],"directionality":"pro_risk","scoring_method_default":"percentile","bands_or_thresholds":[],"notes":["Used to gauge corporate distribution cycle; requires data source verification."],"page_refs":["p47"],"needs_verification":true}
{"id":"equity_flows_buybacks_vs_earnings_proxy","name":"Buybacks vs Earnings (relationship proxy)","category":"Equity Flows","asset_class":"Equity","frequency":"weekly","source_frequency":"quarterly","raw_definition":"Seminar states buybacks and earnings are tightly linked; chart referenced.","source_hint":"Chart source not captured in text extraction","transforms":["ratio","zscore_10y"],"directionality":"mixed","scoring_method_default":"zscore","bands_or_thresholds":[],"notes":["Potential contradictions input: earnings weakening but buybacks high (or vice versa)."],"page_refs":["p46"],"needs_verification":true}
{"id":"rates_yield_curve_us_10y_minus_2y_t10y2y","name":"US Yield Curve Slope: 10Y minus 2Y (T10Y2Y)","category":"Rates","asset_class":"Rates","frequency":"weekly","source_frequency":"daily","raw_definition":"Key maturities: 10Y and 2Y; inversion historically precedes recessions.","source_hint":"FRED series T10Y2Y","transforms":["level","1w_change","4w_change","percentile_20y","inversion_flag"],"directionality":"pro_risk","scoring_method_default":"band","bands_or_thresholds":[{"rule":"Spread < 0 (inverted) => recession risk elevated","score":20},{"rule":"Spread > 0 and steepening => risk-on tailwind","score":65}],"notes":["Primary recession-risk governor for risk budget."],"page_refs":["p52","p54","p55"],"needs_verification":false}
{"id":"rates_yield_curve_us_10y_minus_3m","name":"US Yield Curve Slope: 10Y minus 3M (often cited as very reliable)","category":"Rates","asset_class":"Rates","frequency":"weekly","source_frequency":"daily","raw_definition":"Seminar notes 3M–10Y spread as historically very reliable indicator (alongside 2Y–10Y).","source_hint":"FRED (commonly T10Y3M) or equivalent","transforms":["level","percentile_20y","inversion_flag"],"directionality":"pro_risk","scoring_method_default":"band","bands_or_thresholds":[{"rule":"Spread < 0 => recession risk elevated","score":20}],"notes":["Use alongside T10Y2Y; treat as confirmation/contradiction pair."],"page_refs":["p56"],"needs_verification":true}

## RULE_EXTRACT (Autonomous) — `rules.jsonl`
**PDF:** `/mnt/data/onvista Aktien-Intensiv-Seminar 11-2025.pdf`  
**Pages:** 15–56 (1-based)  
**Batch cap:** 40 → extracted **26** high-impact rules  
**Note applied:** Fear & Greed is treated as an **external composite** (no attempt to rebuild components).

```jsonl
{"id":"rule_framework_three_drivers_use_as_modules","scope":"process","applies_to":["drivers_three_factor_framework"],"if":"building the IPOS macro stack","then":{"interpretation":"Organize indicators into Liquidity, Sentiment/Positioning, Fundamentals (+ optional Buybacks) modules.","score_adjustment":"n/a","confidence_adjustment":"n/a"},"rationale":"Seminar defines 3 main forces behind market direction (+ buybacks as increasingly important).","failure_modes":["Over-simplification; some indicators belong to multiple modules."],"page_refs":["p15"],"needs_verification":false}
{"id":"rule_liquidity_policy_rate_cut_supports_risk_assets","scope":"module","applies_to":["LIQUIDITY_POLICY"],"if":"central bank cuts policy rate materially vs prior trend","then":{"interpretation":"Easier financial conditions tend to support consumption/investment and risk assets.","score_adjustment":"+10","confidence_adjustment":"+0"},"rationale":"Seminar: standard stimulus via lowering policy rate; banks fund cheaper and pass on conditions.","failure_modes":["Cuts can occur during recession stress; effect can lag or be dominated by credit events."],"page_refs":["p17"],"needs_verification":false}
{"id":"rule_qe_definition_bond_buying_increases_liquidity","scope":"module","applies_to":["LIQUIDITY_POLICY"],"if":"central bank expands balance sheet via large-scale bond purchases (QE)","then":{"interpretation":"Liquidity impulse increases; treat as risk-on tailwind.","score_adjustment":"+15","confidence_adjustment":"+5"},"rationale":"Seminar: QE increases money supply by buying government bonds from banks/large investors.","failure_modes":["Transmission can be weaker under broken credit channels; QT expectations can offset."],"page_refs":["p17"],"needs_verification":false}
{"id":"rule_use_fed_walcl_as_qe_proxy","scope":"indicator","applies_to":["liquidity_fed_balance_sheet_total_assets_walcl"],"if":"WALCL is rising persistently vs recent months","then":{"interpretation":"Liquidity tailwind; treat as supportive for risk assets.","score_adjustment":"+10","confidence_adjustment":"+5"},"rationale":"Seminar directly links Fed balance sheet series WALCL as the QE/QT proxy.","failure_modes":["Other liquidity drivers (fiscal, foreign CBs) can dominate; asset prices can front-run changes."],"page_refs":["p18"],"needs_verification":false}
{"id":"rule_qe_supports_equities_but_volatility_can_increase","scope":"process","applies_to":["LIQUIDITY_POLICY","equity_sp500_index"],"if":"QE phase is active","then":{"interpretation":"Equity trend support is common, but price swings/volatility may rise; avoid overconfidence.","score_adjustment":"+5","confidence_adjustment":"-5"},"rationale":"Seminar slide: QE programs push prices up; fluctuations get larger; QE/QT phases shorten.","failure_modes":["Regime-dependent; volatility can compress under strong forward guidance."],"page_refs":["p19"],"needs_verification":false}
{"id":"rule_fiscal_can_replace_qe_as_market_support","scope":"process","applies_to":["LIQUIDITY_POLICY","equity_sp500_index"],"if":"fiscal support is dominant (state support) even without QE","then":{"interpretation":"Do not rely solely on QE proxy; treat market support as possibly coming from fiscal impulse.","score_adjustment":"+0","confidence_adjustment":"+0"},"rationale":"Seminar: 2020 the state 'took over'; market rose without QE.","failure_modes":["Fiscal measures vary; hard to quantify without a fiscal proxy."],"page_refs":["p20"],"needs_verification":false}
{"id":"rule_sentiment_sources_surveys_vs_transactions","scope":"process","applies_to":["SENTIMENT_POSITIONING"],"if":"building sentiment module","then":{"interpretation":"Track both survey sentiment (opinions) and transactional sentiment (positioning); extremes matter most.","score_adjustment":"n/a","confidence_adjustment":"n/a"},"rationale":"Seminar distinguishes surveys (AAII, consumer confidence, ISM experts) vs transactions (put/call, COT). Emphasizes extremes fear/greed.","failure_modes":["Survey data can lag; transactional data can be noisy or structurally shifting."],"page_refs":["p22"],"needs_verification":false}
{"id":"rule_focus_on_extremes_fear_greed","scope":"indicator","applies_to":["sentiment_cnn_fear_greed_index"],"if":"Fear & Greed is not at an extreme","then":{"interpretation":"Mid-range values are less actionable; prioritize only extreme fear/greed states.","score_adjustment":"0","confidence_adjustment":"0"},"rationale":"Seminar note: only extreme values are interesting.","failure_modes":["Ignoring mid-range can miss transitions; extremes can persist."],"page_refs":["p35"],"needs_verification":false}
{"id":"rule_fear_greed_contrarian_at_extremes","scope":"indicator","applies_to":["sentiment_cnn_fear_greed_index"],"if":"Fear & Greed indicates extreme fear (near 0)","then":{"interpretation":"Contrarian bullish bias (market lows easier than tops).","score_adjustment":"+15","confidence_adjustment":"+5"},"rationale":"Seminar: markets can stay bullish long; lows tend to be easier; extremes are the actionable zone.","failure_modes":["Catching falling knives; macro shocks can keep fear elevated."],"page_refs":["p35"],"needs_verification":false}
{"id":"rule_fear_greed_extreme_greed_caution","scope":"indicator","applies_to":["sentiment_cnn_fear_greed_index"],"if":"Fear & Greed indicates extreme greed (near 100)","then":{"interpretation":"Increase caution; market tops are hard to time; avoid aggressive risk increases.","score_adjustment":"-10","confidence_adjustment":"-5"},"rationale":"Seminar: tops are difficult; extreme greed is mainly a warning zone.","failure_modes":["Momentum can persist; early de-risking can cause opportunity cost."],"page_refs":["p35"],"needs_verification":false}
{"id":"rule_aaii_is_weekly_survey_input_extremes_matter","scope":"indicator","applies_to":["sentiment_aaii_sentiment_survey"],"if":"AAII sentiment is at an extreme (very bullish or very bearish)","then":{"interpretation":"Treat extremes as contrarian information; use percentile-based extreme detection.","score_adjustment":"+/-10","confidence_adjustment":"+0"},"rationale":"Seminar frames sentiment as important mainly at extremes (fear/greed).","failure_modes":["Regime shifts; structural changes in survey participation."],"page_refs":["p22","p23"],"needs_verification":false}
{"id":"rule_consumer_confidence_extremes_contrarian","scope":"indicator","applies_to":["macro_consumer_sentiment_university_of_michigan"],"if":"consumer confidence/sentiment is at an extreme level","then":{"interpretation":"Usually contrarian at extremes (per seminar note).","score_adjustment":"+/-10","confidence_adjustment":"+0"},"rationale":"Seminar explicitly: at extreme values it is mostly a contrarian indicator.","failure_modes":["Extremes can align with real macro turns; beware false contrarian calls in recessions."],"page_refs":["p32"],"needs_verification":false}
{"id":"rule_put_call_high_bearish_positioning_buy_signal","scope":"indicator","applies_to":["sentiment_cboe_put_call_ratio_pcratcbo"],"if":"put/call ratio is high (market participants bearish)","then":{"interpretation":"Contrarian buy signal bias.","score_adjustment":"+15","confidence_adjustment":"+5"},"rationale":"Seminar: high put/call means bearish sentiment → buy signal.","failure_modes":["Fear can persist; options market structure can change; use with confirmation."],"page_refs":["p36"],"needs_verification":false}
{"id":"rule_put_call_threshold_1_1_signal_value","scope":"indicator","applies_to":["sentiment_cboe_put_call_ratio_pcratcbo"],"if":"put/call ratio > 1.1","then":{"interpretation":"Noted as a good signal value (strong fear).","score_adjustment":"+20","confidence_adjustment":"+5"},"rationale":"Seminar gives explicit threshold: >1.1 is a good signal value.","failure_modes":["Spikes during crises; can overshoot; timing uncertain."],"page_refs":["p37"],"needs_verification":false}
{"id":"rule_positioning_cot_use_extremes","scope":"indicator","applies_to":["positioning_cftc_commitments_of_traders_net_positions"],"if":"COT net positioning is at an extreme relative to history","then":{"interpretation":"Crowding signal; treat as potential reversal risk or contrarian indicator depending on asset.","score_adjustment":"+/-10","confidence_adjustment":"+0"},"rationale":"Seminar lists COT under transactional sentiment; extremes are key in sentiment work.","failure_modes":["Trend-following positioning can stay extreme; requires asset-specific interpretation."],"page_refs":["p22"],"needs_verification":true}
{"id":"rule_ism_is_reliable_leading_indicator","scope":"process","applies_to":["macro_ism_manufacturing_pmi_headline"],"if":"selecting macro leading indicators","then":{"interpretation":"Use ISM/PMI as one of the most reliable early indicators for US activity.","score_adjustment":"n/a","confidence_adjustment":"+0"},"rationale":"Seminar: ISM/PMI is among the most important and reliable leading indicators.","failure_modes":["Survey noise; sector composition changes; global vs US mismatch."],"page_refs":["p39"],"needs_verification":false}
{"id":"rule_ism_above_50_expansion","scope":"indicator","applies_to":["macro_ism_manufacturing_pmi_headline"],"if":"ISM > 50","then":{"interpretation":"Rising/economic expansion regime; supportive for equities.","score_adjustment":"+15","confidence_adjustment":"+5"},"rationale":"Seminar explicitly: ISM above 50 implies rising activity.","failure_modes":["Expansion can coexist with tightening; inflation shocks can still hurt risk assets."],"page_refs":["p39","p40"],"needs_verification":false}
{"id":"rule_ism_below_50_downside_risk","scope":"indicator","applies_to":["macro_ism_manufacturing_pmi_headline"],"if":"ISM < 50","then":{"interpretation":"Contraction risk; often at the start of larger US index drawdowns.","score_adjustment":"-20","confidence_adjustment":"+5"},"rationale":"Seminar: below 50 often at the beginning of a larger downward move in US indices.","failure_modes":["False dips; policy easing can offset; equity can bottom before ISM recovers."],"page_refs":["p39"],"needs_verification":false}
{"id":"rule_prefer_manufacturing_over_services_for_signal_quality","scope":"process","applies_to":["MACRO_GROWTH"],"if":"comparing PMI/ISM services vs manufacturing for cycle signal","then":{"interpretation":"Manufacturing is the better indicator; services often stays positive and is less informative.","score_adjustment":"n/a","confidence_adjustment":"n/a"},"rationale":"Seminar note: services is almost always positive; manufacturing is a better indicator.","failure_modes":["Service-led recessions exist; economy increasingly service-heavy."],"page_refs":["p40"],"needs_verification":false}
{"id":"rule_buybacks_when_cash_no_better_use","scope":"process","applies_to":["EQUITY_FLOWS_BUYBACKS"],"if":"corporates increase buybacks materially","then":{"interpretation":"Can indicate excess cash and preference for shareholder returns; treat as equity demand tailwind but not pure growth signal.","score_adjustment":"+5","confidence_adjustment":"0"},"rationale":"Seminar: buybacks happen when firm does not invest in M&A/R&D/dividends and avoids holding high cash.","failure_modes":["Can signal lack of growth opportunities; can be financially engineered."],"page_refs":["p43"],"needs_verification":false}
{"id":"rule_buybacks_reduce_float_boost_eps","scope":"process","applies_to":["EQUITY_FLOWS_BUYBACKS"],"if":"buybacks reduce shares outstanding","then":{"interpretation":"Float reduction can support price; EPS mechanically improves; treat as supportive but distinguish from fundamental earnings growth.","score_adjustment":"+5","confidence_adjustment":"0"},"rationale":"Seminar lists effects: fewer shares, higher intrinsic value per share, EPS improves.","failure_modes":["EPS boost can mask weak operating earnings; leverage-funded buybacks increase risk."],"page_refs":["p44"],"needs_verification":false}
{"id":"rule_exec_incentives_bias_toward_buybacks","scope":"process","applies_to":["EQUITY_FLOWS_BUYBACKS"],"if":"buybacks are high while capex/rnd weak","then":{"interpretation":"Possible incentive-driven financial engineering; reduce confidence in bullish interpretation.","score_adjustment":"0","confidence_adjustment":"-10"},"rationale":"Seminar: US execs often paid in options; rising stock price helps them; dividends don’t help options similarly.","failure_modes":["Some firms genuinely undervalued; buybacks can still be rational."],"page_refs":["p44","p43"],"needs_verification":false}
{"id":"rule_buybacks_flexible_dividends_sticky","scope":"process","applies_to":["EQUITY_FLOWS_BUYBACKS"],"if":"interpreting payout changes","then":{"interpretation":"Buybacks adjust fast (flexible), dividends adjust slowly (sticky). Use buybacks as faster-cycle signal; treat dividend changes as structural.","score_adjustment":"n/a","confidence_adjustment":"n/a"},"rationale":"Seminar: buybacks are flexible; dividends are long-term and not easily changed; highlights sharp drop Q2 2020.","failure_modes":["Buyback blackout periods; regulatory shifts; accounting changes."],"page_refs":["p47"],"needs_verification":false}
{"id":"rule_buybacks_record_year_supportive_but_watch_for_pullback","scope":"process","applies_to":["equity_flows_us_corporate_share_buybacks_total"],"if":"buybacks are at record-high level","then":{"interpretation":"Can be a major bullish backdrop driver, but expectation of pullback is a forward risk to monitor.","score_adjustment":"+5","confidence_adjustment":"-5"},"rationale":"Seminar: 2025 record year; big factor for bullishness; may be reduced; earnings efficiency might need to compensate.","failure_modes":["Forecasting buybacks is hard; could remain high; firm-specific concentration."],"page_refs":["p48","p49"],"needs_verification":true}
{"id":"rule_yield_curve_inversion_recession_warning_10y_2y","scope":"indicator","applies_to":["rates_yield_curve_us_10y_minus_2y_t10y2y"],"if":"10Y-2Y spread < 0","then":{"interpretation":"Recession risk elevated; tighten risk budget.","score_adjustment":"-25","confidence_adjustment":"+10"},"rationale":"Seminar: postwar recessions were announced by inversion of 10Y vs 2Y maturities.","failure_modes":["Long lead time; false signals; special episodes (e.g., Corona) can distort.","page_refs":["p52","p55"],"needs_verification":false}
{"id":"rule_define_flat_and_inverse_curve","scope":"process","applies_to":["RATES_YIELD_CURVE"],"if":"classifying yield curve shape","then":{"interpretation":"Flat = spread near 0; Inverse = spread negative (short yields higher than long).","score_adjustment":"n/a","confidence_adjustment":"n/a"},"rationale":"Seminar defines flat and inverted yield curves explicitly.","failure_modes":["Choice of maturities matters; term premia distort."],"page_refs":["p54"],"needs_verification":false}
{"id":"rule_yield_curve_interpretation_growth_expectations","scope":"process","applies_to":["RATES_YIELD_CURVE"],"if":"curve is steepening meaningfully","then":{"interpretation":"Often consistent with stronger growth/inflation expectations; can be risk-on unless driven by inflation shock.","score_adjustment":"+5","confidence_adjustment":"0"},"rationale":"Seminar: yield curve reflects growth expectations; strong growth often implies inflation and higher long-term premia.","failure_modes":["Steepening from inflation scare can hurt equities; need inflation context."],"page_refs":["p56"],"needs_verification":false}
{"id":"rule_most_reliable_spreads_3m10y_and_2y10y","scope":"process","applies_to":["rates_yield_curve_us_10y_minus_2y_t10y2y","rates_yield_curve_us_10y_minus_3m"],"if":"building recession-risk governor","then":{"interpretation":"Use both 3M–10Y and 2Y–10Y spreads as primary curve signals; treat agreement as higher confidence.","score_adjustment":"n/a","confidence_adjustment":"+5"},"rationale":"Seminar: historically most reliable indicator was 3M–10Y spread, as well as 2Y–10Y.","failure_modes":["Policy distortions; ZLB/QE effects; supply/demand for bills/notes."],"page_refs":["p56"],"needs_verification":false}
{"id":"rule_curve_signal_can_fail_in_special_shocks","scope":"indicator","applies_to":["rates_yield_curve_us_10y_minus_2y_t10y2y"],"if":"macro environment includes special shock/policy distortion (e.g., pandemic episode)","then":{"interpretation":"Reduce reliance/confidence in curve signal; require confirmation from other modules.","score_adjustment":"0","confidence_adjustment":"-15"},"rationale":"Seminar notes Corona special effect: signal did not work for 10Y-2Y at that time.","failure_modes":["Over-discounting genuine signals; hard to define 'special shock' precisely."],"page_refs":["p55"],"needs_verification":false}


## NORMALIZE_MERGE (Autonomous) — merge/prune plan + module candidates
**Goal:** Apply your efficiency directive: keep only high-impact MVP signals active now; preserve optional detail for later without deletion.

```json
{
  "merge_map": [],
  "patches": [
    {
      "target": "indicator",
      "id": "sentiment_cnn_fear_greed_component_market_momentum",
      "set": {
        "is_active": false,
        "mvp_priority": "defer",
        "notes": [
          "Do NOT rebuild Fear & Greed components internally. Keep only the external composite index."
        ]
      }
    },
    {
      "target": "indicator",
      "id": "sentiment_cnn_fear_greed_component_stock_price_strength",
      "set": {
        "is_active": false,
        "mvp_priority": "defer",
        "notes": [
          "Do NOT rebuild Fear & Greed components internally. Keep only the external composite index."
        ]
      }
    },
    {
      "target": "indicator",
      "id": "sentiment_cnn_fear_greed_component_stock_price_breadth",
      "set": {
        "is_active": false,
        "mvp_priority": "defer",
        "notes": [
          "Do NOT rebuild Fear & Greed components internally. Keep only the external composite index."
        ]
      }
    },
    {
      "target": "indicator",
      "id": "macro_ism_new_orders",
      "set": {
        "is_active": false,
        "mvp_priority": "defer",
        "notes": [
          "Keep ISM headline as MVP. Subcomponents are optional for later contradictions/early-warning refinement."
        ]
      }
    },
    {
      "target": "indicator",
      "id": "macro_ism_production",
      "set": {
        "is_active": false,
        "mvp_priority": "defer",
        "notes": [
          "Defer to phase 2. Use only if you want deeper macro decomposition."
        ]
      }
    },
    {
      "target": "indicator",
      "id": "macro_ism_employment",
      "set": {
        "is_active": false,
        "mvp_priority": "defer",
        "notes": [
          "Defer. Add later if labor regime becomes a core module."
        ]
      }
    },
    {
      "target": "indicator",
      "id": "macro_ism_supplier_deliveries",
      "set": {
        "is_active": false,
        "mvp_priority": "defer",
        "notes": [
          "Interpretation is ambiguous (demand vs supply constraints). Defer for MVP."
        ]
      }
    },
    {
      "target": "indicator",
      "id": "macro_ism_inventories",
      "set": {
        "is_active": false,
        "mvp_priority": "defer",
        "notes": [
          "Defer. Use later for contradictions with orders/production."
        ]
      }
    },
    {
      "target": "indicator",
      "id": "drivers_three_factor_framework",
      "set": {
        "is_timeseries": false,
        "is_active": true,
        "mvp_priority": "core",
        "notes": [
          "Framework node (module structure), not a market data series. Keep as process anchor."
        ]
      }
    },
    {
      "target": "indicator",
      "id": "equity_sp500_index",
      "set": {
        "is_scored": false,
        "is_context_series": true,
        "mvp_priority": "core",
        "notes": [
          "Context/overlay series for charts and regime trail validation; do not treat as a macro indicator score."
        ]
      }
    },
    {
      "target": "indicator",
      "id": "positioning_cftc_commitments_of_traders_net_positions",
      "set": {
        "indicator_family": true,
        "mvp_priority": "defer",
        "notes": [
          "Implement later as a family by asset (USD, EUR, Gold, Oil, Equity index futures). Too broad for MVP unless you pick 1–2 assets."
        ]
      }
    },
    {
      "target": "indicator",
      "id": "equity_flows_us_corporate_share_buybacks_total",
      "set": {
        "mvp_priority": "defer",
        "notes": [
          "High conceptual value but data sourcing is ambiguous in the PDF extract. Defer until a clean external series is selected."
        ]
      }
    },
    {
      "target": "indicator",
      "id": "equity_flows_us_buybacks_plus_dividends",
      "set": {
        "mvp_priority": "defer",
        "notes": [
          "Defer until a robust source is selected."
        ]
      }
    },
    {
      "target": "indicator",
      "id": "equity_flows_buybacks_vs_earnings_proxy",
      "set": {
        "mvp_priority": "defer",
        "notes": [
          "Defer; requires consistent earnings series + buybacks series definition."
        ]
      }
    },
    {
      "target": "indicator",
      "id": "rates_yield_curve_us_10y_minus_3m",
      "set": {
        "mvp_priority": "core",
        "notes": [
          "Keep alongside 10Y–2Y as confirmation/contradiction pair. Treat agreement as higher confidence."
        ]
      }
    }
  ],
  "new_module_candidates": [
    {
      "module_id": "DRIVERS_3FACTOR",
      "why": "Top-level structure: Liquidity / Sentiment / Fundamentals (+ optional Buybacks).",
      "indicators": ["drivers_three_factor_framework"]
    },
    {
      "module_id": "LIQUIDITY_POLICY",
      "why": "Single high-leverage proxy + clear rules for easing/tightening impulse.",
      "indicators": ["liquidity_fed_balance_sheet_total_assets_walcl"]
    },
    {
      "module_id": "SENTIMENT_POSITIONING",
      "why": "High impact for timing/risk budget via contrarian extremes; minimal set is sufficient for MVP.",
      "indicators": [
        "sentiment_aaii_sentiment_survey",
        "sentiment_naaim_exposure_index",
        "sentiment_cnn_fear_greed_index",
        "sentiment_cboe_put_call_ratio_pcratcbo"
      ]
    },
    {
      "module_id": "MACRO_GROWTH",
      "why": "Single robust cycle indicator with explicit threshold logic (50).",
      "indicators": ["macro_ism_manufacturing_pmi_headline"]
    },
    {
      "module_id": "RATES_YIELD_CURVE",
      "why": "Primary recession-risk governor for risk budget; strong interpretability.",
      "indicators": [
        "rates_yield_curve_us_10y_minus_2y_t10y2y",
        "rates_yield_curve_us_10y_minus_3m"
      ]
    },
    {
      "module_id": "MARKET_CONTEXT",
      "why": "Chart overlays + sanity checks (not scored).",
      "indicators": ["equity_sp500_index"]
    }
  ]
}

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

---
module_id: MARKET_CONDITIONS
scope: module
tags: [regime, trend, volatility, execution, risk_budget]
version: 0.1
source: seminar_pdf
cadence: weekly
---

## Purpose
Classify the market into **CHOPPY / TRENDY / MOMENTUM** and translate that into **risk posture + position sizing + entry style + stop policy**. This module is a *governor* for the whole IPOS.

## Inputs (minimal)
- **Market price series (context)**: e.g., `equity_sp500_index` (or your chosen benchmark per asset bucket)
- **Derived features (computed weekly)**:
  - `overlap_index` (how often weekly ranges overlap)
  - `retracement_ratio` (pullback size / prior impulse size)
  - `atr_weekly` and `atr_change_rate` (ATR level + acceleration)
  - `swing_structure` (HH/HL vs LH/LL counts; pivot-based)

## Outputs (stored weekly)
- `regime_label` ∈ {CHOPPY, TRENDY, MOMENTUM}
- `regime_confidence` ∈ [0,100]
- `risk_scaler` (multiplier applied to risk budget + stance magnitude)
- `policy_selectors`: {position_size, entry_style, trailing_stop, initial_stop}

---

## Core Definitions (from seminar)
### CHOPPY
- Sideways / range-like (or weak trend)
- Many **false breakouts**
- High overlap of highs/lows
- Retracements often **80–100%** of the prior move

### TRENDY
- Clear direction
- Uptrend: higher highs + higher lows (HH/HL)
- Downtrend: lower highs + lower lows (LH/LL)
- Few overlaps of highs/lows

### MOMENTUM
- Very high dynamics
- **ATR rises quickly**
- No overlap of highs/lows
- Can run with or against the prevailing trend (treat as “fast conditions”)

---

## Classification Rules (simple, efficient)
Use these as a first MVP classifier (tune later):

1) **Uncertain → Defensive (priority rule)**
- If: regime_confidence is low / signals mixed / swings not established
- Then: label = `UNCERTAIN` (internally) → act like CHOPPY for risk

2) **CHOPPY signature**
- If: `retracement_ratio ∈ [0.8, 1.0]` AND `overlap_index` high
- Then: regime_label = CHOPPY

3) **MOMENTUM signature**
- If: `atr_change_rate` high AND `overlap_index` very low
- Then: regime_label = MOMENTUM

4) **TRENDY signature**
- If: `swing_structure` indicates HH/HL (or LH/LL) AND overlap low
- Then: regime_label = TRENDY

### Trend Structure Minimum (for confidence)
- A trend exists after **3 consecutive moves** produce visible swing highs/lows.
- Uptrend formed with **≥1 higher low and ≥2 higher highs**.
- Downtrend formed with **≥1 lower high and ≥2 lower lows**.

---

## Regime → Portfolio Policies (direct seminar mapping)
### Position sizing
- CHOPPY: **small**
- TRENDY: **large**
- MOMENTUM: **medium**
- If unsure: **defensive + small** (cap risk)

**Recommended risk_scaler (MVP default)**
- CHOPPY: `0.50x`
- TRENDY: `1.00x`
- MOMENTUM: `0.75x`
- UNCERTAIN: `0.40x`

### Entry style
- CHOPPY: **penalize breakouts** (don’t rely on them)
- TRENDY: **retracements + breakouts** both allowed (prefer confirmation)
- MOMENTUM: **anticipate continuation**; do not expect big retracements

### Trailing stops (policy selector, not numbers)
- CHOPPY: none / defensive (quick exit mindset)
- TRENDY: relative highs/lows (swing-based trailing)
- MOMENTUM: Supertrend-like (volatility-aware trailing)

### Initial stops
- CHOPPY: far away (translate as wider volatility buffer in implementation)
- TRENDY: last swing low/high
- MOMENTUM: **1–2 ATR** (explicit)

---

## Confidence Heuristic (0–100)
Start at 50, then adjust:
- +15 if swing structure satisfies “trend exists” criteria (≥3 swings)
- +10 if overlap + retracement agree strongly with a regime
- +10 if ATR acceleration cleanly signals momentum
- -20 if signals conflict (e.g., overlap high but ATR accelerating)
- -25 if “uncertain / cannot assess” condition is met

If `regime_confidence < 40`: enforce **UNCERTAIN → defensive cap**.

---

## Contradictions to Watch (trigger investigation)
- **TRENDY label but retracement_ratio ~ 0.9** → trend may be illusory; likely CHOPPY.
- **MOMENTUM label while overlap remains high** → volatility spike inside range; reduce confidence.
- **Regime = UNCERTAIN** but other modules scream risk-on/off → flag “process risk”: environment unclear, so cap risk budget anyway.

---

## Implementation Notes (IPOS-friendly)
- Compute all regime features weekly from daily bars (or weekly OHLC if you have it).
- Store `policy_selectors` in the weekly snapshot so your report can explain *why* risk changed.
- Keep this module “light”: it’s a governor, not a full technical system.

---

## NEXT ACTION (say “continue”)
**Stage:** DOC_MAP  
**Pages:** 81–110 (autonomous)  
**Focus:** Trend sizes (primary/secondary/tertiary), sideways phases, trend-break definitions, and any additional regime rules that strengthen the Regime Map + trail.

## DOC_MAP (Autonomous) — Seminar PDF → IPOS Extraction Queue (Refined Process)
**PDF:** `/mnt/data/onvista Aktien-Intensiv-Seminar 11-2025.pdf`  
**Chunk analyzed:** pages **81–110** (1-based)  
**Composite policy:** external composites only (no rebuilding)  
**ROI focus:** high-impact weekly governance rules (regime/trend/risk)

```json
{
  "chunk": {
    "pages": "81-110",
    "density": "high",
    "topics": [
      "Trend hierarchy",
      "Sideways phases",
      "Trend break",
      "Trend resumption vs reversal",
      "Trend trading workflow",
      "Multi-timescale alignment",
      "Early trend entry criteria",
      "Correction patterns",
      "Risk/reward discipline"
    ],
    "subtopics": [
      "Primary/Secondary/Tertiary trend sizes and their roles",
      "Sideways phases inside trends (correction vs weakness)",
      "Trend break definition (uptrend low broken / downtrend high broken)",
      "After trend break: trendless phase; possible counter-trend or old-trend resumption",
      "Fundamental change tends to drive real reversals vs short-term noise resuming old trend",
      "Trend traders enter on confirmations; protect at trend-break levels",
      "Trend-size alignment: when multiple trend sizes point same direction → high profitability potential",
      "Corrections in larger trend start with break of the directly lower trend",
      "Trend resumption begins with break of the correction trend (lower timeframe)",
      "Early trend trading requires a minimum 'trend combination' structure",
      "Correction/continuation formations: breakout types + classification (continuation vs reversal)",
      "Minimum risk/reward: should not be below 1.3:1"
    ]
  },
  "extract_targets": {
    "indicator_pages": [],
    "rules_pages": [
      "82-85",
      "87-88",
      "90",
      "92-93",
      "98-105",
      "102-105",
      "108"
    ],
    "process_pages": [
      "82-85",
      "87-88",
      "90",
      "92-93",
      "98-105",
      "107-108"
    ],
    "low_value_pages": [
      "81",
      "86",
      "89",
      "91",
      "94-97",
      "99-101",
      "106",
      "109-110"
    ]
  },
  "likely_modules": [
    {
      "module_id": "TREND_HIERARCHY",
      "why": "Primary/Secondary/Tertiary trend roles map directly to signal generation and stop management."
    },
    {
      "module_id": "TREND_BREAKS_TRANSITIONS",
      "why": "Trend break definition + post-break scenarios (trendless → reversal vs resumption) is essential for regime trail + contradiction handling."
    },
    {
      "module_id": "TREND_TRADING_WORKFLOW",
      "why": "Operational rules: confirmations, add-ons, and protecting at trend-break levels."
    },
    {
      "module_id": "MULTI_TIMESCALE_ALIGNMENT",
      "why": "When multiple trend sizes align → higher expected payoff; correction/resumption logic uses lower-timeframe breaks."
    },
    {
      "module_id": "PATTERNS_CONTINUATION_REVERSAL",
      "why": "Continuations vs reversals; breakouts; used for signal validity gating."
    },
    {
      "module_id": "RISK_REWARD_FLOOR",
      "why": "Explicit CRV rule: risk/reward should not be below 1.3:1 (hard risk discipline)."
    }
  ],
  "recommended_next_chunks": [
    {
      "pages": "111-135",
      "why": "Likely transitions into more concrete technical tools/indicators and operational scan logic (feeds indicator registry)."
    }
  ],
  "checkpoint": {
    "pages_done": "81-110",
    "artifacts_written": ["doc_map"],
    "counts": { "chunks_mapped": 3 }
  }
}

## ROI_GATE (Autonomous) — Pages 81–110 (High-ROI Weekly Governance Only)
**PDF:** `/mnt/data/onvista Aktien-Intensiv-Seminar 11-2025.pdf`  
**Chunk:** 81–110 (1-based)  
**What I learned from scanning this chunk:** it’s **mostly process/rules** (trend hierarchy, trend breaks, timescale alignment, CRV floor) — **not new macro time-series indicators**. So we treat it as **Playbook + regime logic**, not registry expansion.

```json
{
  "active_now": [
    {
      "id": "TREND_HIERARCHY_PRIMARY_SECONDARY_TERTIARY",
      "type": "process_rule_set",
      "why": "Directly governs weekly decision workflow: primary sets direction, secondary generates signals, tertiary fine-tunes entries/trailing stops (core for Regime Map + trail).",
      "page_refs": ["p82", "p83", "p84"]
    },
    {
      "id": "TREND_BREAK_DEFINITION_AND_IMPLICATIONS",
      "type": "process_rule_set",
      "why": "Trend break definition + implications (trendless phase, possible countertrend vs resumption) is a cornerstone for contradictions + confidence gating.",
      "page_refs": ["p90", "p92", "p93"]
    },
    {
      "id": "TREND_TRADER_WAIT_FOR_CLARITY_AFTER_BREAK",
      "type": "process_rule",
      "why": "Operational rule for weekly posture: after break, reduce activity until structure reforms (ties to 'uncertain → defensive').",
      "page_refs": ["p92"]
    },
    {
      "id": "MULTI_TIMESCALE_ALIGNMENT_PROFITABILITY",
      "type": "process_rule_set",
      "why": "When multiple trend sizes align, expected payoff improves; use as confidence booster and stance amplifier (high ROI for weekly stance).",
      "page_refs": ["p102"]
    },
    {
      "id": "CORRECTION_AND_RESUMPTION_LOGIC_SUBORDINATE_TREND_BREAKS",
      "type": "process_rule_set",
      "why": "Correction begins with break of the directly lower trend; resumption begins with break of the correction trend (powerful for regime trail and early warnings).",
      "page_refs": ["p103"]
    },
    {
      "id": "EARLY_TREND_TRADE_MINIMUM_TREND_COMBINATION",
      "type": "process_rule_set",
      "why": "Defines when a trend is tradable early: requires a minimum structural combination (reduces false starts).",
      "page_refs": ["p104", "p105"]
    },
    {
      "id": "RISK_REWARD_FLOOR_CRV_1_3",
      "type": "risk_rule",
      "why": "Explicit, simple, high-impact discipline: chance-risk ratio should not be below 1.3:1. Converts directly into a hard gating rule for adding risk.",
      "page_refs": ["p108"]
    }
  ],
  "defer": [
    {
      "id": "PATTERN_CATALOG_CONTINUATION_VS_REVERSAL",
      "type": "reference_material",
      "why": "Useful later for signal library, but too detailed for MVP weekly governance. Keep as optional appendix module.",
      "page_refs": ["p108", "p109"]
    },
    {
      "id": "EXTERNAL_LINKS_PATTERN_ENCYCLOPEDIA",
      "type": "reference_material",
      "why": "Not needed for IPOS mechanics. Keep only as a link note.",
      "page_refs": ["p108"]
    },
    {
      "id": "ANALOGIES_EXPECTANCY_CASINO_LIMITS",
      "type": "storytelling",
      "why": "Conceptually fine but low operational value vs space/tokens. Don’t encode into rules.",
      "page_refs": ["p82", "p85"]
    }
  ],
  "drop": [],
  "notes": [
    "No composite reconstruction tasks triggered in this chunk.",
    "No new time-series indicators needed here; focus stays on regime/trend governance + risk discipline."
  ],
  "checkpoint": {
    "pages_done": "81-110",
    "artifacts_written": ["roi_gate"],
    "counts": { "active_items": 7, "deferred_items": 3, "dropped_items": 0 }
  }
}
## PROCESS_EXTRACT (Autonomous) — `process.jsonl`
**PDF:** `/mnt/data/onvista Aktien-Intensiv-Seminar 11-2025.pdf`  
**Pages:** 81–110 (1-based)  
**ROI_GATE:** active items only  
**Batch cap:** 20 → extracted **10**

```jsonl
{"id":"process_trend_hierarchy_primary_sets_direction","topic":"trend_hierarchy","statement":"Primary trend defines the overall direction and should govern strategic bias; it is not used for frequent timing.","operationalization":["Represent trend hierarchy per market as (primary, secondary, tertiary) trend labels on weekly data.","Use primary trend as a stance prior (tilt direction) and a gating input for risk budget expansion."],"page_refs":["p82","p83"]}
{"id":"process_trend_hierarchy_secondary_generates_signals","topic":"trend_hierarchy","statement":"Secondary trend is used for signal generation within the primary trend direction (timing layer).","operationalization":["Define secondary-trend signals that can trigger adds/hedges (e.g., breakouts/resumptions) only when aligned with primary trend.","Store secondary trend state as a weekly categorical feature and use it to gate tactical signals."],"page_refs":["p82","p83"]}
{"id":"process_trend_hierarchy_tertiary_fine_tunes_entries_stops","topic":"trend_hierarchy","statement":"Tertiary trend is used to fine-tune entries and trailing stops (execution layer).","operationalization":["Use tertiary trend for stop policies (swing-based or ATR-based) and for “entry timing refinement” labels.","Do not overfit tertiary signals in weekly reporting; keep it as execution metadata."],"page_refs":["p82","p83","p84"]}
{"id":"process_trend_break_definition_uptrend_low_breaks_downtrend_high_breaks","topic":"trend_breaks","statement":"Trend break definition: in an uptrend, breaking the last low breaks the uptrend; in a downtrend, breaking the last high breaks the downtrend.","operationalization":["Implement trend-break flags based on swing points (last swing low/high).","When a trend-break flag triggers, downgrade trend confidence and force regime reassessment (often TRENDY→UNCERTAIN/CHOPPY)."],"page_refs":["p90","p92"]}
{"id":"process_after_trend_break_trendless_phase_then_resumption_or_countertrend","topic":"trend_breaks","statement":"After a trend break, the market enters a trendless phase; next can be a countertrend move, sideways phase, or resumption of the old trend.","operationalization":["Create a post-break state machine: BREAK → TRENDLESS → {RESUME_OLD, COUNTERTREND, RANGE}.","In weekly workflow, treat TRENDLESS as low-confidence: cap risk budget and reduce stance amplitude."],"page_refs":["p92","p93"]}
{"id":"process_trend_trader_wait_after_break_until_structure_reforms","topic":"workflow","statement":"After a trend break, trend traders should generally wait for clarity/structure to reform rather than forcing trades.","operationalization":["Add operational gate: if state=TRENDLESS then reduce new risk adds; only allow small exploratory positions if other modules strongly agree.","Log a contradiction trigger: 'trendless + strong risk-on signals' requiring review."],"page_refs":["p92"]}
{"id":"process_multi_timescale_alignment_increases_profitability","topic":"multi_timescale_alignment","statement":"When multiple trend sizes (primary/secondary/tertiary) point in the same direction, profitability potential is high.","operationalization":["Compute alignment_score = count(aligned directions) / 3.","Map alignment_score to confidence bonus and stance multiplier (bounded).","Use alignment as a positive confirmation for adding risk in TRENDY conditions."],"page_refs":["p102"]}
{"id":"process_correction_begins_with_break_of_lower_trend","topic":"correction_resumption","statement":"A correction in a larger trend typically begins with the break of the directly lower trend size.","operationalization":["Detect correction onset by tertiary trend break while primary remains intact.","Flag 'correction_phase' to reduce aggressiveness but not flip stance unless primary breaks."],"page_refs":["p103"]}
{"id":"process_resumption_begins_with_break_of_correction_trend","topic":"correction_resumption","statement":"Trend resumption begins with the break of the correction trend (lower timeframe), signaling a potential continuation in the larger trend direction.","operationalization":["Implement a resumption trigger: if correction_phase=true and correction_trend_breaks in primary direction => RESUME signal.","Use as a high-ROI tactical add trigger when other modules agree."],"page_refs":["p103"]}
{"id":"process_risk_reward_floor_min_1_3","topic":"risk_management","statement":"Minimum chance-risk ratio (CRV) rule: risk/reward should not be below 1.3:1.","operationalization":["Add a gating rule: if expected_reward / risk < 1.3 then do not take/scale the trade (or reduce size).","In weekly IPOS context, use this as a universal 'do not add risk' constraint when implementing tactical adds."],"page_refs":["p108"]}

## RULE_EXTRACT (Autonomous) — `rules.jsonl`
**PDF:** `/mnt/data/onvista Aktien-Intensiv-Seminar 11-2025.pdf`  
**Pages:** 81–110 (1-based)  
**ROI_GATE:** active items only  
**Batch cap:** 40 → extracted **16** (high-impact, weekly-governance)

```jsonl
{"id":"rule_primary_trend_sets_strategic_bias","scope":"process","applies_to":["TREND_HIERARCHY"],"if":"primary trend direction is UP (or DOWN)","then":{"interpretation":"Use primary trend as the strategic stance prior; avoid frequent flips against it.","score_adjustment":"+0","confidence_adjustment":"+5"},"rationale":"Primary trend defines overall direction; governs bias rather than timing.","failure_modes":["Major regime shifts can invalidate; require break/transition logic."],"page_refs":["p82","p83"],"needs_verification":false}
{"id":"rule_secondary_trend_is_signal_layer","scope":"process","applies_to":["TREND_HIERARCHY"],"if":"generating tactical actions within primary trend","then":{"interpretation":"Use secondary trend for timing signals; prioritize signals aligned with primary trend.","score_adjustment":"+0","confidence_adjustment":"+0"},"rationale":"Secondary trend is used for signal generation within the primary trend direction.","failure_modes":["If primary is unclear, secondary signals become noisy."],"page_refs":["p82","p83"],"needs_verification":false}
{"id":"rule_tertiary_trend_is_execution_layer","scope":"process","applies_to":["TREND_HIERARCHY"],"if":"executing entries / managing trailing stops","then":{"interpretation":"Use tertiary trend to fine-tune entries and stops; do not let it override primary bias.","score_adjustment":"+0","confidence_adjustment":"+0"},"rationale":"Tertiary trend is execution layer (entry refinement + trailing stops).","failure_modes":["Overfitting micro swings; should be lightweight in weekly OS."],"page_refs":["p82","p83","p84"],"needs_verification":false}
{"id":"rule_trend_break_uptrend_break_last_low","scope":"module","applies_to":["TREND_BREAKS_TRANSITIONS"],"if":"in an uptrend AND price breaks the last swing low","then":{"interpretation":"Uptrend is broken; downgrade trend confidence; transition to TRENDLESS/UNCERTAIN until structure reforms.","score_adjustment":"-10","confidence_adjustment":"-15"},"rationale":"Trend break definition for uptrend: breaking the last low breaks the uptrend.","failure_modes":["False breaks; swing detection sensitivity; consider weekly close confirmation."],"page_refs":["p90","p92"],"needs_verification":false}
{"id":"rule_trend_break_downtrend_break_last_high","scope":"module","applies_to":["TREND_BREAKS_TRANSITIONS"],"if":"in a downtrend AND price breaks the last swing high","then":{"interpretation":"Downtrend is broken; downgrade trend confidence; transition to TRENDLESS/UNCERTAIN until structure reforms.","score_adjustment":"+10","confidence_adjustment":"-15"},"rationale":"Trend break definition for downtrend: breaking the last high breaks the downtrend.","failure_modes":["Bear market rallies; confirmation criteria needed."],"page_refs":["p90","p92"],"needs_verification":false}
{"id":"rule_post_break_enter_trendless_state","scope":"process","applies_to":["TREND_BREAKS_TRANSITIONS"],"if":"a trend break has occurred","then":{"interpretation":"Assume trendless phase first; next can be countertrend, sideways, or resumption of old trend.","score_adjustment":"n/a","confidence_adjustment":"-10"},"rationale":"After trend break, market enters trendless phase; multiple next scenarios possible.","failure_modes":["Fast V-reversals can skip prolonged trendless phase."],"page_refs":["p92","p93"],"needs_verification":false}
{"id":"rule_after_break_wait_for_structure","scope":"portfolio","applies_to":["TREND_BREAKS_TRANSITIONS","MARKET_CONDITIONS"],"if":"state is TRENDLESS / structure unclear after break","then":{"interpretation":"Wait for clarity; reduce new risk adds; keep positions small/defensive.","score_adjustment":"-10","confidence_adjustment":"-10"},"rationale":"Trend traders typically wait after breaks until structure reforms.","failure_modes":["Can miss early re-entry; allow small exploratory positions with strong confirmation."],"page_refs":["p92"],"needs_verification":false}
{"id":"rule_multi_timescale_alignment_boosts_confidence","scope":"module","applies_to":["MULTI_TIMESCALE_ALIGNMENT"],"if":"primary, secondary, tertiary trends point in same direction","then":{"interpretation":"High expected payoff environment; allow stronger stance (bounded) and higher confidence.","score_adjustment":"+5","confidence_adjustment":"+15"},"rationale":"When multiple trend sizes align, profitability potential is high.","failure_modes":["Late-stage alignment can occur near exhaustion; combine with MARKET_CONDITIONS (avoid CHOPPY)."],"page_refs":["p102"],"needs_verification":false}
{"id":"rule_misalignment_reduces_confidence","scope":"module","applies_to":["MULTI_TIMESCALE_ALIGNMENT"],"if":"trend sizes disagree materially (e.g., primary up, secondary down)","then":{"interpretation":"Lower conviction; reduce stance magnitude and/or cap risk budget until alignment improves.","score_adjustment":"-5","confidence_adjustment":"-15"},"rationale":"Implicit inverse of alignment rule; disagreement implies transition/correction noise.","failure_modes":["Countertrend opportunities exist; keep as ‘reduce’ not ‘ban’."],"page_refs":["p102"],"needs_verification":true}
{"id":"rule_correction_starts_with_lower_trend_break","scope":"module","applies_to":["CORRECTION_RESUMPTION_LOGIC"],"if":"primary trend intact AND directly lower trend breaks against it","then":{"interpretation":"Treat as correction inside larger trend; reduce aggressiveness but do not flip strategic bias.","score_adjustment":"-5","confidence_adjustment":"-5"},"rationale":"Corrections in larger trend typically begin with break of directly lower trend size.","failure_modes":["Lower-trend break can sometimes be the start of a full reversal; watch for primary break."],"page_refs":["p103"],"needs_verification":false}
{"id":"rule_resumption_starts_with_break_of_correction_trend","scope":"module","applies_to":["CORRECTION_RESUMPTION_LOGIC"],"if":"in correction_phase AND correction-trend breaks back in primary direction","then":{"interpretation":"Trend resumption signal; allow tactical add if other modules confirm.","score_adjustment":"+5","confidence_adjustment":"+10"},"rationale":"Trend resumption begins with break of the correction trend (lower timeframe).","failure_modes":["Fake resumption in choppy regimes; require MARKET_CONDITIONS not CHOPPY."],"page_refs":["p103"],"needs_verification":false}
{"id":"rule_early_trend_trade_requires_minimum_structure","scope":"process","applies_to":["TREND_TRADING_WORKFLOW"],"if":"attempting early trend entry","then":{"interpretation":"Only trade early when minimum trend-combination/structure exists; otherwise treat as low-quality setup.","score_adjustment":"n/a","confidence_adjustment":"-10"},"rationale":"Seminar: early trend trading requires a minimum ‘trend combination’ structure.","failure_modes":["Structure criteria need explicit definition in your implementation (pivot rules)."],"page_refs":["p104","p105"],"needs_verification":false}
{"id":"rule_risk_reward_floor_crv_1_3","scope":"portfolio","applies_to":["RISK_REWARD_FLOOR"],"if":"expected_reward / risk < 1.3","then":{"interpretation":"Do not take/scale the trade; reduce size or skip.","score_adjustment":"n/a","confidence_adjustment":"n/a"},"rationale":"Seminar: chance-risk ratio should not be below 1.3:1.","failure_modes":["Estimating reward/risk is noisy; use conservative estimates."],"page_refs":["p108"],"needs_verification":false}
{"id":"rule_crv_gate_applies_to_adds_not_just_entries","scope":"portfolio","applies_to":["RISK_REWARD_FLOOR"],"if":"considering adding risk (position add, leverage, risk budget increase)","then":{"interpretation":"Apply CRV≥1.3 gate to adds as well; avoid compounding poor payoff setups.","score_adjustment":"n/a","confidence_adjustment":"n/a"},"rationale":"Operational extension of the CRV floor to weekly OS decisioning.","failure_modes":["Can be too restrictive; allow overrides only with explicit logging."],"page_refs":["p108"],"needs_verification":true}
{"id":"rule_contradiction_trendless_but_other_modules_strong","scope":"portfolio","applies_to":["TREND_BREAKS_TRANSITIONS","MARKET_CONDITIONS"],"if":"state is TRENDLESS/UNCERTAIN AND other modules strongly risk-on or risk-off","then":{"interpretation":"Flag contradiction: environment unclear; cap risk budget and request investigation.","score_adjustment":"0","confidence_adjustment":"-10"},"rationale":"Waiting/defensive rule after break conflicts with strong macro/sentiment signals; needs review.","failure_modes":["Sometimes macro leads price; may justify small probe positions."],"page_refs":["p92","p59"],"needs_verification":true}

---
module_id: TREND_BREAKS_TRANSITIONS
scope: module
tags: [trend, regime, transitions, confidence, risk_rules]
version: 0.1
source: seminar_pdf
cadence: weekly
---

## Purpose
Turn trend **breaks** and **timescale alignment** into a weekly governance layer:
- when to **cap risk** (trendless/uncertain),
- when to **add** (resumption + alignment),
- how to avoid false regime switches,
- enforce a **CRV floor** for any risk adds.

## Inputs (weekly)
- Swing points: `last_swing_low`, `last_swing_high` (pivot-based)
- Trend hierarchy labels (per market): `primary_trend_dir`, `secondary_trend_dir`, `tertiary_trend_dir`
- Derived flags:
  - `trend_break_flag`
  - `trendless_flag`
  - `correction_phase_flag`
  - `alignment_score` (0–3 aligned)

## Outputs (weekly)
- `transition_state` ∈ {STABLE_TREND, CORRECTION, BREAK, TRENDLESS, RESUME_OLD, COUNTERTREND, RANGE}
- `transition_confidence` ∈ [0,100]
- Governance actions:
  - `risk_cap_active` (bool)
  - `add_risk_allowed` (bool)
  - `contradiction_flags` (list)

---

## Trend Hierarchy Roles (short)
- **Primary trend**: strategic bias (stance prior)
- **Secondary trend**: timing signals inside primary
- **Tertiary trend**: execution refinement (entries/stops); should not override primary

---

## Trend Break Definitions (hard rules)
### Uptrend break
- If: in uptrend AND **break the last swing low**
- Then: uptrend is broken → transition to **TRENDLESS**

### Downtrend break
- If: in downtrend AND **break the last swing high**
- Then: downtrend is broken → transition to **TRENDLESS**

**Implementation note:** require weekly close confirmation if you want fewer false breaks.

---

## Post-Break State Machine (weekly governance)
1) **BREAK** (event)
2) **TRENDLESS** (default after break)
3) Next outcomes (don’t force prediction):
   - **RESUME_OLD** (old trend continues)
   - **COUNTERTREND** (new opposite trend develops)
   - **RANGE** (sideways)

### Core operating rule
- In **TRENDLESS / structure unclear**:
  - **Wait for clarity** (reduce activity)
  - **Cap risk budget**
  - Allow only **small probes** if other modules strongly agree

---

## Correction vs Resumption Logic (timescale-based)
### Correction starts (inside larger trend)
- If: **primary trend intact**
- AND: the **directly lower trend breaks against it**
- Then: `correction_phase_flag = true` (reduce aggressiveness, do not flip bias)

### Resumption starts
- If: in correction
- AND: **correction trend breaks back in primary direction**
- Then: **resumption signal** → tactical add is allowed *if* not CHOPPY and other modules confirm

---

## Multi-Timescale Alignment (confidence amplifier)
### Alignment score
- `alignment_score = count(primary==secondary==tertiary direction)`

**Rule**
- If alignment_score = 3:
  - Increase confidence
  - Allow stronger stance (bounded)
- If misaligned:
  - Reduce stance magnitude
  - Prefer “wait / smaller risk” until alignment improves

---

## Hard Risk Rule: CRV Floor (non-negotiable gate)
### CRV ≥ 1.3 for any risk adds
- If expected_reward / risk < **1.3**
- Then: do not enter / do not scale / reduce size or skip

**Apply this to:**
- new positions
- position adds
- leverage increases
- any risk budget expansion based on tactical setups

---

## Contradictions to Watch (trigger investigation)
- **TRENDLESS**, but macro/sentiment modules are strongly risk-on/off  
  → cap risk anyway; investigate why price structure is unclear.
- **Resumption signal**, but MARKET_CONDITIONS = CHOPPY  
  → likely false resumption; reduce confidence.
- High alignment, but yield curve inversion + tightening liquidity  
  → “technical vs macro” contradiction; reduce confidence, demand confirmation.

---

## Dashboard Hooks (what to visualize)
- Regime Map trail: show `transition_state` over time as a ribbon
- Mark BREAK events with vertical lines
- Overlay alignment_score and CRV gate triggers on the timeline

---

## NEXT ACTION (say “continue”)
**Stage:** DOC_MAP  
**Pages:** 111–135 (autonomous)  
**Focus:** Find the first cluster of **concrete technical indicators / scan rules** to add high-ROI indicator candidates (still MVP-efficient).

## DOC_MAP (Autonomous) — Seminar PDF → IPOS Extraction Queue (Patterns → Indicators Transition)
**PDF:** `/mnt/data/onvista Aktien-Intensiv-Seminar 11-2025.pdf`  
**Chunk analyzed:** pages **111–135** (1-based)  
**Reality check:** this chunk is **mostly chart-heavy pattern slides** + a **transition** into “Important indicators”. Text density is low on many pages → use ROI gating before doing any image-based extraction.

```json
{
  "chunk": {
    "pages": "111-135",
    "density": "medium",
    "topics": [
      "Correction patterns",
      "Continuation setups",
      "Retracement levels",
      "Candlestick reversals",
      "Trend change patterns",
      "Head & shoulders",
      "Important indicators (section start)"
    ],
    "subtopics": [
      "Ascending triangle in uptrend (buyers step in earlier; rising lows)",
      "Descending triangle in uptrend (falling highs; no meaningful new lows)",
      "Sideways range in uptrend (time-based correction)",
      "Flag in uptrend (lower-timeframe downtrend; break is buy signal)",
      "Cup-with-handle notes (symmetry, handle in upper third, watch volume)",
      "Contraction patterns (pattern family; likely chart examples)",
      "Retracement levels (chart-only slides; likely numeric levels—requires image pass if activated)",
      "Candlestick reversal concept (reversal bar / hammer / shooting star; chart examples)",
      "Trading at trend change (pattern-driven workflow cues)",
      "Head-and-shoulders (labels: neckline, target, stops; chart examples)",
      "‘Important indicators’ heading appears (list likely starts here; chart/text extraction incomplete)"
    ]
  },
  "extract_targets": {
    "indicator_pages": [
      "135 (section start; likely list continues on 136+)"
    ],
    "rules_pages": [
      "111",
      "114",
      "116",
      "118",
      "120",
      "126",
      "131-133",
      "135"
    ],
    "process_pages": [
      "111",
      "114",
      "116",
      "118",
      "120",
      "126",
      "131-133"
    ],
    "chart_only_pages": [
      "113",
      "115",
      "117",
      "119",
      "121-125",
      "127-130",
      "134-135"
    ],
    "low_value_pages": [
      "112",
      "113",
      "115",
      "117",
      "119",
      "121-125",
      "127-130",
      "134"
    ]
  },
  "likely_modules": [
    {
      "module_id": "PATTERNS_CONTINUATION_CORRECTION",
      "why": "Continuation/correction patterns (triangles, range, flag, cup-with-handle). Likely defer for MVP; can become a reference module later."
    },
    {
      "module_id": "RETRACEMENT_LEVELS",
      "why": "Potentially high ROI if numeric retracement levels are explicitly taught; could feed pullback-depth features and regime logic. Needs image pass if activated."
    },
    {
      "module_id": "CANDLESTICK_REVERSALS",
      "why": "Mostly tactical/shorter-term; likely defer for MVP weekly OS."
    },
    {
      "module_id": "TREND_CHANGE_PATTERNS",
      "why": "Head & shoulders / trend change trading — may be useful as a contradiction trigger, but likely defer for MVP."
    },
    {
      "module_id": "TECHNICAL_INDICATORS_START",
      "why": "‘Important indicators’ section begins here; likely where RSI/MAs/MACD/Stoch/etc start (high ROI for registry)."
    }
  ],
  "recommended_next_chunks": [
    {
      "pages": "136-160",
      "why": "Likely contains the concrete list of ‘Important indicators’ and the first technical indicator definitions (high ROI for the indicator registry)."
    },
    {
      "pages": "161-182",
      "why": "Continuation into scan rules/technical methods; feeds scoring logic and indicator detail pages in the dashboard."
    }
  ],
  "checkpoint": {
    "pages_done": "111-135",
    "artifacts_written": ["doc_map"],
    "counts": { "chunks_mapped": 4 }
  }
}

## ROI_GATE (Autonomous) — Pages 111–135 (Pattern Slides → MVP Efficiency Filter)
**PDF:** `/mnt/data/onvista Aktien-Intensiv-Seminar 11-2025.pdf`  
**Chunk:** 111–135 (1-based)  
**Observation:** This chunk is **mostly pattern examples** with **very limited extractable text** (many chart-only slides). High risk of low ROI for a weekly IPOS MVP.

```json
{
  "active_now": [
    {
      "id": "OBJECTIVE_BREAKOUT_CONFIRMATION_NOT_TRENDLINES",
      "type": "process_rule",
      "why": "High-ROI general lesson for automation: avoid subjective drawn lines; use objective price levels (prior swing/bar high/low) for confirmations. This directly improves robustness of regime/trend/resumption triggers in a weekly system.",
      "page_refs": ["p118"]
    }
  ],
  "defer": [
    {
      "id": "PATTERN_CATALOG_TRIANGLES_RANGES_FLAGS_CUP_HANDLE",
      "type": "reference_material",
      "why": "Useful later as a pattern library, but too tactical/detail-heavy for weekly MVP governance. Keep as optional module later.",
      "page_refs": ["p111-121","p126-134"]
    },
    {
      "id": "RETRACEMENT_LEVEL_SLIDES",
      "type": "chart_only",
      "why": "Text does not contain numeric levels; extracting would require an image pass. MVP already uses retracement_ratio and choppy thresholds from earlier section (80–100%). Defer unless you explicitly want numeric retracement bands now.",
      "page_refs": ["p122-124"]
    },
    {
      "id": "CANDLESTICK_REVERSALS_REVERSAL_BAR_HAMMER_OUTSIDE_REVERSAL",
      "type": "tactical_setup",
      "why": "Mostly shorter-term timing; low incremental value for weekly IPOS relative to regime/trend modules already extracted.",
      "page_refs": ["p126"]
    },
    {
      "id": "HEAD_AND_SHOULDERS_DETAILS",
      "type": "tactical_setup",
      "why": "Classic pattern; operationalization exists but adds noise/complexity for MVP weekly governance. Defer to phase 2.",
      "page_refs": ["p133-134"]
    }
  ],
  "drop": [],
  "notes": [
    "No new time-series indicators are worth adding from 111–135 for MVP.",
    "The 'Important indicators' list starts at p135 but content likely continues on 136+; handle in next chunk.",
    "We avoid image-based extraction unless it unlocks high-impact numeric thresholds you explicitly want."
  ],
  "checkpoint": {
    "pages_done": "111-135",
    "artifacts_written": ["roi_gate"],
    "counts": { "active_items": 1, "deferred_items": 4, "dropped_items": 0 }
  }
}

## PROCESS_EXTRACT (Autonomous) — `process.jsonl`
**PDF:** `/mnt/data/onvista Aktien-Intensiv-Seminar 11-2025.pdf`  
**Pages:** 111–135 (1-based)  
**ROI_GATE:** active items only  
**Batch cap:** 20 → extracted **1**

```jsonl
{"id":"process_use_objective_levels_for_breakout_confirmation","topic":"robust_signal_design","statement":"Prefer objective breakout confirmation levels (e.g., prior swing highs/lows or bar highs/lows) over subjective drawn trendlines.","operationalization":["Implement breakout/resumption triggers using explicit pivot levels from swing detection (last_swing_high/low) rather than discretionary trendline geometry.","In the dashboard, show confirmation levels as horizontal bands/lines derived from stored pivot points.","In the Playbook, define confirmations in terms of 'weekly close above/below pivot' to reduce noise and ambiguity."],"page_refs":["p118"]}

## DOC_MAP (Autonomous) — Seminar PDF → IPOS Extraction Queue (Technical Indicators Core)
**PDF:** `/mnt/data/onvista Aktien-Intensiv-Seminar 11-2025.pdf`  
**Chunk analyzed:** pages **136–160** (1-based)  
**ROI focus:** extract only **high-impact, operational** indicators/rules for weekly IPOS

```json
{
  "chunk": {
    "pages": "136-160",
    "density": "high",
    "topics": [
      "Volume confirmation",
      "Moving averages",
      "Slow Stochastic",
      "RSI",
      "Proprietary trend indicator",
      "Technical vs fundamental workflow",
      "Follow the smart money"
    ],
    "subtopics": [
      "Volume as secondary confirmation: trend strength/weakness",
      "Volume behavior: higher volume in trend direction; lower in corrections",
      "Volume at breakouts (high) vs waiting trend (low); candle color irrelevant",
      "Moving averages: smoothing, trend detection, lagging nature",
      "Key MAs: 50 & 200 emphasized; rule: price below 200 as an investment filter (used for funds)",
      "MA contraction phases as precursor to new trend",
      "Slow Stochastic (0–100): overbought >80, oversold <20; crossover signals",
      "Slow Stochastic setup example (14,3,3); trading-oriented indicator",
      "RSI (0–100): classical >70 overbought, <30 oversold",
      "RSI 'Power Zone' concept: weekly RSI >70 used as momentum confirmation (NOT contrarian)",
      "Goersch Trend: color bars (up/down) + bar height indicates momentum change; shows divergences/trend changes",
      "Workflow: when technical trend strategies provide few signals → use fundamental approach",
      "Combined technical+fundamental: scan technical signals on high-quality universe",
      "Smart money concept: institutional behavior drives trends; avoid fighting it",
      "How to find smart money: ownership summaries, institutional ownership, insider trades, 13F filings, government member trades; example platforms listed"
    ]
  },
  "extract_targets": {
    "indicator_pages": [
      "136-137",
      "138-140",
      "141-145",
      "146-149",
      "150-151",
      "156-157"
    ],
    "rules_pages": [
      "137",
      "139",
      "142-144",
      "147-149",
      "151",
      "153-155",
      "156"
    ],
    "process_pages": [
      "153-155",
      "156-157"
    ],
    "low_value_pages": [
      "158-160 (mostly links/examples; keep as reference only)"
    ]
  },
  "likely_modules": [
    {
      "module_id": "TECH_VOLUME_CONFIRMATION",
      "why": "High-ROI confirmation layer: volume in trend direction vs corrections; breakout confirmation."
    },
    {
      "module_id": "TECH_MOVING_AVERAGES",
      "why": "Clear, interpretable rules (50/200 emphasis; 'below 200' as investment filter; contraction as trend precursor)."
    },
    {
      "module_id": "TECH_OSCILLATORS",
      "why": "Slow Stochastic and RSI provide explicit thresholds and crossover rules; can be implemented robustly in weekly system."
    },
    {
      "module_id": "MOMENTUM_POWER_ZONE",
      "why": "Weekly RSI >70 used as momentum confirmation (explicitly NOT contrarian); feeds stance confidence and breakout suitability."
    },
    {
      "module_id": "PROPRIETARY_TREND_SIGNAL",
      "why": "Goersch Trend appears as a composite trend/momentum visualization; may be deferred unless definition is given later."
    },
    {
      "module_id": "SMART_MONEY_UNIVERSE",
      "why": "Institutional ownership/insider/13F concepts define a stock-universe quality filter; likely defer for MVP unless you want equity selection module now."
    }
  ],
  "recommended_next_chunks": [
    {
      "pages": "161-182",
      "why": "Likely continues technical indicator set and moves into scan rules/operational signal generation (high ROI for registry + scoring logic)."
    },
    {
      "pages": "183-195",
      "why": "Potential bridge into more execution/risk rules; use if it contains explicit constraints or scoring hints."
    }
  ],
  "checkpoint": {
    "pages_done": "136-160",
    "artifacts_written": ["doc_map"],
    "counts": { "chunks_mapped": 5 }
  }
}


## ROI_GATE (Autonomous) — Pages 136–160 (Technical Indicators MVP Filter)
**PDF:** `/mnt/data/onvista Aktien-Intensiv-Seminar 11-2025.pdf`  
**Chunk:** 136–160 (1-based)  
**Selection rule:** keep indicators/rules that are (a) implementable as time-series features weekly, and (b) materially improve stance/risk/confidence.

```json
{
  "active_now": [
    {
      "id": "TECH_VOLUME_CONFIRMATION_RULES",
      "type": "indicator_family + rules",
      "why": "High ROI confirmation layer for trend vs correction and breakout validity; implementable from price+volume data.",
      "page_refs": ["p136", "p137"]
    },
    {
      "id": "TECH_MOVING_AVERAGES_50_200",
      "type": "indicator_family + rules",
      "why": "Simple, interpretable, widely used; explicit 50/200 emphasis and 'below 200' investment filter; MA contraction as precursor is operational.",
      "page_refs": ["p138", "p139", "p140"]
    },
    {
      "id": "TECH_SLOW_STOCHASTIC_14_3_3",
      "type": "indicator + rules",
      "why": "Explicit 0–100 thresholds (80/20) + crossover signals; good for weekly oscillation and mean-reversion vs momentum gating.",
      "page_refs": ["p141", "p142", "p143", "p144", "p145"]
    },
    {
      "id": "TECH_RSI_70_30_AND_POWER_ZONE",
      "type": "indicator + rules",
      "why": "Explicit 0–100 thresholds (70/30) plus weekly 'Power Zone' (RSI>70 as momentum confirmation, not contrarian). Strong for regime suitability.",
      "page_refs": ["p146", "p147", "p148", "p149"]
    }
  ],
  "defer": [
    {
      "id": "GOERSCH_TREND_PROPRIETARY_VISUAL",
      "type": "composite_indicator",
      "why": "Definition appears qualitative (colors + bar height). Defer unless a precise formula/source is provided later.",
      "page_refs": ["p150", "p151"]
    },
    {
      "id": "SMART_MONEY_DATA_SOURCES_LIST",
      "type": "reference_material",
      "why": "Platforms/links are not needed for the macro IPOS MVP; can become an optional equity-selection module later.",
      "page_refs": ["p156", "p157", "p158-160"]
    },
    {
      "id": "TECHNICAL_VS_FUNDAMENTAL_WORKFLOW_NARRATIVE",
      "type": "process_note",
      "why": "Conceptually useful but low incremental operational value vs existing regime modules; keep as a short note later if needed.",
      "page_refs": ["p153-155"]
    }
  ],
  "drop": [],
  "notes": [
    "We will not build Goersch Trend without a precise series definition.",
    "Volume/MA/Stoch/RSI are implementable from OHLCV and fit weekly cadence well."
  ],
  "checkpoint": {
    "pages_done": "136-160",
    "artifacts_written": ["roi_gate"],
    "counts": { "active_items": 4, "deferred_items": 3, "dropped_items": 0 }
  }
}

## INDICATOR_EXTRACT (Autonomous) — `indicators.jsonl`
**PDF:** `/mnt/data/onvista Aktien-Intensiv-Seminar 11-2025.pdf`  
**Pages:** 136–160 (1-based)  
**ROI_GATE:** active items only  
**Batch cap:** 25 → extracted **12** (indicator family encoded as a small set)

```jsonl
{"id":"tech_volume_raw","name":"Volume (raw)","category":"Technical","asset_class":"Equity","frequency":"weekly","source_frequency":"daily","raw_definition":"Trading volume used as confirmation for trend/correction and breakouts; candle color irrelevant.","source_hint":"From OHLCV provider","transforms":["level","1w_change","4w_avg","12w_avg","zscore_3y","percentile_5y"],"directionality":"mixed","scoring_method_default":"percentile","bands_or_thresholds":[],"notes":["Use primarily for confirmation, not standalone signals."],"page_refs":["p136","p137"],"needs_verification":false}
{"id":"tech_volume_trend_vs_correction_ratio","name":"Volume trend vs correction ratio","category":"Technical","asset_class":"Equity","frequency":"weekly","raw_definition":"Volume tends to be higher in the direction of the trend and lower during corrections; use as confirmation.","source_hint":"Derived from OHLCV + trend direction classifier","transforms":["ratio_trend_weeks_to_correction_weeks","rolling_ratio_12w","zscore_3y"],"directionality":"pro_risk","scoring_method_default":"zscore","bands_or_thresholds":[{"rule":"Higher volume on trend legs than on pullbacks => trend quality higher","score":65}],"notes":["Requires classifying weeks as impulse vs correction (from trend module)."],"page_refs":["p136"],"needs_verification":false}
{"id":"tech_volume_breakout_confirmation","name":"Volume breakout confirmation (relative volume)","category":"Technical","asset_class":"Equity","frequency":"weekly","raw_definition":"Breakouts tend to occur with high volume; low volume during consolidation/waiting phases.","source_hint":"Derived from OHLCV","transforms":["rel_volume_vs_12w_avg","spike_flag","zscore_3y"],"directionality":"pro_risk","scoring_method_default":"band","bands_or_thresholds":[{"rule":"Breakout week volume >> recent average => confirm signal","score":70},{"rule":"Breakout on low volume => reduce confidence","score":45}],"notes":["Use as confidence modifier for breakout/resumption events."],"page_refs":["p137"],"needs_verification":false}
{"id":"tech_ma_50w","name":"Moving Average (50-period; weekly)","category":"Technical","asset_class":"Equity","frequency":"weekly","raw_definition":"Moving average smooths prices; used to identify trend; emphasized 50 and 200 in seminar.","source_hint":"Derived from price series","transforms":["ma_level","slope_4w","price_minus_ma","cross_flags"],"directionality":"pro_risk","scoring_method_default":"percentile","bands_or_thresholds":[],"notes":["Lagging by nature; use with regime/trend module."],"page_refs":["p138","p139"],"needs_verification":false}
{"id":"tech_ma_200w","name":"Moving Average (200-period; weekly)","category":"Technical","asset_class":"Equity","frequency":"weekly","raw_definition":"Long moving average emphasized as an investment filter; below 200 MA considered avoid for funds (per seminar).","source_hint":"Derived from price series","transforms":["ma_level","slope_12w","price_minus_ma","below_flag"],"directionality":"pro_risk","scoring_method_default":"band","bands_or_thresholds":[{"rule":"Price below 200 MA => investment filter negative (risk-off bias)","score":30},{"rule":"Price above 200 MA => supportive backdrop","score":65}],"notes":["Use as risk budget governor for equity exposure; do not overtrade."],"page_refs":["p139"],"needs_verification":false}
{"id":"tech_ma_50_200_cross","name":"MA cross (50 vs 200)","category":"Technical","asset_class":"Equity","frequency":"weekly","raw_definition":"Relative position of 50 and 200 moving averages as trend filter (classic golden/death cross style).","source_hint":"Derived from price series","transforms":["sign_50_minus_200","cross_event_flag","time_since_cross"],"directionality":"pro_risk","scoring_method_default":"band","bands_or_thresholds":[{"rule":"50 MA above 200 MA => trend supportive","score":65},{"rule":"50 MA below 200 MA => trend weak","score":35}],"notes":["Lagging; best as confirmation and risk budget bias, not timing."],"page_refs":["p138","p139"],"needs_verification":true}
{"id":"tech_ma_contraction_index","name":"MA contraction / low-volatility precursor","category":"Technical","asset_class":"Equity","frequency":"weekly","raw_definition":"When the moving average (and price action) runs sideways/contracting, a new trend may form afterward (per seminar).","source_hint":"Derived from MA slope + price range compression","transforms":["ma_slope_abs","range_compression","boll_width_proxy","contraction_flag"],"directionality":"mixed","scoring_method_default":"percentile","bands_or_thresholds":[{"rule":"Sustained low slope + compressed range => potential setup (watch for breakout)","score":55}],"notes":["Use as 'setup' context; combine with breakout + volume confirmation."],"page_refs":["p140"],"needs_verification":false}
{"id":"tech_slow_stochastic_14_3_3","name":"Slow Stochastic (14,3,3)","category":"Technical","asset_class":"Equity","frequency":"weekly","raw_definition":"Slow stochastic oscillator (0–100) with standard thresholds: overbought >80, oversold <20; uses %K/%D smoothing (14,3,3 shown).","source_hint":"Computed from OHLC","transforms":["k","d","k_minus_d","cross_flags","time_in_zone"],"directionality":"mixed","scoring_method_default":"band","bands_or_thresholds":[{"rule":">80 => overbought zone","score":70},{"rule":"<20 => oversold zone","score":30}],"notes":["Use with regime: choppy favors mean reversion; trendy/momentum favors trend confirmation."],"page_refs":["p141","p142"],"needs_verification":false}
{"id":"tech_slow_stoch_crossover_signal","name":"Slow Stochastic crossover signal","category":"Technical","asset_class":"Equity","frequency":"weekly","raw_definition":"Signal from %K/%D crossovers (classic stochastic use).","source_hint":"Derived from Slow Stochastic series","transforms":["bull_cross_flag","bear_cross_flag","cross_in_zone_flag"],"directionality":"mixed","scoring_method_default":"band","bands_or_thresholds":[{"rule":"Bullish crossover out of oversold => supportive","score":65},{"rule":"Bearish crossover out of overbought => caution","score":35}],"notes":["Treat as tactical; gate with MARKET_CONDITIONS (avoid in CHOPPY breakouts)."],"page_refs":["p144","p145"],"needs_verification":true}
{"id":"tech_rsi_14","name":"RSI (14)","category":"Technical","asset_class":"Equity","frequency":"weekly","raw_definition":"Relative Strength Index oscillator (0–100): classical overbought >70, oversold <30.","source_hint":"Computed from OHLC","transforms":["level","time_in_zone","1w_change","zscore_3y","percentile_5y"],"directionality":"mixed","scoring_method_default":"band","bands_or_thresholds":[{"rule":">70 => overbought zone","score":70},{"rule":"<30 => oversold zone","score":30}],"notes":["Default RSI can be contrarian in choppy; but see Power Zone rule for trend/momentum."],"page_refs":["p146","p147"],"needs_verification":false}
{"id":"tech_rsi_power_zone_weekly","name":"RSI Power Zone (weekly momentum confirmation)","category":"Technical","asset_class":"Equity","frequency":"weekly","raw_definition":"Power Zone concept: weekly RSI above ~70 acts as momentum confirmation (trend-following), not contrarian.","source_hint":"Seminar definition","transforms":["power_zone_flag","time_above_70","time_below_40_proxy"],"directionality":"pro_risk","scoring_method_default":"band","bands_or_thresholds":[{"rule":"Weekly RSI > 70 => strong momentum / trend confirmation","score":80}],"notes":["Use to increase confidence in TRENDY/MOMENTUM regimes; do not treat as 'overbought means sell' in this context."],"page_refs":["p148","p149"],"needs_verification":false}

## RULE_EXTRACT (Autonomous) — `rules.jsonl`
**PDF:** `/mnt/data/onvista Aktien-Intensiv-Seminar 11-2025.pdf`  
**Pages:** 136–160 (1-based)  
**ROI_GATE:** active items only  
**Batch cap:** 40 → extracted **22** (high-impact, weekly-operational)

```jsonl
{"id":"rule_volume_is_secondary_confirmation_not_primary_signal","scope":"process","applies_to":["TECH_VOLUME_CONFIRMATION"],"if":"using volume in the weekly OS","then":{"interpretation":"Use volume mainly as a confirmation layer for trends/breakouts; do not treat it as a standalone direction signal.","score_adjustment":"n/a","confidence_adjustment":"+0"},"rationale":"Seminar presents volume as 'second signal' confirming the main signal.","failure_modes":["In low-liquidity assets volume can be noisy; data quality matters."],"page_refs":["p136"],"needs_verification":false}
{"id":"rule_volume_higher_in_trend_direction_lower_in_corrections","scope":"module","applies_to":["tech_volume_trend_vs_correction_ratio"],"if":"volume is higher during impulse/trend legs than during corrections","then":{"interpretation":"Trend quality/commitment is higher; increase confidence in trend-following stance.","score_adjustment":"+5","confidence_adjustment":"+10"},"rationale":"Seminar: volume is higher in direction of the move and lower in corrections; confirms strength.","failure_modes":["Earnings/news weeks distort; ETFs may show different volume behavior."],"page_refs":["p136"],"needs_verification":false}
{"id":"rule_volume_low_in_waiting_phases","scope":"process","applies_to":["TECH_VOLUME_CONFIRMATION"],"if":"volume remains low during consolidation/waiting phases","then":{"interpretation":"This is normal; do not interpret low volume alone as bearish.","score_adjustment":"0","confidence_adjustment":"0"},"rationale":"Seminar: low volume while market 'waits' / consolidates.","failure_modes":["Prolonged low volume can coincide with low participation and fragile breakouts; use breakout confirmation rule."],"page_refs":["p137"],"needs_verification":false}
{"id":"rule_breakout_should_show_high_volume","scope":"module","applies_to":["tech_volume_breakout_confirmation"],"if":"breakout occurs AND relative volume is high vs recent average","then":{"interpretation":"Breakout is more credible; increase confidence and allow stronger stance (bounded).","score_adjustment":"+5","confidence_adjustment":"+15"},"rationale":"Seminar: high volume at breakouts; low volume during waiting; volume is key for breakout quality.","failure_modes":["Some breakouts happen on moderate volume; confirm with price follow-through."],"page_refs":["p137"],"needs_verification":false}
{"id":"rule_breakout_on_low_volume_reduce_confidence","scope":"module","applies_to":["tech_volume_breakout_confirmation"],"if":"breakout occurs AND relative volume is low","then":{"interpretation":"Reduce confidence; treat as higher false-break risk.","score_adjustment":"0","confidence_adjustment":"-15"},"rationale":"Seminar implies breakout validity is supported by higher volume; absence reduces credibility.","failure_modes":["In some markets, volume data is incomplete; avoid overpenalizing if data quality low."],"page_refs":["p137"],"needs_verification":true}
{"id":"rule_candle_color_irrelevant_for_volume_confirmation","scope":"process","applies_to":["TECH_VOLUME_CONFIRMATION"],"if":"assessing volume in a weekly candle","then":{"interpretation":"Ignore candle color; focus on volume behavior relative to trend/correction context.","score_adjustment":"n/a","confidence_adjustment":"n/a"},"rationale":"Seminar: candle color does not matter for volume interpretation.","failure_modes":["None meaningful; keep as simplification."],"page_refs":["p137"],"needs_verification":false}
{"id":"rule_moving_average_is_lagging_use_as_filter","scope":"process","applies_to":["TECH_MOVING_AVERAGES"],"if":"using moving averages for decisions","then":{"interpretation":"Treat MAs as trend filters (lagging), not as early timing tools.","score_adjustment":"n/a","confidence_adjustment":"n/a"},"rationale":"Seminar: MAs smooth prices and are lagging indicators.","failure_modes":["Overreliance can delay turns; combine with trend-break logic."],"page_refs":["p138"],"needs_verification":false}
{"id":"rule_focus_on_50_and_200_ma","scope":"process","applies_to":["TECH_MOVING_AVERAGES"],"if":"choosing MA lengths for MVP","then":{"interpretation":"Emphasize 50 and 200 moving averages as the primary reference lengths.","score_adjustment":"n/a","confidence_adjustment":"n/a"},"rationale":"Seminar highlights 50 and 200 as key MAs.","failure_modes":["Other lengths may suit some assets; keep configurable."],"page_refs":["p139"],"needs_verification":false}
{"id":"rule_price_below_200ma_negative_investment_filter","scope":"portfolio","applies_to":["tech_ma_200w"],"if":"price is below the 200-period MA","then":{"interpretation":"Apply negative investment filter (avoid/underweight); treat as risk budget governor for equity exposure.","score_adjustment":"-15","confidence_adjustment":"+10"},"rationale":"Seminar: for funds, price below 200 MA is a negative filter.","failure_modes":["Whipsaws around MA; define confirmation (e.g., 2-week close) if needed."],"page_refs":["p139"],"needs_verification":false}
{"id":"rule_price_above_200ma_supportive_backdrop","scope":"portfolio","applies_to":["tech_ma_200w"],"if":"price is above the 200-period MA","then":{"interpretation":"Supportive backdrop; allow normal risk budget (subject to other modules).","score_adjustment":"+5","confidence_adjustment":"+5"},"rationale":"Complementary interpretation to the below-200 filter logic.","failure_modes":["Late-cycle tops can still be above 200; avoid complacency."],"page_refs":["p139"],"needs_verification":true}
{"id":"rule_ma_contraction_can_precede_new_trend","scope":"module","applies_to":["tech_ma_contraction_index"],"if":"MA slope is low and price/MA are contracting sideways","then":{"interpretation":"Potential setup for a new trend; watch for breakout + volume confirmation before acting.","score_adjustment":"0","confidence_adjustment":"+5"},"rationale":"Seminar: MA can become flat; if contraction ends, a new trend may form.","failure_modes":["Many contractions resolve into continued chop; require confirmation."],"page_refs":["p140"],"needs_verification":false}
{"id":"rule_stochastic_overbought_over80","scope":"indicator","applies_to":["tech_slow_stochastic_14_3_3"],"if":"slow stochastic > 80","then":{"interpretation":"Overbought zone; in CHOPPY regimes can support mean-reversion caution; in TRENDY/MOMENTUM treat as strength unless reversal confirmed.","score_adjustment":"0","confidence_adjustment":"+0"},"rationale":"Seminar: stochastic overbought above 80.","failure_modes":["Overbought can persist in trends; do not auto-sell."],"page_refs":["p142","p143"],"needs_verification":false}
{"id":"rule_stochastic_oversold_under20","scope":"indicator","applies_to":["tech_slow_stochastic_14_3_3"],"if":"slow stochastic < 20","then":{"interpretation":"Oversold zone; in CHOPPY can support mean-reversion; in downtrends treat as weak confirmation only.","score_adjustment":"0","confidence_adjustment":"+0"},"rationale":"Seminar: stochastic oversold below 20.","failure_modes":["Oversold can persist in strong downtrends."],"page_refs":["p142","p143"],"needs_verification":false}
{"id":"rule_stochastic_bull_cross_out_of_oversold_supportive","scope":"indicator","applies_to":["tech_slow_stoch_crossover_signal"],"if":"%K crosses above %D AND (optional) occurs near/after oversold zone","then":{"interpretation":"Supportive tactical signal; increase confidence for risk-on adds if regime is not CHOPPY-uncertain.","score_adjustment":"+5","confidence_adjustment":"+5"},"rationale":"Seminar uses stochastic crossovers as signals; oversold/overbought context is emphasized.","failure_modes":["Whipsaw crosses in choppy markets; gate with regime classifier."],"page_refs":["p144","p145"],"needs_verification":false}
{"id":"rule_stochastic_bear_cross_out_of_overbought_caution","scope":"indicator","applies_to":["tech_slow_stoch_crossover_signal"],"if":"%K crosses below %D AND (optional) occurs near/after overbought zone","then":{"interpretation":"Caution tactical signal; reduce confidence or tighten stops.","score_adjustment":"-5","confidence_adjustment":"-5"},"rationale":"Seminar crossovers + zone context.","failure_modes":["In strong trends, overbought reversals fail; combine with trend-break/pivot breaks."],"page_refs":["p144","p145"],"needs_verification":true}
{"id":"rule_rsi_overbought_over70","scope":"indicator","applies_to":["tech_rsi_14"],"if":"RSI > 70","then":{"interpretation":"Classical overbought zone; do not automatically sell—interpret using regime + Power Zone rule.","score_adjustment":"0","confidence_adjustment":"0"},"rationale":"Seminar: RSI overbought above 70.","failure_modes":["Overbought can persist; wrong contrarian trades possible."],"page_refs":["p146","p147"],"needs_verification":false}
{"id":"rule_rsi_oversold_under30","scope":"indicator","applies_to":["tech_rsi_14"],"if":"RSI < 30","then":{"interpretation":"Classical oversold zone; may support mean-reversion in CHOPPY; treat cautiously in downtrends.","score_adjustment":"0","confidence_adjustment":"0"},"rationale":"Seminar: RSI oversold below 30.","failure_modes":["Oversold can persist in bear markets."],"page_refs":["p146","p147"],"needs_verification":false}
{"id":"rule_rsi_power_zone_weekly_over70_is_momentum","scope":"indicator","applies_to":["tech_rsi_power_zone_weekly"],"if":"weekly RSI > 70","then":{"interpretation":"Momentum confirmation (Power Zone); treat as trend-following strength, not contrarian overbought.","score_adjustment":"+10","confidence_adjustment":"+10"},"rationale":"Seminar: weekly RSI >70 in Power Zone context supports momentum/trend continuation.","failure_modes":["Late-stage blow-off; pair with volume + trend-break logic."],"page_refs":["p148","p149"],"needs_verification":false}
{"id":"rule_power_zone_supports_breakout_suitability","scope":"process","applies_to":["MOMENTUM_POWER_ZONE","MARKET_CONDITIONS"],"if":"Power Zone is active AND regime is TRENDY or MOMENTUM","then":{"interpretation":"Breakouts/resumption signals are more suitable; allow incremental adds (bounded).","score_adjustment":"+5","confidence_adjustment":"+5"},"rationale":"Power Zone described as momentum confirmation; best used when regime supports trend continuation.","failure_modes":["In CHOPPY, high RSI can mean failed breakout; use regime gating."],"page_refs":["p148","p149"],"needs_verification":true}
{"id":"rule_contradiction_volume_confirms_but_trend_break_flagged","scope":"portfolio","applies_to":["TECH_VOLUME_CONFIRMATION","TREND_BREAKS_TRANSITIONS"],"if":"volume confirms breakout (high rel volume) BUT trend break/transition state is TRENDLESS/UNCERTAIN","then":{"interpretation":"Contradiction: confirmation vs structure. Keep risk capped; require follow-through or structural reform.","score_adjustment":"0","confidence_adjustment":"-10"},"rationale":"Combines ‘wait after break’ governance with volume confirmation to prevent false positives.","failure_modes":["Early re-entry can be missed; allow small probes only."],"page_refs":["p137","p92"],"needs_verification":true}
{"id":"rule_contradiction_price_below_200ma_but_power_zone_active","scope":"portfolio","applies_to":["tech_ma_200w","tech_rsi_power_zone_weekly"],"if":"price below 200 MA BUT RSI Power Zone active","then":{"interpretation":"Contradiction: momentum vs long-term filter. Reduce confidence and size; treat as tactical rally in weak trend unless structure reforms above 200 MA.","score_adjustment":"0","confidence_adjustment":"-10"},"rationale":"200 MA filter is strategic; Power Zone is tactical momentum. Conflict warrants caution.","failure_modes":["True trend reversals begin with momentum; resolve via close above 200 MA + trend structure."],"page_refs":["p139","p148"],"needs_verification":true}


---
module_id: TECH_OSCILLATORS
scope: module
tags: [technical, oscillators, rsi, stochastic, momentum, regime_gating]
version: 0.1
source: seminar_pdf
cadence: weekly
---

## Purpose
Use **Slow Stochastic** and **RSI** as a weekly oscillator layer that:
- adapts behavior by **market regime** (CHOPPY vs TRENDY vs MOMENTUM),
- supports **tactical timing** without overriding the governance modules,
- treats **RSI Power Zone** as **trend-following momentum**, not contrarian.

## Inputs (weekly)
- `tech_slow_stochastic_14_3_3` (K/D, 14,3,3)
- `tech_slow_stoch_crossover_signal` (K/D cross flags)
- `tech_rsi_14`
- `tech_rsi_power_zone_weekly` (Power Zone flag)
- Regime context from `MARKET_CONDITIONS`:
  - `regime_label`
  - `regime_confidence`

## Outputs (weekly)
- `oscillator_bias` ∈ {MEAN_REVERT, TREND_CONFIRM, NEUTRAL}
- `oscillator_score` (0–100, bounded)
- `oscillator_confidence` (0–100)
- `tactical_flags` (e.g., stoch_bull_cross, stoch_bear_cross, rsi_power_zone)

---

## Core Thresholds (explicit)
### Slow Stochastic
- Overbought: **>80**
- Oversold: **<20**
- Signals: **%K / %D crossovers** (use zone context when possible)

### RSI
- Overbought: **>70**
- Oversold: **<30**
- **Power Zone (weekly): RSI > 70 = momentum confirmation** (NOT contrarian)

---

## Regime Gating (how to interpret signals)
### CHOPPY (range / overlap)
- Oscillator bias: **MEAN_REVERT**
- Stochastic:
  - Oversold (<20) + bullish crossover → supportive bounce bias
  - Overbought (>80) + bearish crossover → caution / mean-reversion bias
- RSI:
  - <30 supports bounce bias (with confirmation)
  - >70 is *not* automatically bearish; treat cautiously but do not force sells

### TRENDY (directional HH/HL or LH/LL)
- Oscillator bias: **TREND_CONFIRM**
- Stochastic:
  - Overbought can persist; do not auto-sell
  - Use crossovers mainly as “tighten/loosen stops” not as trend reversal by itself
- RSI:
  - RSI >70 can be strength; use Power Zone as confirmation

### MOMENTUM (ATR expanding, fast moves)
- Oscillator bias: **TREND_CONFIRM** (but with higher noise)
- Stochastic/RSI extremes are less reliable contrarianly
- Power Zone is most useful here as a continuation confirmation
- Keep sizing rules from MARKET_CONDITIONS (momentum = medium size, wider stops)

---

## Operational Rules (compact)
1) **Stochastic zone awareness**
- >80 = overbought zone, <20 = oversold zone
- Don’t auto-trade zones without regime context

2) **Stochastic crossovers**
- Bull cross near/after oversold → supportive (tactical)
- Bear cross near/after overbought → caution (tactical)
- In CHOPPY: crossovers are more actionable
- In TRENDY/MOMENTUM: crossovers are mostly management (tighten/loosen), not reversal calls

3) **RSI classical zones**
- >70 / <30 are context flags, not standalone actions

4) **RSI Power Zone (weekly RSI > 70)**
- Treat as **momentum confirmation**
- Best used when regime ∈ {TRENDY, MOMENTUM}
- Explicit: **do not use as contrarian “overbought means sell”**

---

## Confidence Heuristic (0–100)
Start at 50, adjust:
- +15 if regime_confidence high AND regime ≠ UNCERTAIN
- +10 if RSI Power Zone active in TRENDY/MOMENTUM
- +5 if Stochastic crossover occurs with zone context (oversold/overbought)
- -20 if regime is UNCERTAIN (cap influence)
- -10 if oscillator signals conflict (e.g., stoch bear cross while Power Zone active)

---

## Contradictions (trigger investigation)
- RSI Power Zone active but price below 200 MA (long filter negative)
  - Treat as tactical rally in weak structure unless price/structure recovers.
- Strong oscillator signals while trend state is TRENDLESS after break
  - Cap risk; require structural reform (pivot break / alignment improvement).

---

## Implementation Notes (IPOS-friendly)
- Keep oscillator influence bounded: it should not override macro/rates risk governors.
- Store tactical flags in snapshot for explainability:
  - `rsi_power_zone_flag`
  - `stoch_cross_flag`
  - `stoch_zone`
- Default scoring approach:
  - CHOPPY → allow oscillator to tilt more (mean reversion)
  - TRENDY/MOMENTUM → oscillator mostly influences confidence/stops

---

## NEXT ACTION (say “continue”)
**Stage:** PLAYBOOK_WRITE  
**Module:** TECH_MOVING_AVERAGES  
**Focus:** Compact rules for 50/200 MA filters, cross-state, “below 200” investment filter, MA contraction setups, and contradictions with momentum signals.


---
module_id: TECH_MOVING_AVERAGES
scope: module
tags: [technical, moving_averages, trend_filter, risk_budget_governor]
version: 0.1
source: seminar_pdf
cadence: weekly
---

## Purpose
Use moving averages as **lagging trend filters** and **risk governors**:
- emphasize **50** and **200** (per seminar),
- apply a simple **“below 200 = negative filter”** rule,
- treat MA contraction as a **setup context**, not a signal.

## Inputs (weekly)
- `tech_ma_50w`
- `tech_ma_200w`
- `tech_ma_50_200_cross`
- `tech_ma_contraction_index`
- Market context: `equity_sp500_index` (or chosen benchmark)

## Outputs (weekly)
- `ma_trend_filter` ∈ {STRONG_POSITIVE, POSITIVE, NEUTRAL, NEGATIVE}
- `ma_confidence` (0–100)
- `risk_governor_flag` (bool)  // used in risk budget computation
- `contradiction_flags` (list)

---

## Core Principles (explicit)
- Moving averages **smooth** prices and are **lagging** → use as filters, not early timing.
- Focus lengths: **50** and **200**.
- For “investment style” (fund-like), **price below 200 MA is a negative filter**.

---

## Filter Logic (MVP)
### 1) 200 MA investment filter (governor)
- If `price < MA200`:
  - `ma_trend_filter = NEGATIVE`
  - set `risk_governor_flag = true`
  - apply equity risk budget cap / underweight bias

- If `price >= MA200`:
  - `ma_trend_filter = POSITIVE` (subject to other context)

### 2) 50 vs 200 cross (secondary confirmation)
- If `MA50 > MA200`: trend supportive confirmation (but lagging)
- If `MA50 < MA200`: trend weaker confirmation

### 3) Price distance and slope (optional refinement)
- `price_minus_ma200` (distance) and MA slope can add confidence but should not dominate.

---

## MA Contraction (setup context)
### What it means
- MA and price action can go sideways / contract (flat slope + compressed range).
- After a contraction ends, a **new trend may form**.

### How to use (efficient)
- Contraction does **not** change stance by itself.
- It adds a “setup” tag:
  - *Watch for breakout + volume confirmation + regime suitability*

---

## Confidence Heuristic (0–100)
Start at 50:
- +20 if price is clearly above MA200 (and MA200 slope not deteriorating)
- +10 if MA50 > MA200
- -25 if price below MA200 (governor active)
- -10 if whipsaw zone (price near MA200; frequent crossings)
- +5 if contraction_flag true (setup awareness, not direction)

---

## Contradictions (trigger investigation)
- **Price below MA200** but **RSI Power Zone active**
  - interpret as tactical rally inside structurally weak trend unless price reclaims MA200 and trend structure reforms.
- **MA50 > MA200** but **trend-break / TRENDLESS** state active
  - lagging MA confirms old regime; do not ignore structure break.
- **Contraction setup** but MARKET_CONDITIONS = CHOPPY and no volume confirmation
  - likely continued chop; reduce expectation of clean breakout.

---

## Implementation Notes (IPOS-friendly)
- Treat MA200 filter as a **risk budget governor** (hard bias), not a trading trigger.
- Keep changes slow:
  - optionally require 2 weekly closes to confirm “below/above MA200” to reduce whipsaws.
- Store in snapshot:
  - `price_vs_ma200_flag`, `ma50_vs_ma200_flag`, `contraction_flag`, and any contradiction flags.

---

## NEXT ACTION (say “continue”)
**Stage:** PLAYBOOK_WRITE  
**Module:** TECH_VOLUME_CONFIRMATION  
**Focus:** Write a compact volume module (trend vs correction volume, breakout volume confirmation, and contradictions vs trendless/break states).

---
module_id: TECH_VOLUME_CONFIRMATION
scope: module
tags: [technical, volume, confirmation, breakouts, confidence]
version: 0.1
source: seminar_pdf
cadence: weekly
---

## Purpose
Use **volume** as a **secondary confirmation** layer to:
- validate trend quality (impulse volume vs correction volume),
- validate breakouts (relative volume spikes),
- **adjust confidence** rather than force direction.

## Inputs (weekly)
- `tech_volume_raw`
- `tech_volume_trend_vs_correction_ratio`
- `tech_volume_breakout_confirmation` (relative volume vs baseline)
- Context from other modules:
  - `MARKET_CONDITIONS.regime_label` / `regime_confidence`
  - `TREND_BREAKS_TRANSITIONS.transition_state`

## Outputs (weekly)
- `volume_confirmation_score` (0–100, bounded)
- `volume_confidence_delta` (signed modifier)
- `breakout_quality_flag` ∈ {CONFIRMED, WEAK, NA}
- `contradiction_flags` (list)

---

## Core Principles (explicit)
- Volume is the **second signal** (confirmation), not the main signal.
- Candle color is irrelevant for volume interpretation.
- Typical behavior:
  - Higher volume in trend direction (impulses)
  - Lower volume during corrections/consolidation
  - Breakouts often show higher relative volume

---

## Rules (compact)
### 1) Trend quality confirmation
- If impulse/trend legs show higher volume than correction legs
  - increase confidence in trend-following posture

### 2) Consolidation volume
- Low volume during “waiting / consolidation” is normal
  - do not interpret as bearish alone

### 3) Breakout confirmation
- If breakout + relative volume high
  - classify breakout as **CONFIRMED**
  - increase confidence and allow bounded incremental adds (subject to governance)

- If breakout + relative volume low
  - classify breakout as **WEAK**
  - reduce confidence; higher false-break risk

---

## Confidence Heuristic
Start at 50:
- +15 if breakout CONFIRMED (high rel volume)
- -15 if breakout WEAK (low rel volume)
- +10 if trend_vs_correction_ratio strongly favors impulses
- -10 if volume data quality is low or missing (then neutralize volume effects)

---

## Contradictions (trigger investigation)
- Breakout volume confirms, but transition_state is TRENDLESS/UNCERTAIN after a break
  - governance wins: keep risk capped; require follow-through + structure reform
- Volume confirms breakouts, but regime_label is CHOPPY with high overlap/retracements
  - likely false breakout environment; treat as lower quality
- Volume weak during a supposed momentum breakout
  - momentum label questionable; re-check ATR expansion and overlap features

---

## Implementation Notes (IPOS-friendly)
- Use volume as a **confidence modifier** (affects confidence score, not core direction score).
- Store in snapshot:
  - `rel_volume`, `breakout_quality_flag`, `trend_vs_correction_ratio`, and contradiction flags.
- Default: if volume unavailable/unreliable for an asset class, set module to neutral.

---

## NEXT ACTION (say “continue”)
**Stage:** DOC_MAP  
**Pages:** 161–182 (autonomous)  
**Focus:** Continue the technical indicator section: extract any additional high-ROI indicators (e.g., MACD, ATR, Bollinger, trend strength, breadth) and any explicit thresholds or workflow rules.

## DOC_MAP (Autonomous) — Seminar PDF → IPOS Extraction Queue (Equity Universe + Fundamental Scanning)
**PDF:** `/mnt/data/onvista Aktien-Intensiv-Seminar 11-2025.pdf`  
**Chunk analyzed:** pages **161–182** (1-based)  
**ROI lens:** This chunk is **equity-universe / stock-selection process**, not macro time-series. High value *if* you want a stock-selection layer; otherwise mostly **defer** for the macro-first IPOS MVP.

```json
{
  "chunk": {
    "pages": "161-182",
    "density": "medium",
    "topics": [
      "Building an equity universe",
      "Screening process design",
      "Top-down screening (macro→sector→stocks)",
      "Bottom-up growth stock filters",
      "Fundamental scanner long (Finviz example)",
      "Execution/liquidity filters (ADTV, price)"
    ],
    "subtopics": [
      "Two screening approaches: Top-Down vs Bottom-Up",
      "Top-Down flow: strong region/index → strong sector → strongest stocks",
      "Bottom-Up: screen by fundamental + technical criteria; sector/index irrelevant post-filter",
      "Growth framework: revenue growth + earnings growth as success measures",
      "Sales q/q filter: >= 15% (best companies); strong phases > 25%",
      "Sales y/y filter: >= 20% over last 5 years",
      "EPS q/q filter: >= 20% (strong phases 40–50%); ignore one-offs (use Non-GAAP)",
      "EPS y/y filter: >= 25% over last 5 years (EPS-rating sorting idea)",
      "ROE filter: >= 15% (TTM)",
      "Market cap bands: small <2B, mid 2–10B, large >10B (risk preference)",
      "ADTV: liquidity, reliability of support/resistance, institutional activity; slippage decreases as liquidity rises",
      "KGV/P/E note: for growth stocks, P/E is not decisive; high P/E can reflect growth expectations",
      "Scanner example (Finviz US): mkt cap >2B, sales q/q >15%, sales 5y >20%, EPS q/q >20%, EPS 5y >25%, ROE >15%, avg vol >400k, price >$10"
    ]
  },
  "extract_targets": {
    "indicator_pages": [
      "172-181 (explicit numeric thresholds; suitable as stock-level features)",
      "179-181 (ADTV + scanner thresholds)"
    ],
    "rules_pages": [
      "163 (screening process options)",
      "172-181 (growth filters + numeric thresholds)",
      "181 (scanner parameter list)"
    ],
    "process_pages": [
      "163 (Top-Down vs Bottom-Up definitions)",
      "164-171 (Top-Down relative strength scanning workflow; tool references)",
      "182 (scanner goal: long candidates)"
    ],
    "low_value_pages": [
      "161-162 (mostly links/headings)",
      "164-171 (tool/platform pointers; keep as reference notes unless you implement integrations)"
    ]
  },
  "likely_modules": [
    {
      "module_id": "EQUITY_UNIVERSE_TOP_DOWN",
      "why": "Defines top-down workflow: index/region → sector → stocks; aligns with relative-strength selection."
    },
    {
      "module_id": "EQUITY_GROWTH_FUNDAMENTAL_FILTERS",
      "why": "Contains concrete numeric thresholds for growth stock screening (sales/eps growth, ROE)."
    },
    {
      "module_id": "EXECUTION_LIQUIDITY_FILTERS",
      "why": "ADTV + price filters directly reduce slippage and improve robustness; useful even if you keep stock selection optional."
    },
    {
      "module_id": "FUNDAMENTAL_SCANNER_LONG_TEMPLATE",
      "why": "Provides a ready-to-encode scanner parameter set (Finviz example)."
    }
  ],
  "recommended_next_chunks": [
    {
      "pages": "183-205",
      "why": "Often where ‘how to trade/scan’ becomes more explicit (watchlists, triggers, risk rules). Potentially also more indicator definitions."
    }
  ],
  "checkpoint": {
    "pages_done": "161-182",
    "artifacts_written": ["doc_map"],
    "counts": { "chunks_mapped": 6 }
  }
}

## ROI_GATE (Autonomous) — Pages 161–182 (Equity Screening Content → MVP Filter)
**PDF:** `/mnt/data/onvista Aktien-Intensiv-Seminar 11-2025.pdf`  
**Chunk:** 161–182 (1-based)  
**MVP scope assumption:** IPOS is **macro-first (A2)**; stock-selection is **optional** and should not bloat MVP unless explicitly requested.

```json
{
  "active_now": [
    {
      "id": "EXECUTION_LIQUIDITY_FILTERS_ADTV_PRICE",
      "type": "process_rule_set",
      "why": "Universally useful risk-control even in a macro-first OS: ensures tradability, reduces slippage, increases reliability of technical levels and execution.",
      "page_refs": ["p179", "p180", "p181"]
    }
  ],
  "defer": [
    {
      "id": "EQUITY_UNIVERSE_TOP_DOWN_WORKFLOW",
      "type": "optional_module",
      "why": "High value for equity selection, but outside macro-first MVP. Keep as optional later (macro→sector→stocks).",
      "page_refs": ["p163", "p164-171"]
    },
    {
      "id": "EQUITY_GROWTH_FUNDAMENTAL_FILTERS_NUMERIC_THRESHOLDS",
      "type": "optional_module",
      "why": "Concrete thresholds (sales/eps growth, ROE, etc.) are great but create a stock-selection subsystem. Defer unless you explicitly want equity screening now.",
      "page_refs": ["p172-181"]
    },
    {
      "id": "FINVIZ_LONG_SCANNER_TEMPLATE",
      "type": "optional_module",
      "why": "Ready-made scanner settings; useful later if you implement a stock-selection layer or manual screening workflow.",
      "page_refs": ["p181", "p182"]
    }
  ],
  "drop": [],
  "notes": [
    "This section does not add macro time-series indicators; it adds stock-universe selection logic.",
    "We keep only execution-liquidity filters active because they reduce operational risk across strategies."
  ],
  "checkpoint": {
    "pages_done": "161-182",
    "artifacts_written": ["roi_gate"],
    "counts": { "active_items": 1, "deferred_items": 3, "dropped_items": 0 }
  }
}

## PROCESS_EXTRACT (Autonomous) — `process.jsonl`
**PDF:** `/mnt/data/onvista Aktien-Intensiv-Seminar 11-2025.pdf`  
**Pages:** 161–182 (1-based)  
**ROI_GATE:** active items only (execution/liquidity filters)  
**Batch cap:** 20 → extracted **3**

```jsonl
{"id":"process_liquidity_filter_use_adtv_to_reduce_slippage","topic":"execution_liquidity","statement":"Use liquidity (average daily trading volume / ADTV) as a tradability filter to reduce slippage and improve execution reliability.","operationalization":["Add a hard pre-trade gate for any equity/ETF instrument: ADTV >= threshold (default: 400k shares/day as cited in scanner example).","Store ADTV and pass/fail flag in the weekly snapshot for auditability.","If ADTV fails: reduce position sizing, widen expected slippage, or exclude from candidate set."],"page_refs":["p179","p181"]}
{"id":"process_liquidity_improves_reliability_of_levels","topic":"execution_liquidity","statement":"Higher liquidity tends to make support/resistance and technical levels more reliable, because institutional participation is stronger and price discovery is better.","operationalization":["Use liquidity tiering (low/med/high) to adjust confidence in technical modules (MA/volume/breakouts).","Log a contradiction if technical signals are strong but liquidity tier is low (forces manual review)."],"page_refs":["p180"]}
{"id":"process_minimum_price_filter_to_avoid_microcaps_noise","topic":"execution_liquidity","statement":"Apply a minimum price filter to avoid very low-priced instruments where spreads/slippage and noise can dominate.","operationalization":["Default gate: price >= $10 (as cited in scanner example) or equivalent in your trading currency.","If price < threshold: cap risk budget contribution for that instrument or exclude from selection workflow."],"page_refs":["p181"]}

## RULE_EXTRACT (Autonomous) — `rules.jsonl`
**PDF:** `/mnt/data/onvista Aktien-Intensiv-Seminar 11-2025.pdf`  
**Pages:** 161–182 (1-based)  
**ROI_GATE:** active items only  
**Batch cap:** 40 → extracted **10**

```jsonl
{"id":"rule_liquidity_gate_min_adtv_default","scope":"portfolio","applies_to":["EXECUTION_LIQUIDITY_FILTERS"],"if":"instrument ADTV < 400000 shares/day (default)","then":{"interpretation":"Fail tradability gate: exclude from candidate list or apply strong size reduction and higher slippage assumptions.","score_adjustment":"n/a","confidence_adjustment":"-20"},"rationale":"Seminar emphasizes liquidity (ADTV) and provides a scanner example using avg volume >400k.","failure_modes":["Threshold depends on market/venue; for ETFs use $ volume instead of shares."],"page_refs":["p179","p181"],"needs_verification":false}
{"id":"rule_liquidity_pass_increases_technical_reliability","scope":"process","applies_to":["EXECUTION_LIQUIDITY_FILTERS"],"if":"instrument liquidity tier is high (passes ADTV)","then":{"interpretation":"Increase trust in technical levels/signals (MA/breakouts/support-resistance).","score_adjustment":"0","confidence_adjustment":"+5"},"rationale":"Seminar: liquidity improves reliability of levels due to institutional activity and better price discovery.","failure_modes":["In crises, even liquid assets gap; do not overtrust."],"page_refs":["p180"],"needs_verification":false}
{"id":"rule_low_liquidity_reduces_level_reliability","scope":"process","applies_to":["EXECUTION_LIQUIDITY_FILTERS"],"if":"instrument liquidity tier is low","then":{"interpretation":"Reduce confidence in technical signals and increase expected slippage; require stronger confirmations.","score_adjustment":"0","confidence_adjustment":"-10"},"rationale":"Seminar: low liquidity increases slippage and reduces reliability of levels.","failure_modes":["Some low-liquidity names still trend cleanly; keep this as a bias not absolute."],"page_refs":["p180"],"needs_verification":true}
{"id":"rule_min_price_gate_default_10","scope":"portfolio","applies_to":["EXECUTION_LIQUIDITY_FILTERS"],"if":"instrument price < 10 (default)","then":{"interpretation":"Fail minimum price gate: avoid or cap size due to spreads/noise and microcap effects.","score_adjustment":"n/a","confidence_adjustment":"-10"},"rationale":"Seminar scanner example includes price > $10.","failure_modes":["For some markets (FX/futures) price scale differs; apply only to equities."],"page_refs":["p181"],"needs_verification":false}
{"id":"rule_translate_adtv_to_dollar_volume_for_etfs","scope":"process","applies_to":["EXECUTION_LIQUIDITY_FILTERS"],"if":"instrument is ETF and shares-based ADTV is misleading","then":{"interpretation":"Use average daily $ volume (price * shares) for liquidity gating.","score_adjustment":"n/a","confidence_adjustment":"n/a"},"rationale":"Operational adaptation: ETF share counts vary; $ volume better reflects tradability.","failure_modes":["Data availability; use best available liquidity proxy."],"page_refs":["p179"],"needs_verification":true}
{"id":"rule_liquidity_gate_affects_position_size","scope":"portfolio","applies_to":["EXECUTION_LIQUIDITY_FILTERS"],"if":"liquidity gate fails OR liquidity tier low","then":{"interpretation":"Reduce position size and/or cap risk budget contribution for that instrument.","score_adjustment":"n/a","confidence_adjustment":"n/a"},"rationale":"Seminar connects higher liquidity with lower slippage and better execution.","failure_modes":["Overly restrictive in niche strategies; allow manual overrides with logging."],"page_refs":["p179","p180"],"needs_verification":false}
{"id":"rule_contradiction_strong_technical_signal_low_liquidity","scope":"portfolio","applies_to":["EXECUTION_LIQUIDITY_FILTERS","TECH_MOVING_AVERAGES","TECH_VOLUME_CONFIRMATION","TECH_OSCILLATORS"],"if":"technical signals are strong BUT liquidity gate fails or tier is low","then":{"interpretation":"Contradiction: signal quality vs execution risk. Require manual review; do not scale aggressively.","score_adjustment":"0","confidence_adjustment":"-15"},"rationale":"Seminar: liquidity affects reliability and slippage; strong signals in illiquid names are riskier.","failure_modes":["Sometimes illiquid names trend strongly; still requires caution."],"page_refs":["p180"],"needs_verification":true}
{"id":"rule_liquidity_metrics_must_be_in_snapshot","scope":"process","applies_to":["EXECUTION_LIQUIDITY_FILTERS"],"if":"running weekly snapshot/report","then":{"interpretation":"Always include ADTV (or $ volume) and pass/fail gates to support auditability and explainability.","score_adjustment":"n/a","confidence_adjustment":"n/a"},"rationale":"Operational requirement implied by using scanner/gates; supports process discipline.","failure_modes":["None; small payload."],"page_refs":["p179","p181"],"needs_verification":true}
{"id":"rule_gate_scope_equities_only","scope":"process","applies_to":["EXECUTION_LIQUIDITY_FILTERS"],"if":"instrument is not equity/ETF (e.g., rates/fx/commodities futures)","then":{"interpretation":"Do not apply price>$10 gate; use asset-appropriate liquidity proxies (open interest, bid-ask, turnover).","score_adjustment":"n/a","confidence_adjustment":"n/a"},"rationale":"Scanner thresholds are equity-specific; avoid misapplying across asset classes.","failure_modes":["Cross-asset gating requires separate configuration."],"page_refs":["p181"],"needs_verification":true}
{"id":"rule_default_thresholds_are_configurable","scope":"process","applies_to":["EXECUTION_LIQUIDITY_FILTERS"],"if":"implementing gates in IPOS","then":{"interpretation":"Treat thresholds (ADTV, price) as defaults; keep configurable per market and instrument type.","score_adjustment":"n/a","confidence_adjustment":"n/a"},"rationale":"Operational best practice; seminar thresholds are examples, not universal constants.","failure_modes":["Too many knobs; keep defaults and only override when needed."],"page_refs":["p181"],"needs_verification":true}



module_id: EXECUTION_LIQUIDITY_FILTERS
scope: module
tags: [execution, liquidity, slippage, tradability, risk_controls]
version: 0.1
source: seminar_pdf
cadence: weekly


## Purpose
Reduce operational risk by enforcing **tradability gates**:
- avoid instruments where **slippage/spreads** dominate,
- improve reliability of technical levels (support/resistance),
- make liquidity constraints explicit in the weekly snapshot.

## Inputs (weekly)
- For equities/ETFs:
  - `adtv_shares` (avg daily shares) and/or `avg_dollar_volume`
  - `last_price`
- For other assets (rates/fx/commodities):
  - use appropriate proxies (open interest, bid-ask, turnover) — configuration-driven

## Outputs (weekly)
- `liquidity_tier` ∈ {LOW, MED, HIGH}
- `liquidity_gate_pass` (bool)
- `price_gate_pass` (bool)  // equities only
- `execution_confidence_modifier` (signed)
- `execution_size_cap` (multiplier)
- `contradiction_flags` (list)

---

## Core Principles (explicit)
- Higher liquidity:
  - lowers slippage
  - increases reliability of technical levels
  - reflects stronger institutional participation (better price discovery)

---

## Default Gates (MVP)
### 1) Liquidity gate (equities)
- Default: **ADTV ≥ 400k shares/day** (example threshold)
- If ETF: prefer **avg $ volume** (price × shares) as more comparable.

### 2) Minimum price gate (equities)
- Default: **price ≥ $10** (example threshold)

**Note:** These are defaults; keep configurable per market/instrument.

---

## Governance Effects (how gates impact IPOS)
### If gates pass (HIGH liquidity)
- Increase confidence in technical signals slightly (MA, breakouts, volume behavior)
- Allow normal sizing under the global risk budget

### If liquidity gate fails / LOW tier
- Reduce confidence in technical signals
- Increase expected slippage assumption
- Enforce **position size reduction** or exclude instrument

### If price gate fails (equities)
- Treat as higher noise/spread risk (microcap/low-price effects)
- Exclude or cap size strongly

---

## Contradictions (trigger investigation)
- Strong technical signals but liquidity gate fails / LOW tier
  - contradiction: “signal quality vs execution risk”
  - require manual review; do not scale aggressively
- Breakout confirmations in illiquid names
  - treat as higher false breakout risk due to slippage + thin order books

---

## Snapshot Requirements (AI + auditability)
Always include:
- ADTV (or avg $ volume)
- liquidity_tier
- gate pass/fail flags
- size cap applied
- any contradiction flags

This keeps weekly reports explainable and prevents “invisible” execution risk.

---

## Implementation Notes (IPOS-friendly)
- Encode as a **pre-trade governor** (applies before scoring/stance execution).
- If you keep instruments in the DB but fail gates:
  - still compute scores (for learning),
  - but enforce the size cap and label as “non-tradable” for action.

---

## NEXT ACTION (say “continue”)
**Stage:** DOC_MAP  
**Pages:** 183–205 (autonomous)  
**Focus:** Find any remaining **high-impact indicators, scan rules, or risk constraints** (especially anything that can map to 0–100 scoring or contradiction detection).

## DOC_MAP (Autonomous) — Seminar PDF → IPOS Extraction Queue (Options Intro + Risk Management Core)
**PDF:** `/mnt/data/onvista Aktien-Intensiv-Seminar 11-2025.pdf`  
**Chunk analyzed:** pages **183–205** (1-based)  
**ROI lens:** macro-first IPOS (A2) → prioritize **portfolio risk governance**; treat **options/warrants primer** as optional/deferred.

```json
{
  "chunk": {
    "pages": "183-205",
    "density": "medium",
    "topics": [
      "Optionsscheine (warrants) basics",
      "Option Greeks (Delta/Gamma/Vega/Theta)",
      "Implied volatility + event risk",
      "Risk management (investing)",
      "Risk & money management (trading)",
      "Drawdown recovery math (loss pyramid)",
      "Losing streak probability",
      "Max risk per trade from drawdown cap",
      "Chance-risk ratio (section start)"
    ],
    "subtopics": [
      "Warrant lifetime, expiry, in-the-money payout logic",
      "Bezugsverhältnis (ratio) adjustment for Greeks",
      "Delta as price sensitivity and ITM probability; Delta ranges ITM/ATM/OTM",
      "Gamma as delta-of-delta; higher near ATM and nearer expiry",
      "Vega: options expensive when volatility high; volatility rises before events; prefer buying when IV is low",
      "Theta: time decay increases as expiry approaches",
      "Investing risk management: diversification across asset classes (rates/commodities) + regional diversification; tradeoff vs performance",
      "Correlation risk: too many stocks in one sector increases risk; control correlation via sector diversification and/or market leader selection",
      "Trading risk framework: define trading capital fraction; define max portfolio risk; define max initial position risk (emotionally tolerable)",
      "Loss pyramid: drawdown requires disproportionate recovery; absolute limits implied",
      "Losing streak likelihood depends on hit rate and trade frequency",
      "Drawdown cap example: max drawdown should not exceed 30%; derive max risk per trade ~1.66% (30%/18)",
      "Chance-risk ratio section begins here (likely continues beyond p205)"
    ]
  },
  "extract_targets": {
    "indicator_pages": [],
    "rules_pages": [
      "191-194 (IV/time decay principles if ever used for derivatives module)",
      "197-199 (diversification + correlation + risk budget definitions)",
      "200 (loss pyramid concept)",
      "204 (max DD 30% and risk-per-trade derivation 1.66%)",
      "205 (CRV section start; continuation likely beyond)"
    ],
    "process_pages": [
      "197-199",
      "200",
      "201-203 (losing streak tables; likely chart/table-heavy)",
      "204-205"
    ],
    "chart_or_table_heavy_pages": [
      "200-203 (loss pyramid + streak probability tables)"
    ],
    "low_value_pages_for_macro_mvp": [
      "183-194 (options/warrants mechanics & Greeks unless you explicitly want derivatives execution rules)"
    ]
  },
  "likely_modules": [
    {
      "module_id": "RISK_MANAGEMENT_PORTFOLIO",
      "why": "Diversification across asset classes/regions + correlation control → directly supports A2 risk budget + contradictions."
    },
    {
      "module_id": "RISK_MANAGEMENT_TRADING_CAPS",
      "why": "Defines portfolio risk cap, position risk sizing, and drawdown-aware risk per trade (convert to risk budget rules)."
    },
    {
      "module_id": "DRAW_DOWN_AND_RECOVERY_GOVERNOR",
      "why": "Loss pyramid + max drawdown cap (30%) → can become a hard governor for risk budget limits."
    },
    {
      "module_id": "DERIVATIVES_OPTIONS_PRIMER",
      "why": "Options/warrants & Greeks; likely defer for macro-first MVP (unless you build an options execution layer)."
    }
  ],
  "recommended_next_chunks": [
    {
      "pages": "206-231",
      "why": "The Chance-Risk Ratio section likely continues; also possible further risk rules, execution constraints, or concluding process logic."
    }
  ],
  "checkpoint": {
    "pages_done": "183-205",
    "artifacts_written": ["doc_map"],
    "counts": { "chunks_mapped": 7 }
  }
}


## ROI_GATE (Autonomous) — Pages 183–205 (Risk Governance → Macro-first MVP)
**PDF:** `/mnt/data/onvista Aktien-Intensiv-Seminar 11-2025.pdf`  
**Chunk:** 183–205 (1-based)  
**MVP lens:** macro-first IPOS (A2) → prioritize **risk budget / drawdown / diversification / correlation**.  
**Defer:** options/warrants mechanics & Greeks unless you explicitly want a derivatives execution layer.

```json
{
  "active_now": [
    {
      "id": "PORTFOLIO_DIVERSIFICATION_ASSET_CLASSES",
      "type": "portfolio_rule_set",
      "why": "Directly informs A2 risk budget and stance constraints: rates + commodities reduce portfolio volatility; explicit tradeoff vs performance.",
      "page_refs": ["p197"]
    },
    {
      "id": "PORTFOLIO_DIVERSIFICATION_REGIONS",
      "type": "portfolio_rule_set",
      "why": "Reduces volatility / concentration risk; relevant to weekly risk posture even in macro-first system.",
      "page_refs": ["p197"]
    },
    {
      "id": "CORRELATION_RISK_SECTOR_CONCENTRATION",
      "type": "portfolio_rule_set",
      "why": "Operational contradiction driver: sector clustering creates hidden risk; useful for contradictions + confidence adjustments.",
      "page_refs": ["p198"]
    },
    {
      "id": "TRADING_CAPITAL_AND_RISK_CAPS",
      "type": "risk_framework",
      "why": "Defines practical sizing architecture: trading-capital fraction, max portfolio risk, max initial position risk (emotion tolerance). Maps cleanly to IPOS risk budget controls.",
      "page_refs": ["p199"]
    },
    {
      "id": "DRAWDOWN_RECOVERY_NONLINEARITY_LOSS_PYRAMID",
      "type": "risk_framework",
      "why": "High-impact governor: drawdowns require disproportionate recovery; supports hard risk budgeting and de-risking policies.",
      "page_refs": ["p200"]
    },
    {
      "id": "LOSING_STREAK_EXPECTATION_TABLE_TQ40",
      "type": "risk_framework",
      "why": "Justifies conservative per-trade risk: loss streaks are statistically inevitable; supports sizing discipline and ‘do not martingale’ posture.",
      "page_refs": ["p203"]
    },
    {
      "id": "MAX_DRAWDOWN_CAP_30_AND_RISK_PER_TRADE_1_66",
      "type": "hard_risk_rule",
      "why": "Concrete numeric governance: cap max drawdown at 30%; with TQ=40% example implies max loss streak 18 → risk/trade ≈ 1.66%. This is directly implementable as a default risk cap.",
      "page_refs": ["p204"]
    },
    {
      "id": "CRV_SECTION_START",
      "type": "pending_rule_set",
      "why": "Chance-risk ratio section starts here (details likely in next chunk). We already have CRV≥1.3 from earlier; this may add more guidance.",
      "page_refs": ["p205"]
    }
  ],
  "defer": [
    {
      "id": "WARRANTS_OPTIONS_PRIMER_GREEKS",
      "type": "derivatives_execution_layer",
      "why": "Options/warrants mechanics + Greeks are not needed for macro-first MVP unless you plan an options execution subsystem.",
      "page_refs": ["p183-194"]
    },
    {
      "id": "VEGA_IV_EVENT_TIMING_RULES",
      "type": "derivatives_tactical",
      "why": "Buying options when IV is low is useful but only relevant if you execute options strategies inside IPOS.",
      "page_refs": ["p191"]
    }
  ],
  "drop": [],
  "notes": [
    "Pages 201–202 are table-heavy with limited clean text extraction; p203 contains the readable losing-streak table.",
    "We will encode losing-streak logic generically (hit-rate driven) but keep the TQ=40% / 4000 trades example as reference."
  ],
  "checkpoint": {
    "pages_done": "183-205",
    "artifacts_written": ["roi_gate"],
    "counts": { "active_items": 8, "deferred_items": 2, "dropped_items": 0 }
  }
}

## PROCESS_EXTRACT (Autonomous) — `process.jsonl`
**PDF:** `/mnt/data/onvista Aktien-Intensiv-Seminar 11-2025.pdf`  
**Pages:** 183–205 (1-based)  
**ROI_GATE:** active items only (macro-first risk governance)  
**Batch cap:** 20 → extracted **9**

```jsonl
{"id":"process_diversify_across_asset_classes_reduce_volatility","topic":"risk_management_investing","statement":"Diversify across asset classes; rates add stability and reduce volatility, commodities can reduce volatility due to low/negative correlation.","operationalization":["In IPOS, enforce a diversification constraint at the portfolio layer: max contribution per asset bucket (Equity/Rates/Credit/FX/Commodities).","Use cross-asset correlation assumptions as a governance check: if portfolio becomes single-factor (equity beta), cap risk budget.","In weekly report: show asset-bucket weights + implied diversification score."],"page_refs":["p197"]}
{"id":"process_diversification_tradeoff_lower_vol_possible_lower_return","topic":"risk_management_investing","statement":"Diversification can reduce volatility and increase safety but may reduce performance.","operationalization":["Make diversification a configurable policy knob: 'risk-reduction priority' vs 'return-seeking priority'.","Report the tradeoff explicitly: diversification score vs trailing performance."],"page_refs":["p197"]}
{"id":"process_regional_diversification_reduces_volatility","topic":"risk_management_investing","statement":"Regional diversification reduces volatility and increases safety, but can reduce performance.","operationalization":["Track exposures by region (US/EU/Asia/EM) in snapshot metadata (even if implemented manually at first).","Add a contradiction flag if regional concentration is high while macro regime is uncertain."],"page_refs":["p197"]}
{"id":"process_correlation_risk_sector_concentration","topic":"risk_management_investing","statement":"Too many stocks in one sector/asset group increases risk; when the sector falls, many positions fall together.","operationalization":["Add a 'correlation risk' check: if too many exposures share the same driver (sector/credit beta/FX), reduce confidence and cap risk budget.","If you later add equity selection, enforce sector caps and/or prefer market leaders."],"page_refs":["p198"]}
{"id":"process_control_correlation_via_market_leader_or_sector_diversification","topic":"risk_management_investing","statement":"Control correlation by buying the market leader in a sector and/or diversifying sectors in the portfolio.","operationalization":["Encode as optional equity-layer policy: sector cap + leader preference tag.","In macro-first MVP: keep as a manual checklist line in weekly report until stock-layer exists."],"page_refs":["p198"]}
{"id":"process_define_trading_capital_fraction","topic":"risk_management_trading","statement":"Define trading capital as a fraction of total wealth (example: 20% of 100k = 20k).","operationalization":["In IPOS config, define `trading_capital` and `total_wealth` (optional) to compute risk in absolute € terms.","Use trading_capital as the base for all risk budgeting and sizing computations."],"page_refs":["p199"]}
{"id":"process_define_max_portfolio_risk_emotionally_tolerable","topic":"risk_management_trading","statement":"Define a maximum portfolio risk (example: 10% of trading capital = 2k) as an amount that supports emotional calm.","operationalization":["Create `max_portfolio_risk_amount` and/or `max_portfolio_risk_pct` as hard caps.","Map IPOS risk budget (0–100) to this cap (e.g., 100 ↔ max_portfolio_risk_pct).","If exceeded: force de-risk recommendations and log event."],"page_refs":["p199"]}
{"id":"process_define_max_initial_position_risk","topic":"risk_management_trading","statement":"Define a maximum initial position risk as a fixed amount depending on max number of positions (example: 200).","operationalization":["Config: `max_initial_position_risk_amount` (or %), derived from `max_positions`.","Enforce per-instrument size cap so stop distance × size ≤ max_initial_position_risk.","Include in snapshot: per-position risk estimate + pass/fail."],"page_refs":["p199"]}
{"id":"process_drawdown_governor_loss_pyramid_and_risk_per_trade","topic":"risk_management_trading","statement":"Drawdown recovery is nonlinear (loss pyramid). With a max drawdown cap of 30% and hit-rate example TQ=40%, max losing streak ~18 implies max risk per trade ≈ 1.66% (30%/18).","operationalization":["Set default policy: `max_drawdown_cap_pct = 30` (tunable).","Derive default `max_risk_per_trade_pct` from (max_drawdown_cap_pct / assumed_max_losing_streak). Use 1.66% as the seminar example default for TQ=40%.","Add a weekly governor: if realized drawdown approaches cap, progressively reduce risk budget and disallow adds.","Keep losing-streak logic generic: depends on hit rate and trade frequency; table is reference."],"page_refs":["p200","p203","p204"]}


## RULE_EXTRACT (Autonomous) — `rules.jsonl`
**PDF:** `/mnt/data/onvista Aktien-Intensiv-Seminar 11-2025.pdf`  
**Pages:** 183–205 (1-based)  
**ROI_GATE:** active items only (macro-first risk governance)  
**Batch cap:** 40 → extracted **18**

```jsonl
{"id":"rule_diversify_across_asset_classes_reduce_volatility","scope":"portfolio","applies_to":["RISK_MANAGEMENT_PORTFOLIO"],"if":"portfolio exposure is dominated by a single asset bucket (e.g., equity beta)","then":{"interpretation":"Increase diversification across asset classes (rates/commodities as stabilizers) and cap risk budget until diversification improves.","score_adjustment":"n/a","confidence_adjustment":"-10"},"rationale":"Diversification across asset classes reduces volatility; rates stabilize; commodities can reduce volatility due to lower correlation.","failure_modes":["Correlations rise in crises; diversification helps but is not a guarantee."],"page_refs":["p197"],"needs_verification":false}
{"id":"rule_diversification_tradeoff_acknowledged","scope":"process","applies_to":["RISK_MANAGEMENT_PORTFOLIO"],"if":"diversification constraints reduce returns in a strong single-factor trend","then":{"interpretation":"Allow configurable policy: prioritize safety (lower vol) vs performance (higher concentration), but log changes and keep caps explicit.","score_adjustment":"n/a","confidence_adjustment":"n/a"},"rationale":"Seminar notes diversification can reduce volatility and increase safety but may reduce performance.","failure_modes":["Policy drift; too many discretionary overrides."],"page_refs":["p197"],"needs_verification":false}
{"id":"rule_regional_diversification_reduce_concentration_risk","scope":"portfolio","applies_to":["RISK_MANAGEMENT_PORTFOLIO"],"if":"regional concentration is high (e.g., mostly one region)","then":{"interpretation":"Reduce risk budget and/or add cross-region diversification; flag concentration if macro regime uncertain.","score_adjustment":"n/a","confidence_adjustment":"-10"},"rationale":"Regional diversification reduces volatility and increases safety; concentration increases risk.","failure_modes":["Home bias may be intentional; keep as a warning + governor, not a forced action."],"page_refs":["p197"],"needs_verification":false}
{"id":"rule_sector_concentration_increases_correlation_risk","scope":"portfolio","applies_to":["RISK_MANAGEMENT_PORTFOLIO"],"if":"many exposures belong to one sector/driver cluster","then":{"interpretation":"Flag correlation risk and cap risk budget; require diversification or consolidation into fewer, higher-quality exposures.","score_adjustment":"n/a","confidence_adjustment":"-15"},"rationale":"Too many stocks in one sector increases risk; when the sector falls, many positions fall together.","failure_modes":["Sector leadership phases exist; allow bounded concentration with explicit logging."],"page_refs":["p198"],"needs_verification":false}
{"id":"rule_correlation_control_via_leader_or_sector_diversification","scope":"process","applies_to":["RISK_MANAGEMENT_PORTFOLIO"],"if":"sector exposure is required","then":{"interpretation":"Prefer market leader and/or diversify across sectors to reduce correlated drawdowns.","score_adjustment":"n/a","confidence_adjustment":"n/a"},"rationale":"Seminar: correlation can be controlled by market leader selection and sector diversification.","failure_modes":["Leader selection can be subjective; defer until equity-layer exists."],"page_refs":["p198"],"needs_verification":false}
{"id":"rule_define_trading_capital_base_for_risk","scope":"process","applies_to":["RISK_MANAGEMENT_TRADING_CAPS"],"if":"running the IPOS weekly risk budget","then":{"interpretation":"Use configured trading capital as the base for all risk and sizing computations (not total wealth).","score_adjustment":"n/a","confidence_adjustment":"n/a"},"rationale":"Seminar defines trading capital as a fraction of total wealth; sizing should reference that base.","failure_modes":["If trading capital changes, comparability breaks unless logged."],"page_refs":["p199"],"needs_verification":false}
{"id":"rule_set_max_portfolio_risk_cap","scope":"portfolio","applies_to":["RISK_MANAGEMENT_TRADING_CAPS"],"if":"risk budget would imply exposures beyond max portfolio risk","then":{"interpretation":"Hard-cap total portfolio risk at configured max (example: 10% of trading capital).","score_adjustment":"n/a","confidence_adjustment":"n/a"},"rationale":"Seminar: define max portfolio risk as an amount that supports emotional calm.","failure_modes":["Risk estimation errors; use conservative assumptions."],"page_refs":["p199"],"needs_verification":false}
{"id":"rule_set_max_initial_position_risk_cap","scope":"portfolio","applies_to":["RISK_MANAGEMENT_TRADING_CAPS"],"if":"any single position initial risk exceeds configured cap","then":{"interpretation":"Reduce size or widen stop logic (only if policy allows) so stop-distance × size ≤ max initial position risk.","score_adjustment":"n/a","confidence_adjustment":"n/a"},"rationale":"Seminar: define max initial position risk based on tolerable amount / number of positions.","failure_modes":["Stop distance estimation depends on regime; use regime-based stop policy."],"page_refs":["p199"],"needs_verification":false}
{"id":"rule_loss_pyramid_drawdown_recovery_nonlinear","scope":"process","applies_to":["DRAW_DOWN_AND_RECOVERY_GOVERNOR"],"if":"portfolio drawdown increases","then":{"interpretation":"Increase caution because required recovery becomes disproportionately larger; avoid compounding losses via oversized risk.","score_adjustment":"n/a","confidence_adjustment":"n/a"},"rationale":"Seminar loss pyramid: drawdown recovery is nonlinear; larger losses need much larger gains to recover.","failure_modes":["Overreacting to small drawdowns; apply progressive reductions."],"page_refs":["p200"],"needs_verification":false}
{"id":"rule_max_drawdown_cap_default_30","scope":"portfolio","applies_to":["DRAW_DOWN_AND_RECOVERY_GOVERNOR"],"if":"risk policy is not configured yet","then":{"interpretation":"Use default max drawdown cap of 30% (example) as a hard governance constraint; tune later.","score_adjustment":"n/a","confidence_adjustment":"n/a"},"rationale":"Seminar example uses max drawdown cap 30%.","failure_modes":["User risk tolerance may differ; must be configurable."],"page_refs":["p204"],"needs_verification":false}
{"id":"rule_derive_max_risk_per_trade_from_dd_cap","scope":"portfolio","applies_to":["RISK_MANAGEMENT_TRADING_CAPS","DRAW_DOWN_AND_RECOVERY_GOVERNOR"],"if":"max_drawdown_cap_pct is set AND assumed_max_losing_streak is set","then":{"interpretation":"Set max risk per trade ≈ max_drawdown_cap_pct / assumed_max_losing_streak (seminar example: 30%/18 ≈ 1.67%).","score_adjustment":"n/a","confidence_adjustment":"n/a"},"rationale":"Seminar derives risk/trade from DD cap and losing streak (TQ=40% example: 18 losses).","failure_modes":["Assumed losing streak depends on hit rate and trade count; treat as policy with conservative defaults."],"page_refs":["p203","p204"],"needs_verification":false}
{"id":"rule_losing_streaks_are_statistically_inevitable","scope":"process","applies_to":["RISK_MANAGEMENT_TRADING_CAPS"],"if":"planning risk sizing based on 'unlikely to lose many times in a row'","then":{"interpretation":"Reject that assumption; losing streaks occur with high probability over many trades; size accordingly.","score_adjustment":"n/a","confidence_adjustment":"n/a"},"rationale":"Seminar table shows losing streaks are likely even with decent hit rates when trade count is high.","failure_modes":["Small sample periods can mislead; keep sizing stable."],"page_refs":["p203"],"needs_verification":false}
{"id":"rule_progressive_derisk_near_drawdown_cap","scope":"portfolio","applies_to":["DRAW_DOWN_AND_RECOVERY_GOVERNOR"],"if":"realized drawdown approaches the drawdown cap (e.g., >80% of cap)","then":{"interpretation":"Progressively reduce risk budget and disallow adds; prioritize capital preservation until drawdown recovers.","score_adjustment":"n/a","confidence_adjustment":"-10"},"rationale":"Operational extension of loss pyramid + drawdown cap: avoid catastrophic compounding near limits.","failure_modes":["Too strict can delay recovery; allow gradual re-risking rules later."],"page_refs":["p200","p204"],"needs_verification":true}
{"id":"rule_contradiction_high_risk_budget_while_drawdown_high","scope":"portfolio","applies_to":["DRAW_DOWN_AND_RECOVERY_GOVERNOR"],"if":"risk budget suggests risk-on BUT realized drawdown is high/near cap","then":{"interpretation":"Contradiction: signals vs risk state. Override: cap risk and focus on recovery mode.","score_adjustment":"n/a","confidence_adjustment":"-15"},"rationale":"Drawdown governor should override tactical signals to prevent ruin risk.","failure_modes":["Strong rebounds exist; allow small probes only."],"page_refs":["p200","p204"],"needs_verification":true}
{"id":"rule_contradiction_concentration_high_when_regime_uncertain","scope":"portfolio","applies_to":["RISK_MANAGEMENT_PORTFOLIO","MARKET_CONDITIONS"],"if":"concentration/correlation risk is high AND regime_confidence is low/UNCERTAIN","then":{"interpretation":"Contradiction: unclear environment + concentrated exposure. Reduce risk budget and demand diversification.","score_adjustment":"n/a","confidence_adjustment":"-15"},"rationale":"Concentration magnifies risk; uncertainty increases error; together warrant caution.","failure_modes":["If concentration is intentional and hedged, downgrade severity."],"page_refs":["p198","p59"],"needs_verification":true}
{"id":"rule_risk_caps_must_be_logged_in_snapshot","scope":"process","applies_to":["RISK_MANAGEMENT_TRADING_CAPS"],"if":"weekly snapshot/report is produced","then":{"interpretation":"Always include trading capital base, max portfolio risk cap, max position risk cap, drawdown cap, and risk-per-trade cap (if used).","score_adjustment":"n/a","confidence_adjustment":"n/a"},"rationale":"Operational necessity: governance must be transparent and auditable.","failure_modes":["None; small payload cost."],"page_refs":["p199","p204"],"needs_verification":true}
{"id":"rule_crv_section_pending_extract_next_chunk","scope":"process","applies_to":["RISK_MANAGEMENT_TRADING_CAPS"],"if":"CRV guidance is needed beyond CRV≥1.3 already captured earlier","then":{"interpretation":"Defer to next chunk extraction (206–231) where CRV section likely continues; do not invent additional thresholds now.","score_adjustment":"n/a","confidence_adjustment":"n/a"},"rationale":"CRV section begins at p205; details likely continue after p205.","failure_modes":["None; avoid hallucination."],"page_refs":["p205"],"needs_verification":false}


---
module_id: DRAW_DOWN_AND_RECOVERY_GOVERNOR
scope: module
tags: [risk_budget, drawdown, portfolio_caps, governance, diversification]
version: 0.1
source: seminar_pdf
cadence: weekly
---

## Purpose
Provide the **hard risk governors** that override tactical signals when needed:
- diversification & correlation checks,
- trading capital base + portfolio/position risk caps,
- drawdown cap logic (“loss pyramid”),
- derived max risk-per-trade example (30%/18 ≈ 1.67%),
- contradiction overrides for capital preservation.

## Inputs (weekly)
- Portfolio metadata (can be manual in MVP):
  - `trading_capital`
  - exposures by bucket (Equity/Rates/Credit/FX/Commodities)
  - exposures by region/sector (optional)
- Risk state:
  - `realized_drawdown_pct` (vs peak)
  - `max_drawdown_cap_pct` (default 30)
  - `max_portfolio_risk_pct` (policy)
  - `max_initial_position_risk_pct` or amount (policy)
  - `assumed_hit_rate` (optional) and `assumed_max_losing_streak` (policy)
- Signals context:
  - `risk_budget_suggested` (0–100)
  - `regime_confidence`

## Outputs (weekly)
- `risk_budget_cap` (0–100)
- `risk_mode` ∈ {NORMAL, CAUTION, RECOVERY, DEFENSIVE}
- `risk_per_trade_cap_pct` (if used)
- `diversification_score` (0–100, coarse)
- `correlation_risk_flag` (bool)
- `override_flags` (list)

---

## Core Principles
### Diversification
- Cross-asset diversification reduces volatility; rates stabilize; commodities can reduce volatility due to lower correlation.
- Regional diversification reduces concentration risk.
- Diversification may reduce performance → must be a configurable policy choice.

### Correlation risk
- Sector/driver clustering increases risk: many positions fall together.
- When environment is uncertain, concentration risk is especially dangerous.

### Loss pyramid (drawdown recovery)
- Drawdown recovery is **nonlinear**:
  - larger losses require disproportionately larger gains to recover.
- Therefore, risk must be reduced as drawdown grows.

---

## Default Governance (MVP)
### 1) Drawdown cap (hard)
- Default `max_drawdown_cap_pct = 30` (example; configurable)
- Define thresholds for progressive de-risking:
  - `CAUTION` when drawdown > 50% of cap
  - `RECOVERY` when drawdown > 80% of cap
  - `DEFENSIVE` when drawdown approaches cap

### 2) Derived max risk per trade (example policy)
- Seminar example (TQ=40%): max losing streak ≈ 18
- With DD cap 30% → max risk/trade ≈ `30% / 18 ≈ 1.67%`
- Treat as a **default** until you set your own hit-rate/streak assumptions.

### 3) Portfolio and position caps
- `max_portfolio_risk_pct`: hard cap for total portfolio risk (config)
- `max_initial_position_risk_pct/amount`: hard cap per position (config)
- Use trading capital as base (not total wealth).

---

## Overrides (how this module caps risk)
### Risk budget cap logic (simple)
- Start with `risk_budget_cap = risk_budget_suggested`
- Apply hard constraints:
  - If drawdown in RECOVERY/DEFENSIVE → cap risk_budget_cap lower
  - If concentration/correlation risk high → cap risk_budget_cap lower
  - If regime_confidence low + concentration high → cap further

**Rule of thumb caps (MVP defaults)**
- NORMAL: cap = 100
- CAUTION: cap = 70
- RECOVERY: cap = 40
- DEFENSIVE: cap = 25

---

## Contradictions (override wins)
- Risk budget signals risk-on while drawdown is high/near cap
  - override: RECOVERY/DEFENSIVE caps apply
- High concentration (sector/driver) while regime uncertain
  - override: reduce risk budget; require diversification
- Strong tactical setups but portfolio caps would be exceeded
  - override: size down or skip

---

## Snapshot Requirements (AI-safe)
Include:
- trading capital base
- drawdown %, drawdown cap %, risk mode
- portfolio/position caps
- risk-per-trade cap (if used)
- diversification score + correlation flags
- overrides applied (why)

---

## Implementation Notes (IPOS-friendly)
- Start with manual entry for exposures and drawdown in MVP.
- Later automate using broker exports or portfolio CSV.
- Keep all caps configurable, but ship sensible defaults.

---

## NEXT ACTION (say “continue”)
**Stage:** DOC_MAP  
**Pages:** 206–231 (autonomous)  
**Focus:** Continue the **Chance–Risk Ratio** section and any remaining hard risk constraints. Extract only explicit numeric thresholds or operational decision rules (no fluff).


## DOC_MAP (Autonomous) — Seminar PDF → IPOS Extraction Queue (CRV + Trailing Stops + Scanner Criteria)
**PDF:** `/mnt/data/onvista Aktien-Intensiv-Seminar 11-2025.pdf`  
**Chunk analyzed:** pages **206–231** (1-based)  
**Composite policy:** treat proprietary/composites as **external inputs** (no rebuilding)  
**ROI focus:** weekly governance + implementable rules (risk/CRV/stop policies)

```json
{
  "chunk": {
    "pages": "206-231",
    "density": "medium",
    "topics": [
      "Chance–Risk Ratio (CRV) / expectancy",
      "Trailing stops (forms + examples)",
      "Relative High/Low stop (swing-based trailing)",
      "Donchian Channel stop (channel-based trailing)",
      "Technical scanner criteria (Goersch Signals)",
      "Tool/platform references (TradingView, dashboards)"
    ],
    "subtopics": [
      "CRV definition: expected gain relative to risk (R-multiples)",
      "Profit tables after 100 trades for CRV 1:1 / 2:1 / 3:1 at varying win rates",
      "Trailing stops purpose: secure profits / reduce risk (phase 2 management)",
      "Relative High/Low stop: stop follows swing lows/highs; can be wide; simple and pattern-aligned",
      "Donchian channel stop examples (14 vs 10 period) => shorter period = tighter stop",
      "Scanner goals: strong-trend candidates / strong breakouts / DE equities (TradingView screens)",
      "Goersch Signals scanner inputs (explicit list):",
      "  - Goersch Trend (D) positive; Goersch Trend (W) positive (proprietary)",
      "  - Slow Stochastic K < 50 and K crosses D from below",
      "  - EMA(13) > EMA(48)",
      "  - Chaikin Money Flow positive"
    ]
  },
  "extract_targets": {
    "indicator_pages": [
      "226 (EMA13/EMA48, Chaikin Money Flow; Goersch Trend as external series if used)"
    ],
    "rules_pages": [
      "206-209 (CRV tables => expectancy logic and win-rate thresholds)",
      "211-212 (trailing stop forms + pros/cons)",
      "218-219 (Donchian stop parameter effect)",
      "226 (scanner rule set)"
    ],
    "process_pages": [
      "206 (CRV definition)",
      "211-212 (stop policy definitions)",
      "218-219 (parameterization guidance)",
      "226 (scanner objective for bullish phases)"
    ],
    "low_value_pages": [
      "220-225 (TradingView screener placeholders/screenshots)",
      "227-231 (tool promo/contact)"
    ]
  },
  "likely_modules": [
    {
      "module_id": "EXPECTANCY_CRV",
      "why": "CRV tables translate into a robust expectancy model: profitability depends on win rate and R-multiple. High ROI for risk governance and sizing discipline."
    },
    {
      "module_id": "TRAILING_STOP_POLICIES",
      "why": "Concrete trailing stop policies (swing-based, Donchian) can be used as execution policy selectors and explained in weekly reports."
    },
    {
      "module_id": "OPTIONAL_TECH_SCANNER_GOERSCH_SIGNALS",
      "why": "Explicit scan criteria (EMA13/48, CMF, Stoch cross, proprietary Goersch Trend). Likely optional/deferred for macro-first MVP."
    }
  ],
  "recommended_next_chunks": [],
  "checkpoint": {
    "pages_done": "206-231",
    "artifacts_written": ["doc_map"],
    "counts": { "chunks_mapped": 8 },
    "pdf_status": "end_of_document_reached"
  }
}

## ROI_GATE (Autonomous) — Pages 206–231 (CRV + Trailing Stops + Optional Scanner)
**PDF:** `/mnt/data/onvista Aktien-Intensiv-Seminar 11-2025.pdf`  
**Chunk:** 206–231 (1-based)  
**MVP lens:** macro-first IPOS (A2) → prioritize **governance rules** that generalize across markets.  
**Composite policy:** proprietary/composites remain **external** (no rebuilding).

```json
{
  "active_now": [
    {
      "id": "EXPECTANCY_CRV_CORE",
      "type": "risk_framework",
      "why": "High-ROI, universal: expectancy depends on win rate and R-multiple (CRV). Directly improves weekly risk discipline, sizing governance, and ‘when to add risk’ logic.",
      "page_refs": ["p206-209"]
    },
    {
      "id": "TRAILING_STOP_POLICIES_RELATIVE_HILO",
      "type": "execution_policy",
      "why": "Simple, robust stop policy selector that aligns with swing structure already extracted (trend/regime modules). Adds explainability to weekly reports without needing extra data sources.",
      "page_refs": ["p211-212"]
    },
    {
      "id": "TRAILING_STOP_POLICIES_DONCHIAN",
      "type": "execution_policy",
      "why": "Parameterized channel stop (period controls tightness). Implementable from price only; useful as an alternative trailing policy for TRENDY/MOMENTUM regimes.",
      "page_refs": ["p218-219"]
    }
  ],
  "defer": [
    {
      "id": "GOERSCH_SIGNALS_SCANNER_FULL",
      "type": "optional_equity_scanner",
      "why": "Scanner is equity-selection oriented and includes proprietary Goersch Trend; outside macro-first MVP. Keep as optional phase-2 feature.",
      "page_refs": ["p220-226"]
    },
    {
      "id": "GOERSCH_TREND_PROPRIETARY",
      "type": "composite_indicator",
      "why": "Proprietary; not precisely defined. Treat as external series only if you already have it from the vendor/platform.",
      "page_refs": ["p226"]
    },
    {
      "id": "TRADINGVIEW_SCREENSHOTS_AND_TOOL_REFERENCES",
      "type": "reference_material",
      "why": "Low operational value for the IPOS engine; keep as links/notes only.",
      "page_refs": ["p220-225","p227-231"]
    }
  ],
  "optional_quick_add": [
    {
      "id": "NON_PROPRIETARY_SCAN_COMPONENTS",
      "type": "indicator_candidates",
      "why": "If we want a small extra lift in technical breadth later: EMA13/EMA48 cross + Chaikin Money Flow + Stoch cross are implementable from OHLCV. Not required for macro-first MVP right now.",
      "page_refs": ["p226"]
    }
  ],
  "drop": [],
  "notes": [
    "We already captured CRV≥1.3 earlier; this chunk adds expectancy tables/logic (win-rate × CRV).",
    "Trailing stop policies should be implemented as policy selectors (metadata + parameters), not as a full backtest system in MVP.",
    "Avoid building any proprietary ‘Goersch Trend’ internals."
  ],
  "checkpoint": {
    "pages_done": "206-231",
    "artifacts_written": ["roi_gate"],
    "counts": { "active_items": 3, "deferred_items": 3, "optional_quick_add": 1, "dropped_items": 0 },
    "pdf_status": "end_of_document_reached"
  }
}

## PROCESS_EXTRACT (Autonomous) — `process.jsonl`
**PDF:** `/mnt/data/onvista Aktien-Intensiv-Seminar 11-2025.pdf`  
**Pages:** 206–231 (1-based)  
**ROI_GATE:** active items only  
**Batch cap:** 20 → extracted **8**

```jsonl
{"id":"process_crv_is_r_multiple_expected_gain_vs_risk","topic":"expectancy_crv","statement":"Chance–Risk Ratio (CRV) describes expected gain relative to risk in R-multiples (reward vs defined risk).","operationalization":["In IPOS, store per-signal expected_reward_R and defined_risk_R (or stop-distance-based risk).","Compute CRV = expected_reward_R / defined_risk_R and apply CRV gates (already: CRV≥1.3).","Display CRV in weekly report for any proposed adds or tactical actions."],"page_refs":["p206"]}
{"id":"process_expectancy_depends_on_win_rate_and_crv","topic":"expectancy_crv","statement":"Profitability over many trades depends jointly on win rate and CRV (R-multiple). Higher CRV can compensate for lower win rate.","operationalization":["Model expectancy E ≈ p_win*avg_win_R - (1-p_win)*avg_loss_R (where avg_loss_R ≈ 1 by definition).","Use expectancy logic as a governance explanation: do not chase high win rate with poor CRV; enforce CRV floor.","In weekly OS: require stronger confirmation for low-CRV setups; allow more flexibility if CRV is high and risk is controlled."],"page_refs":["p206-209"]}
{"id":"process_use_crv_tables_as_intuition_not_overfit","topic":"expectancy_crv","statement":"CRV outcome tables (after 100 trades) illustrate how different CRVs and win rates compound results; use them as intuition, not as precise forecasting.","operationalization":["Store a short reference note in Playbook: CRV/win-rate tradeoff.","Do not hardcode exact table values into the engine; use them for user understanding and discipline."],"page_refs":["p206-209"]}
{"id":"process_trailing_stop_phase2_profit_protection","topic":"trailing_stops","statement":"Trailing stops are used to secure profits and reduce risk after entry (management phase).","operationalization":["In IPOS, treat trailing stop as an execution policy selector attached to regime (CHOPPY/TRENDY/MOMENTUM).","Log the chosen trailing policy in snapshot for explainability."],"page_refs":["p211"]}
{"id":"process_relative_hilo_stop_follows_swings","topic":"trailing_stops","statement":"Relative High/Low trailing stop follows swing lows/highs (structure-based) and can be wide but aligns with trend swings.","operationalization":["Implement as policy: stop = last swing low (long) / last swing high (short), updated on new swing formation.","Best paired with TREND_STRUCTURE module already in IPOS.","Expose as an option in regime policies (TRENDY default)."],"page_refs":["p211","p212"]}
{"id":"process_relative_hilo_stop_is_simple_and_pattern_aligned","topic":"trailing_stops","statement":"Relative High/Low stop is simple and consistent with chart patterns; it tends to keep positions through normal pullbacks.","operationalization":["Use as default trailing policy when regime is TRENDY and alignment_score is high.","If market becomes CHOPPY or TRENDLESS, tighten policy or reduce size instead of widening further."],"page_refs":["p212"]}
{"id":"process_donchian_channel_stop_trails_by_channel","topic":"trailing_stops","statement":"Donchian channel trailing stop uses highest high / lowest low over a lookback window; it can be parameterized by period length.","operationalization":["Policy: for long positions, stop = lowest low over N periods; for shorts, stop = highest high over N periods (variant configurable).","Store parameter N in policy selector; compute from weekly bars.","Use as alternate trailing policy in TRENDY/MOMENTUM when you want systematic trailing."],"page_refs":["p218","p219"]}
{"id":"process_donchian_period_controls_tightness","topic":"trailing_stops","statement":"Shorter Donchian periods (e.g., 10) are tighter (more exits/churn); longer periods (e.g., 14) give more room (fewer exits).","operationalization":["Encode policy guidance: choose smaller N in MOMENTUM if you want tighter risk control; choose larger N in TRENDY for trend capture.","Expose N as a configurable parameter with defaults (e.g., N=14 TRENDY, N=10 MOMENTUM)."],"page_refs":["p218","p219"]}

## RULE_EXTRACT (Autonomous) — `rules.jsonl`
**PDF:** `/mnt/data/onvista Aktien-Intensiv-Seminar 11-2025.pdf`  
**Pages:** 206–231 (1-based)  
**ROI_GATE:** active items only (Expectancy/CRV + trailing stop policies)  
**Batch cap:** 40 → extracted **18** (governance + policy selectors)

```jsonl
{"id":"rule_crv_definition_r_multiple","scope":"process","applies_to":["EXPECTANCY_CRV"],"if":"evaluating any setup/add/scale decision","then":{"interpretation":"Express payoff in R-multiples: CRV = expected_reward_R / defined_risk_R.","score_adjustment":"n/a","confidence_adjustment":"n/a"},"rationale":"CRV is defined as expected gain relative to risk (R-multiple framing).","failure_modes":["Reward/risk estimates can be noisy; use conservative assumptions."],"page_refs":["p206"],"needs_verification":false}
{"id":"rule_expectancy_joint_winrate_and_crv","scope":"process","applies_to":["EXPECTANCY_CRV"],"if":"assessing long-run profitability logic","then":{"interpretation":"Profitability depends jointly on win rate and CRV; higher CRV can compensate for lower win rate.","score_adjustment":"n/a","confidence_adjustment":"n/a"},"rationale":"Seminar tables illustrate outcomes by win rate × CRV after 100 trades.","failure_modes":["Overfitting to table values; use as intuition not forecasting."],"page_refs":["p206-209"],"needs_verification":false}
{"id":"rule_do_not_optimize_for_winrate_only","scope":"process","applies_to":["EXPECTANCY_CRV"],"if":"a strategy seems great only because win rate is high but CRV is low","then":{"interpretation":"Treat as fragile; require CRV floor and/or reduce sizing; do not chase win rate at expense of payoff quality.","score_adjustment":"n/a","confidence_adjustment":"-5"},"rationale":"Tables imply CRV materially influences long-run results; win rate alone is insufficient.","failure_modes":["Some market-making styles rely on high win rate; outside MVP scope."],"page_refs":["p206-209"],"needs_verification":true}
{"id":"rule_crv_floor_applies_to_adds_and_entries","scope":"portfolio","applies_to":["EXPECTANCY_CRV","RISK_REWARD_FLOOR"],"if":"CRV < 1.3 for an entry or add","then":{"interpretation":"Do not take/scale; reduce size or skip. (Hard gate)","score_adjustment":"n/a","confidence_adjustment":"n/a"},"rationale":"CRV gate already captured earlier; reinforced here as the core discipline layer alongside expectancy logic.","failure_modes":["CRV estimation errors; require conservative reward projection."],"page_refs":["p206","p108"],"needs_verification":true}
{"id":"rule_expectancy_used_as_governance_explanation","scope":"process","applies_to":["EXPECTANCY_CRV"],"if":"generating weekly report explanations","then":{"interpretation":"Explain decisions using expectancy logic: win rate × payoff, not vibes. Avoid quoting exact table values; summarize the tradeoff.","score_adjustment":"n/a","confidence_adjustment":"n/a"},"rationale":"Seminar presents CRV outcome tables as educational guidance.","failure_modes":["Too much math in report; keep concise."],"page_refs":["p206-209"],"needs_verification":false}
{"id":"rule_trailing_stop_is_phase2_management","scope":"process","applies_to":["TRAILING_STOP_POLICIES"],"if":"position is open and management is active","then":{"interpretation":"Trailing stops are phase-2 tools for profit protection and risk reduction; select policy by regime and structure.","score_adjustment":"n/a","confidence_adjustment":"n/a"},"rationale":"Seminar frames trailing stops as management tools to secure profits / reduce risk.","failure_modes":["Over-tight trailing in trends causes churn."],"page_refs":["p211"],"needs_verification":false}
{"id":"rule_policy_selector_relative_hilo","scope":"process","applies_to":["TRAILING_STOP_POLICIES"],"if":"regime is TRENDY and swing structure is well-defined","then":{"interpretation":"Prefer Relative High/Low trailing: stop follows swing lows/highs; keeps position through normal pullbacks.","score_adjustment":"n/a","confidence_adjustment":"+5"},"rationale":"Relative Hi/Lo stop aligns with swing structure and can be wide but trend-consistent.","failure_modes":["Too wide in momentum reversals; pair with regime changes."],"page_refs":["p211-212"],"needs_verification":false}
{"id":"rule_relative_hilo_requires_objective_swings","scope":"process","applies_to":["TRAILING_STOP_POLICIES","TREND_STRUCTURE"],"if":"using Relative High/Low stop","then":{"interpretation":"Use objective pivot highs/lows (not subjective trendlines) to update stop levels.","score_adjustment":"n/a","confidence_adjustment":"n/a"},"rationale":"Relative stop depends on swing points; earlier lesson: prefer objective levels over drawn trendlines.","failure_modes":["Pivot sensitivity; choose stable weekly pivots."],"page_refs":["p211-212","p118"],"needs_verification":true}
{"id":"rule_relative_hilo_not_for_choppy_uncertain","scope":"process","applies_to":["TRAILING_STOP_POLICIES","MARKET_CONDITIONS"],"if":"regime is CHOPPY or transition_state is TRENDLESS/UNCERTAIN","then":{"interpretation":"Avoid wide swing-based trailing as default; instead cap risk and consider tighter management or reduced exposure.","score_adjustment":"n/a","confidence_adjustment":"-5"},"rationale":"In choppy/uncertain markets, wide trailing can lead to poor R outcomes and whipsaws; governance favors defensive posture.","failure_modes":["Occasional breakouts; allow small probes only."],"page_refs":["p59","p211"],"needs_verification":true}
{"id":"rule_policy_selector_donchian_channel","scope":"process","applies_to":["TRAILING_STOP_POLICIES"],"if":"want systematic trailing independent of discretionary pivots","then":{"interpretation":"Use Donchian channel trailing stop based on N-period highs/lows (parameterized).","score_adjustment":"n/a","confidence_adjustment":"+0"},"rationale":"Seminar provides Donchian stop examples and parameter effect guidance.","failure_modes":["Too tight N increases churn; too wide delays exits."],"page_refs":["p218-219"],"needs_verification":false}
{"id":"rule_donchian_period_tightness_tradeoff","scope":"process","applies_to":["TRAILING_STOP_POLICIES"],"if":"choosing Donchian parameter N","then":{"interpretation":"Smaller N (e.g., 10) = tighter stop (more exits); larger N (e.g., 14) = wider stop (fewer exits).","score_adjustment":"n/a","confidence_adjustment":"n/a"},"rationale":"Seminar shows 10 vs 14 Donchian: shorter is tighter, longer gives more room.","failure_modes":["Asset volatility differs; keep N configurable."],"page_refs":["p218-219"],"needs_verification":false}
{"id":"rule_default_donchian_by_regime","scope":"process","applies_to":["TRAILING_STOP_POLICIES","MARKET_CONDITIONS"],"if":"selecting default Donchian N by regime","then":{"interpretation":"Suggested default: TRENDY → wider (N≈14), MOMENTUM → tighter (N≈10). CHOPPY → avoid using as primary trailing; reduce risk instead.","score_adjustment":"n/a","confidence_adjustment":"n/a"},"rationale":"Parameter effect + regime context: momentum needs tighter control; trendy needs room; choppy is whipsaw-prone.","failure_modes":["Some momentum trends need room; use ATR confirmation."],"page_refs":["p218-219","p69"],"needs_verification":true}
{"id":"rule_trailing_policy_must_be_logged","scope":"process","applies_to":["TRAILING_STOP_POLICIES"],"if":"exporting weekly snapshot/report","then":{"interpretation":"Always log trailing policy (REL_HILO vs DONCHIAN), parameters (e.g., N), and the active stop reference level type.","score_adjustment":"n/a","confidence_adjustment":"n/a"},"rationale":"Operational transparency: policies explain exits and de-risking decisions.","failure_modes":["None; small payload."],"page_refs":["p211","p218"],"needs_verification":true}
{"id":"rule_contradiction_tight_trailing_in_trendy_alignment","scope":"portfolio","applies_to":["TRAILING_STOP_POLICIES","MULTI_TIMESCALE_ALIGNMENT"],"if":"alignment_score is high (3/3) AND trailing policy is very tight (e.g., Donchian N too small)","then":{"interpretation":"Contradiction: high trend quality but tight trailing likely causes churn; consider widening trailing or reducing noise sensitivity.","score_adjustment":"n/a","confidence_adjustment":"-5"},"rationale":"When multiple trend sizes align, profitability potential is high; overly tight stops can undermine capture.","failure_modes":["If volatility spikes, tighter stops may be justified; check ATR regime."],"page_refs":["p102","p218"],"needs_verification":true}
{"id":"rule_contradiction_wide_trailing_in_momentum_spike","scope":"portfolio","applies_to":["TRAILING_STOP_POLICIES","MARKET_CONDITIONS"],"if":"regime is MOMENTUM (ATR expanding) AND trailing policy is very wide","then":{"interpretation":"Contradiction: momentum is fast; wide trailing may give back too much. Consider tighter Donchian/ATR-aware management or smaller size.","score_adjustment":"n/a","confidence_adjustment":"-5"},"rationale":"Momentum defined by high dynamics; management often benefits from tighter control or smaller size.","failure_modes":["Strong runaway trends exist; adjust based on risk appetite."],"page_refs":["p69","p218"],"needs_verification":true}
{"id":"rule_crv_and_trailing_are_linked","scope":"process","applies_to":["EXPECTANCY_CRV","TRAILING_STOP_POLICIES"],"if":"trailing policy materially changes realized payoff distribution","then":{"interpretation":"Treat trailing policy selection as a lever that changes effective CRV distribution; avoid policies that systematically compress winners below CRV floor.","score_adjustment":"n/a","confidence_adjustment":"n/a"},"rationale":"Expectancy depends on payoff sizes; trailing stops change payoff distribution and win rate/CRV balance.","failure_modes":["Requires empirical calibration later; MVP uses qualitative governance."],"page_refs":["p206-209","p211"],"needs_verification":true}
{"id":"rule_do_not_build_proprietary_goersch_trend","scope":"process","applies_to":["OPTIONAL_TECH_SCANNER_GOERSCH_SIGNALS"],"if":"encountering Goersch Trend references","then":{"interpretation":"Treat as external series only if you already have vendor/platform data; do not attempt to reconstruct internals.","score_adjustment":"n/a","confidence_adjustment":"n/a"},"rationale":"Composite/proprietary indicators must not be rebuilt in MVP (efficiency + definitional uncertainty).","failure_modes":["None; explicit policy constraint."],"page_refs":["p226"],"needs_verification":false}


---
module_id: EXPECTANCY_CRV
scope: module
tags: [risk_management, expectancy, crv, r_multiple, governance]
version: 0.1
source: seminar_pdf
cadence: weekly
---

## Purpose
Anchor the IPOS risk discipline in **expectancy**:
- explain why **win rate alone is not enough**,
- enforce a hard **CRV floor** for entries and adds,
- connect management policies (e.g., trailing stops) to the payoff distribution.

## Inputs (weekly)
- For any proposed action (entry/add/scale):
  - `defined_risk_R` (usually 1R by construction; derived from stop distance × size)
  - `expected_reward_R` (target, trend path expectation, or conservative scenario)
  - `CRV = expected_reward_R / defined_risk_R`
- Optional strategy assumptions:
  - `assumed_win_rate` (p_win)
  - `avg_win_R`, `avg_loss_R` (loss ~ 1R)

## Outputs (weekly)
- `crv_gate_pass` (bool)
- `expectancy_note` (short explanation string for report)
- `expectancy_confidence` (0–100)

---

## Core Concepts
### CRV as R-multiple framing
- Express payoff and risk in **R**:
  - risk = 1R (your defined loss if stop is hit)
  - reward = expected multiple of R
- CRV is simply:
  - `CRV = reward / risk`

### Expectancy (intuition-level)
- Long-run profitability depends on:
  - **win rate** and **payoff size**
- Simple model:
  - `E ≈ p_win * avg_win_R - (1 - p_win) * avg_loss_R`
- Therefore:
  - higher CRV can offset lower win rate
  - high win rate with tiny CRV can still be fragile

---

## Hard Governance Rule (non-negotiable)
### CRV ≥ 1.3 gate (entries + adds)
- If `CRV < 1.3`:
  - do not enter
  - do not add/scale
  - reduce size or skip
- This is a **process gate**, not a “score”.

---

## Practical Use in Weekly IPOS
### What goes into the weekly report (short)
- For any tactical “add risk” recommendation:
  - show CRV estimate (conservative)
  - state whether the CRV gate passes
  - if it fails: explain why no add is recommended even if signals look good

### Avoid table overfitting
- The seminar’s win-rate × CRV tables are for intuition.
- IPOS should:
  - enforce the CRV floor
  - avoid quoting exact table outcomes
  - keep the explanation simple: “payoff quality matters”

---

## Link to Management (Trailing policies matter)
Trailing stops change your realized payoff distribution:
- tighter trailing:
  - tends to increase win rate but can compress winners (lower avg_win_R)
- wider trailing:
  - allows larger winners but can give back more and reduce win rate

**Governance implication**
- do not choose trailing policies that systematically compress winners so much that your effective CRV deteriorates.

---

## Contradictions (trigger investigation)
- Signals suggest adding risk, but CRV gate fails
  - override: no add; investigate whether target assumptions are unrealistic or stop too wide/tight
- Strategy claims “high win rate” but frequent drawdowns
  - likely poor payoff quality or correlation risk; review CRV and loss distribution

---

## Implementation Notes (IPOS-friendly)
- In macro-first IPOS, CRV is mainly applied to:
  - tactical adds (tilt increases, lever changes, adding exposures)
- Keep CRV estimation conservative:
  - reward scenarios should be plausible within the current regime/trend state

---

## NEXT ACTION (say “continue”)
**Stage:** PLAYBOOK_WRITE  
**Module:** TRAILING_STOP_POLICIES  
**Focus:** Compact module for Relative Hi/Lo and Donchian trailing, with regime defaults and parameter guidance (10 vs 14).
