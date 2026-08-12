import streamlit as st
def show():
    st.write("Material module loaded")

    st.title("📦 Construction Material Calculator")
    st.write("Estimate the materials required for your construction project.")

    col1, col2 = st.columns(2)

    with col1:
        area = st.number_input(
            "Land Area (sq.ft)",
            min_value=500,
            step=100
        )

        floors = st.number_input(
            "Number of Floors",
            min_value=1,
            max_value=20
        )

    with col2:
        quality = st.selectbox(
            "Material Quality",
            ["Basic", "Standard", "Premium"]
        )

        waste = st.slider(
            "Material Wastage (%)",
            0,
            20,
            5
        )

    if st.button("Calculate Materials", use_container_width=True):

        total_area = area * floors

        cement = total_area * 0.42
        bricks = total_area * 55
        steel = total_area * 3.5
        sand = total_area * 0.06

        cement *= (1 + waste/100)
        bricks *= (1 + waste/100)
        steel *= (1 + waste/100)
        sand *= (1 + waste/100)

        material_cost = (
            cement * 420 +
            bricks * 8 +
            steel * 70 +
            sand * 1800
        )

        st.success("Material Estimation Completed Successfully")

        c1, c2 = st.columns(2)

        with c1:

            st.metric(
                "🧱 Cement Bags",
                f"{cement:.0f}"
            )

            st.metric(
                "🧱 Bricks",
                f"{bricks:,.0f}"
            )

        with c2:

            st.metric(
                "🏗 Steel (kg)",
                f"{steel:,.0f}"
            )

            st.metric(
                "🏜 Sand (Ton)",
                f"{sand:.1f}"
            )

        st.markdown("---")

        st.metric(
            "💰 Estimated Material Cost",
            f"₹ {material_cost:,.0f}"
        )

        st.info(
            "This estimation is based on standard construction practices. "
            "Actual material requirements may vary depending on structural design."
        )