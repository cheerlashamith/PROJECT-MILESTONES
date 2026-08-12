import streamlit as st
import pandas as pd
import random
from database import save_project


def show():

    st.title("🎨 Smart Painting Cost Calculator")
    st.write("Estimate paint quantity, labour, materials and total painting cost.")

    col1, col2 = st.columns(2)

    with col1:

        wall_area = st.number_input(
            "Wall Area (sq.ft)",
            min_value=100,
            step=50
        )

        painting_type = st.selectbox(
            "Painting Type",
            [
                "Interior",
                "Exterior",
                "Interior + Exterior"
            ]
        )

        coats = st.selectbox(
            "Number of Coats",
            [1, 2, 3]
        )

        primer = st.checkbox("Include Primer")

        putty = st.checkbox("Include Wall Putty")

    with col2:

        quality = st.selectbox(
            "Paint Quality",
            [
                "Basic",
                "Standard",
                "Premium"
            ]
        )

        brand = st.selectbox(
            "Paint Brand",
            [
                "Asian Paints",
                "Berger",
                "Nerolac",
                "Dulux"
            ]
        )

        labour_charge = st.number_input(
            "Labour Charge per Worker (₹)",
            min_value=500,
            value=800
        )

    if st.button("🎨 Calculate Painting", use_container_width=True):

        # --------------------------------
        # Paint Required
        # --------------------------------

        paint_litres = round((wall_area * coats) / 120, 2)

        # --------------------------------
        # Paint Cost
        # --------------------------------

        rates = {

            "Basic":250,

            "Standard":400,

            "Premium":650

        }

        paint_price = rates[quality]

        paint_cost = paint_litres * paint_price

        # --------------------------------
        # Primer
        # --------------------------------

        primer_cost = 0

        if primer:

            primer_cost = wall_area * 8

        # --------------------------------
        # Putty
        # --------------------------------

        putty_cost = 0

        if putty:

            putty_cost = wall_area * 12

        # --------------------------------
        # Labour
        # --------------------------------

        workers = max(2, int(wall_area / 800))

        labour_cost = workers * labour_charge

        # --------------------------------
        # Duration
        # --------------------------------

        days = max(1, int(wall_area / 1000))

        # --------------------------------
        # GST
        # --------------------------------

        subtotal = (

            paint_cost

            + primer_cost

            + putty_cost

            + labour_cost

        )

        gst = subtotal * 0.18

        total_cost = subtotal + gst

        # --------------------------------
        # Results
        # --------------------------------

        st.success("✅ Painting Estimation Completed Successfully")

        c1, c2 = st.columns(2)

        with c1:

            st.metric(
                "🎨 Paint Required",
                f"{paint_litres:.1f} Litres"
            )

            st.metric(
                "👷 Workers Required",
                workers
            )

            st.metric(
                "📅 Completion Time",
                f"{days} Days"
            )

        with c2:

            st.metric(
                "💰 Paint Cost",
                f"₹ {paint_cost:,.0f}"
            )

            st.metric(
                "🪜 Primer Cost",
                f"₹ {primer_cost:,.0f}"
            )

            st.metric(
                "🧱 Putty Cost",
                f"₹ {putty_cost:,.0f}"
            )

        st.divider()

        st.subheader("💵 Cost Summary")

        st.metric(
            "Labour Cost",
            f"₹ {labour_cost:,.0f}"
        )

        st.metric(
            "GST (18%)",
            f"₹ {gst:,.0f}"
        )

        st.metric(
            "Total Estimated Cost",
            f"₹ {total_cost:,.0f}"
        )

        # --------------------------------
        # Cost Breakdown Chart
        # --------------------------------

        st.subheader("📊 Cost Breakdown")

        chart = pd.DataFrame(

            {

                "Amount":[

                    paint_cost,

                    primer_cost,

                    putty_cost,

                    labour_cost

                ]

            },

            index=[

                "Paint",

                "Primer",

                "Putty",

                "Labour"

            ]

        )

        st.bar_chart(chart)

        st.divider()

        st.subheader("🎯 AI Recommendation")

        if quality == "Premium":

            st.success(
                "Premium quality paint provides better durability, weather resistance and long life."
            )

        elif quality == "Standard":

            st.info(
                "Standard paint offers a good balance between quality and cost."
            )

        else:

            st.warning(
                "Basic paint is economical but may require repainting sooner."
            )

        st.success(f"Recommended Paint Brand : {brand}")

        # --------------------------------
        # Save Project
        # --------------------------------

        project = {

            "Project ID": f"PNT{random.randint(1000,9999)}",

            "Project Name": "Painting",

            "Area": wall_area,

            "Floors": "-",

            "Material": brand,

            "Estimated Cost": total_cost,

            "Workers": workers,

            "Duration": f"{days} Days",

            "Status": "Completed"

        }

        save_project(project)

        st.success("💾 Painting Report Saved Successfully")