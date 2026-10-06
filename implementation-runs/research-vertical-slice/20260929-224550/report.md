# IPOS Weekly Report — 2026-09-25

_Scoring version 1.0 · schema 1.0 · code computes, LLM narrates._

## Overall
- **Risk budget:** 29.6 / 100 (base 59.2 × regime scaler 0.5)
- **Confidence:** 69.0 / 100
- **Breadth:** 64% of 22 indicators score above 50; 14% improved this week
- **Regime:** CHOPPY (confidence 75, risk_scaler 0.5)
  - _Policy:_ size small · entry penalize_breakouts · trail defensive_quick_exit · stop wide_buffer
  - _Classifier measurements:_ atr_change_rate = 0.7731 · atr_source = ohlc · efficiency_ratio = 0.2417 · n_swings = 8.0 · overlap_index = 0.7583 · range_overlap = 0.4814 · retracement_ratio = 1.3643 · swing_structure = up
- ⚠️ **Degraded run:** 9 stale, 0 missing series
### Stance vector
| Dimension | Tilt |
|---|---|
| commodities | +0.81 |
| credit | +0.01 |
| duration | -0.50 |
| equity | +0.81 |
| fundamentals | -0.01 |
| growth | +0.15 |
| liquidity | +0.34 |
| usd | -0.13 |

## Modules
| Module | Score | Tilt | Confidence |
|---|---|---|---|
| Commodities | 90.4 | +0.81 | 85.0 |
| Credit | 50.6 | +0.01 | 52.0 |
| EquityRisk | 90.3 | +0.81 | 88.8 |
| FX | 43.6 | -0.13 | 64.8 |
| Fundamentals | 49.4 | -0.01 | 58.5 |
| GrowthRisk | 57.5 | +0.15 | 85.3 |
| Liquidity | 66.9 | +0.34 | 51.5 |
| RatesLiquidity | 25.2 | -0.50 | 66.5 |

## Portfolio vs. Stance
| Module | Your weight | Suggested tilt | Read |
|---|---|---|---|
| Commodities | 26.3% | +0.81 | aligned |
| Credit | 0.0% | +0.01 | aligned |
| EquityRisk | 73.7% | +0.81 | aligned |
| FX | 0.0% | -0.13 | aligned |
| Fundamentals | 0.0% | -0.01 | aligned |
| GrowthRisk | 0.0% | +0.15 | aligned |
| Liquidity | 0.0% | +0.34 | not participating in a signal the system currently likes |
| RatesLiquidity | 0.0% | -0.50 | aligned (out of a signal the system currently dislikes) |
_Total portfolio value: €40248_

## Macro-to-Portfolio Decision Flow (WF-07 Stage 4)
_Macro Confidence: **69.0%** (Gate: **PASS**) · Rebalancing Stance: **ADDITIONS PERMITTED** · Active Research Alerts: **0**_

| Sector Cluster | Current (€ / %) | Macro Tilt | Stance Flow | Target % | Delta % | Active Research Alerts | Rationale |
|---|---|---|---|---|---|---|---|
| **Technology, AI & Semiconductors** | €15176 (37.7%) | 1.16x | 🟢 **TAILWIND** | 9.6% | -28.1% | — | Equity stance (+0.81) & duration sensitivity (-0.50) |
| **Energy & Commodities** | €10592 (26.3%) | 1.67x | 🟢 **TAILWIND** | 9.7% | -16.6% | — | Commodities stance (+0.81) & USD impact (-0.13) |
| **Crypto & Digital Assets** | €7229 (18.0%) | 1.53x | 🟢 **TAILWIND** | 6.0% | -11.9% | — | Risk appetite (+0.81), credit liquidity (+0.01), USD drag (-0.13) |
| **Healthcare & Biotechnology** | €6681 (16.6%) | 1.02x | ⚪ NEUTRAL | 3.8% | -12.8% | — | Duration sensitivity (-0.50) & equity stance (+0.81) |
| **Defense & Industrials** | €571 (1.4%) | 1.48x | 🟢 **TAILWIND** | 0.5% | -1.0% | — | Economic growth stance (+0.15) & equity stance (+0.81) |
| **Financials & Value Preservers** | €0 (0.0%) | 1.65x | 🟢 **TAILWIND** | 0.0% | +0.0% | — | Net interest margin tilt & equity stance (+0.81) |

