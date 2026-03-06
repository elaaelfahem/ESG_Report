import streamlit as st
import os
import json
from orchestrator import run_esg_pipeline

# Page Config
st.set_page_config(page_title="ESG AI Reporter", page_icon="🌱", layout="wide")

st.title("🌱 ESG Multi-Agent Reporting Suite")
st.markdown("Automate Sustainability Reports using **RAG** and **Multi-Agent Orchestration**.")

# --- SIDEBAR: Upload & Config ---
with st.sidebar:
    st.header("1. Data Ingestion")
    uploaded_files = st.file_uploader("Upload ESG PDFs", type="pdf", accept_multiple_files=True)
    
    if uploaded_files:
        if not os.path.exists("data"):
            os.makedirs("data")
        for f in uploaded_files:
            with open(os.path.join("data", f.name), "wb") as buffer:
                buffer.write(f.getbuffer())
        st.success(f"Uploaded {len(uploaded_files)} files to /data")

    st.header("2. Settings")
    report_topic = st.text_input("Report Topic", "Environmental Sustainability 2024")
    kpi_list = st.text_area("KPIs to Extract (one per line)", 
                          "Total electricity usage\nTotal carbon footprint (CO2)")

# --- MAIN AREA: Execution ---
if st.button("🚀 Generate ESG Report", use_container_width=True):
    if not uploaded_files:
        st.error("Please upload at least one PDF first.")
    else:
        questions = [q.strip() for q in kpi_list.split('\n') if q.strip()]
        
        # UI Feedback
        with st.status("Agents are working...", expanded=True) as status:
            st.write("🔍 Agent A: Extracting data from Vector Store...")
            # Here we trigger the pipeline
            try:
                final_report = run_esg_pipeline(report_topic, questions)
                status.update(label="✅ Report Generated!", state="complete", expanded=False)
                
                # --- DISPLAY RESULTS ---
                st.divider()
                st.subheader("📄 Final Generated Report")
                st.markdown(final_report)
                
                # Download Button
                st.download_button(
                    label="📥 Download Markdown Report",
                    data=final_report,
                    file_name="ESG_Report.md",
                    mime="text/markdown"
                )
            except Exception as e:
                st.error(f"Pipeline failed: {e}")
                status.update(label="❌ Error occurred", state="error")

else:
    st.info("Upload PDFs and click 'Generate' to begin the agentic workflow.")