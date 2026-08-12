import streamlit as st
import random
import pandas as pd
from database import save_project

def show():

    st.title("🏗 Smart Construction Planner")
    st.write(
        "Enter project details once and generate complete construction estimates."
    )

    st.subheader("📋 Project Details")

    # Load defaults from session if available
    current = st.session_state.get("shared_project", {})
    
    col1, col2, col3 = st.columns(3)

    with col1:
        project_name = st.text_input("Project Name", current.get("Project Name", "Enterprise Project Alpha"))
        construction_type = st.selectbox("Construction Type", ["House", "Apartment", "Office", "Hospital", "School"], index=["House", "Apartment", "Office", "Hospital", "School"].index(current.get("Type", "House")))
        area = st.number_input("Land Area (sq.ft)", min_value=500, value=current.get("Area", 1200), step=100)
        floors = st.number_input("Floors", min_value=1, value=current.get("Floors", 2))

    with col2:
        quality = st.selectbox("Material Quality", ["Basic", "Standard", "Premium"], index=["Basic", "Standard", "Premium"].index(current.get("Material", "Standard")))
        bedrooms = st.number_input("Bedrooms", min_value=1, value=current.get("Bedrooms", 3))
        bathrooms = st.number_input("Bathrooms", min_value=1, value=current.get("Bathrooms", 2))
        kitchens = st.number_input("Kitchens", min_value=1, value=current.get("Kitchens", 1))

    with col3:
        parking = st.selectbox("Parking Requirement", ["None", "1 Car", "2 Cars", "Covered Garage", "Underground"], index=["None", "1 Car", "2 Cars", "Covered Garage", "Underground"].index(current.get("Parking", "1 Car")))
        garden = st.selectbox("Garden Requirement", ["None", "Small Front Garden", "Backyard", "Rooftop Garden"], index=["None", "Small Front Garden", "Backyard", "Rooftop Garden"].index(current.get("Garden", "Small Front Garden")))
        paint_quality = st.selectbox("Paint Quality", ["Basic", "Standard", "Premium"], index=["Basic", "Standard", "Premium"].index(current.get("Paint", "Standard")))

    if st.button("🚀 Generate Complete Construction Plan", use_container_width=True):

        rates = {"Basic": 1800, "Standard": 2500, "Premium": 3500}
        total_cost = area * floors * rates[quality]
        workers = max(10, int(area / 150))
        duration = floors * 4 # months

        # Materials
        cement = int(area * floors * 0.4)
        bricks = int(area * floors * 8)
        steel = int(area * floors * 4)
        sand = round(area * floors * 0.05, 2)
        material_cost = int(total_cost * 0.45)

        # Painting
        wall_area = area * floors * 3
        paint_required = round(wall_area / 120, 2)
        painters = max(2, int(area / 800))
        paint_rates = {"Basic": 300, "Standard": 500, "Premium": 800}
        paint_cost = int(paint_required * paint_rates[paint_quality])
        painting_days = max(2, int(area / 1000))

        # Plumbing
        pvc = bathrooms * 40 + kitchens * 20
        water_pipes = bathrooms * 30 + kitchens * 15
        plumbers = max(2, bathrooms)
        plumbing_cost = (pvc * 150 + water_pipes * 200)

        # Labour
        civil_workers = workers
        electricians = max(2, int(area / 1000))
        supervisors = max(1, int(workers / 15))
        total_workers = (civil_workers + electricians + plumbers + painters + supervisors)

        # Delay Risk Assessment calculation
        delay_risk_score = 0
        if floors > 5: delay_risk_score += 20
        if quality == "Basic": delay_risk_score += 10
        if area > 5000: delay_risk_score += 15
        
        delay_status = "Low Risk"
        if delay_risk_score > 30: delay_status = "High Risk"
        elif delay_risk_score > 15: delay_status = "Medium Risk"

        # Interconnected Project Data
        project = {
            "Project ID": f"P{random.randint(1000,9999)}",
            "Project Name": project_name,
            "Type": construction_type,
            "Area": area,
            "Floors": floors,
            "Material": quality,
            "Bedrooms": bedrooms,
            "Bathrooms": bathrooms,
            "Kitchens": kitchens,
            "Parking": parking,
            "Garden": garden,
            "Paint": paint_quality,
            "Estimated Cost": total_cost,
            "Workers": total_workers,
            "Duration": duration,
            "Status": "Pending Approval",
            "Delay Risk": delay_status
        }
        
        st.session_state["shared_project"] = project
        st.session_state["pending_project"] = project

        st.success("✅ Project Analysis Completed and Shared across all interconnected modules!")
        st.info(f"Generated Project ID : {project['Project ID']}")

        # ================= METRICS =================
        st.header("📊 Master Project Estimates")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Estimated Cost", f"₹ {total_cost:,.0f}")
        c2.metric("Workers Required", total_workers)
        c3.metric("Duration", f"{duration} Months")
        c4.metric("Delay Risk", delay_status)
        st.divider()

        # Details in Expanders for neat UI
        with st.expander("🧱 Material Estimation", expanded=True):
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Cement Bags", cement)
            col2.metric("Bricks", bricks)
            col3.metric("Steel (kg)", steel)
            col4.metric("Sand (tons)", sand)
            st.metric("Total Material Cost", f"₹ {material_cost:,.0f}")

        with st.expander("🎨 Painting Estimation", expanded=True):
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Paint Required", f"{paint_required} L")
            col2.metric("Painters", painters)
            col3.metric("Painting Days", painting_days)
            col4.metric("Painting Total Cost", f"₹ {paint_cost:,.0f}")

        with st.expander("🚰 Plumbing Estimation", expanded=True):
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("PVC Pipes", pvc)
            col2.metric("Water Pipes", water_pipes)
            col3.metric("Plumbers", plumbers)
            col4.metric("Plumbing Total Cost", f"₹ {plumbing_cost:,.0f}")

        with st.expander("👷 Workforce Requirements", expanded=True):
            col1, col2, col3, col4, col5 = st.columns(5)
            col1.metric("Civil Workers", civil_workers)
            col2.metric("Electricians", electricians)
            col3.metric("Plumbers", plumbers)
            col4.metric("Painters", painters)
            col5.metric("Supervisors", supervisors)
            
        st.subheader("🤖 AI Construction Recommendations")
        if st.button("Generate AI Construction Insights", use_container_width=True):
            with st.spinner("AI is generating custom construction recommendations..."):
                import requests
                prompt = f"""
                You are a senior construction consultant.
                Project Name: {project_name}
                Type: {construction_type}
                Area: {area} sq.ft, Floors: {floors}, Quality: {quality}
                Estimated Coast: INR {total_cost}, Duration: {duration} months
                Provide 3 key actionable recommendations for optimizing cost and materials for this specific build.
                """
                try:
                    res = requests.post(
                        "http://localhost:11434/api/generate",
                        json={"model": "qwen2.5:0.5b", "prompt": prompt, "stream": False}
                    )
                    ai_insight = res.json().get("response", "No AI response.")
                    st.info(ai_insight)
                except Exception as e:
                    st.error(f"Error querying AI model: {e}")

        # Generate Downloadable Report
        report_text = f"""
        CONSTRUCTION ESTIMATION REPORT
        ------------------------------
        Project Name: {project_name}
        Construction Type: {construction_type}
        Total Cost: INR {total_cost}
        Project Duration: {duration} months
        Risk Assessment: {delay_status}
        
        Materials:
        - Cement: {cement} bags
        - Bricks: {bricks}
        - Steel: {steel} kg
        - Sand: {sand} tons
        
        Workforce: {total_workers} personnel
        - Civil: {civil_workers}
        - Electricians: {electricians}
        - Plumbers: {plumbers}
        - Painters: {painters}
        - Supervisors: {supervisors}
        """

        st.download_button(
            "📄 Download Construction Estimation Report",
            data=report_text,
            file_name=f"{project_name}_Construction_Estimation.txt",
            mime="text/plain",
            use_container_width=True
        )

    # Approval Section
    if "pending_project" in st.session_state:
        st.divider()
        st.header("📋 Project Approval")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Approve Project", use_container_width=True):
                approved_project = st.session_state["pending_project"]
                approved_project["Status"] = "Ongoing"
                save_project(approved_project)
                st.success(f"{approved_project['Project ID']} added successfully to Analytics!")
                del st.session_state["pending_project"]
                st.rerun()

        with col2:
            if st.button("❌ Reject Project", use_container_width=True):
                st.warning("Project rejected successfully.")
                del st.session_state["pending_project"]
                st.rerun()