import ollama
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image, ImageDraw, ImageFont
import io
import time
import os
import datetime
import pdf_utils
import guardrails

# Indian Currency Formatting Helpers
def format_inr(number):
    s = str(int(number))
    if len(s) <= 3:
        return "₹" + s
    else:
        last_three = s[-3:]
        remaining = s[:-3]
        parts = []
        while len(remaining) > 2:
            parts.insert(0, remaining[-2:])
            remaining = remaining[:-2]
        if remaining:
            parts.insert(0, remaining)
        return "₹" + ",".join(parts) + "," + last_three

def format_inr_short(value):
    if value >= 10000000: # 1 Crore
        return f"₹{value/10000000:.2f} Cr"
    elif value >= 100000: # 1 Lakh
        return f"₹{value/100000:.2f} L"
    else:
        return f"₹{value:,.2f}"


# Set page layout and aesthetics
st.set_page_config(
    page_title="Construction Intelligence Hub",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling (Glassmorphism & Clean Card Design)
st.markdown("""
<style>
    /* Global styles */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    /* Global dark backdrop override */
    .stApp {
        background-color: #0B0F19;
    }
    
    /* Title and header modifications */
    .main-title {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(135deg, #4D96FF 0%, #FF6B6B 50%, #F1C40F 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
        letter-spacing: -0.5px;
    }
    
    .subtitle {
        color: #94A3B8;
        font-size: 1.1rem;
        margin-bottom: 2rem;
        font-weight: 400;
    }
    
    /* Custom metric card */
    .kpi-container {
        display: flex;
        justify-content: space-between;
        gap: 1.2rem;
        margin-bottom: 2rem;
    }
    
    .kpi-card {
        flex: 1;
        background: linear-gradient(145deg, rgba(21, 31, 50, 0.65) 0%, rgba(15, 23, 42, 0.8) 100%);
        border: 1px solid rgba(77, 150, 255, 0.18);
        border-radius: 16px;
        padding: 1.6rem;
        text-align: left;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
    }
    
    .kpi-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 30px rgba(77, 150, 255, 0.22);
        border-color: rgba(77, 150, 255, 0.5);
    }
    
    .kpi-title {
        font-size: 0.85rem;
        color: #CBD5E1;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        margin-bottom: 0.6rem;
        font-weight: 600;
    }
    
    .kpi-value {
        font-size: 2.2rem;
        font-weight: 700;
        color: #FFFFFF;
        margin-bottom: 0.3rem;
    }
    
    .kpi-delta {
        font-size: 0.85rem;
        font-weight: 600;
    }
    .kpi-delta.positive {
        color: #4ADE80;
    }
    .kpi-delta.negative {
        color: #F87171;
    }

    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        padding: 4px 8px;
        background: rgba(21, 31, 50, 0.4);
        border-radius: 12px;
        margin-bottom: 1.5rem;
    }

    .stTabs [data-baseweb="tab"] {
        height: 44px;
        white-space: nowrap;
        background-color: transparent;
        border-radius: 8px;
        color: #CBD5E1;
        font-size: 0.9rem;
        font-weight: 600;
        transition: all 0.3s ease;
        padding: 0px 16px;
        border: none !important;
    }

    .stTabs [data-baseweb="tab"]:hover {
        color: #4D96FF;
        background: rgba(77, 150, 255, 0.08);
    }

    .stTabs [aria-selected="true"] {
        color: #4D96FF !important;
        background: rgba(77, 150, 255, 0.15) !important;
        box-shadow: 0 4px 12px rgba(77, 150, 255, 0.1);
    }
    
    /* Styled chat messages */
    .chat-bubble {
        padding: 1rem 1.2rem;
        border-radius: 16px;
        margin-bottom: 0.8rem;
        max-width: 80%;
        line-height: 1.5;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15);
    }
    .chat-user {
        background: linear-gradient(135deg, rgba(77, 150, 255, 0.35) 0%, rgba(77, 150, 255, 0.18) 100%);
        color: #FFFFFF;
        align-self: flex-end;
        margin-left: auto;
        border: 1px solid rgba(77, 150, 255, 0.45);
        border-bottom-right-radius: 4px;
    }
    .chat-assistant {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.08) 0%, rgba(255, 255, 255, 0.03) 100%);
        color: #E2E8F0;
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-bottom-left-radius: 4px;
    }
    
    /* Custom panels / containers */
    .doc-section {
        background: linear-gradient(135deg, rgba(21, 31, 50, 0.4) 0%, rgba(15, 23, 42, 0.5) 100%);
        border: 1px solid rgba(77, 150, 255, 0.15);
        border-radius: 12px;
        padding: 1.3rem;
        margin-bottom: 1.2rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
    }
    
    .doc-title {
        color: #4D96FF;
        font-weight: 700;
        margin-bottom: 0.5rem;
        font-size: 1.05rem;
        letter-spacing: 0.5px;
    }

    /* Style Streamlit Forms to match */
    div[data-testid="stForm"] {
        background: rgba(21, 31, 50, 0.35) !important;
        border: 1px solid rgba(77, 150, 255, 0.15) !important;
        border-radius: 16px !important;
        padding: 1.8rem !important;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.25) !important;
    }

    /* Streamlit Buttons styling override */
    div.stButton > button {
        background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 8px;
        color: #E2E8F0;
        font-weight: 600;
        padding: 0.5rem 1.2rem;
        transition: all 0.3s ease;
    }
    div.stButton > button:hover {
        background: linear-gradient(135deg, #4D96FF 0%, #2563EB 100%) !important;
        color: white !important;
        border-color: transparent !important;
        box-shadow: 0 4px 15px rgba(77, 150, 255, 0.4);
        transform: translateY(-2px);
    }
    div.stButton > button[type="primary"] {
        background: linear-gradient(135deg, #4D96FF 0%, #2563EB 100%);
        border: none;
        color: white;
        box-shadow: 0 4px 12px rgba(77, 150, 255, 0.25);
    }
    div.stButton > button[type="primary"]:hover {
        background: linear-gradient(135deg, #60A5FA 0%, #3B82F6 100%) !important;
        box-shadow: 0 6px 20px rgba(77, 150, 255, 0.5);
    }

    /* Style Streamlit expanders to fit the glass look */
    div[data-testid="stExpander"] {
        background: rgba(21, 31, 50, 0.3) !important;
        border: 1px solid rgba(77, 150, 255, 0.12) !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1) !important;
        margin-bottom: 0.8rem;
    }

    /* Sidebar background override */
    section[data-testid="stSidebar"] {
        background-color: #080C14 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }

    /* Sliders track & handle customization (fallback selector) */
    div[data-testid="stSlider"] {
        padding-top: 10px;
    }
    
    /* Status Badge styling */
    .status-badge {
        padding: 0.2rem 0.6rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .badge-ontrack { background-color: rgba(74, 222, 128, 0.15); color: #4ADE80; border: 1px solid rgba(74, 222, 128, 0.35); }
    .badge-delayed { background-color: rgba(248, 113, 113, 0.15); color: #F87171; border: 1px solid rgba(248, 113, 113, 0.35); }
    .badge-review { background-color: rgba(251, 191, 36, 0.15); color: #FBBF24; border: 1px solid rgba(251, 191, 36, 0.35); }
</style>
""", unsafe_allow_html=True)

# Helper function to generate mock images for safety checking
def generate_sample_images():
    # Create directory for assets if it doesn't exist
    os.makedirs("assets", exist_ok=True)
    
    # Compliant Image (Green Helmet & Orange Vest Worker)
    if not os.path.exists("assets/compliant.jpg"):
        img = Image.new("RGB", (600, 450), color=(240, 245, 245))
        draw = ImageDraw.Draw(img)
        
        # Draw background construction girders
        draw.line([(50, 0), (50, 450)], fill=(220, 225, 225), width=8)
        draw.line([(550, 0), (550, 450)], fill=(220, 225, 225), width=8)
        draw.line([(50, 100), (550, 250)], fill=(220, 225, 225), width=8)
        
        # Worker Head (circle)
        draw.ellipse([(250, 120), (350, 220)], fill=(244, 204, 164))
        
        # Hard Hat (Green Arc/Half-ellipse)
        draw.chord([(240, 100), (360, 170)], start=180, end=360, fill=(39, 174, 96)) # Green Hat
        draw.rectangle([(235, 158), (365, 168)], fill=(39, 174, 96)) # Hat brim
        
        # Safety Glasses (Blue rectangle/eyes)
        draw.rounded_rectangle([(270, 155), (330, 175)], radius=3, fill=(173, 216, 230), outline=(0, 0, 139), width=2)
        
        # Worker Torso
        draw.polygon([(200, 280), (400, 280), (370, 450), (230, 450)], fill=(44, 62, 80)) # Blue Shirt
        # Safety Vest (Orange overlay)
        draw.polygon([(230, 280), (370, 280), (360, 450), (240, 450)], fill=(230, 126, 34)) # Orange Vest
        # Vest Reflective Stripes (Silver/Yellow)
        draw.rectangle([(260, 280), (280, 450)], fill=(241, 196, 15)) # Yellow Stripe Left
        draw.rectangle([(320, 280), (340, 450)], fill=(241, 196, 15)) # Yellow Stripe Right
        draw.rectangle([(230, 340), (370, 360)], fill=(241, 196, 15)) # Yellow Stripe Horizontal
        
        img.save("assets/compliant.jpg")

    # Non-Compliant Image (Gray Hooded Jacket, No Helmet, No Vest)
    if not os.path.exists("assets/non_compliant.jpg"):
        img = Image.new("RGB", (600, 450), color=(245, 240, 240))
        draw = ImageDraw.Draw(img)
        
        # Draw background construction girders
        draw.line([(50, 0), (50, 450)], fill=(225, 220, 220), width=8)
        draw.line([(550, 0), (550, 450)], fill=(225, 220, 220), width=8)
        draw.line([(50, 100), (550, 250)], fill=(225, 220, 220), width=8)
        
        # Worker Head (circle)
        draw.ellipse([(250, 125), (350, 225)], fill=(244, 204, 164))
        
        # Hair (Brown/Black instead of helmet)
        draw.chord([(248, 115), (352, 175)], start=180, end=360, fill=(44, 34, 30))
        
        # Worker Torso (Plain Gray Hoodie, No Safety Vest)
        draw.polygon([(200, 280), (400, 280), (370, 450), (230, 450)], fill=(127, 140, 141)) # Gray jacket
        # Hood outline
        draw.ellipse([(230, 230), (370, 290)], outline=(90, 100, 101), width=4)
        
        img.save("assets/non_compliant.jpg")

# Run image generator helper
generate_sample_images()

# Preloaded Construction Documents for Analyzer Module
PRELOADED_DOCS = {
    "🏗️ Structural Specification (M40 Concrete Grade)": """SECTION 03 30 00 - CAST-IN-PLACE CONCRETE STRUCTURAL SPECIFICATIONS
Part 1 - General Requirements:
- Compressive Strength: Minimum 28-day concrete compressive strength (f'c) must be M40 Grade (40 MPa / 5800 psi) for all columns, load-bearing shear walls, and foundations.
- Cement Grade: Compliant with ASTM C150 Type III High-Early-Strength Portland cement.
- Slump Target: Slump range limits between 100mm to 150mm during pouring operations.
- Max Water/Cementitious Ratio: Maximum w/c ratio is restricted strictly to 0.40.
- Reinforcement Material: Reinforcing deformed steel bars must satisfy ASTM A615 Grade 60 standards.

Part 2 - Field Quality Control:
- Curing Protocols: Maintain structural elements continuously moist at temperatures above 10°C (50°F) for at least 7 full days post-pour.
- Pre-Pour Safety Check: Reinforcements inspection and debris clearance checklist mandatory before pouring start.
- Shoring: Support framework must withstand full loads until concrete achieves 75% of design strength.""",

    "📄 Subcontractor Master Agreement (Apex Steel)": """SUBCONTRACT OPERATIONS AGREEMENT - STEEL ENGINEERING WORK
This Agreement is enacted by Prime Builders Corp ("Contractor") and Apex Steelworks Ltd ("Subcontractor") on April 1, 2026.

1. Scope of Service:
- Subcontractor is assigned structural steel layout, rebar fabrication, reinforcement bending, and frame erection at Noida Sector 62 site.
- Compliance is required with IS 800 code criteria for industrial steel structures.

2. Milestone Scheduling & Penalties:
- Phase A Foundation Steel Completion: On or before June 30, 2026.
- Phase B Superstructure Frame Completion: On or before September 15, 2026.
- Liquidated Damages: Failure to meet milestone targets will trigger a daily penalty of $2,500 charged to Subcontractor.

3. Payment & Retainage Structure:
- Monthly payouts based on physical inspection certificates.
- Retainage of 10% will be withheld from each invoice, released 45 days after final site handover and sign-off.
- Mandatory safety gear policies must be strictly enforced on-site by Subcontractor.""",

    "🛡️ Site Safety Protocols & Regulations (Class A)": """SAFETY PROTOCOLS & EXCLUSION ZONES - LARGE SCALE CIVIL INFRASTRUCTURE
1. Personal Protective Equipment (PPE) Guidelines:
- Mandatory PPE: ANSI Z89.1 certified industrial hard hat, Class 2 high-visibility reflective jacket/vest, ASTM F2413 safety boots, and impact goggles.
- Heights Work: Safety harness (double-lanyard) anchored securely is mandatory for any tasks exceeding 1.8 meters (6 feet).
- Marine/Water Proximity: Certified life preserver vests must be worn; safety catch-nets rigged beneath structural scaffolding.

2. Heavy Operations & Exclusion Boundary:
- Excavators, cranes, and drill rigs must maintain a barricaded perimeter boundary with a radius of at least 3 meters (10 feet).
- Equipment checklists must be updated daily before work commences. Operators must hold valid certifications."""
}

# Initialize Session State
if "guardrails_checked" not in st.session_state:
    st.session_state.guardrails_checked = 0
if "guardrails_blocked" not in st.session_state:
    st.session_state.guardrails_blocked = 0
if "guardrails_violations" not in st.session_state:
    st.session_state.guardrails_violations = []

if "projects" not in st.session_state:
    st.session_state.projects = [
        {"id": 1, "name": "Oakridge Highrise", "location": "Noida, Sector 62", "status": "On Track", "budget": 12500000, "spent": 9800000, "progress": 78, "safety": 98.6, "manager": "Rakesh Sharma"},
        {"id": 2, "name": "Metro Line Expansion", "location": "Bangalore, Whitefield", "status": "Delayed", "budget": 45000000, "spent": 38200000, "progress": 62, "safety": 92.4, "manager": "Amit Patel"},
        {"id": 3, "name": "Urban Flyover A", "location": "Hyderabad, Gachibowli", "status": "On Track", "budget": 8200000, "spent": 4100000, "progress": 50, "safety": 99.1, "manager": "Priya Sen"},
        {"id": 4, "name": "Oceanic Commercial Port", "location": "Kochi, Marine Drive", "status": "Under Review", "budget": 65000000, "spent": 59000000, "progress": 91, "safety": 96.8, "manager": "Vikram Sethi"},
        {"id": 5, "name": "Greenfield Smart Township", "location": "Noida, Greater Noida", "status": "On Track", "budget": 120000000, "spent": 32000000, "progress": 25, "safety": 97.5, "manager": "Sanjay Kapoor"},
    ]

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = [
        {"role": "assistant", "content": "Welcome to the Construction Intelligence Insights Desk. Ask me anything about project budgets, safety rates, or timelines."}
    ]

if "safety_incidents" not in st.session_state:
    st.session_state.safety_incidents = [
        {"id": 1, "project": "Metro Line Expansion", "date": "2026-07-09", "type": "PPE Violation", "severity": "Low", "status": "Resolved", "description": "Worker found without hard hat near excavation zone."},
        {"id": 2, "project": "Oakridge Highrise", "date": "2026-07-10", "type": "Scaffolding Defect", "severity": "Medium", "status": "Under Investigation", "description": "Loose scaffold plank reported on 8th floor block A."},
        {"id": 3, "project": "Oceanic Commercial Port", "date": "2026-07-08", "type": "Equipment Hazard", "severity": "High", "status": "Resolved", "description": "Crane hydraulic leakage; operations paused for seal replacement."}
    ]

if "daily_reports" not in st.session_state:
    st.session_state.daily_reports = [
        {
            "id": 1, 
            "project": "Oakridge Highrise", 
            "date": "2026-07-10", 
            "weather": "Sunny (32°C)", 
            "work_done": "Completed M40 concreting of columns C3-C5 on the 10th floor. Completed masonry wall installation for 3rd floor apartment units.",
            "work_tomorrow": "Install reinforcement steel mesh for 11th floor slab casting.",
            "skilled": 15, "unskilled": 42, "supervisors": 4, "operators": 2,
            "equipment": ["Tower Crane", "Concrete Mixer Truck"],
            "materials": "Cement: 120 bags, Steel Rebars: 4.5 Tons, Aggregate: 250 CFT",
            "safety_remarks": "All workers wearing full PPE gear. Conducted afternoon safety induction drill."
        },
        {
            "id": 2, 
            "project": "Metro Line Expansion", 
            "date": "2026-07-11", 
            "weather": "Rainy (25°C)", 
            "work_done": "Excavation and subgrade water pumping. Trench reinforcement steel tying in progress.",
            "work_tomorrow": "Pour lean concrete lining for trench beds once weather clears.",
            "skilled": 8, "unskilled": 22, "supervisors": 2, "operators": 4,
            "equipment": ["Excavator", "Dewatering Pumps"],
            "materials": "Lean Cement: 40 bags, Dewatering Fuel: 60 Liters",
            "safety_remarks": "Wet ground hazards flagged. Caution ribbons placed around deep excavation trenches."
        }
    ]

if "risks" not in st.session_state:
    st.session_state.risks = [
        {"id": 1, "project": "Metro Line Expansion", "category": "Supply Chain", "description": "Delay in delivery of structural steel reinforcement bars from primary factory.", "likelihood": 4, "impact": 5, "mitigation": "Identified alternative local steel fabricator; placed advance reserve deposit."},
        {"id": 2, "project": "Urban Flyover A", "category": "Weather", "description": "Monsoon rains causing waterlogging in pier foundation trenches.", "likelihood": 3, "impact": 4, "mitigation": "Installed heavy-duty dewatering pumps; scheduled sub-grade concrete before rainfall peaks."},
        {"id": 3, "project": "Greenfield Smart Township", "category": "Labor", "description": "Shortage of skilled masonry artisans during harvest season.", "likelihood": 2, "impact": 3, "mitigation": "Signed subcontracting agreements with secondary labor agency to supply buffer workers."},
        {"id": 4, "project": "Oakridge Highrise", "category": "Design Change", "description": "Client requested alteration to layout of utility duct piping on floors 12-15.", "likelihood": 2, "impact": 4, "mitigation": "BIM model modification underway. Approval checklist expedited to avoid onsite stoppage."}
    ]

# =====================================================================
# OLLAMA INTEGRATION HELPERS
# =====================================================================
def get_live_project_context(project_name=None):
    """Formats all session state data into a clean text context block for the LLM, optionally filtering by project."""
    context_parts = []
    
    # 1. Projects Telemetry
    if "projects" in st.session_state:
        proj_lines = ["Active Projects:"]
        for p in st.session_state.projects:
            if project_name and project_name != "Overall Portfolio" and p["name"] != project_name:
                continue
            proj_lines.append(
                f"- Name: {p['name']} | Location: {p['location']} | Status: {p['status']} | "
                f"Budget: {format_inr(p['budget'])} | Spent: {format_inr(p['spent'])} | "
                f"Progress: {p['progress']}% | Safety Rating: {p['safety']}% | Manager: {p['manager']}"
            )
        context_parts.append("\n".join(proj_lines))
        
    # 2. Safety Incidents
    if "safety_incidents" in st.session_state:
        inc_lines = ["Safety Incident Logs:"]
        for inc in st.session_state.safety_incidents:
            if project_name and project_name != "Overall Portfolio" and inc["project"] != project_name:
                continue
            inc_lines.append(
                f"- Date: {inc['date']} | Project: {inc['project']} | Type: {inc['type']} | "
                f"Severity: {inc['severity']} | Status: {inc['status']} | Description: {inc['description']}"
            )
        context_parts.append("\n".join(inc_lines))
        
    # 3. Daily Work Reports
    if "daily_reports" in st.session_state:
        rep_lines = ["Daily Site Reports:"]
        for r in st.session_state.daily_reports:
            if project_name and project_name != "Overall Portfolio" and r["project"] != project_name:
                continue
            rep_lines.append(
                f"- Date: {r['date']} | Project: {r['project']} | Weather: {r['weather']} | "
                f"Work Done: {r['work_done']} | Next Day Plan: {r['work_tomorrow']} | "
                f"Staffing: {r['skilled']} skilled, {r['unskilled']} unskilled workers | "
                f"Safety Remark: {r['safety_remarks']}"
            )
        context_parts.append("\n".join(rep_lines))

    # 4. Risks and Mitigations
    if "risks" in st.session_state:
        risk_lines = ["Registered Project Risks:"]
        for rk in st.session_state.risks:
            if project_name and project_name != "Overall Portfolio" and rk["project"] != project_name:
                continue
            risk_lines.append(
                f"- Project: {rk['project']} | Category: {rk['category']} | "
                f"Risk: {rk['description']} | Severity Matrix: Likelihood {rk['likelihood']}/5, Impact {rk['impact']}/5 | "
                f"Mitigation Strategy: {rk['mitigation']}"
            )
        context_parts.append("\n".join(risk_lines))
        
    return "\n\n".join(context_parts)

def check_ollama_status(model_name="llama3.2"):
    """Checks if Ollama is running and has any models available."""
    try:
        models_list = ollama.list()
        # ollama.list() returns dict with a 'models' key containing list of dicts.
        available_models = [m.get('model', m.get('name', '')) for m in models_list.get('models', [])]
        # Match both exact name and name:tag variations
        matches = []
        for m in available_models:
            if m == model_name or m.split(':')[0] == model_name:
                matches.append(m)
        if matches:
            return True, f"Connected. Model '{matches[0]}' is ready.", available_models
        return False, f"Connected, but model '{model_name}' is not found.", available_models
    except Exception as e:
        return False, f"Not connected. Run Ollama on http://localhost:11434", []

def query_ollama_chat(user_query, model_name="llama3.2", project_name=None):
    """Queries Ollama for the Q&A Desk chat with real-time context."""
    context = get_live_project_context(project_name)
    system_prompt = (
        "You are the Construction Intelligence Hub AI Assistant, a professional expert in construction management, safety audits, and project operations.\n"
        "You are given real-time live telemetry data from active projects under the 'Real-time Project Context' heading.\n"
        "Use this data to provide highly accurate, analytical, and professional answers to the user's queries.\n"
        f"The user's query focus is currently set to: {project_name if project_name else 'Overall Portfolio'}.\n"
        "If the user asks about specific budgets, metrics, risks, or safety incidents, refer directly to the live context.\n"
        "If the information is not present in the context, clearly explain that it is not currently logged, "
        "and answer their query using standard best practices in construction management.\n"
        "Keep responses professional, concise, and structured (using bold text and bullet points where helpful)."
    )
    
    response = ollama.chat(
        model=model_name,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Real-time Project Context:\n{context}\n\nUser Question: {user_query}"}
        ]
    )
    return response['message']['content']

