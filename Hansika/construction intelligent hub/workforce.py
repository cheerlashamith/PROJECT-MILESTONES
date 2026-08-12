import streamlit as st
from database import load_projects
from worker_db import workers
from allocation_db import load_allocations, save_allocations


def show():

    st.title("👷 Smart Workforce Allocator")

    # -----------------------------
    # Load Projects
    # -----------------------------

    df = load_projects()

    if df.empty:
        st.warning("No projects available.")
        return

    # Remove Painting Projects
    df = df[
        ~df["Project ID"].astype(str).str.startswith("PNT")
    ]

    project_ids = df["Project ID"].tolist()

    if len(project_ids) == 0:
        st.warning(
            "No construction projects available."
        )
        return

    # -----------------------------
    # Select Project
    # -----------------------------

    project_id = st.selectbox(
        "Select Project ID",
        project_ids
    )

    project_data = df[
        df["Project ID"] == project_id
    ].iloc[0]

    # -----------------------------
    # Project Overview
    # -----------------------------

    st.subheader("📋 Project Overview")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Project Name",
        project_data["Project Name"]
    )

    c2.metric(
        "Area",
        f"{project_data['Area']} sq.ft"
    )

    c3.metric(
        "Floors",
        project_data["Floors"]
    )

    c4.metric(
        "Workers Required",
        project_data["Workers"]
    )

    c5, c6, c7, c8 = st.columns(4)

    c5.metric(
        "Material",
        project_data["Material"]
    )

    c6.metric(
        "Estimated Cost",
        f"₹ {int(project_data['Estimated Cost']):,}"
    )

    c7.metric(
        "Duration",
        f"{project_data['Duration']} Months"
    )

    c8.metric(
        "Status",
        project_data["Status"]
    )

    st.divider()

    # -----------------------------
    # AI Workforce Recommendation
    # -----------------------------

    area = project_data["Area"]

    if area <= 500:
        mason_count = 3
        helper_count = 3

    elif area <= 1000:
        mason_count = 5
        helper_count = 5

    else:
        mason_count = 8
        helper_count = 8

    st.subheader("🤖 AI Workforce Recommendation")

    col_rec1, col_rec2 = st.columns([1, 1])
    with col_rec1:
        st.info(f"""
🏠 Project Type       : {project_data['Project Name']}
📐 Area               : {project_data['Area']} sq.ft
🏢 Floors             : {project_data['Floors']}

Auto-Calculated Minimum Baseline:
👷 Site Engineers : 1
🏗 Supervisors    : 1
🧱 Masons         : {mason_count}
🧰 Helpers        : {helper_count}
⚡ Electricians   : 2
🚿 Plumbers       : 2
🎨 Painters       : 3
    """)
    
    with col_rec2:
        if st.button("Generate AI Custom Allocation Strategy"):
            with st.spinner("AI is calculating the optimal workforce strategy..."):
                import requests
                prompt = f"""
                You are a construction workforce allocator. 
                Project: {project_data['Project Name']}, Area: {area} sq.ft, Floors: {project_data['Floors']}.
                Currently we estimate {mason_count} Masons and {helper_count} Helpers.
                Give a brief 3-point strategy on optimally allocating shifts and managing this workforce to maximize efficiency without burnout.
                """
                try:
                    res = requests.post(
                        "http://localhost:11434/api/generate",
                        json={"model": "qwen2.5:0.5b", "prompt": prompt, "stream": False}
                    )
                    ai_rec = res.json().get("response", "No AI response.")
                    st.success("AI Strategy:\n" + ai_rec)
                except Exception as e:
                    st.error(f"Error querying AI model: {e}")

    # -----------------------------
    # Allocate Workforce
    # -----------------------------

    if st.button(
        "🚀 Allocate Workforce",
        use_container_width=True
    ):

        site_engineers = [
            w["name"]
            for w in workers
            if w["role"] == "Site Engineer"
        ][:1]

        supervisors = [
            w["name"]
            for w in workers
            if w["role"] == "Supervisor"
        ][:1]

        masons = [
            w["name"]
            for w in workers
            if w["role"] == "Mason"
        ][:mason_count]

        helpers = [
            w["name"]
            for w in workers
            if w["role"] == "Helper"
        ][:helper_count]

        electricians = [
            w["name"]
            for w in workers
            if w["role"] == "Electrician"
        ][:2]

        plumbers = [
            w["name"]
            for w in workers
            if w["role"] == "Plumber"
        ][:2]

        painters = [
            w["name"]
            for w in workers
            if w["role"] == "Painter"
        ][:3]

        allocated_workers = (
            site_engineers +
            supervisors +
            masons +
            helpers +
            electricians +
            plumbers +
            painters
        )

        allocations = load_allocations()

        allocations[project_id] = allocated_workers

        save_allocations(
            allocations
        )

        st.success(
            f"✅ {len(allocated_workers)} workers allocated successfully for Project {project_id}"
        )

        # -----------------------------
        # Workforce Summary
        # -----------------------------

        st.subheader("📊 Workforce Summary")

        col1, col2, col3, col4 = st.columns(4)

        col1.metric(
            "Total Workers",
            len(allocated_workers)
        )

        col2.metric(
            "Engineers",
            len(site_engineers)
        )

        col3.metric(
            "Supervisors",
            len(supervisors)
        )

        col4.metric(
            "Skilled Workers",
            len(masons) +
            len(electricians) +
            len(plumbers) +
            len(painters)
        )

        st.divider()

        # -----------------------------
        # Worker Details
        # -----------------------------

        st.subheader("📋 Allocated Workforce")

        st.markdown("### 👷 Site Engineers")
        for worker in site_engineers:
            st.write(f"• {worker}")

        st.markdown("### 🏗 Supervisors")
        for worker in supervisors:
            st.write(f"• {worker}")

        st.markdown("### 🧱 Masons")
        for worker in masons:
            st.write(f"• {worker}")

        st.markdown("### 🧰 Helpers")
        for worker in helpers:
            st.write(f"• {worker}")

        st.markdown("### ⚡ Electricians")
        for worker in electricians:
            st.write(f"• {worker}")

        st.markdown("### 🚿 Plumbers")
        for worker in plumbers:
            st.write(f"• {worker}")

        st.markdown("### 🎨 Painters")
        for worker in painters:
            st.write(f"• {worker}")

        st.divider()

        st.success(
            "📌 Workforce allocation saved successfully and is now available in Attendance Management."
        )