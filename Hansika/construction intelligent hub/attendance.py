import streamlit as st
import requests
import matplotlib.pyplot as plt
from database import load_projects
from allocation_db import load_allocations
from attendance_db import save_attendance, load_attendance
from datetime import datetime


def ask_ai(question, attendance_data):

    prompt = f"""
You are an AI Attendance Analyst for a Construction Company.

Attendance Data:
{attendance_data}

User Question:
{question}

Provide:
1. Answer to the question.
2. Attendance insights.
3. Recommendation if required.
"""

    try:

        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "qwen2.5:0.5b",
                "prompt": prompt,
                "stream": False
            }
        )

        return response.json()["response"]

    except Exception as e:
        return f"Unable to connect to Qwen AI: {e}"


def show():

    st.title("📅 Attendance Management Dashboard")

    # ----------------------------
    # Load Projects
    # ----------------------------

    df = load_projects()

    if df.empty:
        st.warning("No projects available.")
        return

    df = df[
        ~df["Project ID"].astype(str).str.startswith("PNT")
    ]

    project_ids = df["Project ID"].tolist()

    project_id = st.selectbox(
        "🏗 Select Project ID",
        project_ids
    )

    attendance_df = load_attendance()

    if attendance_df.empty:
        project_history = attendance_df
    else:
        project_history = attendance_df[
            attendance_df["Project ID"] == project_id
        ]

    # ----------------------------
    # Analytics Dashboard
    # ----------------------------

    st.subheader("📊 Project Attendance Analytics")

    total_records = len(project_history)

    present_count = len(
        project_history[
            project_history["Status"] == "Present"
        ]
    ) if not project_history.empty else 0

    absent_count = len(
        project_history[
            project_history["Status"] == "Absent"
        ]
    ) if not project_history.empty else 0

    attendance_percentage = (
        round(
            present_count / total_records * 100,
            2
        )
        if total_records > 0
        else 0
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Records",
        total_records
    )

    c2.metric(
        "Present",
        present_count
    )

    c3.metric(
        "Absent",
        absent_count
    )

    c4.metric(
        "Attendance %",
        f"{attendance_percentage}%"
    )

    # ----------------------------
    # Attendance History
    # ----------------------------

    st.subheader("🕒 Attendance History")

    if not project_history.empty:

        st.dataframe(
            project_history.sort_values(
                by=["Date", "Time"],
                ascending=False
            ),
            use_container_width=True
        )

    else:
        st.info(
            "No attendance records available for this project."
        )

    # ----------------------------
    # Load Allocated Workers
    # ----------------------------

    allocations = load_allocations()

    workers = allocations.get(
        project_id,
        []
    )

    if len(workers) == 0:
        st.warning(
            "No workers allocated for this project yet."
        )
        return

    st.divider()

    # ----------------------------
    # Mark Attendance
    # ----------------------------

    st.subheader("✅ Mark Attendance")

    worker_name = st.selectbox(
        "Select Worker",
        workers
    )

    status = st.selectbox(
        "Attendance Status",
        [
            "Present",
            "Absent"
        ]
    )

    if st.button(
        "Mark Attendance",
        use_container_width=True
    ):

        attendance_record = {
            "Project ID": project_id,
            "Worker Name": worker_name,
            "Date": datetime.now().strftime("%Y-%m-%d"),
            "Time": datetime.now().strftime("%H:%M:%S"),
            "Status": status
        }

        save_attendance(
            attendance_record
        )

        st.success(
            f"{worker_name} marked as {status} successfully."
        )

        st.rerun()

    st.divider()

    # ====================================
    # Qwen AI Attendance Assistant
    # ====================================

    st.subheader(
        "🤖 Qwen Attendance Intelligence Assistant"
    )

    recommended_queries = [
        "How many workers were absent this month?",
        "How many workers were present this month?",
        "Which worker has the highest attendance?",
        "Which worker has the highest absenteeism?",
        "What is the attendance percentage for this project?",
        "Show attendance trend for this project.",
        "Which date had the highest absenteeism?",
        "Give attendance summary for this month.",
        "Is additional workforce required based on attendance?",
        "Provide workforce recommendations based on attendance patterns."
    ]

    selected_query = st.selectbox(
        "📌 Recommended AI Queries",
        ["Select a Query"] + recommended_queries
    )

    manual_question = st.text_input(
        "💬 Ask Attendance AI",
        placeholder="Example: How many workers were absent this month?"
    )

    question = None

    if manual_question.strip() != "":
        question = manual_question

    elif selected_query != "Select a Query":
        question = selected_query

    if st.button(
        "🤖 Analyze Attendance",
        use_container_width=True
    ):

        if attendance_df.empty:

            st.warning(
                "No attendance records available."
            )

        elif question is None:

            st.warning(
                "Please select a query or type your own question."
            )

        else:

            with st.spinner(
                "Qwen AI is analyzing attendance..."
            ):

                summary = attendance_df.to_string()

                answer = ask_ai(
                    question,
                    summary
                )

            st.success(
                "AI Analysis Completed"
            )

            st.markdown(
                "### 🤖 AI Response"
            )

            st.write(
                answer
            )

            # ------------------------
            # Attendance Chart
            # ------------------------

            if total_records > 0:

                st.markdown(
                    "### 📊 Attendance Visualization"
                )

                fig, ax = plt.subplots(
                    figsize=(4, 4)
                )

                ax.pie(
                    [present_count, absent_count],
                    labels=[
                        "Present",
                        "Absent"
                    ],
                    autopct="%1.1f%%",
                    startangle=90
                )

                ax.set_title(
                    "Attendance Summary"
                )

                st.pyplot(
                    fig,
                    use_container_width=False
                )

    st.divider()

    # ----------------------------
    # Complete Attendance Report
    # ----------------------------

    st.subheader(
        "📋 Complete Attendance Report"
    )

    if not attendance_df.empty:

        st.dataframe(
            attendance_df.sort_values(
                by=["Date", "Time"],
                ascending=False
            ),
            use_container_width=True
        )

    else:

        st.info(
            "No attendance records available."
        )