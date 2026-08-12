import streamlit as st
from database import load_projects
from datetime import datetime
import pandas as pd
import os

REPORT_FILE = "daily_reports.csv"


def save_report(report):

    if os.path.exists(REPORT_FILE):
        df = pd.read_csv(REPORT_FILE)
    else:
        df = pd.DataFrame()

    df = pd.concat(
        [df, pd.DataFrame([report])],
        ignore_index=True
    )

    df.to_csv(
        REPORT_FILE,
        index=False
    )


def load_reports():

    if os.path.exists(REPORT_FILE):
        return pd.read_csv(REPORT_FILE)

    return pd.DataFrame()


def show():

    st.title("📋 Daily Site Report Analyzer")

    projects = load_projects()

    if projects.empty:
        st.warning(
            "No projects available."
        )
        return

    projects = projects[
        ~projects["Project ID"].astype(str).str.startswith("PNT")
    ]

    project_ids = projects["Project ID"].tolist()

    project_id = st.selectbox(
        "Select Project ID",
        project_ids
    )

    project = projects[
        projects["Project ID"] == project_id
    ].iloc[0]

    st.subheader("🏗 Project Overview")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Project",
        project["Project Name"]
    )

    c2.metric(
        "Area",
        f"{project['Area']} sq.ft"
    )

    c3.metric(
        "Floors",
        project["Floors"]
    )

    c4.metric(
        "Status",
        project["Status"]
    )

    st.divider()

    workers_present = st.number_input(
        "👷 Workers Present Today",
        min_value=0,
        value=int(project["Workers"])
    )

    work_completed = st.text_area(
        "✅ Work Completed Today",
        placeholder="Example: Foundation work completed and brick work reached 40%."
    )

    materials_used = st.text_area(
        "🧱 Materials Used Today",
        placeholder="Example: Cement - 25 bags, Steel - 300kg, Sand - 2 loads"
    )

    issues = st.text_area(
        "⚠ Issues Faced Today",
        placeholder="Example: Heavy rain delayed concrete curing."
    )

    tomorrow_plan = st.text_area(
        "📅 Tomorrow's Plan",
        placeholder="Example: Continue first floor brick work."
    )

    safety_score = st.slider(
        "🦺 Safety Compliance Score",
        0,
        100,
        90
    )

    if st.button(
        "💾 Generate Daily Report",
        use_container_width=True
    ):

        report = {
            "Project ID": project_id,
            "Date": datetime.now().strftime("%Y-%m-%d"),
            "Time": datetime.now().strftime("%H:%M:%S"),
            "Workers Present": workers_present,
            "Work Completed": work_completed,
            "Materials Used": materials_used,
            "Issues": issues,
            "Tomorrow Plan": tomorrow_plan,
            "Safety Score": safety_score
        }

        save_report(report)

        st.success(
            "✅ Daily report generated successfully."
        )

    st.divider()

    st.subheader("📊 Previous Daily Reports")

    reports = load_reports()

    if not reports.empty:

        project_reports = reports[
            reports["Project ID"] == project_id
        ]

        if not project_reports.empty:

            st.dataframe(
                project_reports.sort_values(
                    by=["Date", "Time"],
                    ascending=False
                ),
                use_container_width=True
            )

            col1, col2, col3 = st.columns(3)

            col1.metric(
                "Reports Generated",
                len(project_reports)
            )

            col2.metric(
                "Average Safety",
                f"{round(project_reports['Safety Score'].mean(),1)}%"
            )

            col3.metric(
                "Latest Report",
                project_reports.iloc[-1]["Date"]
            )

        else:
            st.info(
                "No reports available for this project."
            )