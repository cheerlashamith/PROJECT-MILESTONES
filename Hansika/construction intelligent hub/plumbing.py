import streamlit as st

def show():

    st.title("🚰 Plumbing Cost Calculator")
    st.write("Estimate plumbing materials, workers, cost and duration.")

    col1, col2 = st.columns(2)

    with col1:

        area = st.number_input(
            "House Area (sq.ft)",
            min_value=500,
            step=100
        )

        bathrooms = st.number_input(
            "Number of Bathrooms",
            min_value=1,
            max_value=20
        )

    with col2:

        kitchens = st.number_input(
            "Number of Kitchens",
            min_value=1,
            max_value=10
        )

        quality = st.selectbox(
            "Pipe Quality",
            [
                "Basic",
                "Standard",
                "Premium"
            ]
        )

    if st.button("Calculate Plumbing", use_container_width=True):

        pvc_pipe = area * 0.25
        water_pipe = area * 0.18

        fittings = bathrooms * 8 + kitchens * 5

        workers = max(2, bathrooms)

        if quality == "Basic":
            cost = pvc_pipe * 120 + water_pipe * 90 + fittings * 250

        elif quality == "Standard":
            cost = pvc_pipe * 160 + water_pipe * 120 + fittings * 350

        else:
            cost = pvc_pipe * 220 + water_pipe * 180 + fittings * 500

        days = workers + 2

        st.success("Plumbing Estimation Completed")

        c1, c2 = st.columns(2)

        with c1:

            st.metric(
                "PVC Pipes",
                f"{pvc_pipe:.1f} m"
            )

            st.metric(
                "Water Pipes",
                f"{water_pipe:.1f} m"
            )

            st.metric(
                "Pipe Fittings",
                fittings
            )

        with c2:

            st.metric(
                "Plumbers Required",
                workers
            )

            st.metric(
                "Estimated Cost",
                f"₹ {cost:,.0f}"
            )

            st.metric(
                "Completion Time",
                f"{days} Days"
            )

        st.info(
            "The estimation includes pipe length, fittings, labour and approximate completion time."
        )