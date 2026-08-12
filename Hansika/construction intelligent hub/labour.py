import streamlit as st

def show():

    st.title("👷 Labour Requirement Estimator")
    st.write("Estimate manpower, labour cost and project duration.")

    col1, col2 = st.columns(2)

    with col1:

        area = st.number_input(
            "Construction Area (sq.ft)",
            min_value=500,
            step=100
        )

        floors = st.number_input(
            "Number of Floors",
            min_value=1,
            max_value=20
        )

    with col2:

        project_type = st.selectbox(
            "Project Type",
            [
                "Residential",
                "Commercial",
                "Hospital",
                "School",
                "Apartment"
            ]
        )

        wage = st.number_input(
            "Daily Wage per Worker (₹)",
            min_value=500,
            value=900
        )

    if st.button("Estimate Labour", use_container_width=True):

        total_area = area * floors

        civil = max(6, int(total_area / 900))
        electricians = max(2, int(total_area / 2500))
        plumbers = max(2, int(total_area / 3000))
        painters = max(2, int(total_area / 1800))
        supervisors = max(1, int(total_area / 5000))

        total_workers = (
            civil +
            electricians +
            plumbers +
            painters +
            supervisors
        )

        duration = max(3, int(total_area / 2500))

        labour_cost = total_workers * wage * duration * 30

        st.success("Labour Estimation Completed Successfully")

        c1, c2 = st.columns(2)

        with c1:

            st.metric("👷 Civil Workers", civil)
            st.metric("⚡ Electricians", electricians)
            st.metric("🚰 Plumbers", plumbers)

        with c2:

            st.metric("🎨 Painters", painters)
            st.metric("👨‍💼 Supervisors", supervisors)
            st.metric("👥 Total Workers", total_workers)

        st.markdown("---")

        st.metric(
            "💰 Estimated Labour Cost",
            f"₹ {labour_cost:,.0f}"
        )

        st.metric(
            "📅 Estimated Project Duration",
            f"{duration} Months"
        )

        st.info(
            "This estimation is based on standard labour allocation for construction projects."
        )