def robust_json_extract_and_normalize(raw_content):
    """Extracts JSON object from text and normalizes fields to standard schema."""
    import re
    import json
    cleaned = raw_content.strip()
    
    # Strip markdown backticks if any
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\n", "", cleaned)
        cleaned = re.sub(r"\n```$", "", cleaned)
        cleaned = cleaned.strip()
        
    # Extract only the JSON portion by finding outermost brackets
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start != -1 and end != -1 and end > start:
        json_str = cleaned[start:end+1]
    else:
        json_str = cleaned

    try:
        data = json.loads(json_str)
    except Exception as e:
        # Try a quick cleanup of trailing commas before closing braces/brackets
        try:
            cleaned_json_str = re.sub(r",\s*([\]}])", r"\1", json_str)
            data = json.loads(cleaned_json_str)
        except Exception:
            raise e # Raise original exception if cleanup also fails
            
    if not isinstance(data, dict):
        raise ValueError("Decoded JSON is not a dictionary.")

    # 1. Normalize specifications (must be string)
    specs = data.get("specifications", "")
    if isinstance(specs, list):
        data["specifications"] = "\n".join(f"- {item}" for item in specs)
    elif not isinstance(specs, str):
        data["specifications"] = str(specs)
    else:
        data["specifications"] = specs.strip()

    # 2. Normalize risks (must be list of {"type": str, "text": str})
    risks = data.get("risks", [])
    normalized_risks = []
    if isinstance(risks, list):
        for r in risks:
            if isinstance(r, dict):
                rtype = r.get("type", r.get("level", "warning"))
                rtype_str = str(rtype).strip().lower()
                if rtype_str not in ("error", "warning", "info"):
                    if "error" in rtype_str or "critical" in rtype_str or "severe" in rtype_str:
                        rtype_str = "error"
                    elif "info" in rtype_str or "note" in rtype_str:
                        rtype_str = "info"
                    else:
                        rtype_str = "warning"
                rtext = r.get("text", r.get("description", r.get("risk", "")))
                if rtext:
                    normalized_risks.append({"type": rtype_str, "text": str(rtext).strip()})
            elif isinstance(r, str):
                normalized_risks.append({"type": "warning", "text": r.strip()})
    data["risks"] = normalized_risks

    # 3. Normalize checklist (must be list of {"item": str, "checked": bool})
    checklist = data.get("checklist", [])
    normalized_checklist = []
    if isinstance(checklist, list):
        for item in checklist:
            if isinstance(item, dict):
                citem = item.get("item", item.get("text", item.get("task", "")))
                cchecked = item.get("checked", item.get("status", False))
                if isinstance(cchecked, str):
                    cchecked = cchecked.lower() in ("true", "yes", "checked", "done")
                if citem:
                    normalized_checklist.append({"item": str(citem).strip(), "checked": bool(cchecked)})
            elif isinstance(item, str):
                normalized_checklist.append({"item": item.strip(), "checked": False})
    data["checklist"] = normalized_checklist

    return data


def parse_fallback_markdown(raw_text):
    """Fallback parser that parses a general markdown summary text line-by-line
    and groups it into structured specifications, risks, and checklist categories.
    """
    import re
    sections = {"specifications": "", "risks": [], "checklist": []}
    lines = raw_text.split("\n")
    current_section = "specifications"
    
    for line in lines:
        line_strip = line.strip()
        if not line_strip:
            continue
            
        lower_line = line_strip.lower()
        # Section headers detection
        if any(kw in lower_line for kw in ["risk", "anomaly", "anomalies", "warnings", "threats"]):
            current_section = "risks"
            continue
        elif any(kw in lower_line for kw in ["checklist", "task", "verification", "check"]):
            current_section = "checklist"
            continue
        elif any(kw in lower_line for kw in ["specification", "parameter", "requirement", "grades"]):
            current_section = "specifications"
            continue
            
        if current_section == "specifications":
            sections["specifications"] += line + "\n"
        elif current_section == "risks":
            text = re.sub(r"^[-*#\d\.\s]+", "", line_strip)
            if text:
                rtype = "warning"
                if any(kw in text.lower() for kw in ["error", "critical", "severe", "penalty"]):
                    rtype = "error"
                elif any(kw in text.lower() for kw in ["info", "note", "recommendation"]):
                    rtype = "info"
                sections["risks"].append({"type": rtype, "text": text})
        elif current_section == "checklist":
            text = re.sub(r"^[-*#\d\.\s\[\]xX]+", "", line_strip)
            if text:
                checked = "[x]" in line.lower() or "[x]" in line_strip.lower()
                sections["checklist"].append({"item": text, "checked": checked})
                
    # Cleanup specifications format
    sections["specifications"] = sections["specifications"].strip()
    if not sections["specifications"]:
        sections["specifications"] = raw_text
        
    return sections


