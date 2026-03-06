"""
Quick test: Generate a professional PDF from the most recent report markdown.
Run from the project root: python test_pdf_generation.py
"""
import sys
import os
import json

# Make sure backend is importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.services.report_generator import generate_pdf_report
from backend.core.config import REPORTS_DIR

# Load the best existing markdown report
md_file = os.path.join(REPORTS_DIR, "ESG_Report_20260305_223437.md")
with open(md_file, "r", encoding="utf-8") as f:
    report_md = f.read()

# Simulate audit results (based on what pipeline produces)
mock_audited = [
    {"question": "Electricity usage total energy consumption MWh kWh",
     "audit": {"is_compliant": True, "score": 8, "audit_remarks": "Data is clear and cited.", "recommendation": "Add year-on-year comparison."}},
    {"question": "Renewable energy production sources percentage solar wind",
     "audit": {"is_compliant": True, "score": 7, "audit_remarks": "Percentage reported but no absolute figures.", "recommendation": "Include MWh produced from renewables."}},
    {"question": "GHG emissions Scope 1 2 3 CO2 footprint",
     "audit": {"is_compliant": False, "score": 3, "audit_remarks": "Scope breakdown missing.", "recommendation": "Report Scope 1, 2, and 3 separately with tCO2e units."}},
    {"question": "Water withdrawal consumption discharge m3",
     "audit": {"is_compliant": False, "score": 2, "audit_remarks": "No water data found.", "recommendation": "Establish water metering and disclose annually."}},
    {"question": "Waste weight recycling treatment disposal tons",
     "audit": {"is_compliant": True, "score": 7, "audit_remarks": "Waste weight reported.", "recommendation": "Add recycling breakdown by stream."}},
    {"question": "Smart building area implementation certifications",
     "audit": {"is_compliant": True, "score": 6, "audit_remarks": "Area reported.", "recommendation": "Link to certification body."}},
    {"question": "Sustainability funding budget allocation",
     "audit": {"is_compliant": True, "score": 7, "audit_remarks": "Budget disclosed.", "recommendation": "Provide project-level breakdown."}},
    {"question": "Campus green space area hectares coverage",
     "audit": {"is_compliant": True, "score": 6, "audit_remarks": "Hectares reported.", "recommendation": "Track biodiversity metrics."}},
    {"question": "Employee gender age minority diversity statistics",
     "audit": {"is_compliant": False, "score": 2, "audit_remarks": "No diversity data found.", "recommendation": "Mandate annual DEI reporting."}},
    {"question": "Workplace health safety injury incidents",
     "audit": {"is_compliant": False, "score": 1, "audit_remarks": "No safety data.", "recommendation": "Implement TRIR tracking system."}},
    {"question": "Employee training hours per year average",
     "audit": {"is_compliant": False, "score": 2, "audit_remarks": "No training hours data.", "recommendation": "Track L&D hours per FTE annually."}},
    {"question": "Board composition independence diversity",
     "audit": {"is_compliant": True, "score": 8, "audit_remarks": "Board data disclosed.", "recommendation": "Add skills matrix."}},
    {"question": "Anti-corruption ethics policies training coverage",
     "audit": {"is_compliant": False, "score": 3, "audit_remarks": "Policy exists but coverage % not reported.", "recommendation": "Report annual training completion rate."}},
    {"question": "Social community programs development count",
     "audit": {"is_compliant": False, "score": 2, "audit_remarks": "No community program data.", "recommendation": "Establish community impact KPIs."}},
]

mock_extraction = {
    "extractions": [
        {"question": q["question"],
         "extraction": {
             "status": "success" if q["audit"]["is_compliant"] else "not_found",
             "value": "See report" if q["audit"]["is_compliant"] else "N/A",
             "unit": "—", "year": "2023/24", "source": "Institutional Reports",
             "confidence": "medium"
         }}
        for q in mock_audited
    ]
}

stats = {
    "kpis_extracted": sum(1 for r in mock_audited if r["audit"]["is_compliant"]),
    "kpis_requested": 14,
    "frameworks_count": 3,
}

print("Generating professional PDF report...")
pdf_path = generate_pdf_report(
    report_markdown=report_md,
    extraction_details=mock_extraction,
    audited_results=mock_audited,
    topic="Annual Sustainability Report 2024",
    stats=stats,
    output_filename="TEST_Professional_Report.pdf",
)
print(f"\n✅ PDF generated successfully!")
print(f"   Path: {pdf_path}")
