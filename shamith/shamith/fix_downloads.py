import re
import os

base_dir = r"c:\Users\shami\OneDrive\Desktop\Construction_Intelligence_Hub\public"

# 1. Fix daily-reports.html to export PDF instead of TXT
daily_reports_path = os.path.join(base_dir, "daily-reports.html")
with open(daily_reports_path, "r", encoding="utf-8") as f:
    content = f.read()

# Add html2pdf to head
if "html2pdf" not in content:
    content = content.replace('</title>', '</title>\n  <script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js"></script>')

# Replace generateDailyReport
new_generate_func = """function generateDailyReport(e) {
      e.preventDefault();
      const loc = document.getElementById('report-loc').value;
      const staff = document.getElementById('report-manpower').value;
      const work = document.getElementById('report-work').value;
      const incidents = document.getElementById('report-incidents').value;
      const date = new Date().toLocaleDateString();

      const element = document.createElement('div');
      element.style.padding = '30px';
      element.style.fontFamily = "'Libre Franklin', sans-serif";
      element.innerHTML = `
        <div style="border-bottom: 2px solid #1e3a8a; padding-bottom: 10px; margin-bottom: 20px;">
          <h2 style="color: #1e3a8a; font-family: 'Libre Baskerville', serif; margin:0;">CIH Terminal - Shift Log</h2>
          <p style="color: #64748b; margin:5px 0 0 0; font-size:12px;">Generated: ${date} | Location: ${loc}</p>
        </div>
        <p><strong>Weather:</strong> ${currentWeather}</p>
        <p><strong>Active Manpower:</strong> ${staff} Personnel</p>
        <h4 style="color:#1e3a8a; border-bottom:1px solid #e2e8f0; padding-bottom:5px; margin-top:20px;">Work Accomplished</h4>
        <p style="white-space: pre-wrap;">${work}</p>
        <h4 style="color:#1e3a8a; border-bottom:1px solid #e2e8f0; padding-bottom:5px; margin-top:20px;">Safety Incidents</h4>
        <p style="white-space: pre-wrap;">${incidents || "None reported."}</p>
        <div style="margin-top:40px; border-top:1px solid #e2e8f0; padding-top:10px; text-align:center; font-size:11px; color:#94a3b8;">
          CIH Terminal Generated Report
        </div>
      `;

      html2pdf().set({
        margin: 15,
        filename: `Shift_Log_${date.replace(/\\//g,'-')}.pdf`,
        jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' }
      }).from(element).save();
    }"""
# Using regex to replace the function body
content = re.sub(r'function generateDailyReport\(e\)\s*\{[\s\S]*?\}\s*(?=\window\.onload)', new_generate_func + '\n\n    ', content)
with open(daily_reports_path, "w", encoding="utf-8") as f:
    f.write(content)

# 2. Fix insurance-agent.html to implement Export to PDF
insurance_path = os.path.join(base_dir, "insurance-agent.html")
with open(insurance_path, "r", encoding="utf-8") as f:
    content = f.read()

# Add html2pdf to head
if "html2pdf" not in content:
    content = content.replace('</title>', '</title>\n  <script src="https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js"></script>')

# Add ID to button
content = content.replace('<button class="btn btn-primary" style="margin-top: 15px; width: 100%; justify-content: center;"><i class="fa-solid fa-download"></i> Export to PDF</button>', 
                          '<button id="exportPdfBtn" class="btn btn-primary" style="margin-top: 15px; width: 100%; justify-content: center;"><i class="fa-solid fa-download"></i> Export to PDF</button>')

# Add click handler
export_script = """
    document.getElementById('exportPdfBtn')?.addEventListener('click', function() {
      const claimText = document.getElementById('claimDoc').innerText;
      if (!claimText || claimText.trim() === '') {
        alert("Please submit an event to generate a claim first.");
        return;
      }
      const riskScore = document.getElementById('riskPointer').style.left || '0%';
      const severityText = document.getElementById('recommendationText').innerText || 'N/A';
      
      const element = document.createElement('div');
      element.style.padding = '30px';
      element.style.fontFamily = "'Libre Franklin', sans-serif";
      
      // Convert markdown-like syntax if any to simple HTML
      let formattedClaim = claimText.replace(/\\*\\*(.*?)\\*\\*/g, '<strong>$1</strong>').replace(/\\*(.*?)\\*/g, '<em>$1</em>');
      
      element.innerHTML = `
        <div style="border-bottom: 2px solid #1e3a8a; padding-bottom: 10px; margin-bottom: 20px;">
          <h2 style="color: #1e3a8a; font-family: 'Libre Baskerville', serif; margin:0;">Insurance & Liability Assessment</h2>
          <p style="color: #64748b; margin:5px 0 0 0; font-size:12px;">CIH Terminal Generated</p>
        </div>
        <div style="margin-bottom: 20px;">
          <p><strong>Calculated Liability Risk:</strong> ${riskScore}</p>
          <p><strong>Severity Recommendation:</strong> ${severityText}</p>
        </div>
        <h4 style="color:#1e3a8a; border-bottom:1px solid #e2e8f0; padding-bottom:5px;">Claim Documentation</h4>
        <div style="white-space: pre-wrap; font-size: 14px; line-height: 1.6;">${formattedClaim}</div>
      `;
      
      html2pdf().set({
        margin: 15,
        filename: 'Liability_Claim_Report.pdf',
        jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' }
      }).from(element).save();
    });
"""
if "exportPdfBtn" not in content:
    pass # Wait, we just added it above, so it will be there. We just append to <script>
    
if "Liability_Claim_Report.pdf" not in content:
    content = content.replace("</script>\n</body>", export_script + "\n  </script>\n</body>")

with open(insurance_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Updates completed successfully.")