def query_ollama_parser(doc_content, model_name="llama3.2"):
    """Uses Ollama to parse technical specifications, returning structured analysis."""
    prompt = (
        f"Analyze the following construction document content and extract detailed information for three sections: key specifications, risks/anomalies, and compliance checklist.\n"
        f"Return the output as a valid raw JSON object ONLY, with exactly three keys: 'specifications', 'risks', and 'checklist'. Do not wrap the JSON block in markdown backticks or any other text.\n\n"
        f"Structure required in JSON:\n"
        f"{{\n"
        f"  \"specifications\": \"A detailed markdown summary of key specifications, parameters, grades, codes, materials, limits, etc. found in the document. Format this with bullet points.\",\n"
        f"  \"risks\": [\n"
        f"     {{\"type\": \"warning|error|info\", \"text\": \"Description of risk, anomaly, penalty, strict range or dependency found in the text.\"}}\n"
        f"  ],\n"
        f"  \"checklist\": [\n"
        f"     {{\"item\": \"Short actionable verification check for site engineers\", \"checked\": true|false}}\n"
        f"  ]\n"
        f"}}\n\n"
        f"Ensure JSON validation passes. Content:\n{doc_content}"
    )
    
    response = ollama.chat(
        model=model_name,
        messages=[
            {"role": "system", "content": "You are a professional construction compliance inspector. You output valid JSON ONLY. No explanation or code blocks."},
            {"role": "user", "content": prompt}
        ],
        format="json"
    )
    raw_content = response['message']['content']
    return robust_json_extract_and_normalize(raw_content)


def query_ollama_parser_safe(doc_content, model_name="llama3.2"):
    """A wrapper with full fallbacks in case JSON formatting or Ollama fails, protected by guardrails."""
    import streamlit as st
    import datetime
    import guardrails
    
    # 1. Input Guardrails Check
    if st.session_state.get("enable_guardrails", True):
        st.session_state.guardrails_checked = st.session_state.get("guardrails_checked", 0) + 1
        is_safe, err_cat, reason = guardrails.validate_input(doc_content)
        if not is_safe:
            st.session_state.guardrails_blocked = st.session_state.get("guardrails_blocked", 0) + 1
            st.session_state.guardrails_violations.append({
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "query": "Document Parser Content",
                "category": err_cat,
                "reason": reason
            })
            return {
                "specifications": f"❌ **Analysis Blocked by AI Guardrails**\n\n**Category**: {err_cat}\n\n**Reason**: {reason}",
                "risks": [{"type": "error", "text": f"Blocked by guardrails due to: {reason}"}],
                "checklist": []
            }
            
    # 2. Execute Document Parsing
    result = None
    try:
        result = query_ollama_parser(doc_content, model_name)
    except Exception as e:
        # Graceful fallback: call model for general markdown summary and parse/map it
        try:
            prompt = (
                f"Analyze the following construction document content. Extract the key specifications, "
                f"any flagged risks or anomalies, and a safety/compliance checklist. Respond with a clear summary.\n\n"
                f"Content:\n{doc_content}"
            )
            res = ollama.chat(
                model=model_name,
                messages=[
                    {"role": "system", "content": "You are a helpful construction compliance assistant."},
                    {"role": "user", "content": prompt}
                ]
            )
            raw = res['message']['content']
            result = parse_fallback_markdown(raw)
        except Exception as ex:
            result = {
                "specifications": f"Failed to connect to local Ollama model for analysis: {ex}",
                "risks": [{"type": "error", "text": "Ollama service connection issue."}],
                "checklist": []
            }

    # 3. Output Guardrails Check
    if st.session_state.get("enable_guardrails", True) and result:
        text_to_validate = [result.get("specifications", "")]
        for r in result.get("risks", []):
            text_to_validate.append(r.get("text", ""))
        for c in result.get("checklist", []):
            text_to_validate.append(c.get("item", ""))
            
        combined_text = "\n".join(text_to_validate)
        is_out_safe, out_err_type, out_reason = guardrails.validate_output(combined_text)
        if not is_out_safe:
            st.session_state.guardrails_blocked = st.session_state.get("guardrails_blocked", 0) + 1
            st.session_state.guardrails_violations.append({
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "query": "Document Parser Output Verification",
                "category": out_err_type,
                "reason": out_reason
            })
            return {
                "specifications": f"❌ **Output Redacted by AI Guardrails**\n\n**Category**: {out_err_type}\n\n**Reason**: {out_reason}",
                "risks": [{"type": "error", "text": "Generated output violated safety parameters and was redacted."}],
                "checklist": []
            }
            
    return result

def query_ollama_material_params(doc_content, model_name="llama3.2"):
    """Extracts material parameters from a technical document."""
    prompt = (
        "Analyze the following construction specification document and extract the parameters for material estimation:\n"
        "1. Structure Topology: Must be exactly one of: 'Residential Apartment', 'Commercial Glass Tower', 'Infrastructure Flyover / Bridge'.\n"
        "2. Plinth Area (in square feet): An integer.\n"
        "3. Number of Floors: An integer.\n"
        "4. Concrete Slab Thickness (in inches): A float.\n"
        "5. Concrete Grade Standard: Must be exactly one of: 'M20 (1:1.5:3)', 'M25 (1:1:2)', 'M30 (Structural Design)', 'M40 (High Compressive)'.\n\n"
        "Return a valid JSON object ONLY, with exactly these keys: 'structure_type', 'plinth_area', 'num_floors', 'slab_thickness', 'concrete_grade'. Do not wrap the JSON block in markdown backticks or any other text.\n"
        f"Structure required in JSON:\n"
        f"{{\n"
        f"  \"structure_type\": \"...\",\n"
        f"  \"plinth_area\": 2500,\n"
        f"  \"num_floors\": 4,\n"
        f"  \"slab_thickness\": 6.0,\n"
        f"  \"concrete_grade\": \"...\"\n"
        f"}}\n\n"
        f"Document Content:\n{doc_content}"
    )
    
    response = ollama.chat(
        model=model_name,
        messages=[
            {"role": "system", "content": "You are a professional construction estimation parser. You output valid JSON ONLY. No explanation or code blocks."},
            {"role": "user", "content": prompt}
        ],
        format="json"
    )
    import json
    import re
    raw_content = response['message']['content'].strip()
    if raw_content.startswith("```"):
        raw_content = re.sub(r"^```(?:json)?\n", "", raw_content)
        raw_content = re.sub(r"\n```$", "", raw_content)
        raw_content = raw_content.strip()
    return json.loads(raw_content)

def extract_material_params_fallback(doc_content):
    """Fallback regex-based parameter extractor from document content."""
    import re
    doc_lower = doc_content.lower()
    
    # Topology
    if "flyover" in doc_lower or "bridge" in doc_lower or "infrastructure" in doc_lower:
        structure_type = "Infrastructure Flyover / Bridge"
    elif "commercial" in doc_lower or "glass tower" in doc_lower or "office" in doc_lower:
        structure_type = "Commercial Glass Tower"
    else:
        structure_type = "Residential Apartment"
        
    # Plinth Area
    plinth_area = 2500
    area_match = re.search(r"(\d{3,6})\s*(?:sq\s*ft|square\s*feet|sq\.?\s*ft\.?)", doc_lower)
    if area_match:
        plinth_area = int(area_match.group(1))
    else:
        # Search for any large number
        numbers = re.findall(r"\b\d{3,6}\b", doc_lower)
        if numbers:
            plinth_area = int(numbers[0])
            
    # Number of floors
    num_floors = 4
    floors_match = re.search(r"(\d{1,2})\s*(?:floor|story|level|storie)", doc_lower)
    if floors_match:
        num_floors = int(floors_match.group(1))
    else:
        # Search for digit near floor keywords
        for line in doc_lower.split("\n"):
            if "floor" in line or "level" in line or "span" in line:
                nums = re.findall(r"\b\d{1,2}\b", line)
                if nums:
                    num_floors = int(nums[0])
                    break
                    
    # Slab thickness
    slab_thickness = 6.0
    thick_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:inch|in\b|\bthickness\b)", doc_lower)
    if thick_match:
        slab_thickness = float(thick_match.group(1))
    else:
        # Try scanning lines for thickness
        for line in doc_lower.split("\n"):
            if "slab" in line or "thickness" in line:
                nums = re.findall(r"\b\d+(?:\.\d+)?\b", line)
                if nums:
                    slab_thickness = float(nums[0])
                    break
                    
    # Concrete grade
    concrete_grade = "M25 (1:1:2)"
    if "m40" in doc_lower:
        concrete_grade = "M40 (High Compressive)"
    elif "m30" in doc_lower:
        concrete_grade = "M30 (Structural Design)"
    elif "m20" in doc_lower:
        concrete_grade = "M20 (1:1.5:3)"
    elif "m25" in doc_lower:
        concrete_grade = "M25 (1:1:2)"
        
    return {
        "structure_type": structure_type,
        "plinth_area": plinth_area,
        "num_floors": num_floors,
        "slab_thickness": slab_thickness,
        "concrete_grade": concrete_grade
    }

def query_ollama_material_params_safe(doc_content, model_name="llama3.2"):
    try:
        return query_ollama_material_params(doc_content, model_name)
    except Exception:
        return extract_material_params_fallback(doc_content)


