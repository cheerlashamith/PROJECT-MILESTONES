import streamlit as st
from database import save_project
import random

# -------------------------------
# Cost Prediction Function
# -------------------------------
def estimate_project(area, floors, quality, construction):

    rates = {
        "Basic": 1800,
        "Standard": 2500,
        "Premium": 3500
    }

    rate = rates[quality]

    total_cost = area * floors * rate
    workers = max(10, int(area / 150))
    months = max(4, floors * 2)

    return total_cost, workers, months


# -------------------------------
# Streamlit Page
# -------------------------------
def show():

    st.title("🏠 Construction Cost Prediction")
    st.write("Predict the estimated construction cost using project details.")

    col1, col2 = st.columns(2)

    with col1:

        area = st.number_input(
            "Land Size (sq.ft)",
            min_value=500,
            step=100
        )

        floors = st.number_input(
            "Number of Floors",
            min_value=1,
            max_value=20
        )

    with col2:

        construction = st.selectbox(
            "Construction Type",
            [
                "House",
                "Apartment",
                "Office",
                "Hospital",
                "School"
            ]
        )

        quality = st.selectbox(
            "Material Quality",
            [
                "Basic",
                "Standard",
                "Premium"
            ]
        )

    st.markdown("---")

    if st.button("Analyze Construction", use_container_width=True):

        total_cost, workers, months = estimate_project(
            area,
            floors,
            quality,
            construction
        )

        project = {
            "Project ID": f"P{random.randint(1000,9999)}",
            "Project Name": construction,
            "Area": area,
            "Floors": floors,
            "Material": quality,
            "Estimated Cost": total_cost,
            "Workers": workers,
            "Duration": months,
            "Status": "Ongoing"
        }

        save_project(project)

        st.success("✅ Project Saved Successfully")

        c1, c2, c3 = st.columns(3)

        with c1:
            st.metric(
                "💰 Estimated Cost",
                f"₹ {total_cost:,.0f}"
            )

        with c2:
            st.metric(
                "👷 Workers Needed",
                workers
            )

        with c3:
            st.metric(
                "📅 Duration",
                f"{months} Months"
            )