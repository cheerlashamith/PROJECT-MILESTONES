from PIL import Image, ImageDraw, ImageFont
import os

def create_challenge_images():
    os.makedirs("assets", exist_ok=True)
    
    # Image size: 1000 x 500
    img = Image.new("RGB", (1000, 500), color=(30, 35, 45))
    draw = ImageDraw.Draw(img)
    
    # Draw title / divider
    draw.text((350, 20), "CHALLENGE: STREAMLIT DEFAULT LAYOUT VS CUSTOM CSS", fill=(255, 255, 255))
    draw.line([(500, 50), (500, 480)], fill=(100, 110, 120), width=4)
    
    # --- LEFT SIDE: BEFORE (Default Plain Layout) ---
    draw.text((80, 60), "[BEFORE] DEFAULT STREAMLIT (PLAIN)", fill=(231, 76, 60))
    # Draw plain inputs
    draw.rectangle([(50, 110), (450, 160)], fill=(250, 250, 250), outline=(200, 200, 200), width=1)
    draw.text((60, 125), "Enter project budget: $1,000,000", fill=(0, 0, 0))
    
    # Misaligned element (e.g. Button pushed up/off-center, default button style)
    draw.rectangle([(50, 200), (250, 240)], fill=(240, 242, 246), outline=(200, 203, 207), width=1)
    draw.text((80, 212), "Submit Project", fill=(38, 39, 48))
    draw.text((50, 255), "⚠️ Label pushed below input", fill=(120, 120, 120))
    
    # Generic look
    draw.rectangle([(50, 310), (450, 450)], fill=(240, 242, 246), outline=(220, 220, 220))
    draw.text((65, 330), "Project Details: Plain Box", fill=(0, 0, 0))
    draw.text((65, 360), "- No depth, no highlights, browser default fonts", fill=(100, 100, 100))
    
    # --- RIGHT SIDE: AFTER (Styled Premium Layout) ---
    draw.text((580, 60), "[AFTER] GLASSMORPHISM & ALIGNED", fill=(46, 204, 113))
    # Styled input container
    draw.rounded_rectangle([(550, 110), (950, 170)], radius=8, fill=(45, 55, 72), outline=(77, 150, 255), width=2)
    draw.text((570, 120), "ALLOCATED BUDGET", fill=(138, 153, 173))
    draw.text((570, 140), "$1,000,000", fill=(255, 255, 255))
    
    # Properly aligned submit button with custom styling
    draw.rounded_rectangle([(550, 200), (950, 250)], radius=8, fill=(77, 150, 255))
    draw.text((710, 215), "REGISTER SITE", fill=(255, 255, 255))
    
    # Styled KPI card
    draw.rounded_rectangle([(550, 280), (950, 450)], radius=12, fill=(35, 45, 60), outline=(77, 150, 255, 100), width=1)
    draw.text((575, 305), "OAKRIDGE HIGHRISE STATUS", fill=(138, 153, 173))
    draw.text((575, 335), "Progress: 78% (On Track)", fill=(46, 204, 113))
    draw.text((575, 375), "Spent: $9.8M of $12.5M", fill=(255, 255, 255))
    draw.rounded_rectangle([(575, 410), (925, 420)], radius=5, fill=(45, 55, 72))
    draw.rounded_rectangle([(575, 410), (848, 420)], radius=5, fill=(77, 150, 255)) # 78% progress bar
    
    img.save("assets/challenge_layout.png")

if __name__ == "__main__":
    create_challenge_images()
