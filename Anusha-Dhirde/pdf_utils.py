import io
from fpdf import FPDF

class ConstructionHubPDF(FPDF):
    def normalize_text(self, txt):
        if txt is None:
            return ""
        if not isinstance(txt, str):
            txt = str(txt)
            
        # Clean unicode bullet points and currency characters that Helvetica doesn't support
        txt = txt.replace("•", "-").replace("▪", "-").replace("●", "-")
        txt = txt.replace("₹", "Rs. ")
        txt = txt.replace("\u201c", '"').replace("\u201d", '"')
        txt = txt.replace("\u2018", "'").replace("\u2019", "'")
        txt = txt.replace("\u2013", "-").replace("\u2014", "-")
        
        # Strip any other character that cannot be encoded in latin-1
        cleaned_chars = []
        for char in txt:
            try:
                char.encode('latin-1')
                cleaned_chars.append(char)
            except UnicodeEncodeError:
                cleaned_chars.append('?') # Safeguard replacement
        cleaned_txt = "".join(cleaned_chars)
        
        return super().normalize_text(cleaned_txt)

    def header(self):
        # Top banner color
        self.set_fill_color(21, 31, 50) # Dark Blue
        self.rect(0, 0, 210, 25, 'F')
        
        # Header text
        self.set_font('helvetica', 'B', 15)
        self.set_text_color(255, 255, 255)
        self.cell(0, 10, 'CONSTRUCTION INTELLIGENCE HUB', border=False, align='C')
        
        self.set_font('helvetica', 'I', 8)
        self.ln(5)
        self.cell(0, 10, 'Automated Project Operations & Compliance Report', border=False, align='C')
        
        self.set_text_color(0, 0, 0) # reset
        self.ln(15)
        
    def footer(self):
        # Go to 1.5 cm from bottom
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}} | Construction Intelligence Hub', align='C')

