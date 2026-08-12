import streamlit as st
import base64
import os

# FIRST STREAMLIT COMMAND
st.set_page_config(
    page_title="Construction Intelligence Hub | Enterprise",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

import prediction
import materials
import painting
import plumbing
import labour
import delay
import advisor
import analytics
import color_ai
import master_planner
import workforce
import attendance
import safety
import worker_db
import daily_report
import ai_design_studio

# ---------- SESSION ----------
if "page" not in st.session_state:
    st.session_state.page = "home"

# ---------- IMAGE ----------
IMAGE_PATH = r"C:\Users\DELL\Downloads\hello vanakkkam.jpg"

def get_base64_image(path):
    if not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        data = f.read()
    ext = path.split(".")[-1].lower()
    mime = "jpeg" if ext in ["jpg", "jpeg"] else ext
    return f"data:image/{mime};base64,{base64.b64encode(data).decode()}"

# Try to get background, though we might use a solid dark theme for ERP look.
img_data = get_base64_image(IMAGE_PATH)

# ---------- CSS (Modern ERP Theme) ----------
css_content = """
<style>
/* Global App Background */
[data-testid="stAppViewContainer"] {
    background: #0e1117;
    color: #fafafa;
}

[data-testid="stSidebar"] {
    background: #1a1c23;
    border-right: 1px solid #2b2b36;
}

/* Fix sidebar text color */
[data-testid="stSidebar"] .stRadio label {
    color: #fafafa !important;
    font-size: 16px;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

.main-title {
    text-align: center;
    background: -webkit-linear-gradient(45deg, #2196F3, #00BCD4);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 64px;
    font-weight: 800;
    margin-top: 60px;
    letter-spacing: -2px;
}

.sub-title {
    text-align: center;
    color: #94a3b8;
    font-size: 24px;
    margin-top: 10px;
    font-weight: 400;
}

.tagline {
    text-align: center;
    color: #64748b;
    font-size: 18px;
    margin-top: 20px;
}

.login-card {
    width: 420px;
    margin: auto;
    margin-top: 100px;
    padding: 40px;
    background: #1e212b;
    border: 1px solid #333;
    border-radius: 12px;
    box-shadow: 0 10px 25px rgba(0,0,0,0.5);
}

.metric-card {
    background: #1e212b;
    padding: 20px;
    border-radius: 10px;
    border: 1px solid #333;
    box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    text-align: left;
}

.stButton>button {
    background: linear-gradient(90deg, #1d4ed8, #2563eb);
    color: white;
    border: none;
    border-radius: 8px;
    padding: 10px 20px;
    font-weight: 600;
}

.stButton>button:hover {
    background: linear-gradient(90deg, #2563eb, #3b82f6);
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.4);
}

</style>
"""

# Apply the custom background image ONLY to the home and login pages for dramatic effect
if st.session_state.page in ["home", "login"] and img_data:
    css_content += f"""
<style>
[data-testid="stAppViewContainer"] {{
    background:
        linear-gradient(rgba(15,23,42,0.85), rgba(15,23,42,0.85)),
        url('{img_data}');
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}}
</style>
"""

st.markdown(css_content, unsafe_allow_html=True)

# =========================================================
# HOME PAGE
# =========================================================

if st.session_state.page == "home":
    st.markdown('<div class="main-title">Construction Intelligence Hub</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Enterprise AI Construction Management Platform</div>', unsafe_allow_html=True)
    st.markdown('<div class="tagline">Cost & Material Estimation • AI Design Studio • Delay Predictor • Advanced Analytics</div>', unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([4,3,4])
    with col2:
        if st.button("Access Dashboard 🚀", use_container_width=True):
            st.session_state.page = "login"
            st.rerun()

# =========================================================
# LOGIN PAGE
# =========================================================

elif st.session_state.page == "login":
    st.markdown("""
    <div class="login-card">
        <h1 style="text-align:center; color:white; font-size: 32px; margin-bottom: 5px;">🔐 ERP Login</h1>
        <p style="text-align:center; color:#94a3b8; font-size: 14px; margin-bottom: 25px;">
            Secure Access to Company Hub
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([3,4,3])
    with col2:
        username = st.text_input("User ID", key="username")
        password = st.text_input("Password", type="password", key="password")

        st.markdown("<br>", unsafe_allow_html=True)
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("⬅ Back", use_container_width=True):
                st.session_state.page = "home"
                st.rerun()
        with col_btn2:
            if st.button("Sign In", use_container_width=True):
                if username and password:
                    st.success("Authentication Successful")
                    st.session_state.page = "dashboard"
                    st.rerun()
                else:
                    st.error("Please enter credentials")

# =========================================================
# DASHBOARD PAGE
# =========================================================

elif st.session_state.page == "dashboard":
    
    st.sidebar.markdown("<h2 style='text-align: center; color: white;'>CIH Platform</h2>", unsafe_allow_html=True)
    st.sidebar.markdown("<hr style='border: 1px solid #333;'>", unsafe_allow_html=True)
    
    menu = st.sidebar.radio(
        "Navigation Menu",
        [
            "1. Smart Construction Planner",
            "2. AI Architectural Design Studio",
            "3. Smart Workforce Allocator",
            "4. Attendance Management",
            "5. AI Delay Predictor",
            "6. AI Site Safety Monitor",
            "7. AI Construction Advisor",
            "8. AI Exterior Color Advisor",
            "9. Analytics Dashboard",
            "Logout"
        ]
    )
    
    st.sidebar.markdown("<hr style='border: 1px solid #333;'>", unsafe_allow_html=True)

    if menu == "1. Smart Construction Planner":
        master_planner.show()
    
    elif menu == "2. AI Architectural Design Studio":
        ai_design_studio.show()

    elif menu == "3. Smart Workforce Allocator":
        workforce.show()

    elif menu == "4. Attendance Management":
        attendance.show()
        
    elif menu == "5. AI Delay Predictor":
        delay.show()

    elif menu == "6. AI Site Safety Monitor":
        safety.show()

    elif menu == "7. AI Construction Advisor":
        advisor.show()

    elif menu == "8. AI Exterior Color Advisor":
        color_ai.show()

    elif menu == "9. Analytics Dashboard":
        analytics.show()

    elif menu == "Logout":
        st.session_state.page = "home"
        st.rerun()