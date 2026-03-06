import json
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaLLM

# Import your classes from your existing files
from agent_a import AgentA_Extractor
from agent_b import AgentB_Auditor
from agent_c import AgentC_Writer
from config import VECTORSTORE_PATH, EMBEDDING_MODEL, LLM_MODEL

def run_esg_pipeline(report_topic, questions):
    # 1. Initialize Tools
    print("--- 🛠️ Initializing Pipeline Tools ---")
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    
    # Load the index you created with vector_store_builder.py
    vectorstore = FAISS.load_local(
        VECTORSTORE_PATH, 
        embeddings, 
        allow_dangerous_deserialization=True
    )
    
    # We use temperature 0 for extraction/audit (facts) and 0.7 for writing (style)
    llm_precise = OllamaLLM(model="llama3.2", temperature=0, format="json")
    llm_creative = OllamaLLM(model="llama3.2", temperature=0.7)

    # 2. Initialize Agents
    agent_a = AgentA_Extractor(vectorstore, llm_precise)
    agent_b = AgentB_Auditor(llm_precise)
    agent_c = AgentC_Writer(llm_creative)

    # 3. Step 1: Extraction (Agent A)
    print(f"\n--- 🔍 STEP 1: {agent_a.name} ---")
    extracted_results = agent_a.extract_all_kpis(questions)
    
    # 4. Step 2: Audit (Agent B)
    print(f"\n--- 🕵️ STEP 2: {agent_b.name} ---")
    audited_results = agent_b.audit_data(extracted_results['extractions'])
    
    # 5. Step 3: Write Report (Agent C)
    print(f"\n--- ✍️ STEP 3: {agent_c.name} ---")
    final_report = agent_c.write_section(report_topic, audited_results)
    
    return final_report

if __name__ == "__main__":
    # Define what you want to find
    topic = "Environmental Impact 2024"
    kpi_questions = [
        "What is the total electricity usage in kWh?",
        "What is the total carbon footprint (CO2) in metric tons?"
    ]
    
    # Run the full machine
    report = run_esg_pipeline(topic, kpi_questions)
    
    # Save the final result
    print("\n" + "="*50)
    print("FINAL ESG REPORT GENERATED")
    print("="*50 + "\n")
    print(report)
    
    with open("Final_ESG_Report.md", "w", encoding="utf-8") as f:
        f.write(report)
    print(f"\n✅ Report saved to Final_ESG_Report.md")