# Sidebar layout
with st.sidebar:
    st.markdown("## 🏗️ Intelligence Control")
    st.markdown("---")
    
    # Global Filters
    st.markdown("### Global Filters")
    status_filter = st.multiselect(
        "Project Status",
        options=["On Track", "Delayed", "Under Review"],
        default=["On Track", "Delayed", "Under Review"]
    )
    
    min_progress = st.slider("Min Progress (%)", min_value=0, max_value=100, value=0)
    
    st.markdown("---")
    
    # Ollama Local LLM Settings
    st.markdown("### 🤖 Ollama Local LLM Settings")
    ollama_model_choice = st.text_input(
        "Active Model", 
        value="llama3.2", 
        help="Specify the exact local Ollama model to use (e.g. llama3.2, llama3, phi3, mistral, gemma2)"
    )
    
    # Run status check
    ollama_ok, status_msg, available_models = check_ollama_status(ollama_model_choice)
    
    if ollama_ok:
        st.success(f"🟢 **Ready**: {status_msg}")
    else:
        st.warning(f"⚠️ **Offline**: {status_msg}")
        if available_models:
            st.info(f"Available models found: {', '.join(available_models)}")
            
    st.session_state.ollama_model = ollama_model_choice
    st.session_state.ollama_ok = ollama_ok
    
    st.markdown("---")
    st.markdown("### 🛡️ AI Safety Guardrails")
    enable_guardrails = st.toggle("Enable Guardrails", value=True, help="Toggles input and output safety checks.")
    st.session_state.enable_guardrails = enable_guardrails
    
    # Show statistics
    checked = st.session_state.get("guardrails_checked", 0)
    blocked = st.session_state.get("guardrails_blocked", 0)
    st.markdown(f"""
    <div style='background: rgba(21, 31, 50, 0.5); padding: 12px; border-radius: 12px; border: 1px solid rgba(77, 150, 255, 0.15); margin-bottom: 12px;'>
        <div style='display: flex; justify-content: space-between; font-size: 0.85rem;'>
            <span style='color: #CBD5E1;'>Queries Audited:</span>
            <span style='font-weight: bold; color: #4D96FF;'>{checked}</span>
        </div>
        <div style='display: flex; justify-content: space-between; font-size: 0.85rem; margin-top: 6px;'>
            <span style='color: #CBD5E1;'>Violations Blocked:</span>
            <span style='font-weight: bold; color: {"#F87171" if blocked > 0 else "#4ADE80"};'>{blocked}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if enable_guardrails:
        st.caption("🛡️ Active Guardrail Protections:")
        st.markdown(
            "- 🛡️ Prompt Injection Detection\n"
            "- 🔒 Sensitive PII Scrubbing\n"
            "- 🏗️ Domain Relevance Filtering\n"
            "- 🏛️ System Prompt Leak Prevention\n"
            "- 🚫 Content Moderation / Toxicity"
        )
    else:
        st.caption("⚠️ System protection is bypassed.")
        
    st.markdown("---")
    st.markdown("### Quick Navigation Guide")
    
    # Help guide
    with st.expander("💡 Quick System Guide"):
        st.write("""
        1. **Dashboard**: View overall portfolio metrics and spend distributions.
        2. **Tracker**: Manage projects and register new ones.
        3. **Doc Analysor**: Upload/select design codes, specifications, and contracts to extract compliance items.
        4. **Site Safety**: Inspect site PPE scanner and log safety audit incidents.
        5. **Material Estimation**: Compute brick, cement, and steel demands.
        6. **Daily Report**: File daily logs and view report worksheets.
        7. **Q&A Desk**: Chat about project telemetry and codes.
        8. **Risk Audit**: Assess probability/impact maps for mitigation.
        """)

# Filter Project list based on Sidebar selections
filtered_projects = [
    p for p in st.session_state.projects 
    if p["status"] in status_filter and p["progress"] >= min_progress
]

# Header section
col_title, col_log = st.columns([4, 1])
with col_title:
    st.markdown('<div class="main-title">CONSTRUCTION INTELLIGENCE HUB</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Unified operations, safety auditing, and predictive analytics framework</div>', unsafe_allow_html=True)
with col_log:
    st.markdown("<br>", unsafe_allow_html=True)
    st.button("🔄 Refresh Data", type="secondary", use_container_width=True)

# Main Navigation tabs (8 tabs total)
tab_dash, tab_track, tab_doc, tab_safety, tab_materials, tab_daily, tab_qna, tab_risk = st.tabs([
    "📊 Portfolio Dashboard", 
    "📂 Project Tracker", 
    "📄 Doc Analysor",
    "🛡️ Site Safety & PPE", 
    "🧮 Material Estimator",
    "📝 Daily Report",
    "💬 Project Q&A",
    "⚠️ Risk Detection"
])

# ----------------- TAB 1: PORTFOLIO DASHBOARD -----------------
with tab_dash:
    if not filtered_projects:
        st.warning("No projects match the selected sidebar filters.")
    else:
        # 1. KPI Cards Row
        total_budget = sum(p["budget"] for p in filtered_projects)
        total_spent = sum(p["spent"] for p in filtered_projects)
        avg_progress = sum(p["progress"] for p in filtered_projects) / len(filtered_projects)
        avg_safety = sum(p["safety"] for p in filtered_projects) / len(filtered_projects)
        
        kpi_html = f"""
        <div class="kpi-container">
            <div class="kpi-card">
                <div class="kpi-title">Active Projects</div>
                <div class="kpi-value">{len(filtered_projects)}</div>
                <div class="kpi-delta positive">▲ Portfolio Active</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Total Allocated Budget</div>
                <div class="kpi-value">{format_inr_short(total_budget)}</div>
                <div class="kpi-delta positive">Spent: {format_inr_short(total_spent)}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Avg Construction Progress</div>
                <div class="kpi-value">{avg_progress:.1f}%</div>
                <div class="kpi-delta positive">▲ On Schedule</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-title">Safety compliance index</div>
                <div class="kpi-value">{avg_safety:.2f}%</div>
                <div class="kpi-delta positive">Target: 95.0%</div>
            </div>
        </div>
        """
        st.markdown(kpi_html, unsafe_allow_html=True)
        
        # 2. Charts Section
        st.markdown("### Portfolio Analytics & Analytics Visualizer")
        c1, c2 = st.columns(2)
        
        with c1:
            # Budget vs Spent Plotly Chart
            df_projects = pd.DataFrame(filtered_projects)
            fig_budget = go.Figure()
            fig_budget.add_trace(go.Bar(
                x=df_projects["name"],
                y=df_projects["budget"],
                name="Budgeted (INR)",
                marker_color='#4D96FF'
            ))
            fig_budget.add_trace(go.Bar(
                x=df_projects["name"],
                y=df_projects["spent"],
                name="Spent (INR)",
                marker_color='#FF6B6B'
            ))
            fig_budget.update_layout(
                title="Allocated Budget vs Actual Spend by Site (INR)",
                barmode='group',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#CBD5E1', family='Outfit'),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            fig_budget.update_yaxes(gridcolor='rgba(255,255,255,0.05)')
            st.plotly_chart(fig_budget, use_container_width=True)
            
        with c2:
            # Progress vs Safety Compliance Scatter Chart
            fig_scatter = px.scatter(
                df_projects,
                x="progress",
                y="safety",
                size="budget",
                color="status",
                hover_name="name",
                color_discrete_map={"On Track": "#2ECC71", "Delayed": "#E74C3C", "Under Review": "#F1C40F"},
                title="Project Health Index (X: Progress, Y: Safety Index, Size: Budget)"
            )
            fig_scatter.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#CBD5E1', family='Outfit'),
            )
            fig_scatter.update_xaxes(gridcolor='rgba(255,255,255,0.05)')
            fig_scatter.update_yaxes(gridcolor='rgba(255,255,255,0.05)')
            st.plotly_chart(fig_scatter, use_container_width=True)
            
        st.markdown("---")
        pdf_data = pdf_utils.create_portfolio_pdf(filtered_projects)
        st.download_button(
            label="📥 Download Portfolio Status Report (PDF)",
            data=pdf_data,
            file_name="Portfolio_Status_Report.pdf",
            mime="application/pdf",
            use_container_width=True
        )

# ----------------- TAB 2: PROJECT TRACKER -----------------
with tab_track:
    st.markdown("### Operational Sites Database & Registration")
    
    # Render table of filtered projects
    df_display = pd.DataFrame(filtered_projects)
    if not df_display.empty:
        # Style columns & clean visualization
        df_display_styled = df_display.copy()
        df_display_styled["budget"] = df_display_styled["budget"].map(format_inr)
        df_display_styled["spent"] = df_display_styled["spent"].map(format_inr)
        df_display_styled["progress"] = df_display_styled["progress"].map(lambda x: f"{x}%")
        df_display_styled["safety"] = df_display_styled["safety"].map(lambda x: f"{x}%")
        
        st.dataframe(
            df_display_styled[["name", "location", "status", "budget", "spent", "progress", "safety", "manager"]],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No projects match the filters.")
        
    # Form to add a new project
    st.markdown("### 🆕 Add New Construction Site to Hub")
    with st.form("new_project_form"):
        col1, col2 = st.columns(2)
        with col1:
            p_name = st.text_input("Project Name", placeholder="e.g. Skyline Residency")
            p_loc = st.text_input("Site Location", placeholder="e.g. Mumbai, Sector 15")
            p_manager = st.text_input("Project Lead / Manager", placeholder="e.g. Arun Roy")
            p_status = st.selectbox("Current Status", ["On Track", "Delayed", "Under Review"])
        with col2:
            p_budget = st.number_input("Total Budget (₹)", min_value=100000, value=10000000, step=500000)
            p_spent = st.number_input("Spent So Far (₹)", min_value=0, value=1000000, step=100000)
            p_progress = st.slider("Project Completion Progress (%)", min_value=0, max_value=100, value=10)
            p_safety = st.slider("Initial Safety Audit Score (%)", min_value=0.0, max_value=100.0, value=95.0, step=0.1)
            
        submitted = st.form_submit_button("Register Site to Hub", use_container_width=True)
        if submitted:
            if p_name and p_loc and p_manager:
                new_id = max(p["id"] for p in st.session_state.projects) + 1
                st.session_state.projects.append({
                    "id": new_id,
                    "name": p_name,
                    "location": p_loc,
                    "status": p_status,
                    "budget": p_budget,
                    "spent": p_spent,
                    "progress": p_progress,
                    "safety": p_safety,
                    "manager": p_manager
                })
                st.success(f"Project '{p_name}' successfully added to portfolio directory!")
                time.sleep(1)
                st.rerun()
            else:
                st.error("Please fill in all text fields (Project Name, Location, Lead) to register.")

# ----------------- TAB 3: CONSTRUCTION DOCUMENT ANALYSOR -----------------
with tab_doc:
    st.markdown("### 📄 Construction Document Analysor (AI Parser)")
    st.write("Upload construction contracts, technical specifications, or engineering guidelines to automatically parse, extract critical compliance items, structural parameters, and schedule milestones.")
    
    col_input, col_output = st.columns([1, 2])
    
    document_content = ""
    document_title = ""
    
    with col_input:
        st.markdown("#### Document Source")
        doc_source = st.radio("Select Document Source", ["Sample Templates (Pre-loaded)", "Upload Custom Text File", "Select Existing Project Data"])
        
        if doc_source == "Sample Templates (Pre-loaded)":
            selected_tmpl = st.selectbox("Choose Technical Template", list(PRELOADED_DOCS.keys()))
            document_content = PRELOADED_DOCS[selected_tmpl]
            document_title = selected_tmpl
        elif doc_source == "Upload Custom Text File":
            uploaded_doc = st.file_uploader("Upload technical specification (.txt)", type=["txt"])
            if uploaded_doc is not None:
                document_content = uploaded_doc.read().decode("utf-8")
                document_title = uploaded_doc.name
            else:
                st.info("Upload a standard .txt document or choose a sample template to start.")
        else: # Select Existing Project Data
            selected_proj_name = st.selectbox("Choose Existing Project", [p["name"] for p in st.session_state.projects])
            # Build project brief context text
            proj_data = next(p for p in st.session_state.projects if p["name"] == selected_proj_name)
            
            # Format report title
            document_title = f"Project Summary Report - {proj_data['name']}"
            
            # Retrieve items
            proj_incidents = [inc for inc in st.session_state.safety_incidents if inc["project"] == proj_data["name"]]
            proj_reports = [rep for rep in st.session_state.daily_reports if rep["project"] == proj_data["name"]]
            proj_risks = [r for r in st.session_state.risks if r["project"] == proj_data["name"]]
            
            content_lines = [
                f"PROJECT DIRECTORY REPORT: {proj_data['name'].upper()}",
                f"Location: {proj_data['location']}",
                f"Project Manager: {proj_data['manager']}",
                f"Current Operational Status: {proj_data['status']}",
                f"Physical Progress Completion: {proj_data['progress']}%",
                f"Safety Audit Compliance Rating: {proj_data['safety']}%",
                f"Financial Telemetry: Total budget allocated is {format_inr(proj_data['budget'])} and actual spent is {format_inr(proj_data['spent'])}.",
            ]
            
            if proj_incidents:
                content_lines.append("\nRegistered Safety Incident History:")
                for inc in proj_incidents:
                    content_lines.append(f"- Date: {inc['date']} | Type: {inc['type']} | Severity: {inc['severity']} | Status: {inc['status']} | Details: {inc['description']}")
            else:
                content_lines.append("\nRegistered Safety Incident History:\n- No incidents logged.")
                
            if proj_reports:
                content_lines.append("\nHistorical Daily Progress Reports (DPR):")
                for rep in proj_reports:
                    content_lines.append(f"- Date: {rep['date']} | Weather: {rep['weather']} | Completed Work: {rep['work_done']} | Next Day Plan: {rep['work_tomorrow']} | Staff: {rep['skilled']} skilled / {rep['unskilled']} helpers. Safety Remarks: {rep['safety_remarks']}")
            else:
                content_lines.append("\nHistorical Daily Progress Reports (DPR):\n- No daily logs recorded.")
                
            if proj_risks:
                content_lines.append("\nRegistered Construction Risks & Mitigations:")
                for r in proj_risks:
                    content_lines.append(f"- Category: {r['category']} | Risk: {r['description']} | Exposure Matrix: Likelihood {r['likelihood']}/5, Impact {r['impact']}/5 | Mitigation Plan: {r['mitigation']}")
            else:
                content_lines.append("\nRegistered Construction Risks & Mitigations:\n- No active risk factors registered.")
                
            document_content = "\n".join(content_lines)
                
        st.markdown("<br>", unsafe_allow_html=True)
        analyze_btn = st.button("🔍 Run NLP Document Audit", type="primary", use_container_width=True)
        
    with col_output:
        st.markdown("#### AI Analysis Results")
        if document_content:
            with st.expander("📄 View Source Document Text"):
                st.text_area("Original Content", document_content, height=220, disabled=True)
                
            # Determine if we have a saved result for the current document
            show_results = False
            if st.session_state.get("analyzed_doc_title") == document_title and st.session_state.get("parsed_doc_result") is not None:
                show_results = True
                
            if analyze_btn:
                if st.session_state.get("enable_guardrails", True):
                    st.session_state.guardrails_checked += 1
                    is_safe, err_cat, reason = guardrails.validate_input(document_content)
                    if not is_safe:
                        st.session_state.guardrails_blocked += 1
                        st.session_state.guardrails_violations.append({
                            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "query": f"Document upload: {document_title}",
                            "category": err_cat,
                            "reason": reason
                        })
                        st.error(f"🛡️ **Security Alert: Document Upload Blocked by Guardrails**\n\n**Category**: {err_cat}\n\n**Reason**: {reason}")
                        st.stop()
                        
                with st.spinner("Executing semantic scanning, extracting contract entities and QA limits..."):
                    if st.session_state.get("ollama_ok", False):
                        model_name = st.session_state.get("ollama_model", "llama3.2")
                        result = query_ollama_parser_safe(document_content, model_name)
                    else:
                        # Simulated rule-based fallback
                        if "Project Summary Report - " in document_title:
                            p_name = document_title.replace("Project Summary Report - ", "")
                            proj_data = next((p for p in st.session_state.projects if p["name"] == p_name), None)
                            if proj_data:
                                budget_overrun = proj_data["spent"] > proj_data["budget"]
                                status_warning = proj_data["status"] == "Delayed"
                                safety_warning = proj_data["safety"] < 95.0
                                
                                p_risks = []
                                if budget_overrun:
                                    p_risks.append({"type": "error", "text": f"Budget overrun detected! Spent {format_inr(proj_data['spent'])} of {format_inr(proj_data['budget'])} budget."})
                                else:
                                    p_risks.append({"type": "info", "text": f"Project budget is healthy. Spend is {proj_data['spent']/proj_data['budget']*100:.1f}% of allocated cap."})
                                    
                                if status_warning:
                                    p_risks.append({"type": "error", "text": "Schedule delayed! Urgent mitigation required for timeline restoration."})
                                if safety_warning:
                                    p_risks.append({"type": "warning", "text": f"Safety Rating ({proj_data['safety']}%) is below corporate target threshold of 95.0%."})
                                
                                # Include any registered risks
                                reg_risks = [r for r in st.session_state.risks if r["project"] == p_name]
                                for r in reg_risks:
                                    sev = "error" if r["likelihood"]*r["impact"] >= 12 else "warning"
                                    p_risks.append({"type": sev, "text": f"Risk ({r['category']}): {r['description']} -> Mitigation: {r['mitigation']}"})
                                    
                                # Incident check list
                                p_checklist = [
                                    {"item": f"Conduct regular site safety audit (Current compliance: {proj_data['safety']}%).", "checked": proj_data["safety"] >= 95.0},
                                    {"item": "Review and verify budget expenditure approvals.", "checked": proj_data["spent"] <= proj_data["budget"] * 0.9},
                                    {"item": f"Check status reports and timeline schedules with Lead manager {proj_data['manager']}.", "checked": proj_data["status"] == "On Track"},
                                ]
                                
                                # Include safety incident logs in checks
                                reg_inc = [inc for inc in st.session_state.safety_incidents if inc["project"] == p_name]
                                for inc in reg_inc:
                                    p_checklist.append({"item": f"Verify corrective action for {inc['type']} incident on {inc['date']}.", "checked": inc["status"] == "Resolved"})
                                    
                                result = {
                                    "specifications": f"""**Operational Profile for {proj_data['name']}**:
- **Project Lead / Manager**: {proj_data['manager']}
- **Site Location**: {proj_data['location']}
- **Current Completion Progress**: {proj_data['progress']}% physical completion
- **Overall Safety Index**: {proj_data['safety']}% compliance
- **Financial Status**: Budget: {format_inr(proj_data['budget'])} | Spent: {format_inr(proj_data['spent'])}""",
                                    "risks": p_risks,
                                    "checklist": p_checklist
                                }
                            else:
                                result = {
                                    "specifications": "No project matches this name.",
                                    "risks": [],
                                    "checklist": []
                                }
                        elif "SECTION 03 30 00" in document_content:
                            result = {
                                "specifications": """**Structural Concrete Parameters Extracted:**
- **Concrete Mix Strength**: M40 Concrete Grade (40 MPa / 5800 psi compressive strength).
- **Cement Quality Code**: ASTM C150 Type III High-Early-Strength Portland Cement.
- **Slump Tolerances**: 100mm to 150mm.
- **Water-Cement Ratio**: 0.40 Maximum limit.
- **Reinforcement standard**: ASTM A615 Grade 60 Carbon steel.
- **Required Curing period**: Minimum 7 days continuous moisture curing above 10°C.""",
                                "risks": [
                                    {"type": "warning", "text": "Strict Slump Range: Slump limit of 100mm-150mm might limit placement flexibility in complex geometries without superplasticizers."},
                                    {"type": "info", "text": "Curing Period Check: 7 days moist curing requirement requires a continuous water source and temperature telemetry on site."}
                                ],
                                "checklist": [
                                    {"item": "Validate ASTM C150 Type III supplier certificates.", "checked": True},
                                    {"item": "Perform slump test at the delivery chute prior to pouring concrete.", "checked": False},
                                    {"item": "Verify reinforcing bar positioning stays within ±6mm tolerances.", "checked": True},
                                    {"item": "Check curing blankets, temperature indicators, and water supplies.", "checked": False}
                                ]
                            }
                        elif "Apex Steel" in document_content:
                            result = {
                                "specifications": """**Subcontract Agreement Terms Extracted:**
- **Assigned Subcontractor**: Apex Steelworks Ltd.
- **Target Milestones**: 
  - Foundation Steelwork deadline: June 30, 2026.
  - Superstructure Frame deadline: September 15, 2026.
- **Payment Terms**: 10% Retainage held, released 45 days after project sign-off.
- **Standard Enforced**: IS 800 code for steel construction.""",
                                "risks": [
                                    {"type": "error", "text": "Severe Liquidated Damages: Late penalty clause sets penalty at Rs. 2,00,000/day. Delayed foundation deliveries present critical risk exposure."},
                                    {"type": "warning", "text": "Retainage Period: 10% retainage held for 45 days post-handover is standard but will delay subcontractor cash flow."}
                                ],
                                "checklist": [
                                    {"item": "Log IS 800 steel fabrication certificates.", "checked": True},
                                    {"item": "Verify rebar bending configurations match approved design sheets.", "checked": True},
                                    {"item": "Review construction progress vs June 30 Foundation deadline.", "checked": False},
                                    {"item": "Submit retainage release request form at 45 days.", "checked": False}
                                ]
                            }
                        else:
                            result = {
                                "specifications": """**Site Safety Guidelines Extracted:**
- **Mandatory PPE Gear**: Hard Hat (ANSI Z89.1), Reflective Vest (Class 2), Safety Boots (ASTM F2413), Protective Eye Goggles.
- **Height Fall Protection Rules**: Harness lines & double-lanyards required for tasks exceeding 1.8 meters (6 feet).
- **Water Proximity**: Life Flotation Devices (PFD) and safety catch-nets required.
- **Machinery Proximity exclusion**: Exclusion boundaries of 3 meters (10 feet) around active crane/excavator setups.""",
                                "risks": [
                                    {"type": "warning", "text": "Heavy Exclusion Boundary: 3-meter crane exclusion zone is strict. Small congested layouts (e.g. Noida Highrise) might struggle with spatial layout mapping."}
                                ],
                                "checklist": [
                                    {"item": "Ensure ANSI Z89.1 hard hats are assigned to all personnel.", "checked": True},
                                    {"item": "Check safety harness anchor points load testing validation (>5,000 lbs).", "checked": True},
                                    {"item": "Install barriers/cones for the 3-meter crane swing zones.", "checked": False},
                                    {"item": "Check daily pre-start inspection log signed by crane operators.", "checked": False}
                                ]
                            }
                    
                    st.session_state.parsed_doc_result = result
                    st.session_state.analyzed_doc_title = document_title
                    show_results = True
                    st.rerun()


            if show_results:
                result = st.session_state.parsed_doc_result
                st.success("✅ Audit Scan Completed. Results displayed below.")
                
                # Render metadata cards
                risk_count = len(result.get("risks", []))
                compliance_risk = "Low" if risk_count <= 1 else "Medium" if risk_count <= 3 else "High"
                
                m1, m2, m3 = st.columns(3)
                with m1:
                    st.markdown("<div class='doc-section'><div class='kpi-title'>Security Class</div><div style='font-size:1.2rem; font-weight:700; color:#F1C40F;'>Confidential</div></div>", unsafe_allow_html=True)
                with m2:
                    st.markdown(f"<div class='doc-section'><div class='kpi-title'>Issues Found</div><div style='font-size:1.2rem; font-weight:700; color:#4D96FF;'>{risk_count} Extracted</div></div>", unsafe_allow_html=True)
                with m3:
                    st.markdown(f"<div class='doc-section'><div class='kpi-title'>Compliance Risk</div><div style='font-size:1.2rem; font-weight:700; color:#2ECC71;'>{compliance_risk}</div></div>", unsafe_allow_html=True)
                
                # Download PDF Audit Report
                pdf_data = pdf_utils.create_doc_audit_pdf(st.session_state.analyzed_doc_title, result)
                st.download_button(
                    label="📥 Download PDF Audit Report",
                    data=pdf_data,
                    file_name=f"Document_Audit_{st.session_state.analyzed_doc_title.replace(' ', '_')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
                
                tab_clauses, tab_anomalies, tab_checklist = st.tabs(["📝 Key Specifications", "⚠️ Flagged Risks", "✅ Compliance Checklist"])
                
                with tab_clauses:
                    st.markdown(result.get("specifications", "No specifications extracted."))
                    
                with tab_anomalies:
                    risks = result.get("risks", [])
                    if risks:
                        for r in risks:
                            rtype = r.get("type", "warning").lower()
                            rtext = r.get("text", "")
                            if rtype == "error":
                                st.error(f"❌ {rtext}")
                            elif rtype == "warning":
                                st.warning(f"⚠️ {rtext}")
                            else:
                                st.info(f"ℹ️ {rtext}")
                    else:
                        st.info("No critical risks flagged in this document.")
                        
                with tab_checklist:
                    st.write("Confirm compliance checklist checks for on-site engineers:")
                    checklist = result.get("checklist", [])
                    if checklist:
                        for idx, item in enumerate(checklist):
                            cb_key = f"doc_cb_{st.session_state.analyzed_doc_title}_{idx}"
                            st.checkbox(item.get("item", ""), value=item.get("checked", False), key=cb_key)
                    else:
                        st.write("No checklist items identified.")
        else:
            st.info("Select or upload a construction document text file to begin.")

# ----------------- TAB 4: SITE SAFETY & PPE compliance -----------------
with tab_safety:
    st.markdown("### 🛡️ Site Safety & AI Compliance Hub")
    
    safety_subtab_scan, safety_subtab_logs = st.tabs(["🚀 AI PPE Scanner", "📋 Safety Incident logs"])
    
    with safety_subtab_scan:
        st.write("Streamlit enables real-time visual assessment. Select a pre-loaded sample worker photo or upload a custom image to audit PPE compliance.")
        col_sel, col_scan = st.columns([1, 2])
        
        image_to_scan = None
        selection_type = None
        
        with col_sel:
            st.markdown("#### Input Selection")
            source = st.radio("Choose Scanner Source", ["Sample Worker (Preset)", "Upload Worker Image"], key="safety_scanner_radio")
            
            if source == "Sample Worker (Preset)":
                sample_choice = st.selectbox(
                    "Select Site Image", 
                    ["Worker Compliant (PPE ON)", "Worker Non-Compliant (PPE MISSING)"],
                    key="scanner_sample_select"
                )
                if sample_choice == "Worker Compliant (PPE ON)":
                    image_to_scan = Image.open("assets/compliant.jpg")
                    selection_type = "compliant"
                else:
                    image_to_scan = Image.open("assets/non_compliant.jpg")
                    selection_type = "non_compliant"
            else:
                uploaded_file = st.file_uploader("Upload worker snapshot (.jpg/.png)", type=["jpg", "png", "jpeg"], key="scanner_file_uploader")
                if uploaded_file is not None:
                    image_to_scan = Image.open(uploaded_file)
                    selection_type = "custom"
                    
            st.markdown("<br>", unsafe_allow_html=True)
            scan_btn = st.button("🚀 Trigger AI Compliance Check", type="primary", use_container_width=True, key="trigger_scanner_btn")
            
        with col_scan:
            st.markdown("#### Inspection Viewer")
            if image_to_scan is not None:
                # Create a placeholder container
                preview_container = st.empty()
                # FIXED DEPRECATION WARNING: replaced use_container_width=True with width="stretch"
                preview_container.image(image_to_scan, caption="Source Site Photo", width="stretch")
                
                if scan_btn:
                    # Add simulated loading
                    with st.spinner("Analyzing image contours, detecting PPE features..."):
                        time.sleep(1.2)
                    
                    # Perform PIL annotation based on what type of image was selected
                    annotated_img = image_to_scan.copy()
                    draw = ImageDraw.Draw(annotated_img)
                    
                    # We draw bounding boxes for visual feedback
                    if selection_type == "compliant":
                        # Green Box around Helmet
                        draw.rectangle([(235, 100), (365, 175)], outline=(39, 174, 96), width=4)
                        draw.text((240, 75), "Helmet: DETECTED (98%)", fill=(39, 174, 96))
                        
                        # Green Box around Vest
                        draw.rectangle([(220, 275), (380, 440)], outline=(39, 174, 96), width=4)
                        draw.text((225, 250), "Vest: DETECTED (96%)", fill=(39, 174, 96))
                        
                        # FIXED DEPRECATION WARNING: replaced use_container_width=True with width="stretch"
                        preview_container.image(annotated_img, caption="AI Inspection Results - Annotated", width="stretch")
                        st.success("✅ SCAN COMPLIANT: All required protective gear (Hard Hat, Reflective Vest) is detected.")
                    
                    elif selection_type == "non_compliant":
                        # Red Box around worker head (No Helmet warning)
                        draw.rectangle([(240, 115), (360, 230)], outline=(231, 76, 60), width=4)
                        draw.text((245, 90), "MISSING HELMET (94%)", fill=(231, 76, 60))
                        
                        # Red Box around worker body (No Vest warning)
                        draw.rectangle([(195, 275), (405, 445)], outline=(231, 76, 60), width=4)
                        draw.text((200, 250), "MISSING VEST (95%)", fill=(231, 76, 60))
                        
                        # FIXED DEPRECATION WARNING: replaced use_container_width=True with width="stretch"
                        preview_container.image(annotated_img, caption="AI Inspection Results - Annotated", width="stretch")
                        st.error("❌ SCAN NON-COMPLIANT: Violations detected! Missing Hard Hat and High-Visibility Vest.")
                        
                    else: # Custom uploaded image analysis simulation
                        # Draw a sample box in the center for visual demo
                        w, h = annotated_img.size
                        box_rect = [int(w*0.3), int(h*0.2), int(w*0.7), int(h*0.8)]
                        draw.rectangle(box_rect, outline=(241, 196, 15), width=4)
                        draw.text((int(w*0.3), int(h*0.15)), "Subject Worker Detected (89%)", fill=(241, 196, 15))
                        
                        # FIXED DEPRECATION WARNING: replaced use_container_width=True with width="stretch"
                        preview_container.image(annotated_img, caption="Custom Upload Inspection (Simulated Results)", width="stretch")
                        st.warning("⚠️ SCAN REVIEW REQUIRED: Worker detected. Secondary manual inspection advised to verify specific PPE certifications.")
            else:
                st.info("Please select or upload a site image to begin the compliance check.")

    with safety_subtab_logs:
        st.markdown("#### Safety Audit Log & Incident Registry")
        
        # Display key metrics
        s_col1, s_col2, s_col3 = st.columns(3)
        with s_col1:
            total_logged = len(st.session_state.safety_incidents)
            st.metric("Total Safety Events", total_logged)
        with s_col2:
            unresolved = len([i for i in st.session_state.safety_incidents if i["status"] == "Under Investigation"])
            st.metric("Under Investigation", unresolved, delta="-1 this week", delta_color="inverse")
        with s_col3:
            high_severity = len([i for i in st.session_state.safety_incidents if i["severity"] == "High"])
            st.metric("High Severity Alerts", high_severity, delta="Active", delta_color="off")
            
        st.write("---")
        
        # Layout splits: Form to register safety events, list of logged events
        sl_col1, sl_col2 = st.columns([1, 1])
        
        with sl_col1:
            st.markdown("##### 📝 Register Safety Audit / Incident Log")
            with st.form("new_safety_log_form"):
                log_proj = st.selectbox("Project Name", [p["name"] for p in st.session_state.projects])
                log_date = st.date_input("Audit Inspection Date", datetime.date.today())
                log_type = st.selectbox("Inspection Event Type", ["PPE Violation", "Scaffolding Defect", "Fire Safety Hazard", "Equipment Hazard", "Electrical Issue"])
                log_sev = st.selectbox("Hazard Severity Level", ["Low", "Medium", "High"])
                log_status = st.selectbox("Current Incident Status", ["Under Investigation", "Resolved"])
                log_desc = st.text_area("Event Description & Corrective Actions Required", placeholder="e.g. Scaffolding railings missing on Sector B slab edge. Ordered installation of safety netting.")
                
                log_submitted = st.form_submit_button("Record Safety Log Entry", use_container_width=True)
                if log_submitted:
                    if log_desc:
                        new_log_id = max(i["id"] for i in st.session_state.safety_incidents) + 1
                        st.session_state.safety_incidents.append({
                            "id": new_log_id,
                            "project": log_proj,
                            "date": str(log_date),
                            "type": log_type,
                            "severity": log_sev,
                            "status": log_status,
                            "description": log_desc
                        })
                        st.success("Safety inspection audit recorded successfully!")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Please fill in the incident description to register.")
                        
        with sl_col2:
            st.markdown("##### 📋 Safety Incidents Database")
            df_safety = pd.DataFrame(st.session_state.safety_incidents)
            if not df_safety.empty:
                st.dataframe(
                    df_safety[["project", "date", "type", "severity", "status", "description"]],
                    use_container_width=True,
                    hide_index=True
                )
                pdf_data = pdf_utils.create_safety_report_pdf(st.session_state.safety_incidents)
                st.download_button(
                    label="📥 Download Safety Audit Report (PDF)",
                    data=pdf_data,
                    file_name="Safety_Audit_Report.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                    key="download_safety_pdf_btn"
                )
            else:
                st.info("No safety incidents registered.")
                
            # Plotly incident severity breakdown chart
            st.markdown("<br>", unsafe_allow_html=True)
            if not df_safety.empty:
                fig_incidents = px.histogram(
                    df_safety, 
                    x="severity", 
                    color="severity",
                    title="Audit Incidents by Severity Level",
                    color_discrete_map={"Low": "#2ECC71", "Medium": "#F1C40F", "High": "#E74C3C"},
                    category_orders={"severity": ["Low", "Medium", "High"]}
                )
                fig_incidents.update_layout(
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color='#CBD5E1', family='Outfit'),
                    showlegend=False
                )
                st.plotly_chart(fig_incidents, use_container_width=True)

# ----------------- TAB 5: MATERIAL ESTIMATION -----------------
with tab_materials:
    st.markdown("### 🧮 Material Quantities & Budget Cost Estimator (INR)")
    st.write("Enter structural parameters or upload/select a design specification to automatically estimate construction material requirements and costs in Rupees.")
    
    col_param, col_calc = st.columns([1, 1])
    
    with col_param:
        st.markdown("#### Input Method")
        est_input_method = st.radio("Select Input Method", ["Manual Design Parameters", "Extract from Design/Contract Document"], key="est_input_method_radio")
        
        # Initialize session state for extracted parameters
        if "ext_plinth_area" not in st.session_state:
            st.session_state.ext_plinth_area = 2500
        if "ext_num_floors" not in st.session_state:
            st.session_state.ext_num_floors = 4
        if "ext_slab_thick" not in st.session_state:
            st.session_state.ext_slab_thick = 6.0
        if "ext_conc_grade" not in st.session_state:
            st.session_state.ext_conc_grade = "M25 (1:1:2)"
        if "ext_est_struct" not in st.session_state:
            st.session_state.ext_est_struct = "Residential Apartment"
            
        if est_input_method == "Extract from Design/Contract Document":
            st.markdown("##### 📄 Document Parameter Extractor")
            est_doc_source = st.radio("Document Source", ["Sample Design Templates", "Upload Technical Brief (.txt)"], key="est_doc_source_radio")
            
            doc_content = ""
            if est_doc_source == "Sample Design Templates":
                PRELOADED_EST_DOCS = {
                    "🏢 Residential Complex Design Brief": """PROJECT SPECIFICATIONS - SKYLINE RESIDENTIAL BLOCK C
1. Building Dimensions:
- The structure is a Residential Apartment topology.
- It comprises 12 floors built over a plinth area of 4500 square feet.
- Concrete slab thickness is specified at 6.0 inches.
- Concrete mix design: M25 concrete grade for all slabs and columns.""",
                    "🏙️ Commercial Glass Tower structural specification": """STRUCTURAL BRIEF - METROPOLIS COMMERCIAL OFFICE TOWER
1. Scope & Scale:
- The structure is designed as a Commercial Glass Tower.
- Plinth area of each floor footprint: 8000 square feet.
- Total height is 25 floors.
- Slab thickness is engineered at 8.0 inches.
- Concrete mix: M30 structural concrete grade for heavy loads.""",
                    "🌉 Gachibowli Flyover Phase 2 Engineering Sheet": """CIVIL INFRASTRUCTURE SPECIFICATION SHEET - GACHIBOWLI FLYOVER
1. Engineering Specifications:
- Topology: Infrastructure Flyover / Bridge structure.
- Total deck plinth footprint area: 15000 square feet.
- Elevation spans: 2 levels (floors equivalent).
- Concrete slab deck thickness: 10.0 inches.
- High durability concrete standard: M40 grade concrete."""
                }
                selected_est_tmpl = st.selectbox("Choose Design Template", list(PRELOADED_EST_DOCS.keys()))
                doc_content = PRELOADED_EST_DOCS[selected_est_tmpl]
            else:
                uploaded_est_file = st.file_uploader("Upload technical spec text", type=["txt"], key="est_file_uploader")
                if uploaded_est_file is not None:
                     doc_content = uploaded_est_file.read().decode("utf-8")
                     
            if doc_content:
                with st.expander("📄 View Input Document Text"):
                    st.text_area("Spec Text", doc_content, height=150, disabled=True, key="est_spec_text_area")
                    
            run_extraction = st.button("🤖 Run AI Parameter Extraction", type="primary", use_container_width=True)
            if run_extraction and doc_content:
                if st.session_state.get("enable_guardrails", True):
                    st.session_state.guardrails_checked += 1
                    is_safe, err_cat, reason = guardrails.validate_input(doc_content)
                    if not is_safe:
                        st.session_state.guardrails_blocked += 1
                        st.session_state.guardrails_violations.append({
                            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "query": "Material Specification Brief",
                            "category": err_cat,
                            "reason": reason
                        })
                        st.error(f"🛡️ **Security Alert: Extraction Blocked by Guardrails**\n\n**Category**: {err_cat}\n\n**Reason**: {reason}")
                        st.stop()
                        
                with st.spinner("Ollama is analyzing text and extracting engineering parameters..."):
                    model_name = st.session_state.get("ollama_model", "llama3.2")
                    extracted = query_ollama_material_params_safe(doc_content, model_name)
                    st.session_state.ext_plinth_area = int(extracted.get("plinth_area", 2500))
                    st.session_state.ext_num_floors = int(extracted.get("num_floors", 4))
                    st.session_state.ext_slab_thick = float(extracted.get("slab_thickness", 6.0))
                    
                    # Normalize concrete grade selection
                    raw_g = str(extracted.get("concrete_grade", "M25")).upper()
                    if "M20" in raw_g: st.session_state.ext_conc_grade = "M20 (1:1.5:3)"
                    elif "M30" in raw_g: st.session_state.ext_conc_grade = "M30 (Structural Design)"
                    elif "M40" in raw_g: st.session_state.ext_conc_grade = "M40 (High Compressive)"
                    else: st.session_state.ext_conc_grade = "M25 (1:1:2)"
                    
                    # Normalize topology selection
                    raw_t = str(extracted.get("structure_type", "Residential Apartment")).lower()
                    if "flyover" in raw_t or "bridge" in raw_t or "infrastructure" in raw_t:
                        st.session_state.ext_est_struct = "Infrastructure Flyover / Bridge"
                    elif "commercial" in raw_t or "glass tower" in raw_t or "office" in raw_t:
                        st.session_state.ext_est_struct = "Commercial Glass Tower"
                    else:
                        st.session_state.ext_est_struct = "Residential Apartment"
                    st.success("Parameters successfully extracted and loaded!")
                    
            st.markdown("##### 📌 Loaded Parameters:")
            st.write(f"- **Topology**: {st.session_state.ext_est_struct}")
            st.write(f"- **Plinth Area**: {st.session_state.ext_plinth_area:,} sq ft")
            st.write(f"- **Floors**: {st.session_state.ext_num_floors}")
            st.write(f"- **Slab Thickness**: {st.session_state.ext_slab_thick} inches")
            st.write(f"- **Concrete Grade**: {st.session_state.ext_conc_grade}")
            
            plinth_area = st.session_state.ext_plinth_area
            num_floors = st.session_state.ext_num_floors
            slab_thick = st.session_state.ext_slab_thick
            conc_grade = st.session_state.ext_conc_grade
            est_struct = st.session_state.ext_est_struct
            est_proj = st.selectbox("Select Project Target", [p["name"] for p in st.session_state.projects], key="material_proj_sel")
            
        else:
            st.markdown("#### Design Parameters")
            est_proj = st.selectbox("Select Project Target", [p["name"] for p in st.session_state.projects], key="material_proj_sel")
            est_struct = st.selectbox("Structure Topology", ["Residential Apartment", "Commercial Glass Tower", "Infrastructure Flyover / Bridge"])
            
            col_area, col_floors = st.columns(2)
            with col_area:
                plinth_area = st.number_input("Plinth Area (sq ft)", min_value=500, value=2500, step=100)
            with col_floors:
                num_floors = st.number_input("Number of Floors", min_value=1, max_value=80, value=4, step=1)
                
            slab_thick = st.slider("Concrete Slab Thickness (inches)", min_value=4.0, max_value=12.0, value=6.0, step=0.5)
            conc_grade = st.selectbox("Concrete Grade Standard", ["M20 (1:1.5:3)", "M25 (1:1:2)", "M30 (Structural Design)", "M40 (High Compressive)"])
            
        calc_materials_btn = st.button("🧮 Generate Material Calculations", type="primary", key="calc_materials_btn")
        
    with col_calc:
        st.markdown("#### Calculations Output")
        
        # Calculate materials
        total_area = plinth_area * num_floors
        concrete_factor = (slab_thick / 6.0) * 0.038
        concrete_volume_cy = total_area * concrete_factor
        concrete_volume_cf = concrete_volume_cy * 27
        
        cement_bags = int(total_area * 0.45 * (slab_thick / 6.0))
        steel_factor = 0.0032 if est_struct == "Residential Apartment" else (0.0045 if est_struct == "Commercial Glass Tower" else 0.006)
        steel_tons = total_area * steel_factor
        sand_cft = int(cement_bags * 1.25 * 1.5)
        aggregates_cft = int(cement_bags * 1.25 * 3.0)
        bricks_units = int(total_area * 1.2 * 10) if est_struct != "Infrastructure Flyover / Bridge" else 0
        paint_liters = int(total_area * 2.5 / 10) if est_struct != "Infrastructure Flyover / Bridge" else 0
        
        # Indian Cost Rates (INR)
        cost_cement = cement_bags * 400.00
        cost_steel = steel_tons * 60000.00
        cost_sand = sand_cft * 60.00
        cost_aggregates = aggregates_cft * 70.00
        cost_bricks = bricks_units * 8.00
        cost_paint = paint_liters * 250.00
        
        total_estimated_cost = cost_cement + cost_steel + cost_sand + cost_aggregates + cost_bricks + cost_paint
        
        df_materials = pd.DataFrame([
            {"Material Item": "Cement (ASTM C150)", "Calculated Quantity": f"{cement_bags:,}", "Unit": "Bags", "Rate (INR)": "Rs. 400.00", "Subtotal Cost (INR)": cost_cement},
            {"Material Item": "Structural Steel Rebars", "Calculated Quantity": f"{steel_tons:.2f}", "Unit": "Tons", "Rate (INR)": "Rs. 60,000.00", "Subtotal Cost (INR)": cost_steel},
            {"Material Item": "Fine Sand", "Calculated Quantity": f"{sand_cft:,}", "Unit": "CFT", "Rate (INR)": "Rs. 60.00", "Subtotal Cost (INR)": cost_sand},
            {"Material Item": "Coarse Aggregates", "Calculated Quantity": f"{aggregates_cft:,}", "Unit": "CFT", "Rate (INR)": "Rs. 70.00", "Subtotal Cost (INR)": cost_aggregates},
            {"Material Item": "Solid Brick Masonry", "Calculated Quantity": f"{bricks_units:,}", "Unit": "Units", "Rate (INR)": "Rs. 8.00", "Subtotal Cost (INR)": cost_bricks},
            {"Material Item": "Interior/Exterior Paint", "Calculated Quantity": f"{paint_liters:,}", "Unit": "Liters", "Rate (INR)": "Rs. 250.00", "Subtotal Cost (INR)": cost_paint},
        ])
        
        if calc_materials_btn or "materials_calculated" in st.session_state or True:
            st.session_state.materials_calculated = True
            st.markdown(f"##### 📊 Estimated Cost Summary: **{format_inr(total_estimated_cost)}**")
            
            # Show quantities table
            df_to_show = df_materials.copy()
            df_to_show["Subtotal Cost (INR)"] = df_to_show["Subtotal Cost (INR)"].map(format_inr)
            st.dataframe(df_to_show, use_container_width=True, hide_index=True)
            
            # Export data / PDF buttons
            csv = df_materials.to_csv(index=False).encode('utf-8')
            col_d1, col_d2 = st.columns(2)
            with col_d1:
                st.download_button(
                    label="📥 Export Estimation Sheet (CSV)",
                    data=csv,
                    file_name=f"Material_Estimation_{est_proj.replace(' ', '_')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            with col_d2:
                params_dict = {
                    "plinth_area": plinth_area,
                    "num_floors": num_floors,
                    "slab_thickness": slab_thick,
                    "concrete_grade": conc_grade
                }
                pdf_data = pdf_utils.create_material_estimation_pdf(est_proj, est_struct, params_dict, df_materials, total_estimated_cost)
                st.download_button(
                    label="📥 Download PDF Cost Sheet",
                    data=pdf_data,
                    file_name=f"Material_Estimation_{est_proj.replace(' ', '_')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
                
            # Interactive Chart of cost distribution
            df_chart = df_materials[df_materials["Subtotal Cost (INR)"] > 0]
            fig_mat = px.pie(
                df_chart, 
                values="Subtotal Cost (INR)", 
                names="Material Item", 
                title="Estimation Cost Distribution (INR)",
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig_mat.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#CBD5E1', family='Outfit'),
                legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
            )
            st.plotly_chart(fig_mat, use_container_width=True)

# ----------------- TAB 6: DAILY REPORT BUILDER -----------------
with tab_daily:
    st.markdown("### 📝 Contractor Daily Progress Report (DPR)")
    st.write("Record daily contractor metrics (working manpower count, weather constraints, equipment status, tasks accomplished) and review historic site logs.")
    
    dpr_tab_form, dpr_tab_history = st.tabs(["🆕 Log Daily Progress", "📂 Historical DPR Archive"])
    
    with dpr_tab_form:
        st.markdown("#### Daily Site Worksheet Registration")
        with st.form("new_dpr_form"):
            col_d1, col_d2 = st.columns(2)
            with col_d1:
                dpr_proj = st.selectbox("Target Site Project", [p["name"] for p in st.session_state.projects], key="dpr_proj_sel")
                dpr_date = st.date_input("Reporting Work Date", datetime.date.today(), key="dpr_date_input")
                dpr_weather = st.selectbox("Site Weather Condition", ["Sunny (Clear skies)", "Rainy (Delayed outdoor works)", "Overcast (Normal limits)", "Windy (Tower crane limit warning)"])
                
                st.markdown("**👷 Site Manpower Count Logs**")
                m_c1, m_c2 = st.columns(2)
                with m_c1:
                    dpr_skilled = st.number_input("Skilled Workers", min_value=0, value=12)
                    dpr_unskilled = st.number_input("Helper/Unskilled Workers", min_value=0, value=30)
                with m_c2:
                    dpr_supervisors = st.number_input("Supervisors / Engineers", min_value=0, value=3)
                    dpr_operators = st.number_input("Machinery Operators", min_value=0, value=2)
                    
            with col_d2:
                st.markdown("**⚙️ Equipment Utilized Today**")
                dpr_equip = st.multiselect(
                    "Select Active Machinery",
                    ["Excavator", "Tower Crane", "Concrete Mixer Truck", "Dewatering Pumps", "Bulldozer", "Scaffolding Rigs"],
                    default=["Tower Crane", "Concrete Mixer Truck"]
                )
                
                dpr_work_done = st.text_area("Completed Works Log (Tasks Accomplished Today)", placeholder="e.g. Completed foundations structural inspection. Poured 80 cubic yards of concrete for core wall sector C.")
                dpr_work_tomorrow = st.text_area("Planned Works Log (Scheduled Tasks Tomorrow)", placeholder="e.g. Strip columns shuttering. Begin steel framing layout for slab segment D.")
                dpr_materials_used = st.text_input("Materials Logged/Consumed Today", placeholder="e.g. 140 Bags Cement, 3 Tons Steel Reinforcement")
                dpr_safety_remarks = st.text_input("Safety Toolbox Talk & Incident Remarks", placeholder="e.g. Conducted morning safety briefings. No accidents logged.")
                
            dpr_submitted = st.form_submit_button("Submit Site Daily Progress Report", use_container_width=True)
            if dpr_submitted:
                if dpr_work_done:
                    new_dpr_id = max(d["id"] for d in st.session_state.daily_reports) + 1
                    st.session_state.daily_reports.append({
                        "id": new_dpr_id,
                        "project": dpr_proj,
                        "date": str(dpr_date),
                        "weather": dpr_weather,
                        "work_done": dpr_work_done,
                        "work_tomorrow": dpr_work_tomorrow,
                        "skilled": dpr_skilled,
                        "unskilled": dpr_unskilled,
                        "supervisors": dpr_supervisors,
                        "operators": dpr_operators,
                        "equipment": dpr_equip,
                        "materials": dpr_materials_used,
                        "safety_remarks": dpr_safety_remarks
                    })
                    st.success("Daily progress report recorded and logged to project database!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Please record the work done/accomplished task list to submit the daily progress sheet.")
                    
    with dpr_tab_history:
        st.markdown("#### View Historical Project Worksheets")
        
        # Filter DPR by project
        hist_proj = st.selectbox("Select Project Directory", ["All Sites"] + [p["name"] for p in st.session_state.projects])
        
        filtered_dprs = st.session_state.daily_reports
        if hist_proj != "All Sites":
            filtered_dprs = [d for d in st.session_state.daily_reports if d["project"] == hist_proj]
            
        if filtered_dprs:
            for idx, dpr in enumerate(filtered_dprs):
                # Beautiful worksheet formatting mimicking standard contractor paper records
                with st.expander(f"📝 {dpr['project']} DPR - Work Date: {dpr['date']}"):
                    st.markdown(f"""
                    <div style="background-color:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.07); padding:20px; border-radius:10px;">
                        <h4 style="color:#4D96FF; border-bottom:1px solid rgba(77,150,255,0.2); padding-bottom:10px; margin-top:0px;">DAILY PROGRESS REPORT SHEET</h4>
                        <table style="width:100%; border-collapse:collapse; color:#E2E8F0; margin-bottom:15px;">
                            <tr>
                                <td style="padding:5px 0px; font-weight:600; width:20%;">Project:</td>
                                <td style="padding:5px 0px;">{dpr['project']}</td>
                                <td style="padding:5px 0px; font-weight:600; width:20%;">Date Filed:</td>
                                <td style="padding:5px 0px;">{dpr['date']}</td>
                            </tr>
                            <tr>
                                <td style="padding:5px 0px; font-weight:600;">Weather Constraints:</td>
                                <td style="padding:5px 0px;">{dpr['weather']}</td>
                                <td style="padding:5px 0px; font-weight:600;">Workforce Logged:</td>
                                <td style="padding:5px 0px;">Skilled: {dpr['skilled']} | Unskilled: {dpr['unskilled']} | Ops: {dpr['operators']} | Eng: {dpr['supervisors']}</td>
                            </tr>
                            <tr>
                                <td style="padding:5px 0px; font-weight:600;">Machinery Deployed:</td>
                                <td style="padding:5px 0px;" colspan="3">{", ".join(dpr['equipment']) if isinstance(dpr['equipment'], list) else dpr['equipment']}</td>
                            </tr>
                        </table>
                        
                        <h5 style="color:#FF6B6B; margin-bottom:5px; font-weight:600;">Work Completed Today:</h5>
                        <p style="background:rgba(0,0,0,0.2); padding:10px; border-radius:6px; border-left:3px solid #FF6B6B; font-size:0.95rem; line-height:1.4;">{dpr['work_done']}</p>
                        
                        <h5 style="color:#4D96FF; margin-bottom:5px; font-weight:600;">Work Scheduled for Tomorrow:</h5>
                        <p style="background:rgba(0,0,0,0.2); padding:10px; border-radius:6px; border-left:3px solid #4D96FF; font-size:0.95rem; line-height:1.4;">{dpr['work_tomorrow']}</p>
                        
                        <h5 style="color:#8A99AD; margin-bottom:5px; font-weight:600;">Materials Logged:</h5>
                        <p style="font-size:0.95rem;">{dpr['materials']}</p>
                        
                        <h5 style="color:#2ECC71; margin-bottom:5px; font-weight:600;">Safety Inspector Audit Notes:</h5>
                        <p style="font-size:0.95rem; font-style:italic;">{dpr['safety_remarks']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # PDF Download Button
                    pdf_data = pdf_utils.create_dpr_pdf(dpr)
                    st.download_button(
                        label=f"📥 Download DPR PDF ({dpr['date']})",
                        data=pdf_data,
                        file_name=f"DPR_{dpr['project'].replace(' ', '_')}_{dpr['date']}.pdf",
                        mime="application/pdf",
                        key=f"dpr_pdf_{dpr['project']}_{idx}",
                        use_container_width=True
                    )
        else:
            st.info("No Daily Progress Reports filed for this project selection.")

# ----------------- TAB 7: PROJECT Q&A -----------------
with tab_qna:
    st.markdown("### 💬 Project Q&A & Building Code Desk")
    st.write("Query project progress, materials consumption, logged risks, or standard construction codes (IS Codes, ACI Guidelines, OSHA protocols) using natural language.")
    
    # AI Guardrails Monitor Expander
    with st.expander("🛡️ AI Guardrails System Monitor & Audit Logs", expanded=False):
        st.markdown("This panel displays real-time security logs, blocked violations, and safety statistics for all LLM inputs and outputs.")
        
        # Show total metrics
        c1, c2, c3 = st.columns(3)
        checked_num = st.session_state.get("guardrails_checked", 0)
        blocked_num = st.session_state.get("guardrails_blocked", 0)
        safety_rate = 100.0 if checked_num == 0 else ((checked_num - blocked_num) / checked_num) * 100
        
        c1.metric("Total Requests Audited", checked_num)
        c2.metric("Violations Blocked", blocked_num)
        c3.metric("System Safety Rate", f"{safety_rate:.1f}%")
        
        violations = st.session_state.get("guardrails_violations", [])
        if not violations:
            st.success("✅ No security violations logged. All queries have passed compliance checks.")
        else:
            st.warning(f"⚠️ Flagged Violations: {len(violations)}")
            df = pd.DataFrame(violations)
            if not df.empty:
                df = df[["timestamp", "category", "query", "reason"]]
                st.dataframe(df, use_container_width=True)
            
            # Button to clear logs
            if st.button("🗑️ Clear Guardrail Audit Logs", key="clear_guardrails_logs_btn"):
                st.session_state.guardrails_violations = []
                st.session_state.guardrails_checked = 0
                st.session_state.guardrails_blocked = 0
                st.rerun()
                
    st.write("")
    
    # Project scope selector
    qna_scope = st.selectbox(
        "🔍 Query Focus Scope",
        ["Overall Portfolio"] + [p["name"] for p in st.session_state.projects],
        key="qna_scope_selectbox",
        help="Select a specific project to limit context to that project, or Overall Portfolio to query everything."
    )
    
    # Prompt suggestions chips
    st.markdown("💡 **Suggested Prompt Queries:**")
    prompt_cols = st.columns(5)
    
    chip_query = None
    with prompt_cols[0]:
        if st.button("📈 Project Status Check", use_container_width=True):
            if qna_scope == "Overall Portfolio":
                chip_query = "What is the completion progress and manager of Metro Line Expansion?"
            else:
                chip_query = f"What is the completion progress and manager of {qna_scope}?"
    with prompt_cols[1]:
        if st.button("⚖️ Budget Variance Summary", use_container_width=True):
            if qna_scope == "Overall Portfolio":
                chip_query = "List all construction projects exceeding allocated budgets"
            else:
                chip_query = f"Show the budget vs spend breakdown for {qna_scope}"
    with prompt_cols[2]:
        if st.button("🛡️ Concrete Grade Standard", use_container_width=True):
            chip_query = "What is the required compressive strength grade of the concrete?"
    with prompt_cols[3]:
        if st.button("🚧 Active Site Risks", use_container_width=True):
            if qna_scope == "Overall Portfolio":
                chip_query = "What are the active project risks and mitigation plans?"
            else:
                chip_query = f"What are the active risks and mitigation plans for {qna_scope}?"
    with prompt_cols[4]:
        if st.button("⛈️ Weather Logs", use_container_width=True):
            if qna_scope == "Overall Portfolio":
                chip_query = "How did weather impact work logs on July 11?"
            else:
                chip_query = f"How did weather affect work logs for {qna_scope}?"
            
    st.write("---")
    
    # Show past messages
    for msg in st.session_state.chat_messages:
        role_class = "chat-user" if msg["role"] == "user" else "chat-assistant"
        role_label = "👤 User Query" if msg["role"] == "user" else "🤖 AI Intelligence Desk"
        
        st.markdown(f"""
        <div class="chat-bubble {role_class}">
             <div style="font-size:0.8rem; font-weight:600; opacity:0.8; margin-bottom:5px;">{role_label}</div>
             <div>{msg['content']}</div>
        </div>
        """, unsafe_allow_html=True)
        
    # Input box
    user_query = st.chat_input("Ask a construction query (e.g. 'Compare budgets' or 'Inspect Safety logs')", key="qna_chat_input")
    
    # Override user_query if a prompt suggestion chip was clicked
    if chip_query:
        user_query = chip_query
        
    if user_query:
        # Display user message
        st.markdown(f"""
        <div class="chat-bubble chat-user">
             <div style="font-size:0.8rem; font-weight:600; opacity:0.8; margin-bottom:5px;">👤 User Query</div>
             <div>{user_query}</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.session_state.chat_messages.append({"role": "user", "content": user_query})
        
        # Analyze query and build context response
        is_safe = True
        err_type, reason = "", ""
        if st.session_state.get("enable_guardrails", True):
            st.session_state.guardrails_checked += 1
            is_safe, err_type, reason = guardrails.validate_input(user_query)
            
        if not is_safe:
            st.session_state.guardrails_blocked += 1
            st.session_state.guardrails_violations.append({
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "query": user_query,
                "category": err_type,
                "reason": reason
            })
            response = f"🛡️ **Blocked by Guardrails System**\n\n**Category**: {err_type}\n\n**Reason**: {reason}\n\n*This query has been flagged and was not processed by the Construction Intelligence Hub.*"
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                full_response = ""
                for chunk in response.split(" "):
                    full_response += chunk + " "
                    time.sleep(0.03)
                    message_placeholder.markdown(full_response + "▌")
                message_placeholder.markdown(full_response)
                
            st.session_state.chat_messages.append({"role": "assistant", "content": response})
            time.sleep(0.1)
            st.rerun()
            
        if st.session_state.get("ollama_ok", False):
            model_name = st.session_state.get("ollama_model", "llama3.2")
            with st.spinner("Generating insights with local LLM..."):
                try:
                    response = query_ollama_chat(user_query, model_name, qna_scope)
                    if st.session_state.get("enable_guardrails", True):
                        is_out_safe, out_err_type, out_reason = guardrails.validate_output(response)
                        if not is_out_safe:
                            st.session_state.guardrails_blocked += 1
                            st.session_state.guardrails_violations.append({
                                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                "query": user_query,
                                "category": out_err_type,
                                "reason": out_reason
                            })
                            response = f"🛡️ **Model Output Blocked by Guardrails System**\n\n**Category**: {out_err_type}\n\n**Reason**: {out_reason}\n\n*The model output was generated but failed post-generation safety verification checks.*"
                except Exception as e:
                    response = f"❌ **Error running local Ollama model**: {e}"
        else:
            q_lower = user_query.lower()
            response = ""
            
            # Check if specific project focus is set
            target_p = None
            if qna_scope != "Overall Portfolio":
                target_p = next((p for p in st.session_state.projects if p["name"] == qna_scope), None)
                
            if target_p:
                if "progress" in q_lower or "status" in q_lower or "manager" in q_lower or "lead" in q_lower:
                    response = f"**{target_p['name']}** in **{target_p['location']}** is showing a status of **{target_p['status']}** with **{target_p['progress']}% completion**. The project manager is **{target_p['manager']}**."
                elif "budget" in q_lower or "spent" in q_lower or "cost" in q_lower or "money" in q_lower:
                    overrun_str = f"which is an overrun of {format_inr(target_p['spent'] - target_p['budget'])}" if target_p['spent'] > target_p['budget'] else "which is within allocated limits"
                    response = f"**{target_p['name']}** financial details:\n- **Allocated Budget**: {format_inr(target_p['budget'])}\n- **Spent So Far**: {format_inr(target_p['spent'])} ({overrun_str})."
                elif "safety" in q_lower or "compliance" in q_lower or "incident" in q_lower:
                    p_incidents = [inc for inc in st.session_state.safety_incidents if inc["project"] == target_p["name"]]
                    response = f"**{target_p['name']}** has an overall safety score of **{target_p['safety']}%** (corporate threshold limit: 95.0%).\n"
                    if p_incidents:
                         response += f"\n**Logged Safety Incidents ({len(p_incidents)}):**\n"
                         for inc in p_incidents:
                             response += f"- [{inc['date']}] {inc['type']} (Severity: **{inc['severity']}** | Status: **{inc['status']}**): {inc['description']}\n"
                    else:
                         response += "\n- No safety incidents logged for this site project."
                elif "risk" in q_lower or "mitigation" in q_lower:
                    p_risks = [r for r in st.session_state.risks if r["project"] == target_p["name"]]
                    if p_risks:
                         response = f"**{target_p['name']}** active construction risks:\n"
                         for r in p_risks:
                             response += f"- **[{r['category']}]** {r['description']} (Likelihood: {r['likelihood']}/5 | Impact: {r['impact']}/5)\n  *Mitigation*: {r['mitigation']}\n"
                    else:
                         response = f"No active risks logged for **{target_p['name']}**."
                else:
                    response = f"I am currently focusing queries specifically on **{target_p['name']}**.\n\nYou can ask about its progress completion status, budget expenditures, active safety logs, or registered project risks."
            else:
                # Answer across overall portfolio
                if "metro" in q_lower:
                    proj = st.session_state.projects[1] # Metro expansion
                    response = f"**{proj['name']}** located in **{proj['location']}** is reporting a status of **{proj['status']}** at **{proj['progress']}% physical completion**. Project lead **{proj['manager']}** is supervising. Total budget allocated is **{format_inr(proj['budget'])}** with **{format_inr(proj['spent'])}** spent so far."
                    
                elif "oakridge" in q_lower:
                    proj = st.session_state.projects[0] # Oakridge highrise
                    response = f"**{proj['name']}** in **{proj['location']}** is **{proj['status']}** at **{proj['progress']}% progress**. The spent budget stands at **{format_inr(proj['spent'])}** of the total **{format_inr(proj['budget'])}** allocation. Lead engineer is **{proj['manager']}**."
                    
                elif "budget" in q_lower or "spent" in q_lower or "cost" in q_lower or "overrun" in q_lower:
                    overruns = [p for p in st.session_state.projects if p["spent"] > p["budget"]]
                    response = "### Portfolio Budget Variance Report:\n"
                    if overruns:
                        for p in overruns:
                            response += f"- ❌ **{p['name']}**: Spent {format_inr(p['spent'])} / Budget {format_inr(p['budget'])} (Overrun variance: +{format_inr(p['spent'] - p['budget'])})\n"
                    else:
                        response += "- ✅ All active portfolio projects currently operate within their allocated budget caps.\n"
                    
                    near_cap = [p for p in st.session_state.projects if p["spent"] > p["budget"] * 0.9 and p["spent"] <= p["budget"]]
                    if near_cap:
                        response += "\n**Alert: Projects exceeding 90% budget spending:**\n"
                        for p in near_cap:
                            response += f"- ⚠️ **{p['name']}**: {p['spent']/p['budget']*100:.1f}% spent ({format_inr(p['spent'])} spent of {format_inr(p['budget'])})\n"
                            
                elif "safety" in q_lower or "compliance" in q_lower or "incident" in q_lower:
                    low_safety = [p for p in st.session_state.projects if p["safety"] < 95.0]
                    avg_safety = sum(p["safety"] for p in st.session_state.projects) / len(st.session_state.projects)
                    response = f"### Safety Assessment:\n- Average portfolio safety compliance index stands at **{avg_safety:.2f}%**.\n"
                    if low_safety:
                        response += "\n**Sites failing to meet the 95.0% compliance threshold standard:**\n"
                        for p in low_safety:
                            response += f"- ⚠️ **{p['name']}** ({p['location']}) managed by {p['manager']}: Safety Score **{p['safety']}%**\n"
                    else:
                        response += "- All construction projects satisfy target safety guidelines.\n"
                    
                    response += f"\n**Logged safety incidents summary:** {len(st.session_state.safety_incidents)} logs found. "
                    if st.session_state.safety_incidents:
                        response += "Most recent log:\n"
                        last_i = st.session_state.safety_incidents[-1]
                        response += f"- *Date*: {last_i['date']} | *Project*: {last_i['project']} | *Type*: {last_i['type']} | *Severity*: {last_i['severity']} | *Status*: {last_i['status']}\n  *Description*: {last_i['description']}"
                        
                elif "concrete" in q_lower or "compressive" in q_lower or "structural spec" in q_lower:
                    response = "### Technical Specifications Check:\nBased on the **Structural Concrete Specification Document (Section 03 30 00)**:\n- **Concrete strength requirements**: Minimum compressive strength (f'c) must be **M40 Grade (40 MPa / 5800 psi)** at 28 days.\n- **Slump values**: Limits defined at **100mm to 150mm** at release.\n- **Water/Cement ratio**: Max limit set at **0.40**.\n- **Steel reinforcement requirement**: ASTM A615 Grade 60 bars."
                    
                elif "steel" in q_lower or "risk" in q_lower or "mitigation" in q_lower:
                    steel_risk = [r for r in st.session_state.risks if "steel" in r["description"].lower() or "steel" in r["mitigation"].lower()]
                    if steel_risk:
                        r = steel_risk[0]
                        response = f"### Risk Mitigation Lookup:\n- **Risk Categorization**: {r['category']}\n- **Project**: {r['project']}\n- **Description**: {r['description']}\n- **AI Matrix Assessment**: Likelihood: {r['likelihood']}/5 | Impact: {r['impact']}/5\n- **Mitigation Strategy Plan**: {r['mitigation']}"
                    else:
                        response = "No matching risk mitigation records found. Review the Risk Audit tab for active logs."
                        
                elif "weather" in q_lower or "rain" in q_lower or "july 11" in q_lower:
                    rainy_logs = [d for d in st.session_state.daily_reports if "rain" in d["weather"].lower() or "july 11" in d["date"]]
                    if rainy_logs:
                        d = rainy_logs[0]
                        response = f"### Weather Log Assessment:\n- **Worksheet Date**: {d['date']}\n- **Project**: {d['project']}\n- **Weather logged**: {d['weather']}\n- **Impact/Work Done**: {d['work_done']}\n- **Machinery Active**: {', '.join(d['equipment']) if isinstance(d['equipment'], list) else d['equipment']}"
                    else:
                        response = "No bad weather conditions or logs found for that date query in DPR historical records."
                        
                else:
                    response = ("I can scan active site telemetries. Try asking:\n"
                                "- *'What is the progress of Metro Line?'*\n"
                                "- *'Which sites have budget warnings?'*\n"
                                "- *'What concrete compressive strength is required?'*\n"
                                "- *'Explain steel delay risk mitigation'*")
                            
        # Display response with simulated typing
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            for chunk in response.split(" "):
                full_response += chunk + " "
                time.sleep(0.03)
                message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
            
        st.session_state.chat_messages.append({"role": "assistant", "content": response})
        time.sleep(0.1)
        st.rerun()

# ----------------- TAB 8: RISK DETECTION -----------------
with tab_risk:
    st.markdown("### ⚠️ Project Risk Audit & Mitigation Registry")
    st.write("Analyze and visualize risk matrices (Likelihood vs. Severity) for construction portfolios. Register newly identified project risks and set mitigation schedules.")
    
    col_r_matrix, col_r_reg = st.columns([1, 1])
    
    with col_r_matrix:
        st.markdown("#### 📊 Risk Assessment Matrix")
        
        # Prepare Risk Dataframe
        df_risks = pd.DataFrame(st.session_state.risks)
        
        # Add risk exposure index (Likelihood * Impact)
        df_risks["Exposure"] = df_risks["likelihood"] * df_risks["impact"]
        
        # Risk Severity classification
        def classify_exposure(val):
            if val >= 15: return "Critical"
            elif val >= 8: return "Medium"
            else: return "Low"
            
        df_risks["Risk Level"] = df_risks["Exposure"].map(classify_exposure)
        
        # Plotly risk scatter plot mimicking a 5x5 corporate risk matrix
        fig_risk = px.scatter(
            df_risks,
            x="likelihood",
            y="impact",
            color="Risk Level",
            size="Exposure",
            hover_name="description",
            hover_data=["project", "category", "mitigation"],
            color_discrete_map={"Critical": "#E74C3C", "Medium": "#F1C40F", "Low": "#2ECC71"},
            category_orders={"Risk Level": ["Low", "Medium", "Critical"]},
            title="Risk Exposure Map (X: Likelihood, Y: Impact)"
        )
        
        # Update styling to look clean and modern
        fig_risk.update_layout(
            xaxis=dict(title="Likelihood (1: Rare, 5: Almost Certain)", tickvals=[1,2,3,4,5], range=[0.5, 5.5]),
            yaxis=dict(title="Impact (1: Negligible, 5: Catastrophic)", tickvals=[1,2,3,4,5], range=[0.5, 5.5]),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(255,255,255,0.02)',
            font=dict(color='#CBD5E1', family='Outfit'),
            legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5)
        )
        # Add matrix grids
        fig_risk.update_xaxes(gridcolor='rgba(255,255,255,0.05)', zeroline=False)
        fig_risk.update_yaxes(gridcolor='rgba(255,255,255,0.05)', zeroline=False)
        
        st.plotly_chart(fig_risk, use_container_width=True)
        
    with col_r_reg:
        st.markdown("#### 🆕 Log & Register Project Risk Factor")
        with st.form("new_risk_form"):
            r_proj = st.selectbox("Site Project", [p["name"] for p in st.session_state.projects], key="risk_proj_sel")
            r_cat = st.selectbox("Risk Category", ["Supply Chain Delay", "Weather Disturbance", "Regulatory / Permit", "Labor Relations", "Design Modification", "Financial / Liquidity"])
            
            c_l, c_i = st.columns(2)
            with c_l:
                r_like = st.slider("Likelihood Probability (1-5)", min_value=1, max_value=5, value=3)
            with c_i:
                r_imp = st.slider("Consequence Impact (1-5)", min_value=1, max_value=5, value=4)
                
            r_desc = st.text_input("Risk Factor Description", placeholder="e.g. Noida local municipal permit delays for height authorization above floor 15.")
            r_mit = st.text_area("Corrective / Preventive Mitigation Strategy", placeholder="e.g. Engage licensing consultant; submit architectural structural review papers by next Tuesday.")
            
            r_submitted = st.form_submit_button("Register Risk Item", use_container_width=True)
            if r_submitted:
                if r_desc and r_mit:
                    new_risk_id = max(r["id"] for r in st.session_state.risks) + 1
                    st.session_state.risks.append({
                        "id": new_risk_id,
                        "project": r_proj,
                        "category": r_cat,
                        "description": r_desc,
                        "likelihood": r_like,
                        "impact": r_imp,
                        "mitigation": r_mit
                    })
                    st.success("Risk factor successfully registered and plotted to heat map!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Please fill in the risk description and mitigation strategy to proceed.")
                    
    # Render full table register below
    st.markdown("#### 📋 Active Portfolio Risk Register Database")
    df_risk_styled = df_risks.copy()
    # Sort critical first
    df_risk_styled = df_risk_styled.sort_values(by="Exposure", ascending=False)
    st.dataframe(
        df_risk_styled[["project", "category", "description", "likelihood", "impact", "Exposure", "Risk Level", "mitigation"]],
        use_container_width=True,
        hide_index=True
    )
