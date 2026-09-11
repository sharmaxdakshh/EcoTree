"""
Unit tests for the calculation engine.
"""

import pytest
from datetime import date, timedelta
from src.calculations import (
    calculate_age,
    carbon_sequestration_kg_per_year,
    oxygen_production_kg_per_year,
    calculate_health_score,
    health_status_from_score,
    cooling_effect_kwh,
    predict_future_dbh
)


def test_calculate_age():
    today = date.today()
    assert calculate_age(today - timedelta(days=365 * 10)) == 10
    assert calculate_age(None) == 0
    assert calculate_age(today) == 0


def test_carbon_positive():
    val = carbon_sequestration_kg_per_year(30, 12, 0.25, 15)
    assert val > 0
    assert isinstance(val, float)


def test_oxygen_relation():
    carbon = 50.0
    oxygen = oxygen_production_kg_per_year(carbon)
    assert oxygen == round(carbon * 1.2, 2)


def test_health_score_range():
    score = calculate_health_score(25, 10, 12, 0.9, 0.85, 0.95)
    assert 0 <= score <= 100


def test_health_status_mapping():
    assert health_status_from_score(92) == "Healthy"
    assert health_status_from_score(72) == "Moderate"
    assert health_status_from_score(48) == "At Risk"
    assert health_status_from_score(25) == "Critical"


def test_cooling_positive():
    val = cooling_effect_kwh(15)
    assert val > 0


def test_future_dbh():
    future = predict_future_dbh(20, age=8, years_ahead=5)
    assert future > 20
