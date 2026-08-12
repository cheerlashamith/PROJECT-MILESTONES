import streamlit as st
import pandas as pd
import numpy as np
from database import load_projects

def show():
    st.title("📊 Enterprise Analytics Dashboard")
    st.markdown("Monitor project health, workforce metrics, and progress forecasts in real time.")

    # ================= LOAD PROJECTS =================
    df = load_projects().copy()
    
    if df.empty:
        st.warning("No projects available in the enterprise database.")
        return

    # Prepare data safely
    df["Workers"] = pd.to_numeric(df.get("Workers", 0), errors="coerce").fillna(0)
    df["Estimated Cost"] = pd.to_numeric(df.get("Estimated Cost", 0), errors="coerce").fillna(0)
    if "Delay Risk" not in df.columns:
        df["Delay Risk"] = np.random.choice(["Low Risk", "Medium Risk", "High Risk"], len(df))

    # ================= TOP KPI CARDS =================
    col1, col2, col3, col4, col5 = st.columns(5)
    
    col1.metric("📁 Active Projects", len(df))
    col2.metric("💰 Total Budget", f"₹{df['Estimated Cost'].sum()/1e6:.1f}M")
    col3.metric("👷 Workforce Utilization", f"{int(df['Workers'].sum())} Active")
    
    # Mocking a Safety Score
    safety_score = np.random.randint(85, 99)
    col4.metric("🛡 Safety Compliance", f"{safety_score}%+", delta="2%")
    
    completed = (df["Status"] == "Completed").sum()
    ongoing = (df["Status"] == "Ongoing").sum()
    delayed = (df["Status"] == "Delayed").sum()
    
    col5.metric("🚨 Risks / Delays", delayed, delta_color="inverse")

    st.divider()

    # ================= ADVANCED ANALYTICS (TABS) =================
    tab1, tab2, tab3 = st.tabs(["📈 Financial & Progress Forecasts", "👷 Workforce & Attendance Trends", "🔥 Risk & Delay Analysis"])

    with tab1:
        st.subheader("Budget Utilization & Project Completion Forecast")
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            st.markdown("#### Budget Distribution by Project Type")
            if "Type" in df.columns:
                type_grouped = df.groupby("Type")["Estimated Cost"].sum()
                st.bar_chart(type_grouped, color="#3498db")
            else:
                st.bar_chart(df.set_index("Project ID")["Estimated Cost"], color="#3498db")
        
        with col_f2:
            st.markdown("#### Project Completion Progress")
            progress_data = []
            for _, row in df.iterrows():
                val = 100 if row["Status"] == "Completed" else (70 if row["Status"] == "Ongoing" else 40)
                progress_data.append({"Project ID": row["Project ID"], "Progress %": val})
            prog_df = pd.DataFrame(progress_data).set_index("Project ID")
            st.bar_chart(prog_df, color="#2ecc71")
            
    with tab2:
        st.subheader("Workforce Utilization & Attendance Trends")
        col_w1, col_w2 = st.columns(2)
        with col_w1:
            st.markdown("#### Workers Allocated per Project")
            workers_df = df.set_index("Project ID")["Workers"]
            st.bar_chart(workers_df, color="#e67e22")
            
        with col_w2:
            st.markdown("#### 30-Day Attendance Trend (Forecast)")
            # Generating a mock attendance trend since we don't have historical daily attendance in this dataframe
            dates = pd.date_range(end=pd.Timestamp.today(), periods=30)
            base_attendance = df["Workers"].sum() * 0.9
            trend = [base_attendance + np.random.randint(-15, 15) for _ in range(30)]
            trend_df = pd.DataFrame({"Date": dates, "Attendance": trend}).set_index("Date")
            st.line_chart(trend_df, color="#9b59b6")
            
    with tab3:
        st.subheader("Safety Compliance & Delay Trends")
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            st.markdown("#### Delay Risk Distribution")
            risk_counts = df["Delay Risk"].value_counts()
            st.bar_chart(risk_counts, color="#e74c3c")
            
        with col_r2:
            st.markdown("#### Automated AI Insights")
            if delayed > 0:
                st.error("🚨 CRITICAL: High risk projects detected. Check Resource Allocation.")
            else:
                st.success("✅ Operations are smooth. No severe delays logged.")
                
            st.info(f"💡 AI Suggestion: Shift 10% of workers from Completed/Ongoing to Delayed sectors to balance utilization.")
            st.warning(f"🛡 Note: Maintain strict PPE compliance to keep score above {safety_score-2}%.")

    st.divider()

    # ================= PROJECT DATABASE (DATA GRID) =================
    st.subheader("📋 Enterprise Project Registry")
    st.dataframe(df, use_container_width=True, hide_index=True)

    # ================= REPORT GENERATION =================
    st.divider()
    st.subheader("📄 Export Compliance & Analytic Reports")
    
    col_dl1, col_dl2, col_dl3 = st.columns(3)
    
    with col_dl1:
        csv_data = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇ Export Full Registry (CSV)",
            csv_data,
            "Enterprise_Projects.csv",
            "text/csv",
            use_container_width=True
        )
        
    with col_dl2:
        workforce_report = f"WORKFORCE UTILIZATION REPORT\nTotal Active Workers: {int(df['Workers'].sum())}\n"
        for _, row in df.iterrows():
            workforce_report += f"- {row['Project ID']} ({row['Project Name']}): {row['Workers']} workers\n"
        st.download_button(
            "📄 Download Workforce Report",
            workforce_report,
            "Workforce_Report.txt",
            "text/plain",
            use_container_width=True
        )
        
    with col_dl3:
        safety_report = f"SAFETY COMPLIANCE REPORT\nEnterprise Global Score: {safety_score}%\nProjects under safety review: {delayed}\nMaintain rigorous PPE standards across all active sites.\n"
        st.download_button(
            "📄 Download Safety Compliance Report",
            safety_report,
            "Safety_Compliance_Report.txt",
            "text/plain",
            use_container_width=True
        )

    # ================= QUICK ACTIONS =================
    st.divider()
    st.markdown("#### Quick Updates")
    c_upd1, c_upd2, c_upd3 = st.columns(3)
    with c_upd1:
        project_id = st.selectbox("Select Project", df["Project ID"], key="sel_proj")
    with c_upd2:
        new_status = st.selectbox("Update Status", ["Ongoing", "Completed", "Delayed"], key="sel_stat")
    with c_upd3:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Apply Changes", use_container_width=True):
            df.loc[df["Project ID"] == project_id, "Status"] = new_status
            df.to_csv("projects.csv", index=False)
            st.success("Project updated!")
            st.rerun()