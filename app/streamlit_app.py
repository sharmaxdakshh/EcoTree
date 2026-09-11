"""
EcoTree Interactive Dashboard – Streamlit
Run with:  streamlit run app/streamlit_app.py
"""

import streamlit as st
import pandas as pd
import sys
import os

# Add project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.analysis import (
    load_trees_df, get_summary_stats, zone_summary,
    species_summary, get_critical_trees
)

st.set_page_config(
    page_title="EcoTree Dashboard",
    page_icon="🌳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.4rem;
        color: #1a5f2a;
        font-weight: 700;
        margin-bottom: 0.2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%);
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #2e7d32;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=300)
def get_data():
    return load_trees_df()


def main():
    st.markdown('<p class="main-header">🌳 EcoTree Dashboard</p>', unsafe_allow_html=True)
    st.caption("Tree Inventory • Health Analysis • Environmental Impact")

    try:
        df = get_data()
    except Exception as e:
        st.error("Database not found. Please run first:  `python main.py init`")
        st.stop()

    # Sidebar filters
    st.sidebar.header("Filters")
    zones = ["All Zones"] + sorted(df["zone"].unique().tolist())
    selected_zone = st.sidebar.selectbox("Zone", zones)

    species_list = ["All Species"] + sorted(df["species"].unique().tolist())
    selected_species = st.sidebar.selectbox("Species", species_list)

    status_list = ["All Status"] + ["Healthy", "Moderate", "At Risk", "Critical"]
    selected_status = st.sidebar.selectbox("Health Status", status_list)

    # Apply filters
    filtered = df.copy()
    if selected_zone != "All Zones":
        filtered = filtered[filtered["zone"] == selected_zone]
    if selected_species != "All Species":
        filtered = filtered[filtered["species"] == selected_species]
    if selected_status != "All Status":
        filtered = filtered[filtered["health_status"] == selected_status]

    # ===== KPI Row =====
    stats = get_summary_stats(filtered)

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Trees", f"{stats['total_trees']:,}")
    c2.metric("Carbon (t/yr)", stats["total_carbon_tonnes"])
    c3.metric("Oxygen (t/yr)", stats["total_oxygen_tonnes"])
    c4.metric("Avg Health", stats["avg_health"])
    c5.metric("Critical", stats["critical_count"], delta_color="inverse")

    st.divider()

    # ===== Charts =====
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("Health Status")
        health_counts = filtered["health_status"].value_counts().reindex(
            ["Healthy", "Moderate", "At Risk", "Critical"]
        ).fillna(0)
        st.bar_chart(health_counts, color="#2e7d32")

        st.subheader("Species Distribution")
        st.bar_chart(filtered["species"].value_counts(), color="#1565c0")

    with col_right:
        st.subheader("Carbon by Zone")
        zone_carbon = filtered.groupby("zone")["carbon_kg_year"].sum().sort_values(ascending=False)
        st.bar_chart(zone_carbon, color="#27ae60")

        st.subheader("Age Distribution")
        st.histogram_chart = st.bar_chart(
            filtered["age"].value_counts().sort_index(), color="#6a1b9a"
        )

    st.divider()

    # ===== Map =====
    st.subheader("Geographic Distribution")
    map_df = filtered[["latitude", "longitude"]].rename(
        columns={"latitude": "lat", "longitude": "lon"}
    )
    if not map_df.empty:
        st.map(map_df, zoom=11)
    else:
        st.info("No trees match the current filters.")

    st.divider()

    # ===== Critical Trees Table =====
    st.subheader("Trees Needing Attention")
    critical_df = get_critical_trees(filtered, limit=25)
    if not critical_df.empty:
        st.dataframe(
            critical_df,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.success("No critical or at-risk trees under current filters. Great job!")

    # ===== Raw Data Expander =====
    with st.expander("View Full Filtered Dataset"):
        st.dataframe(filtered, use_container_width=True, hide_index=True)

    st.caption("EcoTree v1.0 • Data is simulated for demonstration purposes.")


if __name__ == "__main__":
    main()