## Action Matrix (Monday Execution & Stop Policies)
_Capital: €40248 · Regime: CHOPPY (scaler 0.5) · Risk Budget: 29.6% · Target Cash/Defensive: 70.4% (€28331)_

| Instrument | Holding / Asset | Sector | Current (€ / %) | Target % | Delta (€) | Action | Stop Policy | Notes |
|---|---|---|---|---|---|---|---|---|
| `US88023B1035` | **Tempus AI Inc.** | Technology, AI & Semiconductors | €10602 (26.3%) | 1.4% | -10059 | **TRIM** (-142) | defensive_quick_exit | Trim 25.0% (€10,059) to align with CHOPPY risk budget (29.6%). |
| `DE000PS7JX34` | **BNP MiniL Gold** | Energy & Commodities | €7513 (18.7%) | 3.7% | -6012 | **TRIM** (-28) | defensive_quick_exit | Trim 14.9% (€6,012) to align with CHOPPY risk budget (29.6%). |
| `CA24477V1058` | **Definium Therapeutics** | Healthcare & Biotechnology | €6380 (15.8%) | 4.1% | -4714 | **TRIM** (-148) | defensive_quick_exit | Trim 11.7% (€4,714) to align with CHOPPY risk budget (29.6%). |
| `SE0007525332` | **Coinshares XBT (Bitcoin)** | Crypto & Digital Assets | €3276 (8.1%) | 0.4% | -3107 | **TRIM** (-1) | defensive_quick_exit | Trim 7.7% (€3,107) to align with CHOPPY risk budget (29.6%). |
| `DE000MB3FKR8` | **MS TurboL Copper Future** | Energy & Commodities | €3056 (7.6%) | 4.2% | -1382 | **TRIM** (-47) | defensive_quick_exit | Trim 3.4% (€1,382) to align with CHOPPY risk budget (29.6%). |
| `DE000MN4NFQ8` | **MS DiscC SoFi 18.12.26** | Technology, AI & Semiconductors | €1072 (2.7%) | 0.1% | -1016 | **TRIM** (-758) | defensive_quick_exit | Trim 2.5% (€1,016) to align with CHOPPY risk budget (29.6%). |
| `US5951121038` | **Micron Technology** | Technology, AI & Semiconductors | €953 (2.4%) | 0.1% | -905 | **TRIM** (-1) | defensive_quick_exit | Trim 2.2% (€905) to align with CHOPPY risk budget (29.6%). |
| `CH0496454155` | **21Shares Binance BNB** | Crypto & Digital Assets | €899 (2.2%) | 0.1% | -850 | **TRIM** (-19) | defensive_quick_exit | Trim 2.1% (€850) to align with CHOPPY risk budget (29.6%). |
| `CH1102728750` | **21Shares Cardano** | Crypto & Digital Assets | €805 (2.0%) | 0.1% | -765 | **TRIM** (-190) | defensive_quick_exit | Trim 1.9% (€765) to align with CHOPPY risk budget (29.6%). |
| `DE000SH7NDN5` | **SG MiniL Pinduoduo** | Technology, AI & Semiconductors | €771 (1.9%) | 0.1% | -731 | **TRIM** (-205) | defensive_quick_exit | Trim 1.8% (€731) to align with CHOPPY risk budget (29.6%). |
| `DE000HM4PTX8` | **HSBC TurboC Seagate** | Technology, AI & Semiconductors | €765 (1.9%) | 0.1% | -725 | **TRIM** (-21) | defensive_quick_exit | Trim 1.8% (€725) to align with CHOPPY risk budget (29.6%). |
| `CH0454664027` | **21Shares Ethereum** | Crypto & Digital Assets | €522 (1.3%) | 0.1% | -493 | **TRIM** (-19) | defensive_quick_exit | Trim 1.2% (€493) to align with CHOPPY risk budget (29.6%). |
| `DE000A2YN504` | **Knaus Tabbert AG** | Defense & Industrials | €519 (1.3%) | 4.4% | +1264 | **BUY** (+122) | defensive_quick_exit | Add 3.1% (€1,264) to reach target allocation. |
| `US09175A2069` | **Bitmine Immersion Tech** | Crypto & Digital Assets | €484 (1.2%) | 0.1% | -460 | **TRIM** (-19) | defensive_quick_exit | Trim 1.1% (€460) to align with CHOPPY risk budget (29.6%). |
| `DE000A3GV1T7` | **VanEck Avalanche** | Crypto & Digital Assets | €470 (1.2%) | 0.1% | -445 | **TRIM** (-474) | defensive_quick_exit | Trim 1.1% (€445) to align with CHOPPY risk budget (29.6%). |
| `CA64073L1013` | **Neptune Digital Assets** | Crypto & Digital Assets | €420 (1.0%) | 0.1% | -400 | **HOLD** | defensive_quick_exit | Holding within ±1.0% tolerance band. |
| `CH1114873776` | **21Shares Solana** | Crypto & Digital Assets | €354 (0.9%) | 0.0% | -338 | **HOLD** | defensive_quick_exit | Holding within ±1.0% tolerance band. |
| `US6974351057` | **Palo Alto Networks** | Technology, AI & Semiconductors | €331 (0.8%) | 0.0% | -315 | **HOLD** | defensive_quick_exit | Holding within ±1.0% tolerance band. |
| `US20451W1018` | **Compass Pathways** | Healthcare & Biotechnology | €236 (0.6%) | 0.1% | -176 | **HOLD** | defensive_quick_exit | Holding within ±1.0% tolerance band. |
| `US67066G1040` | **NVIDIA Corp** | Technology, AI & Semiconductors | €197 (0.5%) | 0.0% | -189 | **HOLD** | defensive_quick_exit | Holding within ±1.0% tolerance band. |
| `DE000VX8PY08` | **Vontobel MiniL Alibaba** | Technology, AI & Semiconductors | €191 (0.5%) | 0.0% | -183 | **HOLD** | defensive_quick_exit | Holding within ±1.0% tolerance band. |
| `DE000MG8GGU2` | **MS MiniL Tencent** | Technology, AI & Semiconductors | €114 (0.3%) | 0.0% | -109 | **HOLD** | defensive_quick_exit | Holding within ±1.0% tolerance band. |
| `US49639K1016` | **Kingsoft Cloud** | Technology, AI & Semiconductors | €86 (0.2%) | 0.1% | -61 | **HOLD** | defensive_quick_exit | Holding within ±1.0% tolerance band. |
| `IE000YYE6WK5` | **VanEck Defense ETF** | Defense & Industrials | €52 (0.1%) | 3.9% | +1526 | **BUY** (+29) | defensive_quick_exit | Add 3.8% (€1,526) to reach target allocation. |
| `DE000MK6QKZ0` | **MS TurboL Broadcom** | Technology, AI & Semiconductors | €49 (0.1%) | 0.0% | -45 | **HOLD** | defensive_quick_exit | Holding within ±1.0% tolerance band. |
| `DE000DN042H8` | **DZ Bank MiniL Micron** | Technology, AI & Semiconductors | €46 (0.1%) | 0.0% | -42 | **HOLD** | defensive_quick_exit | Holding within ±1.0% tolerance band. |
| `CA74447P1009` | **Psyched Wellness** | Healthcare & Biotechnology | €45 (0.1%) | 0.0% | -33 | **HOLD** | defensive_quick_exit | Holding within ±1.0% tolerance band. |
| `US48576U2050` | **Karyopharm Therapeutics** | Healthcare & Biotechnology | €20 (0.1%) | 0.0% | -16 | **HOLD** | defensive_quick_exit | Holding within ±1.0% tolerance band. |
| `US72919P2020` | **Plug Power** | Energy & Commodities | €17 (0.0%) | 0.0% | -13 | **HOLD** | defensive_quick_exit | Holding within ±1.0% tolerance band. |
| `DE000MA5E683` | **MS FaktL Brent Crude** | Energy & Commodities | €6 (0.0%) | 6.1% | +2462 | **BUY** (+440) | defensive_quick_exit | Add 6.1% (€2,462) to reach target allocation. |
| `US04744L2051` | **Athersys Inc.** | Healthcare & Biotechnology | €0 (0.0%) | 0.0% | +0 | **HOLD** | defensive_quick_exit | Zero-value holding; no rebalance action needed. |
| `XC000A42NLY5` | **AtaiBeckley CVR** | Healthcare & Biotechnology | €0 (0.0%) | 0.0% | +0 | **HOLD** | defensive_quick_exit | Zero-value holding; no rebalance action needed. |

