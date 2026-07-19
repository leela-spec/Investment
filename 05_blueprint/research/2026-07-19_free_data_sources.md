# Research Archive — Free Macro Data Sources (July 2026)

**Date:** 2026-07-19 · **Method:** web research agent (WebSearch/WebFetch, primary sources cited) · **Question:** which $0 sources cover a 60-indicator weekly macro stack robustly? · **Feeds:** meso plan C2.

## Source-by-source assessment

- **FRED** — the backbone. Free API key, ~120 req/min, rock-solid, `fredapi` mature. Covers yield curve (DGS*, T10Y2Y, T10Y3M), NFCI/ANFCI, VIXCLS, WALCL, DTWEXBGS (trade-weighted USD), WTI, UMich, credit spreads. **⚠️ Critical 2026 gotcha:** ICE BofA OAS series (BAMLH0A0HYM2, BAMLC0A0CM, …) truncated in **April 2026 to a rolling 3-year window** (per the FRED series page). Latest values still update daily; **archive own history locally now**.
- **yfinance** — actively maintained (v1.5.1, 06/2026) but structurally fragile: scrapes unofficial endpoints; 2025–26 recurring rate-limit waves/breakage (issues #2128, #2431); needs `curl_cffi` impersonation; TOS gray zone. Workable weekly with caching+backoff, but **never sole source**.
- **Stooq** — no key/login; simple CSV endpoint + bulk history zips; indices, FX, commodities, long VIX history. Unpublished soft daily cap (irrelevant weekly). Best free redundancy for yfinance.
- **ECB Data Portal** — free SDMX REST, no key; EUR FX reference rates, euro yield curves; `ecbdata`/`sdmx1`. Very stable.
- **OECD** — free anonymous SDMX; best for CLI (composite leading indicator); awkward query syntax.
- **Alpha Vantage** — free tier now **25 req/day** (5/min), key required. Too thin as primary; fine tertiary fallback at weekly cadence.
- **Tiingo** — free ~1,000 req/day, 50 symbols/h, ~500 uniques/month; clean REST, explicit personal-use license. The most *legitimate* free equity-EOD backup.
- **CBOE** — daily market statistics page has total/equity/index put/call free (scrape weekly). Classic `totalpc.csv` long archive discontinued → build own history.
- **AAII** — weekly headline bull/bear/neutral free on the site; **full history spreadsheet is members-only**. Scrape headline weekly, accumulate locally.
- **CNN Fear & Greed** — unofficial JSON endpoint `production.dataviz.cnn.io/index/fearandgreed/graphdata` still works (needs browser UA); could vanish anytime → log weekly.
- **NAAIM** — exposure index free on naaim.org incl. history; light scrape.
- **ISM PMI** — headline free in monthly press release; sub-index history licensed (off FRED since 2016). Programmatic route: **DBnomics** (free aggregator, `dbnomics` pkg).
- **investing.com / investpy** — **dead** (Cloudflare since issue #611); avoid.

## Recommended mapping (adopted in C2)

| Category | Primary | Backup |
|---|---|---|
| Curve/rates/fin-conditions | FRED | ECB |
| Credit spreads | FRED (⚠ 3y window → archive) | NFCI credit subindex |
| Volatility | FRED VIXCLS | Stooq ^VIX, CBOE CSV |
| Equity indices/ETFs | Stooq / yfinance | Tiingo |
| Put/Call | CBOE scrape | — (own history) |
| Sentiment surveys | AAII/NAAIM/CNN scrapes | — |
| FX | FRED DTWEXBGS | ECB EXR, Stooq |
| Commodities | FRED WTI + Stooq | Alpha Vantage |
| Macro cycle | FRED UMich, DBnomics ISM | OECD CLI |

**Verdict:** FRED + Stooq/yfinance + ECB ≈ 50 of 60 indicators; scrapes add the sentiment block; Tiingo/AV give redundancy. Fully $0-viable at weekly cadence.

**Deprecated/fragile 2026:** investpy (dead), pandas-datareader (unmaintained), Quandl free (sunset), FRED OAS history (windowed), CNN endpoint (unofficial), yfinance (periodic breakage).

Key URLs: fred.stlouisfed.org/docs/api · fred.stlouisfed.org/series/BAMLH0A0HYM2 · github.com/ranaroussi/yfinance · stooq.com/db/h · data.ecb.europa.eu/help/api/overview · alphavantage.co/premium · tiingo.com/about/pricing · cboe.com/us/options/market_statistics/daily · aaii.com/sentimentsurvey · github.com/whit3rabbit/fear-greed-data · ismworld.org · db.nomics.world
