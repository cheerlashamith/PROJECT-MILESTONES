import os
import glob

public_dir = r"c:\Users\shami\OneDrive\Desktop\Construction_Intelligence_Hub\public"

# 1. Rename index.html -> landing.html
os.rename(os.path.join(public_dir, "index.html"), os.path.join(public_dir, "landing.html"))

# 2. Rename login.html -> index.html
os.rename(os.path.join(public_dir, "login.html"), os.path.join(public_dir, "index.html"))

# 3. Update all html and js files
for ext in ["*.html", "*.js"]:
    for filepath in glob.glob(os.path.join(public_dir, ext)):
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Replace href="index.html" with href="dashboard.html" (for brand logos)
        # But wait, in landing.html, it shouldn't change.
        if os.path.basename(filepath) != "landing.html":
            content = content.replace('href="index.html"', 'href="dashboard.html"')
            
        # Replace 'login.html' with 'index.html'
        content = content.replace("'login.html'", "'index.html'")
        content = content.replace('"login.html"', '"index.html"')

        # In the new index.html (former login.html), change the login success redirect
        # Also add session check at the end
        if os.path.basename(filepath) == "index.html":
            # The login submit redirects to index.html -> we already changed login.html to index.html above?
            # Wait, no, the JS has: window.location.href = 'index.html';
            # We want it to redirect to dashboard.html after successful login.
            content = content.replace("window.location.href = 'index.html';", "window.location.href = 'dashboard.html';")
            
            # Add session check script before </body>
            session_check = """
    <script type="module">
        import { supabase } from './auth.js';
        supabase.auth.getSession().then(({ data: { session } }) => {
            if (session) {
                window.location.href = 'dashboard.html';
            }
        });
    </script>
</body>"""
            if "</body>" in content and "supabase.auth.getSession" not in content:
                content = content.replace("</body>", session_check)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

print("Migration completed.")