### Riskfolio-Lib Risk Diagnostics & Risk Parity
_Engine: Riskfolio-Lib v7.3.0 · Solver: Riskfolio-Lib · Active Positions: 30_

| Holding / Asset | Proxy | Capital Wt | Volatility (Ann.) | Risk Contribution | Risk Skew | RP Wt | HRP Wt | Status |
|---|---|---|---|---|---|---|---|---|
| **Tempus AI Inc.** | `NDX` | 26.3% | 39.0% | **31.5%** | 1.20x | 4.6% | 3.4% | BALANCED |
| **BNP MiniL Gold** | `GOLD` | 18.7% | 32.5% | **15.1%** | 0.81x | 12.6% | 15.6% | BALANCED |
| **Definium Therapeutics** | `RUT` | 15.8% | 26.9% | **11.4%** | 0.72x | 14.0% | 14.1% | 🛡️ DIVERSIFIER |
| **Coinshares XBT (Bitcoin)** | `NDX` | 8.1% | 39.0% | **9.7%** | 1.20x | 1.4% | 1.0% | BALANCED |
| **MS TurboL Copper Future** | `COPPER` | 7.6% | 28.0% | **5.3%** | 0.70x | 14.1% | 20.9% | 🛡️ DIVERSIFIER |
| **MS DiscC SoFi 18.12.26** | `NDX` | 2.7% | 39.0% | **3.2%** | 1.20x | 0.5% | 0.3% | BALANCED |
| **Micron Technology** | `NDX` | 2.4% | 39.0% | **2.8%** | 1.20x | 0.4% | 0.3% | BALANCED |
| **21Shares Binance BNB** | `NDX` | 2.2% | 39.0% | **2.7%** | 1.20x | 0.4% | 0.3% | BALANCED |
| **21Shares Cardano** | `NDX` | 2.0% | 39.0% | **2.4%** | 1.20x | 0.3% | 0.3% | BALANCED |
| **SG MiniL Pinduoduo** | `NDX` | 1.9% | 39.0% | **2.3%** | 1.20x | 0.3% | 0.2% | BALANCED |
| **HSBC TurboC Seagate** | `NDX` | 1.9% | 39.0% | **2.3%** | 1.20x | 0.3% | 0.2% | BALANCED |
| **21Shares Ethereum** | `NDX` | 1.3% | 39.0% | **1.6%** | 1.20x | 0.2% | 0.2% | BALANCED |
| **Bitmine Immersion Tech** | `NDX` | 1.2% | 39.0% | **1.4%** | 1.20x | 0.2% | 0.1% | BALANCED |
| **VanEck Avalanche** | `NDX` | 1.2% | 39.0% | **1.4%** | 1.20x | 0.2% | 0.1% | BALANCED |
| **Neptune Digital Assets** | `NDX` | 1.0% | 39.0% | **1.2%** | 1.20x | 0.2% | 0.1% | BALANCED |
| **21Shares Solana** | `NDX` | 0.9% | 39.0% | **1.1%** | 1.20x | 0.1% | 0.1% | BALANCED |
| **Palo Alto Networks** | `NDX` | 0.8% | 39.0% | **1.0%** | 1.20x | 0.1% | 0.1% | BALANCED |
| **Knaus Tabbert AG** | `DAX` | 1.3% | 29.7% | **0.9%** | 0.72x | 14.9% | 11.6% | 🛡️ DIVERSIFIER |
| **NVIDIA Corp** | `NDX` | 0.5% | 39.0% | **0.6%** | 1.20x | 0.1% | 0.1% | BALANCED |
| **Vontobel MiniL Alibaba** | `NDX` | 0.5% | 39.0% | **0.6%** | 1.20x | 0.1% | 0.1% | BALANCED |
| **Compass Pathways** | `RUT` | 0.6% | 26.9% | **0.4%** | 0.72x | 0.5% | 0.5% | 🛡️ DIVERSIFIER |
| **MS MiniL Tencent** | `NDX` | 0.3% | 39.0% | **0.3%** | 1.20x | 0.1% | 0.0% | BALANCED |
| **Kingsoft Cloud** | `RUT` | 0.2% | 26.9% | **0.1%** | 0.72x | 0.2% | 0.2% | 🛡️ DIVERSIFIER |
| **DZ Bank MiniL Micron** | `NDX` | 0.1% | 39.0% | **0.1%** | 1.20x | 0.0% | 0.0% | BALANCED |
| **MS TurboL Broadcom** | `NDX` | 0.1% | 39.0% | **0.1%** | 1.20x | 0.0% | 0.0% | BALANCED |
| **VanEck Defense ETF** | `SPX` | 0.1% | 30.2% | **0.1%** | 0.84x | 13.2% | 11.2% | BALANCED |
| **Psyched Wellness** | `RUT` | 0.1% | 26.9% | **0.1%** | 0.72x | 0.1% | 0.1% | 🛡️ DIVERSIFIER |
| **Karyopharm Therapeutics** | `RUT` | 0.1% | 26.9% | **0.0%** | 0.72x | 0.0% | 0.0% | 🛡️ DIVERSIFIER |
| **Plug Power** | `RUT` | 0.0% | 26.9% | **0.0%** | 0.72x | 0.0% | 0.0% | 🛡️ DIVERSIFIER |
| **MS FaktL Brent Crude** | `WTI` | 0.0% | 39.5% | **0.0%** | 0.07x | 20.7% | 18.6% | 🛡️ DIVERSIFIER |