def create_portfolio_pdf(projects):
    pdf = ConstructionHubPDF()
    pdf.add_page()
    pdf.set_font("helvetica", "B", 13)
    pdf.cell(0, 10, "Portfolio Dashboard Status Report", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)
    
    # Portfolio summaries
    total_budget = sum(p["budget"] for p in projects)
    total_spent = sum(p["spent"] for p in projects)
    avg_progress = sum(p["progress"] for p in projects) / len(projects) if projects else 0
    avg_safety = sum(p["safety"] for p in projects) / len(projects) if projects else 0
    
    pdf.set_font("helvetica", "", 10)
    pdf.cell(0, 6, f"Active Projects: {len(projects)}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, f"Total Allocated Budget: Rs. {total_budget:,.2f}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, f"Total Actual Spend: Rs. {total_spent:,.2f}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, f"Average Completion Progress: {avg_progress:.1f}%", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, f"Average Safety Index: {avg_safety:.2f}%", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    
    # Render table
    headers = ["Project Name", "Location", "Status", "Budget (INR)", "Spent (INR)", "Progress"]
    pdf.set_font("helvetica", "B", 9)
    # Define table column widths (must add up to ~190 for A4 page width margin)
    col_widths = (45, 35, 25, 32, 32, 21)
    
    with pdf.table(col_widths=col_widths, text_align="LEFT") as table:
        row = table.row()
        for h in headers:
            row.cell(h)
        
        pdf.set_font("helvetica", "", 9)
        for p in projects:
            row = table.row()
            row.cell(p["name"])
            row.cell(p["location"])
            row.cell(p["status"])
            row.cell(f"Rs. {p['budget']:,}")
            row.cell(f"Rs. {p['spent']:,}")
            row.cell(f"{p['progress']}%")
            
    return bytes(pdf.output())

def create_doc_audit_pdf(doc_title, result):
    pdf = ConstructionHubPDF()
    pdf.add_page()
    pdf.set_font("helvetica", "B", 13)
    pdf.cell(0, 10, f"Document Audit: {doc_title}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)
    
    # Metadata summaries
    risk_count = len(result.get("risks", []))
    compliance_risk = "Low" if risk_count <= 1 else "Medium" if risk_count <= 3 else "High"
    
    pdf.set_font("helvetica", "", 10)
    pdf.cell(0, 6, f"Audited Specifications Count: {risk_count} Issues Identified", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, f"Compliance Risk Assessment: {compliance_risk}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    
    # 1. Key Specifications
    pdf.set_font("helvetica", "B", 11)
    pdf.cell(0, 8, "Key Technical Specifications & Parameters", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    pdf.set_font("helvetica", "", 9.5)
    specs_text = result.get("specifications", "No specifications extracted.")
    pdf.x = pdf.l_margin
    pdf.multi_cell(pdf.epw, 5.5, specs_text)
    pdf.ln(6)
    
    # 2. Risks
    pdf.set_font("helvetica", "B", 11)
    pdf.cell(0, 8, "Flagged Risks & Contract Anomalies", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    pdf.set_font("helvetica", "", 9.5)
    risks = result.get("risks", [])
    if risks:
        for r in risks:
            pdf.x = pdf.l_margin
            pdf.multi_cell(pdf.epw, 5.5, f"- [{r.get('type','warning').upper()}] {r.get('text','')}")
    else:
        pdf.cell(0, 6, "No critical risks flagged in this document.", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(6)
    
    # 3. Compliance Checklist
    pdf.set_font("helvetica", "B", 11)
    pdf.cell(0, 8, "Compliance Checklist for On-Site Verification", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    pdf.set_font("helvetica", "", 9.5)
    checklist = result.get("checklist", [])
    if checklist:
        for c in checklist:
            pdf.x = pdf.l_margin
            status = "[x]" if c.get("checked") else "[ ]"
            pdf.multi_cell(pdf.epw, 5.5, f"{status} {c.get('item','')}")
    else:
        pdf.cell(0, 6, "No checklist items identified.", new_x="LMARGIN", new_y="NEXT")
        
    return bytes(pdf.output())

def create_safety_report_pdf(incidents):
    pdf = ConstructionHubPDF()
    pdf.add_page()
    pdf.set_font("helvetica", "B", 13)
    pdf.cell(0, 10, "Safety Audit Incident Register", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)
    
    # Safety Stats
    total = len(incidents)
    active = len([i for i in incidents if i["status"] == "Under Investigation"])
    pdf.set_font("helvetica", "", 10)
    pdf.cell(0, 6, f"Total Safety Incidents Logged: {total}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, f"Active/Under Investigation: {active}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    
    headers = ["Project", "Date", "Incident Type", "Severity", "Status", "Description"]
    col_widths = (35, 22, 28, 18, 28, 59)
    pdf.set_font("helvetica", "B", 8.5)
    
    with pdf.table(col_widths=col_widths, text_align="LEFT") as table:
        row = table.row()
        for h in headers:
            row.cell(h)
        
        pdf.set_font("helvetica", "", 8.5)
        for inc in incidents:
            row = table.row()
            row.cell(inc["project"])
            row.cell(inc["date"])
            row.cell(inc["type"])
            row.cell(inc["severity"])
            row.cell(inc["status"])
            row.cell(inc["description"])
            
    return bytes(pdf.output())

def create_material_estimation_pdf(project_name, structure_type, params, df_materials, total_cost):
    pdf = ConstructionHubPDF()
    pdf.add_page()
    pdf.set_font("helvetica", "B", 13)
    pdf.cell(0, 10, f"Material Quantity Estimation: {project_name}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)
    
    pdf.set_font("helvetica", "B", 10.5)
    pdf.cell(0, 6, f"Structure Topology: {structure_type}", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("helvetica", "", 9.5)
    pdf.cell(0, 5, f"Plinth Area: {params['plinth_area']:,} sq ft | Number of Floors: {params['num_floors']} | Slab Thickness: {params['slab_thickness']} in | Grade: {params['concrete_grade']}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)
    
    pdf.set_font("helvetica", "B", 11.5)
    pdf.cell(0, 8, f"Total Estimated Material Budget: Rs. {total_cost:,.2f}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    
    headers = ["Material Item", "Quantity", "Unit", "Rate (INR)", "Subtotal (INR)"]
    col_widths = (65, 30, 20, 35, 40)
    pdf.set_font("helvetica", "B", 9)
    
    with pdf.table(col_widths=col_widths, text_align="LEFT") as table:
        row = table.row()
        for h in headers:
            row.cell(h)
            
        pdf.set_font("helvetica", "", 9)
        for idx, r in df_materials.iterrows():
            row = table.row()
            row.cell(str(r["Material Item"]))
            row.cell(str(r["Calculated Quantity"]))
            row.cell(str(r["Unit"]))
            # Clean Rs./$ symbol to Rs. for safety
            rate_str = str(r["Rate (INR)"])
            sub_str = str(r["Subtotal Cost (INR)"])
            row.cell(rate_str)
            row.cell(sub_str)
            
    return bytes(pdf.output())

def create_dpr_pdf(dpr):
    pdf = ConstructionHubPDF()
    pdf.add_page()
    pdf.set_font("helvetica", "B", 13)
    pdf.cell(0, 10, f"Daily Progress Report: {dpr['project']}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)
    
    pdf.set_font("helvetica", "B", 10.5)
    pdf.cell(0, 6, f"Reporting Date: {dpr['date']} | Weather Conditions: {dpr['weather']}", new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font("helvetica", "", 9.5)
    pdf.cell(0, 5, f"Site Workforce: Skilled: {dpr['skilled']} | Helpers: {dpr['unskilled']} | Engineers: {dpr.get('supervisors', 0)} | Operators: {dpr.get('operators', 0)}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 5, f"Machinery Active: {', '.join(dpr['equipment']) if isinstance(dpr['equipment'], list) else dpr['equipment']}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 5, f"Materials Logged Today: {dpr['materials']}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    
    pdf.set_font("helvetica", "B", 11)
    pdf.cell(0, 7, "Work Accomplished Today", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)
    pdf.set_font("helvetica", "", 9.5)
    pdf.x = pdf.l_margin
    pdf.multi_cell(pdf.epw, 5.5, dpr["work_done"])
    pdf.ln(5)
    
    pdf.set_font("helvetica", "B", 11)
    pdf.cell(0, 7, "Work Scheduled for Tomorrow", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)
    pdf.set_font("helvetica", "", 9.5)
    pdf.x = pdf.l_margin
    pdf.multi_cell(pdf.epw, 5.5, dpr["work_tomorrow"])
    pdf.ln(5)
    
    pdf.set_font("helvetica", "B", 11)
    pdf.cell(0, 7, "Safety Audit Notes & Toolbox Briefings", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)
    pdf.set_font("helvetica", "I", 9.5)
    pdf.x = pdf.l_margin
    pdf.multi_cell(pdf.epw, 5.5, dpr["safety_remarks"])
    
    return bytes(pdf.output())
