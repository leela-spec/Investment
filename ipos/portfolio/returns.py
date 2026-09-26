"""Portfolio return matrix extractor and proxy mapping for Riskfolio-Lib optimization."""

from __future__ import annotations

import datetime as dt
from typing import Any, Tuple

import duckdb
import numpy as np
import pandas as pd

DEFAULT_BENCHMARKS = ["SPX", "NDX", "RUT", "DAX", "GOLD", "COPPER", "WTI"]

# Specific instrument -> benchmark proxy mapping
PROXY_SERIES_MAP = {
    # Commodities
    "DE000PS7JX34": "GOLD",      # BNP Mini Long Gold
    "DE000MB3FKR8": "COPPER",    # MS Turbo Long Copper
    "DE000MA5E683": "WTI",       # MS Factor Long Brent Crude
    # European / German Equities
    "DE000A2YN504": "DAX",       # Knaus Tabbert
    # Small Cap / Biotech / Turnaround
    "CA24477V1058": "RUT",       # Definium Therapeutics
    "US48576U2050": "RUT",       # Karyopharm Therapeutics
    "US04744L2051": "RUT",       # Athersys
    "US72919P2020": "RUT",       # Plug Power
    "CA74447P1009": "RUT",       # Psyched Wellness
    "US20451W1018": "RUT",       # Compass Pathways
    "US49639K1016": "RUT",       # Kingsoft Cloud
    # Tech / AI / Growth / Crypto
    "US88023B1035": "NDX",       # Tempus AI
    "US67066G1040": "NDX",       # NVIDIA
    "US0079031078": "NDX",       # AMD
    "US5951121038": "NDX",       # Micron Technology
    "US6974351057": "NDX",       # Palo Alto Networks
    "US83406F1021": "NDX",       # SoFi Technologies
    "DE000MN4NFQ8": "NDX",       # MS Disc Call SoFi
    "SE0007525332": "NDX",       # Coinshares Bitcoin
    "CA64073L1013": "NDX",       # Neptune Digital Assets
    "AU0000185993": "NDX",       # IREN Ltd
    "CH0454664027": "NDX",       # 21Shares Ethereum
    "CH0496454155": "NDX",       # 21Shares BNB
    "CH1102728750": "NDX",       # 21Shares Cardano
    "CH1114873776": "NDX",       # 21Shares Solana
    "DE000A3GV1T7": "NDX",       # VanEck Avalanche
    "DE000MG8GGU2": "NDX",       # MS MiniL Tencent
    "DE000VX8PY08": "NDX",       # Vontobel MiniL Alibaba
    "US09175A2069": "NDX",       # Bitmine Immersion Tech
    "DE000DN042H8": "NDX",       # DZ Bank MiniL Micron
    "DE000HM4PTX8": "NDX",       # HSBC TurboC Seagate
    "DE000MK6QKZ0": "NDX",       # MS TurboL Broadcom
    "DE000SH7NDN5": "NDX",       # SG MiniL Pinduoduo
    "IE000YYE6WK5": "SPX",       # VanEck Defense ETF
    "XC000A42NLY5": "RUT",       # AtaiBeckley CVR
}


def get_proxy_returns(
    con: duckdb.DuckDBPyConnection,
    as_of: dt.date | str | None = None,
    series_ids: list[str] | None = None,
    min_observations: int = 20,
) -> pd.DataFrame:
    """Fetch and calculate historical percentage returns for benchmark series up to as_of date.

    Guarantees:
    - No future leak: filters obs_date <= as_of
    - Sorted DatetimeIndex without duplicates
    - Pure numeric finite returns
    """
    series = series_ids or DEFAULT_BENCHMARKS
    placeholders = ", ".join(["?"] * len(series))
    params: list[Any] = list(series)

    query = f"""
        SELECT obs_date, series_id, AVG(value) AS value
        FROM fact_observation
        WHERE series_id IN ({placeholders})
    """
    if as_of is not None:
        query += " AND obs_date <= ?"
        params.append(str(as_of))

    query += " GROUP BY obs_date, series_id ORDER BY obs_date ASC"

    df_obs = con.execute(query, params).fetchdf()
    if df_obs.empty:
        raise ValueError("No observation data found in warehouse for proxy series")

    df_obs = df_obs.drop_duplicates(subset=["obs_date", "series_id"], keep="last")
    piv = df_obs.pivot(index="obs_date", columns="series_id", values="value").dropna()
    piv.index = pd.to_datetime(piv.index)
    returns = piv.pct_change().dropna()

    if len(returns) < min_observations:
        raise ValueError(
            f"Insufficient return history: {len(returns)} observations < minimum {min_observations}"
        )

    # Verification: check no future leak
    if as_of is not None:
        as_of_ts = pd.Timestamp(as_of)
        if returns.index.max() > as_of_ts:
            raise ValueError(f"Future leak detected: {returns.index.max()} > {as_of_ts}")

    return returns