## Staged Broker Order Tickets (WF-07 Stage 6)
_Sovereign Manual Execution Gate · Total Executable Tickets: **17** · Capital Release (Batch 1): **€31703** · Capital Deployment (Batch 2): **€5262** · Net Cash Impact: **€+26441**_

> ⚠️ **Sovereign Execution Notice**: Orders are staged strictly for manual review and sovereign entry into broker portals. Zero automated trade execution.

### Batch 1: Capital Release & Risk Reduction (Execute First)
_Defensive TRIM / SELL actions to liberate cash and reduce portfolio volatility before rebalancing._

| Priority | Broker | Action | Instrument | Holding / Asset | Shares | Ref Price | Limit Price (Buffer -0.5%) | Est. Value (€) | Order Type | TIF | Stop Policy |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **#1** | `SMARTBROKER` | **TRIM** | `US88023B1035` | **Tempus AI Inc.** | 142 | €70.68 | €70.3266 | €9986.38 | LIMIT | GFD | defensive_quick_exit |
| **#2** | `SMARTBROKER` | **TRIM** | `DE000PS7JX34` | **BNP MiniL Gold** | 28 | €214.66 | €213.5867 | €5980.43 | LIMIT | GFD | defensive_quick_exit |
| **#3** | `SMARTBROKER` | **TRIM** | `CA24477V1058` | **Definium Therapeutics** | 148 | €31.90 | €31.7405 | €4697.59 | LIMIT | GFD | defensive_quick_exit |
| **#4** | `SMARTBROKER` | **TRIM** | `SE0007525332` | **Coinshares XBT (Bitcoin)** | 1 | €3275.67 | €3259.2917 | €3259.29 | LIMIT | GFD | defensive_quick_exit |
| **#5** | `SMARTBROKER` | **TRIM** | `DE000MB3FKR8` | **MS TurboL Copper Future** | 47 | €29.11 | €28.9595 | €1361.10 | LIMIT | GFD | defensive_quick_exit |
| **#6** | `ZERO` | **TRIM** | `DE000MN4NFQ8` | **MS DiscC SoFi 18.12.26** | 758 | €1.34 | €1.3333 | €1010.64 | LIMIT | GFD | defensive_quick_exit |
| **#7** | `SMARTBROKER` | **TRIM** | `US5951121038` | **Micron Technology** | 1 | €953.00 | €948.2350 | €948.24 | LIMIT | GFD | defensive_quick_exit |
| **#8** | `ZERO` | **TRIM** | `CH0496454155` | **21Shares Binance BNB** | 19 | €44.93 | €44.7014 | €849.33 | LIMIT | GFD | defensive_quick_exit |
| **#9** | `ZERO` | **TRIM** | `CH1102728750` | **21Shares Cardano** | 190 | €4.03 | €4.0057 | €761.08 | LIMIT | GFD | defensive_quick_exit |
| **#10** | `SMARTBROKER` | **TRIM** | `DE000SH7NDN5` | **SG MiniL Pinduoduo** | 205 | €3.57 | €3.5521 | €728.18 | LIMIT | GFD | defensive_quick_exit |
| **#11** | `SMARTBROKER` | **TRIM** | `DE000HM4PTX8` | **HSBC TurboC Seagate** | 21 | €34.79 | €34.6161 | €726.94 | LIMIT | GFD | defensive_quick_exit |
| **#12** | `ZERO` | **TRIM** | `CH0454664027` | **21Shares Ethereum** | 19 | €26.08 | €25.9476 | €493.00 | LIMIT | GFD | defensive_quick_exit |
| **#13** | `ZERO` | **TRIM** | `US09175A2069` | **Bitmine Immersion Tech** | 19 | €24.20 | €24.0790 | €457.50 | LIMIT | GFD | defensive_quick_exit |
| **#14** | `ZERO` | **TRIM** | `DE000A3GV1T7` | **VanEck Avalanche** | 474 | €0.94 | €0.9344 | €442.91 | LIMIT | GFD | defensive_quick_exit |

