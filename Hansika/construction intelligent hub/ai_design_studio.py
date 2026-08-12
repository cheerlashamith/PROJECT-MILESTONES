import streamlit as st
import requests
import urllib.parse
from PIL import Image
from io import BytesIO
import random

# =====================================
# AI Backend Calls
# =====================================

def ask_qwen(prompt):
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "qwen2.5:0.5b",
                "prompt": prompt,
                "stream": False
            }
        )
        return response.json().get("response", "No response from model.")
    except Exception as e:
        return f"Error connecting to Ollama: {str(e)}"

@st.cache_data(show_spinner=False)
def generate_architectural_image(prompt, seed=None):
    """
    Generate an image using Pollinations.ai (Free, no API key required).
    """
    try:
        encoded_prompt = urllib.parse.quote(prompt)
        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=768&nologo=true"
        if seed is not None:
            url += f"&seed={seed}"
            
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            image = Image.open(BytesIO(response.content))
            return image, response.content
        else:
            return None, None
    except Exception as e:
        st.error(f"Image generation failed: {e}")
        return None, None

def image_to_pdf_bytes(img):
    """Converts a PIL Image to PDF bytes for downloading."""
    pdf_bytes = BytesIO()
    # Convert RGBA to RGB if necessary before saving as PDF
    if img.mode == 'RGBA':
        img = img.convert('RGB')
    img.save(pdf_bytes, format='PDF')
    return pdf_bytes.getvalue()

@st.cache_data(show_spinner=False)
def generate_design_report(reqs_str):
    prompt = f"""You are an expert Architect and Construction Planner.
Based on the following building requirements:
{reqs_str}

Please provide a highly professional architectural design report. Ensure your response is strictly formatted with the following markdown sections:

### 🏢 Architecture Summary
(Provide a brief overview of the design concept and style)

### 🧱 Recommended Materials
(List key materials for construction and finishing)

### 💰 Estimated Construction Cost
(Provide a logical cost estimate range based on standard rates)

### ⏱ Estimated Construction Duration
(Provide a logical timeline)

### 🏗 Structural Suggestions
(Key structural advice, e.g., foundation type, beam spacing)

### 📐 Space Utilization Tips
(How to maximize the given area)

### ☀️ Natural Lighting & Ventilation Suggestions
(Windows, orientation, airflow)

### 🌿 Green Building Recommendations
(Sustainability, energy efficiency)

### 🔮 Future Expansion Suggestions
(Provisions for adding floors or rooms later)

Keep it concise, realistic, and highly professional. Do not add conversational filler.
"""
    return ask_qwen(prompt)

def build_image_prompt(inputs, style_override=None):
    style = style_override if style_override else inputs['arch_style']
    
    prompt = (
        f"A photorealistic 3D architectural visualization of a {style.lower()} "
        f"{inputs['project_type'].lower()} building on a {inputs['plot_size']} sq.ft plot. "
        f"It has {inputs['floors']} floors, {inputs['bedrooms']} bedrooms. "
    )
    
    features = []
    if inputs['parking'] != "None": features.append(f"{inputs['parking'].lower()} parking")
    if inputs['garden'] != "None": features.append(f"{inputs['garden'].lower()}")
    if inputs['swimming_pool']: features.append("a swimming pool")
    if inputs['balcony']: features.append("glass balconies")
    if inputs['terrace']: features.append("an open terrace")
    
    if features:
        prompt += "Features include " + ", ".join(features) + ". "
        
    prompt += (
        f"The roof type is {inputs['roof_type'].lower()}. "
        f"Exterior color theme is {inputs['color_theme'].lower()}. "
        "Professional architectural rendering, ultra HD, 8k resolution, highly detailed, "
        "realistic lighting, ray tracing, sharp focus, beautiful landscaping, cinematic angle, front elevation view."
    )
    return prompt

