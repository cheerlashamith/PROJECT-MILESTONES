import streamlit as st
from database import load_projects


def show():

    st.title("⏳ AI Project Delay Predictor")

    st.write(
        "Analyze construction delay risks automatically using project information and weather conditions."
    )

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

    project_id = st.selectbox(
        "Select Project ID",
        project_ids
    )

    project = df[
        df["Project ID"] == project_id
    ].iloc[0]

    # -----------------------------
    # Safe Conversion
    # -----------------------------

    floors = int(project["Floors"])
    workers = int(project["Workers"])
    area = int(project["Area"])

    try:
        duration = int(project["Duration"])
    except:
        duration = 0

    # -----------------------------
    # Project Overview
    # -----------------------------

    st.subheader("📋 Project Overview")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Project Name",
        project["Project Name"]
    )

    c2.metric(
        "Area",
        f"{area} sq.ft"
    )

    c3.metric(
        "Floors",
        floors
    )

    c4.metric(
        "Workers",
        workers
    )

    c5, c6, c7, c8 = st.columns(4)

    c5.metric(
        "Material",
        project["Material"]
    )

    c6.metric(
        "Estimated Cost",
        f"₹ {int(project['Estimated Cost']):,}"
    )

    c7.metric(
        "Duration",
        f"{project['Duration']} Months"
    )

    c8.metric(
        "Status",
        project["Status"]
    )

    st.divider()

    # -----------------------------
    # Weather Condition
    # -----------------------------

    weather = st.selectbox(
        "🌦 Weather Condition",
        [
            "☀ Sunny",
            "☁ Cloudy",
            "🌧 Rainy",
            "⛈ Storm",
            "🌪 Cyclone"
        ]
    )

    progress = st.slider(
        "📈 Current Project Progress (%)",
        0,
        100,
        50
    )

    # -----------------------------
    # Analyze Delay
    # -----------------------------

    if st.button(
        "🔍 Analyze Delay Risk",
        use_container_width=True
    ):

        risk_score = 0

        # Workforce Analysis
        if workers < 10:
            risk_score += 3
        elif workers < 15:
            risk_score += 2

        # Floor Analysis
        if floors >= 5:
            risk_score += 3
        elif floors >= 3:
            risk_score += 2

        # Area Analysis
        if area >= 1000:
            risk_score += 2

        # Duration Analysis
        if duration >= 12:
            risk_score += 2

        # Weather Analysis
        if weather == "☀ Sunny":
            risk_score += 0

        elif weather == "☁ Cloudy":
            risk_score += 1

        elif weather == "🌧 Rainy":
            risk_score += 3

        elif weather == "⛈ Storm":
            risk_score += 5

        elif weather == "🌪 Cyclone":
            risk_score += 8

        # Progress Analysis
        if progress < 30:
            risk_score += 2

        # -----------------------------
        # Final Prediction
        # -----------------------------

        if risk_score >= 12:
            risk = "🔴 High Risk"
            delay_days = 30
            completion = 60

        elif risk_score >= 7:
            risk = "🟠 Medium Risk"
            delay_days = 15
            completion = 80

        else:
            risk = "🟢 Low Risk"
            delay_days = 5
            completion = 95

        st.divider()

        st.subheader("📊 AI Delay Analytics")

        a1, a2, a3, a4 = st.columns(4)

        a1.metric(
            "Risk Level",
            risk
        )

        a2.metric(
            "Estimated Delay",
            f"{delay_days} Days"
        )

        a3.metric(
            "Completion Probability",
            f"{completion}%"
        )

        a4.metric(
            "Risk Score",
            risk_score
        )

        st.divider()

        st.subheader("⚠ AI Detected Risk Factors")

        if workers < 10:
            st.warning(
                "Low workforce availability detected."
            )

        if floors >= 5:
            st.warning(
                "High-rise construction increases project complexity."
            )

        if area >= 1000:
            st.warning(
                "Large project area may increase execution time."
            )

        if duration >= 12:
            st.warning(
                "Long project duration increases schedule dependency risks."
            )

        if weather == "🌧 Rainy":
            st.warning(
                "Rain may delay excavation and outdoor activities."
            )

        elif weather == "⛈ Storm":
            st.warning(
                "Storm conditions may stop crane and electrical operations."
            )

        elif weather == "🌪 Cyclone":
            st.error(
                "Cyclone conditions detected. Construction activities should be suspended."
            )

        if progress < 30:
            st.warning(
                "Project progress is below expected levels."
            )

        st.divider()

        st.subheader("🤖 AI Recommendations")

        if st.button("Generate AI Delay Mitigation Plan"):
            with st.spinner("AI is analyzing risks and generating recommendations..."):
                import requests
                prompt = f"""
                You are a construction project manager. This project '{project['Project Name']}' is at {progress}% completion.
                It has a delay risk score of {risk_score} (Level: {risk}). 
                Weather: {weather}, Floors: {floors}, Area: {area}, Expected duration: {duration} months.
                Provide 3 actionable steps to mitigate the delay and ensure timely completion.
                """
                try:
                    res = requests.post(
                        "http://localhost:11434/api/generate",
                        json={"model": "qwen2.5:0.5b", "prompt": prompt, "stream": False}
                    )
                    ai_recommendation = res.json().get("response", "No AI response.")
                    st.info(ai_recommendation)
                except Exception as e:
                    st.error(f"Error querying AI model: {e}")
                    
        else:
            if risk_score >= 12:
                st.error("Increase workforce allocation immediately.")
                st.error("Conduct daily progress review meetings.")
                st.error("Prepare contingency plans for severe weather.")
            elif risk_score >= 7:
                st.warning("Weekly monitoring is recommended.")
                st.warning("Maintain additional material stock.")
                st.warning("Review manpower utilization regularly.")
            else:
                st.success("Project is progressing within expected timelines.")
                st.success("Continue regular monitoring and reporting.")