### Batch 2: Capital Deployment & Rebalancing (Execute Second)
_Permitted additions to reach target portfolio weights funded by Batch 1 capital release._

| Priority | Broker | Action | Instrument | Holding / Asset | Shares | Ref Price | Limit Price (Cap +0.5%) | Est. Value (€) | Order Type | TIF | Stop Policy |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **#15** | `SMARTBROKER` | **BUY** | `DE000MA5E683` | **MS FaktL Brent Crude** | 440 | €5.60 | €5.6280 | €2476.32 | LIMIT | GFD | defensive_quick_exit |
| **#16** | `SMARTBROKER` | **BUY** | `IE000YYE6WK5` | **VanEck Defense ETF** | 29 | €51.90 | €52.1595 | €1512.63 | LIMIT | GFD | defensive_quick_exit |
| **#17** | `SMARTBROKER` | **BUY** | `DE000A2YN504` | **Knaus Tabbert AG** | 122 | €10.38 | €10.4319 | €1272.69 | LIMIT | GFD | defensive_quick_exit |



## Active Research Theses & Watch Register
_Tracked qualitative macro hypotheses & falsifiable triggers (WF-07 Stage 3)_

> **Decision boundary:** WATCH items are monitoring-only. They do not change target weights or create staged orders; only an operator-approved open ACTION can affect portfolio policy.

