"""
Statistical analysis and data aggregation for EcoTree.
"""

import pandas as pd
import random
from sqlalchemy.orm import joinedload
from src.database import get_session, Tree
from src.calculations import (
    calculate_age,
    carbon_sequestration_kg_per_year,
    oxygen_production_kg_per_year,
    calculate_health_score,
    health_status_from_score,
    cooling_effect_kwh,
    predict_future_dbh
)


def load_trees_df(db_path="database/trees.db"):
    """Load all trees into a rich pandas DataFrame with calculated metrics."""
    session = get_session(db_path)
    trees = session.query(Tree).options(joinedload(Tree.species)).all()

    records = []
    for t in trees:
        age = calculate_age(t.planting_date)
        carbon_rate = t.species.carbon_rate if t.species else 0.25

        carbon = carbon_sequestration_kg_per_year(
            t.dbh_cm, t.height_m, carbon_rate, age
        )
        oxygen = oxygen_production_kg_per_year(carbon)
        cooling = cooling_effect_kwh(t.height_m)

        # Simulated inspection scores (in real system these come from field data)
        leaf = round(random.uniform(0.52, 0.98), 2)
        bark = round(random.uniform(0.48, 0.96), 2)
        pest = round(random.uniform(0.55, 1.00), 2)

        score = calculate_health_score(
            t.dbh_cm, t.height_m, age, leaf, bark, pest
        )
        status = health_status_from_score(score)

        future_dbh_5 = predict_future_dbh(t.dbh_cm, age, years_ahead=5)
        future_dbh_10 = predict_future_dbh(t.dbh_cm, age, years_ahead=10)

        records.append({
            "id": t.id,
            "species": t.common_name,
            "scientific_name": t.species.scientific_name if t.species else "",
            "zone": t.zone,
            "latitude": t.latitude,
            "longitude": t.longitude,
            "planting_date": t.planting_date,
            "age": age,
            "dbh_cm": t.dbh_cm,
            "height_m": t.height_m,
            "carbon_kg_year": carbon,
            "oxygen_kg_year": oxygen,
            "cooling_kwh": cooling,
            "health_score": score,
            "health_status": status,
            "future_dbh_5yr": future_dbh_5,
            "future_dbh_10yr": future_dbh_10,
            "last_inspected": t.last_inspected,
            "notes": t.notes or ""
        })

    session.close()
    df = pd.DataFrame(records)
    return df


def get_summary_stats(df: pd.DataFrame) -> dict:
    """High-level city / project summary."""
    return {
        "total_trees": len(df),
        "total_carbon_tonnes": round(df["carbon_kg_year"].sum() / 1000, 2),
        "total_oxygen_tonnes": round(df["oxygen_kg_year"].sum() / 1000, 2),
        "total_cooling_mwh": round(df["cooling_kwh"].sum() / 1000, 1),
        "avg_health": round(df["health_score"].mean(), 1),
        "healthy_pct": round((df["health_status"] == "Healthy").mean() * 100, 1),
        "moderate_pct": round((df["health_status"] == "Moderate").mean() * 100, 1),
        "at_risk_pct": round((df["health_status"] == "At Risk").mean() * 100, 1),
        "critical_count": int((df["health_status"] == "Critical").sum()),
        "avg_age": round(df["age"].mean(), 1),
        "avg_dbh": round(df["dbh_cm"].mean(), 1),
    }


def zone_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregated metrics by zone."""
    agg = df.groupby("zone").agg(
        tree_count=("id", "count"),
        total_carbon_kg=("carbon_kg_year", "sum"),
        avg_health=("health_score", "mean"),
        critical_trees=("health_status", lambda x: (x == "Critical").sum()),
        avg_age=("age", "mean"),
        avg_dbh=("dbh_cm", "mean")
    ).round(1)
    return agg.sort_values("total_carbon_kg", ascending=False)


def species_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregated metrics by species."""
    return df.groupby("species").agg(
        count=("id", "count"),
        avg_health=("health_score", "mean"),
        total_carbon=("carbon_kg_year", "sum"),
        avg_age=("age", "mean")
    ).round(1).sort_values("count", ascending=False)


def get_critical_trees(df: pd.DataFrame, limit=20) -> pd.DataFrame:
    """Return trees that need immediate attention."""
    critical = df[df["health_status"].isin(["Critical", "At Risk"])]
    return critical.sort_values("health_score").head(limit)[
        ["id", "species", "zone", "age", "dbh_cm", "health_score", "health_status"]
    ]
