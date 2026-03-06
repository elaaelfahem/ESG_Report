"""
Orchestrator: Runs the full ESG pipeline (Agent A → B → C → PDF)
Generates a professional PDF report at the end of the pipeline.
"""
import os
import json
import asyncio
from datetime import datetime
from typing import Callable, Optional

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaLLM

from backend.services.agent_a import AgentA_Extractor
from backend.services.agent_b import AgentB_Auditor
from backend.services.agent_c import AgentC_Writer
from backend.services.report_generator import generate_pdf_report
from backend.core.config import (
    VECTORSTORE_PATH,
    EMBEDDING_MODEL,
    LLM_MODEL,
    REPORTS_DIR,
    setup_logging,
)

logger = setup_logging(__name__)


def run_esg_pipeline(
    report_topic: str,
    questions: list,
    progress_callback: Optional[Callable] = None,
) -> dict:
    """
    Run the full ESG pipeline: Extract → Audit → Write → Generate PDF.
    Returns a dict with the report and metadata.
    """
    def emit(stage, status, detail="", progress=0):
        if progress_callback:
            progress_callback(stage, status, detail, progress)
        logger.info(f"[{stage}] {status}: {detail}")

    emit("init", "running", "Initializing pipeline tools...", 5)

    # 1. Initialize Tools
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    vectorstore = FAISS.load_local(
        VECTORSTORE_PATH,
        embeddings,
        allow_dangerous_deserialization=True
    )

    llm_precise = OllamaLLM(model=LLM_MODEL, temperature=0, format="json")
    llm_creative = OllamaLLM(model=LLM_MODEL, temperature=0.7)

    emit("init", "complete", "Pipeline tools initialized", 10)

    # 2. Initialize Agents
    agent_a = AgentA_Extractor(vectorstore, llm_precise)
    agent_b = AgentB_Auditor(llm_precise)
    agent_c = AgentC_Writer(llm_creative)

    from backend.core.config import KPI_CATEGORIES
    active_questions = questions if questions else KPI_CATEGORIES

    # 3. Agent A — KPI Extraction
    emit("agent_a", "running", f"Extracting {len(active_questions)} KPIs from documents...", 15)
    extracted_results = agent_a.extract_all_kpis(active_questions)
    emit("agent_a", "complete", f"Extracted {extracted_results['successful']}/{extracted_results['total_kpis']} KPIs", 45)

    # 4. Agent B — Compliance Audit
    emit("agent_b", "running", "Auditing compliance against GRI/SASB/ESRS frameworks...", 50)
    audited_results = agent_b.audit_data(extracted_results['extractions'])
    emit("agent_b", "complete", f"Audited {len(audited_results)} KPIs", 70)

    # 5. Agent C — Report Writing
    emit("agent_c", "running", "Writing professional ESG report narrative...", 75)
    final_report_md = agent_c.write_section(report_topic, audited_results)
    emit("agent_c", "complete", "Report narrative drafted successfully", 85)

    # 6. Save Markdown
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    md_filename = f"ESG_Report_{timestamp}.md"
    md_path = f"{REPORTS_DIR}/{md_filename}"

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(final_report_md)

    emit("pdf", "running", "Generating professional PDF report...", 88)

    # 7. Generate PDF Report
    pdf_filename = f"ESG_Report_{timestamp}.pdf"
    stats = {
        "kpis_extracted": extracted_results['successful'],
        "kpis_requested": extracted_results['total_kpis'],
        "frameworks_count": 3,
    }

    try:
        pdf_path = generate_pdf_report(
            report_markdown=final_report_md,
            extraction_details=extracted_results,
            audited_results=audited_results,
            topic=report_topic,
            stats=stats,
            output_filename=pdf_filename,
        )
        emit("pdf", "complete", f"PDF saved as {pdf_filename}", 98)
    except Exception as e:
        logger.error(f"PDF generation failed: {e}")
        pdf_path = None
        emit("pdf", "error", f"PDF generation failed: {e}", 98)

    # 8. Save JSON Data for Analytics
    json_filename = f"ESG_Report_{timestamp}.json"
    json_path = os.path.join(REPORTS_DIR, json_filename)
    analytics_data = {
        "report_filename": md_filename,
        "pdf_filename": pdf_filename if pdf_path else None,
        "topic": report_topic,
        "kpis_requested": len(active_questions),
        "kpis_extracted": extracted_results['successful'],
        "kpis_audited": len(audited_results),
        "extraction_details": extracted_results,
        "audit_details": audited_results,
        "timestamp": timestamp,
    }
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(analytics_data, f, indent=2, ensure_ascii=False)

    emit("save", "complete", "All reports and data saved successfully", 100)

    return {
        "report_content": final_report_md,
        "report_filename": md_filename,
        "pdf_filename": pdf_filename if pdf_path else None,
        "pdf_path": pdf_path,
        "topic": report_topic,
        "kpis_requested": len(active_questions),
        "kpis_extracted": extracted_results['successful'],
        "kpis_audited": len(audited_results),
        "extraction_details": extracted_results,
        "audit_details": audited_results,
        "timestamp": timestamp,
    }
