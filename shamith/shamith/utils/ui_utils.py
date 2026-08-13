import streamlit as st

def inject_custom_css():
    st.markdown("""
        <!-- FontAwesome for iframe icons -->
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        <!-- Google Fonts -->
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Space+Grotesk:wght@400;500;600;700&display=swap');
            
            /* ═══════════════════════════════════════════════════════════
               LIGHT ORANGE/BLUE THEME (Clean UI)
               ═══════════════════════════════════════════════════════════ */

            :root {
                --bg-main: #ffffff;
                --bg-card: #f8fafc;
                --bg-card-hover: #f1f5f9;
                
                --text-main: #0f172a;
                --text-muted: #64748b;
                
                --accent-primary: #f97316;       /* Orange */
                --accent-primary-light: #fdba74; /* Light Orange */
                --accent-primary-glow: rgba(249, 115, 22, 0.2);
                
                --accent-secondary: #0ea5e9;     /* Blue */
                --accent-secondary-glow: rgba(14, 165, 233, 0.2);
                
                --accent-purple: #8b5cf6;
                --accent-green: #10b981;
            }

            /* Global Styles */
            html, body, [class*="css"] {
                font-family: 'Outfit', sans-serif;
                background-color: var(--bg-main) !important;
                color: var(--text-main) !important;
            }
            
            .stApp {
                background-color: var(--bg-main) !important;
            }
            
            /* Sidebar visibility restored */

            /* Typography */
            h1, h2, h3, h4, h5, h6 {
                font-family: 'Space Grotesk', sans-serif !important;
                letter-spacing: 0.5px;
                color: var(--text-main);
            }

            .main-title {
                color: var(--text-main);
                font-family: 'Space Grotesk', sans-serif;
                font-size: 3rem;
                font-weight: 700;
                text-align: center;
                margin-bottom: 0.25rem;
                text-transform: uppercase;
                letter-spacing: 2px;
            }
            .main-title i {
                color: var(--accent-primary);
            }
            
            .sub-title {
                color: var(--accent-secondary);
                font-family: 'Space Grotesk', sans-serif;
                font-size: 1.1rem;
                text-align: center;
                margin-bottom: 2.5rem;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 3px;
            }

            .section-title {
                color: var(--accent-secondary);
                font-family: 'Space Grotesk', sans-serif;
                font-size: 1.4rem;
                font-weight: 700;
                margin-top: 1.5rem;
                margin-bottom: 1rem;
                border-bottom: 2px solid rgba(14, 165, 233, 0.2);
                padding-bottom: 0.5rem;
                text-transform: uppercase;
                letter-spacing: 1px;
                display: flex;
                align-items: center;
                gap: 10px;
            }
            .section-title i {
                color: var(--accent-primary);
                font-size: 1.2rem;
            }

            /* Clean Cards */
            .futuristic-card, .metric-card, .material-card, .cost-card, .report-section {
                background: #ffffff;
                border: 1px solid #e2e8f0;
                padding: 1.5rem;
                border-radius: 12px;
                margin-bottom: 1.5rem;
                position: relative;
                overflow: hidden;
                transition: all 0.3s ease;
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
            }

            .futuristic-card:hover, .material-card:hover, .cost-card:hover {
                border-color: rgba(249, 115, 22, 0.3);
                box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
                transform: translateY(-2px);
            }

            .card-title {
                color: var(--accent-secondary);
                font-family: 'Space Grotesk', sans-serif;
                font-size: 1.1rem;
                font-weight: 700;
                margin-bottom: 1rem;
                display: flex;
                align-items: center;
                gap: 10px;
                text-transform: uppercase;
                letter-spacing: 1px;
            }
            
            /* Card Colored Borders */
            .border-primary { border-left: 4px solid var(--accent-primary); }
            .border-blue { border-left: 4px solid var(--accent-secondary); }
            .border-purple { border-left: 4px solid var(--accent-purple); }
            .border-green { border-left: 4px solid var(--accent-green); }

            /* Metrics & Values */
            .metric-value, .mat-val, .cost-val {
                font-family: 'Space Grotesk', sans-serif;
                font-size: 1.8rem;
                font-weight: 700;
                color: var(--text-main);
            }
            .metric-label, .mat-label, .cost-label {
                font-size: 0.85rem;
                color: var(--text-muted);
                text-transform: uppercase;
                letter-spacing: 1px;
                margin-bottom: 0.25rem;
                font-weight: 600;
            }

            /* Buttons */
            .stButton > button {
                background: #ffffff;
                color: var(--accent-secondary);
                border: 1px solid var(--accent-secondary);
                border-radius: 8px;
                padding: 0.5rem 1rem;
                font-family: 'Space Grotesk', sans-serif;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 1px;
                transition: all 0.3s ease;
                box-shadow: 0 2px 4px rgba(14, 165, 233, 0.1);
            }
            .stButton > button:hover {
                background: var(--accent-secondary);
                color: #ffffff;
                box-shadow: 0 4px 6px rgba(14, 165, 233, 0.2);
                transform: translateY(-1px);
            }

            /* Primary Action Button (Solid Orange) */
            .btn-primary .stButton > button {
                background: var(--accent-primary) !important;
                color: #ffffff !important;
                border: 1px solid var(--accent-primary) !important;
                box-shadow: 0 4px 6px rgba(249, 115, 22, 0.2) !important;
            }
            .btn-primary .stButton > button:hover {
                background: #ea580c !important;
                box-shadow: 0 6px 10px rgba(249, 115, 22, 0.3) !important;
                transform: translateY(-1px) !important;
            }

            /* AI Action Button (Purple) */
            .ai-btn-container .stButton > button {
                background: #f3e8ff !important;
                color: #7e22ce !important;
                border: 1px solid var(--accent-purple) !important;
            }
            .ai-btn-container .stButton > button:hover {
                background: var(--accent-purple) !important;
                color: #ffffff !important;
            }

            /* Inputs & Forms */
            .stTextInput>div>div>input, .stNumberInput>div>div>input, .stSelectbox>div>div>div, .stDateInput>div>div>input {
                background-color: #f8fafc !important;
                border: 1px solid #cbd5e1 !important;
                color: var(--text-main) !important;
                border-radius: 8px !important;
                font-family: 'Space Grotesk', sans-serif !important;
                font-weight: 500 !important;
                transition: all 0.3s ease !important;
            }
            .stTextInput>div>div>input:focus, .stNumberInput>div>div>input:focus {
                border-color: var(--accent-primary) !important;
                box-shadow: 0 0 0 2px rgba(249, 115, 22, 0.2) !important;
                background-color: #ffffff !important;
            }
            
            /* Form Labels */
            .stTextInput label, .stNumberInput label, .stSelectbox label, .stDateInput label {
                color: var(--text-main) !important;
                font-family: 'Space Grotesk', sans-serif !important;
                font-weight: 600 !important;
                text-transform: uppercase !important;
                letter-spacing: 1px !important;
                font-size: 0.85rem !important;
            }

            /* File Uploader */
            .stFileUploader>div>div>button {
                background: #fff7ed !important;
                color: var(--accent-primary) !important;
                border: 1px dashed var(--accent-primary) !important;
            }
            
            /* Native Streamlit Metrics Override */
            div[data-testid="stMetricValue"] {
                color: var(--text-main) !important;
                font-family: 'Space Grotesk', sans-serif !important;
            }
            div[data-testid="stMetricLabel"] {
                color: var(--text-muted) !important;
                text-transform: uppercase !important;
                letter-spacing: 1px !important;
                font-weight: 600 !important;
            }

            /* ── Status Badges ────────────────────────────────────────── */
            .status-badge {
                display: inline-flex;
                align-items: center;
                gap: 8px;
                padding: 6px 16px;
                border-radius: 100px;
                font-size: 0.85rem;
                font-weight: 700;
                letter-spacing: 1px;
                font-family: 'Space Grotesk', sans-serif;
                text-transform: uppercase;
                background: #f8fafc;
                border: 1px solid;
            }
            .status-online {
                color: #15803d;
                border-color: #22c55e;
                background: #f0fdf4;
            }
            .status-online::before {
                content: '';
                width: 8px;
                height: 8px;
                border-radius: 50%;
                background: #22c55e;
            }
            .status-offline {
                color: #b91c1c;
                border-color: #ef4444;
                background: #fef2f2;
            }
            .status-offline::before {
                content: '';
                width: 8px;
                height: 8px;
                border-radius: 50%;
                background: #ef4444;
            }

            /* ── AI Insight Card ──────────────────────────────────────── */
            .ai-insight-card {
                background: #f5f3ff;
                border: 1px solid #ddd6fe;
                border-left: 4px solid var(--accent-purple);
                border-radius: 12px;
                padding: 1.5rem;
                margin: 1rem 0;
                font-size: 0.95rem;
                line-height: 1.7;
                color: var(--text-main);
                position: relative;
            }
            .ai-insight-card h4 {
                color: #6d28d9;
                font-family: 'Space Grotesk', sans-serif;
                margin-bottom: 0.75rem;
                display: flex;
                align-items: center;
                gap: 8px;
                text-transform: uppercase;
                letter-spacing: 1px;
                font-weight: 700;
            }

            /* ── Progress Bars ────────────────────────────────────────── */
            .progress-container {
                width: 100%;
                background-color: #e2e8f0;
                border-radius: 100px;
                margin-top: 8px;
                margin-bottom: 16px;
                overflow: hidden;
            }
            .progress-bar-primary {
                height: 8px;
                background: linear-gradient(90deg, var(--accent-primary), #fb923c);
                border-radius: 100px;
            }
            .progress-bar-blue {
                height: 8px;
                background: linear-gradient(90deg, var(--accent-secondary), #38bdf8);
                border-radius: 100px;
            }

            /* ── Document Upload Preview ──────────────────────────────── */
            .doc-preview {
                display: flex;
                align-items: center;
                gap: 12px;
                background: #f0f9ff;
                border: 1px solid #bae6fd;
                padding: 10px 15px;
                border-radius: 8px;
                margin-bottom: 10px;
            }
            .doc-icon {
                font-size: 1.5rem;
                color: var(--accent-secondary);
            }
            .doc-info {
                flex-grow: 1;
            }
            .doc-name {
                font-weight: 600;
                color: var(--text-main);
                font-size: 0.9rem;
            }
            .doc-size {
                font-size: 0.75rem;
                color: var(--text-muted);
            }

            /* ── Formula Tag ──────────────────────────────────────────── */
            .formula-tag {
                display: inline-block;
                background: #f0fdf4;
                color: #15803d;
                font-size: 0.75rem;
                font-weight: 600;
                padding: 3px 8px;
                border-radius: 4px;
                border: 1px solid #bbf7d0;
                font-family: 'Courier New', monospace;
                margin-top: 8px;
            }
            
            /* Chat Interface Customization */
            .stChatMessage {
                background-color: transparent !important;
            }
            div[data-testid="stChatMessageContent"] {
                background-color: #ffffff !important;
                border: 1px solid #e2e8f0 !important;
                border-radius: 12px !important;
                padding: 1rem !important;
                color: var(--text-main) !important;
                box-shadow: 0 2px 4px rgba(0,0,0,0.02);
            }
            div[data-testid="chatAvatarIcon-user"] {
                background-color: var(--accent-secondary) !important;
            }
            div[data-testid="chatAvatarIcon-assistant"] {
                background-color: var(--accent-primary) !important;
            }
            
            /* Tabs Styling */
            .stTabs [data-baseweb="tab-list"] {
                background-color: transparent;
                border-bottom: 1px solid #e2e8f0;
            }
            .stTabs [data-baseweb="tab"] {
                color: var(--text-muted);
                font-family: 'Space Grotesk', sans-serif;
                text-transform: uppercase;
                letter-spacing: 1px;
                font-weight: 600;
            }
            .stTabs [aria-selected="true"] {
                color: var(--accent-primary) !important;
                background-color: #fff7ed !important;
                border-bottom: 3px solid var(--accent-primary) !important;
            }

        </style>
    """, unsafe_allow_html=True)
