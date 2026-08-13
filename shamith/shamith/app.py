import streamlit as st
import sys
import os
# Required to launch the fixed local FastAPI command.
import subprocess  # nosec B404
import requests
import streamlit.components.v1 as components
import time

from backend.ollama_manager import OllamaManager

BACKEND_URL = "http://localhost:8555"

def ensure_backend_running():
    # Ensure Ollama. The FastAPI startup hook performs the same safe check;
    # this keeps direct Streamlit launches responsive while it starts.
    try:
        requests.get("http://localhost:11434/api/tags", timeout=2).raise_for_status()
    except requests.RequestException:
        OllamaManager().start()

    # Ensure FastAPI is running on port 8555
    try:
        requests.get(f"{BACKEND_URL}/api/health", timeout=2).raise_for_status()
    except requests.RequestException:
        api_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "api.py")
        if os.path.exists(api_path):
            flags = getattr(subprocess, 'CREATE_NO_WINDOW', 0)
            # argv is fixed and uses this interpreter and API path.
            subprocess.Popen(  # nosec B603
                [sys.executable, api_path],
                cwd=os.path.dirname(api_path),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=flags,
            )
            deadline = time.monotonic() + 15
            while time.monotonic() < deadline:
                try:
                    requests.get(f"{BACKEND_URL}/api/health", timeout=1).raise_for_status()
                    break
                except requests.RequestException:
                    time.sleep(0.5)

ensure_backend_running()

st.set_page_config(
    page_title="CIH Terminal",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Hide Streamlit completely to make way for the smooth React frontend
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="collapsedControl"] { display: none; }
    .stApp { margin: 0; padding: 0; }
    .block-container { padding: 0 !important; max-width: 100% !important; margin: 0 !important; }
    /* Hide the gap at the top */
    div.st-emotion-cache-18ni7ap { display: none; }
    </style>
""", unsafe_allow_html=True)

components.iframe(f"{BACKEND_URL}/index.html?t={int(time.time())}", height=1000, scrolling=True)