def build_portfolio_return_matrix(
    positions: pd.DataFrame,
    con: duckdb.DuckDBPyConnection,
    as_of: dt.date | str | None = None,
    proxy_map: dict[str, str] | None = None,
) -> Tuple[pd.DataFrame, pd.Series, dict[str, Any]]:
    """Build asset-level or proxy-level return matrix aligned with active portfolio positions.

    Returns:
        Tuple of:
        - returns_df: Periodic returns with columns matching unique proxy series
        - weights: Series of current weights per proxy series (sums to 1.0)
        - metadata: Dictionary detailing asset-to-proxy mapping and allocations
    """
    if positions.empty:
        raise ValueError("Positions DataFrame is empty")

    active_pos = positions[positions["value_eur"] > 0].copy()
    if active_pos.empty:
        raise ValueError("No positive-value positions found")

    total_val = float(active_pos["value_eur"].sum())
    p_map = proxy_map or PROXY_SERIES_MAP

    proxy_series_needed = set()
    asset_to_proxy = {}

    for _, row in active_pos.iterrows():
        inst = str(row["instrument"])
        proxy = p_map.get(inst, "SPX")
        asset_to_proxy[inst] = proxy
        proxy_series_needed.add(proxy)

    # Get proxy returns from warehouse
    all_returns = get_proxy_returns(con, as_of=as_of, series_ids=list(proxy_series_needed))
    available_proxies = [col for col in all_returns.columns if col in proxy_series_needed]
    returns_df = all_returns[available_proxies].copy()

    # Aggregate position weights by proxy series
    proxy_values: dict[str, float] = {p: 0.0 for p in available_proxies}
    for _, row in active_pos.iterrows():
        inst = str(row["instrument"])
        val = float(row["value_eur"])
        proxy = asset_to_proxy.get(inst, "SPX")
        if proxy in proxy_values:
            proxy_values[proxy] += val
        else:
            fallback = available_proxies[0]
            proxy_values[fallback] += val

    weights = pd.Series({p: proxy_values[p] / total_val for p in available_proxies})

    metadata = {
        "as_of": str(as_of) if as_of else None,
        "total_value_eur": total_val,
        "active_positions_count": len(active_pos),
        "proxy_series_count": len(available_proxies),
        "asset_to_proxy": asset_to_proxy,
        "proxy_values_eur": proxy_values,
    }

    return returns_df, weights, metadata


