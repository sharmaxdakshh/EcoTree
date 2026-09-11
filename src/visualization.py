"""
Visualization module – static plots + interactive map.
"""

import os
import matplotlib.pyplot as plt
import seaborn as sns
import folium
from folium.plugins import MarkerCluster

sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams["figure.facecolor"] = "white"


def plot_species_distribution(df, save_path="outputs/plots/species_dist.png"):
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.figure(figsize=(11, 6))
    counts = df["species"].value_counts()
    ax = sns.barplot(x=counts.values, y=counts.index, hue=counts.index,
                     palette="viridis", legend=False)
    plt.title("Tree Species Distribution", fontsize=14, fontweight="bold")
    plt.xlabel("Number of Trees")
    plt.ylabel("")
    for i, v in enumerate(counts.values):
        ax.text(v + 1, i, str(v), va="center")
    plt.tight_layout()
    plt.savefig(save_path, dpi=160, bbox_inches="tight")
    plt.close()
    return save_path


def plot_health_status(df, save_path="outputs/plots/health_status.png"):
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    order = ["Healthy", "Moderate", "At Risk", "Critical"]
    colors = ["#2ecc71", "#f1c40f", "#e67e22", "#e74c3c"]

    plt.figure(figsize=(9, 6))
    counts = df["health_status"].value_counts().reindex(order).fillna(0)
    bars = plt.bar(order, counts.values, color=colors, edgecolor="black", linewidth=0.6)
    plt.title("Tree Health Status Distribution", fontsize=14, fontweight="bold")
    plt.ylabel("Number of Trees")
    for bar, val in zip(bars, counts.values):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 3,
                 int(val), ha="center", fontweight="bold")
    plt.tight_layout()
    plt.savefig(save_path, dpi=160, bbox_inches="tight")
    plt.close()
    return save_path


def plot_carbon_by_zone(df, save_path="outputs/plots/carbon_zone.png"):
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    zone_carbon = (df.groupby("zone")["carbon_kg_year"]
                     .sum()
                     .sort_values(ascending=True))

    plt.figure(figsize=(10, 6))
    bars = plt.barh(zone_carbon.index, zone_carbon.values, color="#27ae60", edgecolor="black")
    plt.title("Annual Carbon Sequestration by Zone (kg CO₂)", fontsize=14, fontweight="bold")
    plt.xlabel("kg CO₂ / year")
    for bar, val in zip(bars, zone_carbon.values):
        plt.text(val + 20, bar.get_y() + bar.get_height()/2,
                 f"{val:,.0f}", va="center")
    plt.tight_layout()
    plt.savefig(save_path, dpi=160, bbox_inches="tight")
    plt.close()
    return save_path


def plot_age_vs_health(df, save_path="outputs/plots/age_health.png"):
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=df, x="age", y="health_score",
                    hue="health_status", palette={
                        "Healthy": "#2ecc71",
                        "Moderate": "#f1c40f",
                        "At Risk": "#e67e22",
                        "Critical": "#e74c3c"
                    }, alpha=0.7, s=60)
    plt.title("Age vs Health Score", fontsize=14, fontweight="bold")
    plt.xlabel("Age (years)")
    plt.ylabel("Health Score")
    plt.legend(title="Status", loc="lower left")
    plt.tight_layout()
    plt.savefig(save_path, dpi=160, bbox_inches="tight")
    plt.close()
    return save_path


def create_interactive_map(df, save_path="outputs/maps/tree_map.html"):
    """Create Folium map color-coded by health status."""
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    center = [df["latitude"].mean(), df["longitude"].mean()]
    m = folium.Map(location=center, zoom_start=12,
                   tiles="CartoDB positron")

    color_map = {
        "Healthy": "#27ae60",
        "Moderate": "#f39c12",
        "At Risk": "#e67e22",
        "Critical": "#c0392b"
    }

    marker_cluster = MarkerCluster().add_to(m)

    for _, row in df.iterrows():
        popup_html = f"""
        <div style="font-family: Arial; width: 220px">
            <b style="font-size:14px">{row['species']}</b><br>
            <b>Status:</b> {row['health_status']} ({row['health_score']})<br>
            <b>Age:</b> {row['age']} years<br>
            <b>DBH:</b> {row['dbh_cm']} cm<br>
            <b>Height:</b> {row['height_m']} m<br>
            <b>Carbon:</b> {row['carbon_kg_year']} kg/yr<br>
            <b>Zone:</b> {row['zone']}
        </div>
        """
        folium.CircleMarker(
            location=[row["latitude"], row["longitude"]],
            radius=6,
            color=color_map.get(row["health_status"], "#3498db"),
            fill=True,
            fill_color=color_map.get(row["health_status"], "#3498db"),
            fill_opacity=0.75,
            popup=folium.Popup(popup_html, max_width=250)
        ).add_to(marker_cluster)

    # Add legend
    legend_html = """
    <div style="position: fixed; bottom: 40px; left: 40px; z-index: 1000;
                background: white; padding: 12px; border-radius: 6px;
                border: 2px solid #333; font-size: 13px;">
        <b>Health Status</b><br>
        <i style="color:#27ae60">●</i> Healthy<br>
        <i style="color:#f39c12">●</i> Moderate<br>
        <i style="color:#e67e22">●</i> At Risk<br>
        <i style="color:#c0392b">●</i> Critical
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))

    m.save(save_path)
    return save_path