| Item ID | Class | Topic / Instrument | Action / Invalidation Trigger | Status | Rationale | Evidence |
|---|---|---|---|---|---|---|
| `WATCH-IMF-GDP-001` | **WATCH** | `GLOBAL_GDP` | Global GDP projection downgraded below 2.8% | `OPEN` | IMF baseline 3.0% (2026) / 3.4% (2027) indicates growth vulnerability below historical averages |  |
| `WATCH-IMF-TRADE-001` | **WATCH** | `TRADE_GEOPOLITICS` | Escalation in tech export restrictions or bilateral tariff announcements | `OPEN` | Trade barriers and tech correction threaten supply chains and capital expenditure |  |
| `WATCH-IMF-RATE-001` | **WATCH** | `US10Y` | US 10-Year yield crosses above 4.50% / sticky inflation repricing | `OPEN` | Upward inflation revision creates vulnerability to sharp yield spikes across asset classes |  |
| `WATCH-LIVE-IMF-WATCH` | **WATCH** | `TECHNOLOGY_AI` | Monitor Technology, AI & Semiconductors exposure; no automatic target or order change | `OPEN` | IMF flags a technology-expectation correction as a downside risk; retain WATCH pending newer evidence | http://127.0.0.1:3000/dashboard/preview/e2hwjrfsjkws2daadvjfah0y#t=67.5 |

