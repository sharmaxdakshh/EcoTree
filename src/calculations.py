"""
Core environmental and health calculation engine for EcoTree.
"""

from datetime import date
import math


def calculate_age(planting_date):
    """Return age of tree in years."""
    if not planting_date:
        return 0
    return max(0, (date.today() - planting_date).days // 365)


def estimate_biomass_kg(dbh_cm, height_m, species_carbon_rate=0.25):
    """
    Simplified allometric biomass estimation.
    Real projects should use species-specific equations (e.g. from i-Tree).
    """
    a = 0.05 + species_carbon_rate
    b = 2.35
    biomass = a * (dbh_cm ** b) * (height_m / 12.0)
    return max(biomass, 5.0)


def carbon_sequestration_kg_per_year(dbh_cm, height_m, carbon_rate=0.25, age=10):
    """
    Estimate annual carbon sequestration in kg CO₂.
    """
    biomass = estimate_biomass_kg(dbh_cm, height_m, carbon_rate)
    # Younger trees sequester relatively faster, then slows
    age_factor = 0.75 + 0.45 * math.exp(-age / 28.0)
    annual = biomass * 0.47 * age_factor   # ~47% of dry biomass is carbon
    return round(annual, 2)


def oxygen_production_kg_per_year(carbon_kg):
    """Approximate oxygen production from carbon sequestration."""
    return round(carbon_kg * 1.2, 2)


def cooling_effect_kwh(height_m, canopy_radius_m=None):
    """
    Rough estimate of annual cooling / energy saving benefit in kWh.
    """
    if canopy_radius_m is None:
        canopy_radius_m = max(1.5, height_m * 0.38)
    area = math.pi * (canopy_radius_m ** 2)
    # Empirical urban forestry factor
    return round(area * 7.8, 1)


def calculate_health_score(dbh_cm, height_m, age,
                           leaf_condition=0.80,
                           bark_condition=0.75,
                           pest_score=0.90):
    """
    Composite health score (0-100).
    leaf_condition, bark_condition, pest_score should be in range 0.0 – 1.0
    """
    # Expected DBH based on rough age-growth relationship
    expected_dbh = 4.5 + age * 1.35
    growth_ratio = min(dbh_cm / expected_dbh, 1.6) if expected_dbh > 0 else 1.0
    growth_score = min(growth_ratio / 1.15, 1.0)

    # Age penalty for very old trees
    if age < 35:
        age_penalty = 1.0
    else:
        age_penalty = max(0.45, 1.0 - (age - 35) / 55.0)

    score = (
        growth_score * 0.30 +
        leaf_condition * 0.25 +
        bark_condition * 0.20 +
        age_penalty * 0.15 +
        pest_score * 0.10
    ) * 100.0

    return round(min(max(score, 0.0), 100.0), 1)


def health_status_from_score(score):
    """Map numeric score to categorical status."""
    if score >= 80:
        return "Healthy"
    elif score >= 60:
        return "Moderate"
    elif score >= 40:
        return "At Risk"
    else:
        return "Critical"


def predict_future_dbh(current_dbh, age, years_ahead=5, growth_rate=1.15):
    """Simple linear-ish growth projection."""
    remaining_vigor = max(0.4, 1.0 - age / 80.0)
    annual_growth = growth_rate * remaining_vigor
    return round(current_dbh + annual_growth * years_ahead, 1)
