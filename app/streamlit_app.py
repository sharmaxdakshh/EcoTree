"""
EcoTree Interactive Dashboard – Streamlit
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
from src.data_loader import generate_sample_data
from src.database import init_db

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
        font-size: 2.3rem;
        color: #1a5f2a;
        font-weight: 700;
        margin-bottom: 0;
        margin-top: 8px;
    }
    .subtitle {
        color: #555;
        font-size: 1rem;
        margin-top: -5px;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=600)
def get_data():
    db_path = "database/trees.db"
    
    # Agar database nahi hai to automatically create kar do
    if not os.path.exists(db_path):
        with st.spinner("Creating sample database... Please wait"):
            init_db(db_path)
            generate_sample_data(n_trees=500, db_path=db_path)
    
    return load_trees_df(db_path)


def main():
    # ===== Logo + Header =====
    col1, col2 = st.columns([0.7, 5.5])
    
    with col1:
        # Logo path - app folder ke andar logo.png hona chahiye
        if os.path.exists("app/logo.png"):
            st.image("app/logo.png", width=80)
        elif os.path.exists("logo.png"):
            st.image("logo.png", width=80)
        else:
            st.markdown("🌳")
    
    with col2:
        st.markdown('<p class="main-header">EcoTree Dashboard</p>', unsafe_allow_html=True)
        st.markdown('<p class="subtitle">Tree Inventory • Health Analysis • Environmental Impact</p>', unsafe_allow_html=True)

    st.markdown("---")

    try:
        df = get_data()
    except Exception as e:
        st.error(f"Error loading data: {e}")
        st.stop()

    # Sidebar filters
    st.sidebar.header("🔍 Filters")
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
        st.bar_chart(filtered["age"].value_counts().sort_index(), color="#6a1b9a")

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
        st.dataframe(critical_df, use_container_width=True, hide_index=True)
    else:
        st.success("No critical or at-risk trees under current filters.")

    with st.expander("View Full Filtered Dataset"):
        st.dataframe(filtered, use_container_width=True, hide_index=True)

    st.caption("EcoTree v1.0 • Sample data for demonstration purposes.")


if __name__ == "__main__":
    main()