## Top movers (Δscore vs prior week)
| Indicator | Δscore 1w |
|---|---|
| WTI | -5.8 |
| EURUSD | -5.1 |
| GOLD | -4.5 |
| NDX | +3.2 |
| SPX | +2.6 |
| US10Y_STOOQ | -2.4 |
| DGS10 | -2.0 |
| VIXCLS | -1.3 |

## Contradictions
- **[med]** Equities risk-on while rates/liquidity conditions look tight. _(fired 1 of the last 2 weeks)_
  - module(EquityRisk) = 90.2564
  - module(RatesLiquidity) = 25.1536
- **[low]** Mixed signals within the credit module (members strongly disagree). _(fired 2 of the last 2 weeks)_
  - highest(Credit) = IG_OAS 92.9
  - lowest(Credit) = HY_OAS 8.3
  - module_spread(Credit) = 84.6154

## Events this / next week
| Date | When | Event | Category |
|---|---|---|---|
| 2026-10-01 | next week | ISM Manufacturing PMI | growth |
| 2026-10-02 | next week | US Nonfarm Payrolls | growth |

## Indicators
Δ value = change in the indicator's own units (not comparable between indicators).
Δscore 1w/1m/1q/1y = change in the 0-100 score, which _is_ comparable.
Level %ile = where the raw level sits in its own trailing ~3-year distribution.
It is **not** direction-adjusted: for an inverted indicator (e.g. VIXCLS, HY_OAS)
a high percentile means a _low_ score. `hist` = weeks of history behind it.

