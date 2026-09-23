"""Regression tests for the truthful E01 portfolio boundary."""

import datetime as dt

import pandas as pd
import pytest

from ipos.aggregate import portfolio as agg
from ipos.etl import portfolio_csv as csv


@pytest.mark.parametrize("row", [
    ",1,100,EUR", "X,,100,EUR", "X,1,bad,EUR", "X,1,inf,EUR",
    "X,inf,100,EUR", "X,1,100,", "X,1,100,EURO", "X,1,NaN,EUR",
])
def test_invalid_input_cannot_silently_reduce_holdings(tmp_path, row):
    path = tmp_path / "portfolio.csv"
    path.write_text(
        "instrument,quantity,value_eur,currency\nGOOD,1,100,EUR\n" + row + "\n",
        encoding="utf-8",
    )
    with pytest.raises(RuntimeError, match="refusing partial holdings"):
        csv.load_positions(path)


def _positions(currency="USD"):
    return pd.DataFrame({
        "instrument": ["X"],
        "quantity": [2.0],
        "value_eur": [120.0],
        "currency": [currency],
    })


def test_fx_conversion_is_idempotent_and_labels_eur(monkeypatch):
    monkeypatch.setattr(agg, "_latest_fx_value", lambda *args: 1.2)
    first, warnings = agg.convert_to_eur(_positions(), None, dt.date(2026, 9, 18))
    second, _ = agg.convert_to_eur(first, None, dt.date(2026, 9, 18))

    assert not warnings
    assert first.iloc[0]["value_eur"] == pytest.approx(100.0)
    assert first.iloc[0]["currency"] == "EUR"
    pd.testing.assert_frame_equal(first, second)


@pytest.mark.parametrize("rate", [None, 0.0, -1.0, float("nan"), float("inf")])
def test_invalid_fx_cannot_enter_eur_totals(monkeypatch, rate):
    monkeypatch.setattr(agg, "_latest_fx_value", lambda *args: rate)
    frame, warnings = agg.convert_to_eur(_positions(), None, dt.date(2026, 9, 18))

    assert warnings
    with pytest.raises(ValueError, match="unresolved currency"):
        agg.aggregate_portfolio(frame, {"X": "EquityRisk"})


def test_unsupported_currency_cannot_be_counted_as_eur():
    frame, warnings = agg.convert_to_eur(_positions("GBP"), None, dt.date(2026, 9, 18))

    assert warnings
    with pytest.raises(ValueError, match="unresolved currency"):
        agg.aggregate_portfolio(frame, {"X": "EquityRisk"})


@pytest.mark.parametrize("value", [float("nan"), float("inf"), -float("inf")])
def test_nonfinite_aggregate_rejected(value):
    frame = _positions("EUR")
    frame.loc[0, "value_eur"] = value
    with pytest.raises(ValueError, match="non-finite"):
        agg.aggregate_portfolio(frame, {"X": "EquityRisk"})