def compute_portfolio_risk_diagnostics(
    positions: pd.DataFrame,
    con: duckdb.DuckDBPyConnection,
    as_of: dt.date | str | None = None,
    proxy_map: dict[str, str] | None = None,
    names_map: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Execute Riskfolio-Lib portfolio intelligence:
    Computes proxy-level risk contributions, optimal risk parity weights,
    and asset-level risk contribution attribution for active holdings.
    """
    from ipos.portfolio.optimizer import RiskfolioOptimizer
    import riskfolio as rp

    returns_df, proxy_weights, meta = build_portfolio_return_matrix(
        positions=positions, con=con, as_of=as_of, proxy_map=proxy_map
    )

    opt = RiskfolioOptimizer()
    rc_df = opt.compute_risk_contributions(returns_df, proxy_weights)
    w_rp, rp_diag = opt.optimize_risk_parity(returns_df)
    try:
        w_hrp, hrp_diag = opt.optimize_hrp(returns_df)
    except Exception:
        w_hrp = w_rp.copy()
        hrp_diag = {"error": "HRP fallback to RP"}

    active_pos = positions[positions["value_eur"] > 0].copy()
    total_val = float(active_pos["value_eur"].sum())
    asset_to_proxy = meta["asset_to_proxy"]
    proxy_vals = meta["proxy_values_eur"]
    names = names_map or {}

    asset_items = []
    for _, row in active_pos.iterrows():
        inst = str(row["instrument"])
        val = float(row["value_eur"])
        cap_wt = (val / total_val) * 100.0
        proxy = asset_to_proxy.get(inst, "SPX")
        proxy_val = proxy_vals.get(proxy, val)

        proxy_rc_pct = float(rc_df.loc[proxy, "rc_percentage"])
        proxy_vol = float(rc_df.loc[proxy, "volatility_annualized"])
        proxy_rp_wt = float(w_rp.loc[proxy, "weights"])
        proxy_hrp_wt = float(w_hrp.loc[proxy, "weights"]) if proxy in w_hrp.index else proxy_rp_wt

        share_of_proxy = (val / proxy_val) if proxy_val > 0 else 0.0
        asset_rc_pct = proxy_rc_pct * share_of_proxy
        asset_rp_wt_pct = proxy_rp_wt * share_of_proxy * 100.0
        asset_hrp_wt_pct = proxy_hrp_wt * share_of_proxy * 100.0

        skew = round(asset_rc_pct / cap_wt, 2) if cap_wt > 0 else 1.0
        status = "HIGH RISK SKEW" if skew > 1.25 else ("DIVERSIFIER" if skew < 0.75 else "BALANCED")
        asset_items.append({
            "instrument": inst,
            "name": names.get(inst, inst),
            "proxy": proxy,
            "value_eur": round(val, 2),
            "capital_weight_pct": round(cap_wt, 2),
            "volatility_annualized_pct": round(proxy_vol * 100.0, 2),
            "risk_contribution_pct": round(asset_rc_pct, 2),
            "risk_parity_weight_pct": round(asset_rp_wt_pct, 2),
            "hrp_weight_pct": round(asset_hrp_wt_pct, 2),
            "risk_skew_ratio": skew,
            "status": status,
        })

    # Sort descending by risk contribution
    asset_items.sort(key=lambda x: x["risk_contribution_pct"], reverse=True)

    # Portfolio level volatility and diversification metrics
    w_vec = np.asarray(proxy_weights.reindex(returns_df.columns).fillna(0.0), dtype=float)
    cov_mat = returns_df.cov().to_numpy(dtype=float)
    port_var = float(w_vec.T @ cov_mat @ w_vec)
    port_vol_ann = float(np.sqrt(max(port_var, 0.0) * 52.0)) * 100.0

    proxy_rc_fractions = (rc_df["rc_percentage"].to_numpy(dtype=float) / 100.0)
    sum_rc_sq = float(np.sum(proxy_rc_fractions ** 2))
    enc = float(1.0 / sum_rc_sq) if sum_rc_sq > 0 else 0.0

    rp_weights_dict = {
        p: round(float(w_rp.loc[p, "weights"]) * 100.0, 2)
        for p in returns_df.columns
    }
    hrp_weights_dict = {
        p: round(float(w_hrp.loc[p, "weights"]) * 100.0, 2)
        for p in returns_df.columns if p in w_hrp.index
    }

    # Convert proxy diagnostics to clean serializable dict
    proxy_diag_dict = {}
    for p in returns_df.columns:
        proxy_diag_dict[p] = {
            "weight_pct": round(float(proxy_weights.get(p, 0.0)) * 100.0, 2),
            "volatility_annualized_pct": round(float(rc_df.loc[p, "volatility_annualized"]) * 100.0, 2),
            "risk_contribution_pct": round(float(rc_df.loc[p, "rc_percentage"]), 2),
            "optimal_risk_parity_weight_pct": round(float(w_rp.loc[p, "weights"]) * 100.0, 2),
            "optimal_hrp_weight_pct": round(float(w_hrp.loc[p, "weights"]) * 100.0, 2) if p in w_hrp.index else None,
        }

    return {
        "summary": {
            "as_of": str(as_of) if as_of else None,
            "total_value_eur": total_val,
            "active_positions_count": len(active_pos),
            "proxy_series_count": len(returns_df.columns),
            "portfolio_volatility_annualized_pct": round(port_vol_ann, 2),
            "effective_number_of_bets_enc": round(enc, 2),
            "risk_parity_weights": rp_weights_dict,
            "hrp_weights": hrp_weights_dict,
            "solver_engine": "Riskfolio-Lib",
            "riskfolio_version": rp.__version__,
        },
        "proxy_diagnostics": proxy_diag_dict,
        "asset_diagnostics": asset_items,
    }