| ID | Module | Value | Δ value 1w | 4w | 12w | Level %ile | z | hist | Trend | Score | Δscore 1w | 1m | 1q | 1y | Conf | Stale |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| COPPER | Commodities | 6.6955 | 0.0805 | 0.1335 | 0.581 | 100 | +1.84 | 1361 | up | 100.0 | +0.0 | +1.9 | +5.1 | +10.3 | 94 |  |
| DAX | EquityRisk | 25408.6406 | 104.5801 | -1161.3496 | -370.6699 | 95 | +1.07 | 2022 | down | 94.9 | +0.0 | -5.1 | -5.1 | +2.6 | 95 |  |
| DFF | RatesLiquidity | 4.499 | 0.0 | 0.0 | -0.169 | 54 | +0.22 | 230 | flat | 44.5 | -0.2 | -0.8 | +11.0 | -12.9 | 52 | yes |
| DGS10 | RatesLiquidity | 5.17 | 0.16 | 0.44 | 0.68 | 100 | +3.53 | 1917 | up | 2.9 | -2.0 | -10.5 | -22.7 | -56.2 | 89 |  |
| DTWEXBGS | FX | 132.0054 | 0.0 | 0.0 | 1.7223 | 70 | +0.27 | 230 | flat | 30.1 | +0.0 | +0.0 | -2.6 | +24.4 | 52 | yes |
| EURUSD | FX | 1.139 | -0.0087 | -0.0267 | -0.0033 | 57 | +0.11 | 1191 | down | 57.1 | -5.1 | -23.7 | -7.7 | -37.8 | 78 |  |
| GOLD | Commodities | 4321.2002 | -103.6997 | -208.6997 | 195.5 | 79 | +0.71 | 1361 | down | 78.8 | -4.5 | -8.3 | -0.6 | -21.2 | 85 |  |
| HY_OAS | Credit | 3.8965 | 0.0 | 0.0 | -0.0124 | 92 | +1.37 | 230 | flat | 8.3 | +0.0 | +0.0 | +1.9 | -13.5 | 52 | yes |
| ICSA | Fundamentals | 234813.1962 | 0.0 | 0.0 | 5603.2262 | 58 | -0.50 | 230 | flat | 42.3 | +0.0 | +0.0 | -7.1 | +14.7 | 52 | yes |
| IG_OAS | Credit | 0.6933 | 0.0 | 0.0 | -0.0059 | 7 | -1.80 | 230 | flat | 92.9 | -0.6 | -2.6 | -6.4 | +21.2 | 52 | yes |
| NDX | EquityRisk | 30608.1309 | 963.9609 | 1174.7012 | 1278.9199 | 100 | +1.92 | 2139 | up | 100.0 | +3.2 | +4.5 | +2.6 | +0.6 | 90 |  |
| NFCI | RatesLiquidity | -0.014 | 0.0 | 0.0 | -0.0758 | 74 | +0.60 | 230 | flat | 35.5 | -0.1 | -0.2 | +6.0 | -10.6 | 52 | yes |
| RUT | EquityRisk | 2837.55 | -22.8499 | -134.8201 | -158.5601 | 88 | +1.22 | 2038 | down | 88.5 | -0.6 | -7.1 | -10.9 | -10.3 | 91 |  |
| SPX | EquityRisk | 7743.4102 | 92.9102 | 31.6504 | 260.1699 | 99 | +1.77 | 2961 | up | 98.7 | +2.6 | +0.0 | +0.0 | -0.6 | 94 |  |
| T10Y2Y | GrowthRisk | 0.36 | 0.11 | -0.03 | 0.01 | 54 | -0.47 | 1917 | down | 45.0 | +0.0 | +0.0 | +0.0 | -25.0 | 71 |  |
| T10Y3M | GrowthRisk | 0.93 | 0.06 | 0.1 | 0.26 | 100 | +1.71 | 1917 | up | 70.0 | +0.0 | +0.0 | +0.0 | +25.0 | 100 |  |
| UMCSENT | Fundamentals | 64.872 | 0.0 | 0.0 | 0.0 | 56 | +0.42 | 230 | flat | 56.4 | +0.0 | +1.3 | +6.4 | +37.2 | 65 | yes |
| US10Y_STOOQ | RatesLiquidity | 5.184 | 0.186 | 0.464 | 0.699 | 100 | +3.56 | 2961 | up | 2.8 | -2.4 | -11.1 | -23.0 | -57.3 | 89 |  |
| VIXCLS | EquityRisk | 14.87 | 0.06 | 0.44 | -1.28 | 31 | -0.75 | 1917 | down | 69.2 | -1.3 | -5.1 | +18.6 | +9.6 | 73 |  |
| WALCL | Liquidity | 7615229.6686 | 0.0 | 0.0 | 62220.6756 | 99 | +1.58 | 230 | flat | 82.9 | -0.4 | -1.7 | -4.3 | +40.2 | 52 | yes |
| WRESBAL | Liquidity | 3326081.5219 | 0.0 | 0.0 | 128894.4592 | 71 | +0.04 | 230 | flat | 50.9 | +0.0 | -0.2 | +14.4 | -29.0 | 51 | yes |
| WTI | Commodities | 92.41 | -7.89 | 9.01 | 23.72 | 92 | +1.51 | 1362 | up | 92.3 | -5.8 | +10.3 | +56.4 | +79.5 | 76 |  |

## Data quality
- Indicators: 22
- Stale: 9 (DFF, DTWEXBGS, HY_OAS, ICSA, IG_OAS, NFCI, UMCSENT, WALCL, WRESBAL)- Missing: 0- Playbook modules surfaced for narration: MARKET_CONDITIONS, SENTIMENT_POSITIONING