def build_floorplan_prompt(inputs):
    features = []
    if inputs['balcony']: features.append("Balcony")
    if inputs['parking']: features.append("cars parked in driveway")
    if inputs['garden']: features.append("green trees and plants in garden")
    if inputs['staircase']: features.append("Staircase")
    
    features_str = ", ".join(features) if features else "Standard layout"
    
    prompt = (
        f"A highly detailed, professional 2D architectural CAD floor plan of a {inputs['building_type']}. Top-down orthographic view. "
        f"White background with colored CAD lines (blue, orange, black). "
        f"Includes: {inputs['bedrooms']} Bedrooms with beds, {inputs['bathrooms']} Bathrooms with fixtures, {inputs['kitchen']} Kitchen, "
        f"{inputs['living_rooms']} Living Rooms with sofas, {inputs['dining']} Dining Room with table. "
        f"Exterior features: {features_str}. "
        "Must include dimension lines, exterior walls, interior walls, text room names, door swings, window symbols, realistic top-down furniture layout, "
        "textured flooring, green plants outside, highly detailed vector CAD drafting style, architectural schematic, perfectly scaled."
    )
    return prompt


# =====================================
# UI Functions
# =====================================

def show():
    # CSS for modern cards
    st.markdown("""
    <style>
    .report-card {
        background-color: #1e212b;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #333;
        margin-bottom: 20px;
    }
    .img-container {
        border-radius: 12px;
        overflow: hidden;
        border: 2px solid #333;
        box-shadow: 0 10px 20px rgba(0,0,0,0.5);
    }
    </style>
    """, unsafe_allow_html=True)

    st.title("🏗 AI Architectural Design Studio")
    st.markdown("Transform your ideas into stunning 3D architectural visualizations and professional 2D floor plans.")

    # Main Tabs for Modes
    mode_tabs = st.tabs(["🏠 3D Visualizer", "📐 2D Floor Plan Generator"])

    # =====================================
    # MODE 1: 3D Visualizer
    # =====================================
    with mode_tabs[0]:
        with st.form("design_form_3d"):
            st.subheader("📋 3D Building Requirements")
            
            current = st.session_state.get("shared_project", {})
            
            col1, col2, col3 = st.columns(3)
            with col1:
                project_opts = ["House", "Villa", "Apartment", "Commercial", "Office", "Hospital", "School"]
                project_type = st.selectbox("Project Type", project_opts, index=0)
                plot_size = st.number_input("Plot Size (sq.ft)", min_value=500, value=current.get("Area", 2400), step=100)
                floors = st.number_input("Number of Floors", min_value=1, value=current.get("Floors", 2), step=1)
                arch_style = st.selectbox("Architectural Style", ["Modern", "Contemporary", "Luxury", "Traditional", "Minimalist", "Industrial", "Colonial", "Eco Friendly"])
                
            with col2:
                bedrooms = st.number_input("Bedrooms", min_value=1, value=current.get("Bedrooms", 4), step=1)
                bathrooms = st.number_input("Bathrooms", min_value=1, value=current.get("Bathrooms", 3), step=1)
                kitchen = st.selectbox("Kitchen Type", ["Open Kitchen", "Closed Kitchen", "Island Kitchen", "Galley"])
                living = st.number_input("Living Rooms", min_value=1, value=1, step=1)
                color_theme = st.text_input("Exterior Color Theme", value="White and Dark Grey")
                
            with col3:
                st.markdown("<br>", unsafe_allow_html=True)
                parking_opts = ["None", "1 Car", "2 Cars", "Covered Garage", "Underground"]
                parking = st.selectbox("Parking", parking_opts, index=2)
                
                garden_opts = ["None", "Small Front Garden", "Backyard", "Rooftop Garden", "Landscaped Garden"]
                garden = st.selectbox("Garden", garden_opts, index=4)
                
                roof_opts = ["Flat", "Pitched", "Gable", "Hip", "Terrace"]
                roof_type = st.selectbox("Roof Type", roof_opts, index=0)
                
                # Checkboxes
                st.markdown("**Additional Features**")
                balcony = st.checkbox("Balcony", value=True)
                swimming_pool = st.checkbox("Swimming Pool", value=False)
                terrace = st.checkbox("Open Terrace", value=True)

            submit_btn_3d = st.form_submit_button("✨ Generate 3D Design", use_container_width=True)

        if submit_btn_3d:
            inputs_3d = {
                "project_type": project_type,
                "plot_size": plot_size,
                "floors": floors,
                "bedrooms": bedrooms,
                "bathrooms": bathrooms,
                "kitchen": kitchen,
                "living": living,
                "parking": parking,
                "garden": garden,
                "roof_type": roof_type,
                "balcony": balcony,
                "swimming_pool": swimming_pool,
                "terrace": terrace,
                "arch_style": arch_style,
                "color_theme": color_theme
            }
            
            st.session_state.design_inputs_3d = inputs_3d

        # Display 3D results if available
        if "design_inputs_3d" in st.session_state:
            inputs_3d = st.session_state.design_inputs_3d
            
            st.markdown("---")
            st.subheader("🎨 Generated Design Concepts")
            
            styles = [inputs_3d['arch_style'], "Luxury", "Minimalist", "Traditional", "Contemporary"]
            styles = list(dict.fromkeys(styles))
            
            style_tabs = st.tabs([f"✨ {s}" for s in styles])
            
            for i, tab in enumerate(style_tabs):
                current_style = styles[i]
                with tab:
                    image_prompt = build_image_prompt(inputs_3d, style_override=current_style)
                    reqs_str = f"Project: {inputs_3d['project_type']}\nArea: {inputs_3d['plot_size']} sq.ft\nFloors: {inputs_3d['floors']}\nStyle: {current_style}\nRooms: {inputs_3d['bedrooms']} Bed, {inputs_3d['bathrooms']} Bath\nFeatures: {inputs_3d['parking']} parking, {inputs_3d['garden']} garden, Roof: {inputs_3d['roof_type']}"
                    
                    col_img, col_report = st.columns([1.2, 1])
                    
                    with col_img:
                        with st.spinner(f"Rendering 3D Visualization ({current_style})..."):
                            image, img_bytes = generate_architectural_image(image_prompt)
                        
                        if image:
                            st.markdown('<div class="img-container">', unsafe_allow_html=True)
                            st.image(image, caption=f"{current_style} {inputs_3d['project_type']} Concept", use_container_width=True)
                            st.markdown('</div>', unsafe_allow_html=True)
                            
                            st.download_button(
                                label=f"⬇ Download Image ({current_style})",
                                data=img_bytes,
                                file_name=f"architectural_concept_{current_style.lower()}.png",
                                mime="image/png",
                                use_container_width=True
                            )
                        else:
                            st.error("Failed to generate image. Please try again.")
                            
                    with col_report:
                        with st.spinner("Generating Professional Design Report..."):
                            report_content = generate_design_report(reqs_str)
                            
                        st.markdown('<div class="report-card">', unsafe_allow_html=True)
                        st.markdown(report_content)
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                        st.download_button(
                            label=f"📄 Download Report ({current_style})",
                            data=report_content,
                            file_name=f"Design_Report_{current_style.lower()}.txt",
                            mime="text/plain",
                            use_container_width=True
                        )

    # =====================================
    # MODE 2: 2D Floor Plan
    # =====================================
    with mode_tabs[1]:
        
        # Handle clear state
        if "fp_clear" in st.session_state and st.session_state.fp_clear:
            if "floorplan_inputs" in st.session_state: del st.session_state.floorplan_inputs
            st.session_state.fp_clear = False
            
        if "floorplan_inputs" not in st.session_state:
            with st.form("floorplan_form"):
                st.subheader("📐 2D Floor Plan Requirements")
                
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    fp_width = st.number_input("Plot Width (ft)", min_value=10, value=40, step=5)
                    fp_length = st.number_input("Plot Length (ft)", min_value=10, value=60, step=5)
                    fp_type = st.selectbox("Building Type", ["House", "Villa", "Apartment", "Commercial Office"])
                    fp_floors = st.number_input("Number of Floors", min_value=1, value=1, step=1, key="fp_floors")
                    fp_style = st.selectbox("Interior Style", ["Modern Minimalist", "Traditional", "Open Concept", "Luxury"])

                with col_b:
                    fp_beds = st.number_input("Bedrooms", min_value=1, value=3, step=1, key="fp_beds")
                    fp_baths = st.number_input("Bathrooms", min_value=1, value=2, step=1, key="fp_baths")
                    fp_kitchen = st.selectbox("Kitchen Layout", ["Open Kitchen", "Closed Kitchen", "Island Kitchen", "Galley"])
                    fp_living = st.number_input("Living Rooms", min_value=1, value=1, step=1, key="fp_living")
                    fp_dining = st.number_input("Dining Rooms", min_value=0, value=1, step=1, key="fp_dining")
                
                with col_c:
                    st.markdown("**Additional Requirements**")
                    fp_balcony = st.checkbox("Include Balcony", value=True)
                    fp_parking = st.checkbox("Include Parking Area", value=True)
                    fp_garden = st.checkbox("Include Garden/Yard", value=True)
                    fp_stairs = st.checkbox("Include Staircase", value=True)
                
                submit_fp = st.form_submit_button("📐 Generate Floor Plan", use_container_width=True)
                
                if submit_fp:
                    st.session_state.floorplan_inputs = {
                        "width": fp_width,
                        "length": fp_length,
                        "building_type": fp_type,
                        "floors": fp_floors,
                        "style": fp_style,
                        "bedrooms": fp_beds,
                        "bathrooms": fp_baths,
                        "kitchen": fp_kitchen,
                        "living_rooms": fp_living,
                        "dining": fp_dining,
                        "balcony": fp_balcony,
                        "parking": fp_parking,
                        "garden": fp_garden,
                        "staircase": fp_stairs
                    }
                    st.session_state.floorplan_seed = random.randint(1, 1000000)
                    st.rerun()
                    
        else:
            # Display Generated Floor Plan Mode
            inputs_fp = st.session_state.floorplan_inputs
            seed_fp = st.session_state.floorplan_seed
            
            st.subheader("📐 AI Generated Blueprint")
            
            # Action Buttons Row
            btn_col1, btn_col2 = st.columns(2)
            with btn_col1:
                if st.button("🔄 Regenerate Plan", use_container_width=True):
                    st.session_state.floorplan_seed = random.randint(1, 1000000)
                    st.rerun()
            with btn_col2:
                if st.button("🆕 Generate Another Layout", use_container_width=True):
                    st.session_state.fp_clear = True
                    st.rerun()
            
            fp_prompt = build_floorplan_prompt(inputs_fp)
            
            with st.spinner("Drafting Professional 2D Floor Plan..."):
                fp_image, fp_bytes = generate_architectural_image(fp_prompt, seed=seed_fp)
                
            if fp_image:
                st.markdown('<div class="img-container" style="background-color: white; padding: 10px;">', unsafe_allow_html=True)
                st.image(fp_image, caption=f"2D CAD Blueprint - {inputs_fp['width']}x{inputs_fp['length']} {inputs_fp['building_type']}", use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                # Download Buttons
                dl_col1, dl_col2 = st.columns(2)
                with dl_col1:
                    st.download_button(
                        label="🖼️ Download PNG",
                        data=fp_bytes,
                        file_name="floor_plan.png",
                        mime="image/png",
                        use_container_width=True
                    )
                with dl_col2:
                    pdf_bytes = image_to_pdf_bytes(fp_image)
                    st.download_button(
                        label="📄 Download PDF",
                        data=pdf_bytes,
                        file_name="floor_plan.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
            else:
                st.error("Failed to generate floor plan. Please try regenerating.")
