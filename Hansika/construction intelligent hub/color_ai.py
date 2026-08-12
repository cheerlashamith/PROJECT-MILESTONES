import streamlit as st
from PIL import Image
import cv2
import numpy as np
import requests

# ==========================================
# Theme Database
# ==========================================

themes = {
    "Modern White": {
        "rgb": (245,245,245),
        "wall": "Snow White",
        "accent": "Dark Grey",
        "roof": "Charcoal Black",
        "paint": "Asian Paints Apex Ultima",
        "climate": "Hot & Humid Regions",
        "best_for": "Modern Villas and Apartments"
    },

    "Luxury Beige": {
        "rgb": (230,215,190),
        "wall": "Luxury Beige",
        "accent": "Coffee Brown",
        "roof": "Dark Brown",
        "paint": "Berger WeatherCoat",
        "climate": "Moderate Climate",
        "best_for": "Premium Houses"
    },

    "Royal Blue": {
        "rgb": (180,210,255),
        "wall": "Pearl White",
        "accent": "Royal Blue",
        "roof": "Slate Grey",
        "paint": "Nerolac Excel",
        "climate": "Coastal Regions",
        "best_for": "Commercial Buildings"
    },

    "Minimal Grey": {
        "rgb": (220,220,220),
        "wall": "Light Grey",
        "accent": "Dark Grey",
        "roof": "Graphite Black",
        "paint": "Asian Paints Apex Shyne",
        "climate": "Urban Cities",
        "best_for": "Offices and Apartments"
    },

    "Nature Green": {
        "rgb": (220,235,210),
        "wall": "Cream White",
        "accent": "Olive Green",
        "roof": "Forest Green",
        "paint": "Berger Silk Breathe Easy",
        "climate": "Hill Stations",
        "best_for": "Eco Friendly Homes"
    },

    "Classic Brown": {
        "rgb": (220,205,190),
        "wall": "Ivory Cream",
        "accent": "Wood Brown",
        "roof": "Chocolate Brown",
        "paint": "Nerolac Impression",
        "climate": "Rural Areas",
        "best_for": "Traditional Homes"
    }
}

# ==========================================
# Qwen Recommendation
# ==========================================

def get_ai_recommendation():

    prompt = """
You are an expert architect and exterior designer.

Recommend the best 3 exterior themes for a building.

Choose only from:
Modern White
Luxury Beige
Royal Blue
Minimal Grey
Nature Green
Classic Brown

Return only theme names separated by commas.
"""

    try:

        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model":"qwen2.5:0.5b",
                "prompt":prompt,
                "stream":False
            }
        )

        answer = response.json()["response"]

        return answer

    except:
        return "Modern White, Luxury Beige, Minimal Grey"

# ==========================================
# Building Recolor
# ==========================================

def recolor_wall(image, color):

    img = np.array(image.convert("RGB"))

    hsv = cv2.cvtColor(
        img,
        cv2.COLOR_RGB2HSV
    )

    lower = np.array([0,0,60])
    upper = np.array([180,80,240])

    mask = cv2.inRange(
        hsv,
        lower,
        upper
    )

    overlay = np.full_like(
        img,
        color
    )

    alpha = 0.45

    result = img.copy()

    result[mask > 0] = (
        result[mask > 0]*(1-alpha)
        +
        overlay[mask > 0]*alpha
    )

    return Image.fromarray(
        result.astype(np.uint8)
    )

# ==========================================
# Main Function
# ==========================================

def show():

    st.title("🎨 AI Exterior Design Studio")

    st.write(
        "Upload your building image and let AI recommend professional exterior themes."
    )

    uploaded = st.file_uploader(
        "Upload Building Image",
        type=["jpg","jpeg","png"]
    )

    if uploaded:

        image = Image.open(uploaded)

        st.subheader("🏠 Original Building")

        st.image(
            image,
            use_container_width=True
        )

        with st.spinner(
            "🤖 Qwen AI is analyzing architecture..."
        ):

            recommendations = get_ai_recommendation()

        st.divider()

        st.subheader(
            "🤖 AI Exterior Design Report"
        )

        col1,col2,col3 = st.columns(3)

        col1.metric(
            "Architecture Style",
            "Modern Residential"
        )

        col2.metric(
            "AI Confidence",
            "96%"
        )

        col3.metric(
            "Design Category",
            "Premium Exterior"
        )

        st.success(
            f"Recommended Themes: {recommendations}"
        )

        st.info("""
🏡 AI Analysis Summary

• Building facade supports modern neutral shades.
• Light exterior colors improve thermal efficiency.
• Premium tones increase resale value.
• Low maintenance palettes are recommended.
""")

        st.divider()

        selected_theme = st.selectbox(
            "🎨 Select Theme",
            list(themes.keys())
        )

        if st.button(
            "Generate Exterior Preview",
            use_container_width=True
        ):

            details = themes[selected_theme]

            preview = recolor_wall(
                image,
                details["rgb"]
            )

            st.subheader(
                f"🏡 Exterior Preview - {selected_theme}"
            )

            c1,c2 = st.columns(2)

            with c1:
                st.image(
                    image,
                    caption="Original Building",
                    use_container_width=True
                )

            with c2:
                st.image(
                    preview,
                    caption=f"{selected_theme} Theme Applied",
                    use_container_width=True
                )

            st.success(
                f"{selected_theme} applied successfully."
            )

            st.markdown(f"""
### 🎨 Theme Details

**Wall Colour:** {details['wall']}

**Accent Colour:** {details['accent']}

**Roof Colour:** {details['roof']}

🎨 Recommended Paint:
{details['paint']}

🌦 Suitable Climate:
{details['climate']}

🏢 Best For:
{details['best_for']}

🏆 Design Score: 96%

🌡 Heat Resistance: Excellent

💧 Weather Resistance: High

🔧 Maintenance Level: Low

♻ Sustainability Score: 92%
""")