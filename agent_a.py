"""
Agent A: The KPI Extractor
Role: Finds and extracts specific ESG KPIs from the vectorstore
Specialization: Precise data extraction with confidence scores and sources
"""
import json
from typing import List, Dict, Any, Optional

# --- FIXED IMPORTS FOR 2026 ---
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser 
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.llms import Ollama
from langchain_core.runnables import RunnablePassthrough

from config import (
    LLM_MODEL,
    LLM_TEMPERATURE,
    LLM_MAX_TOKENS,
    EMBEDDING_MODEL,
    EMBEDDING_DEVICE,
    VECTORSTORE_PATH,
    AGENT_A_SEARCH_K,
    AGENT_A_CONFIDENCE_THRESHOLD,
    setup_logging,
    KPI_CATEGORIES
)

logger = setup_logging(__name__)

class AgentA_Extractor:
    def __init__(self, vectorstore: FAISS, llm: Ollama):
        self.vectorstore = vectorstore 
        self.llm = llm
        self.name = "Agent A - KPI Extractor"
        self.role = "ESG Data Extraction Specialist"
        
        logger.info(f"Initializing {self.name}")
        
        # Define extraction prompt
        self.prompt = PromptTemplate(
            input_variables=["context", "question"],
            template="""You are Agent A - The KPI Extractor, a specialized ESG data extraction expert.

Context from ESG documents:
{context}

Question to answer:
{question}

EXTRACTION INSTRUCTIONS:
1. FIND the EXACT numerical data requested in the context.
2. EXTRACT: metric, value, unit, year, source document.
3. If data is NOT found, explicitly state "NOT_FOUND".
4. Return ONLY valid JSON. No preamble. No markdown code blocks.

YOUR RESPONSE MUST MATCH THIS JSON SCHEMA:
{{
  "status": "success" or "not_found",
  "metric": "name of the KPI",
  "value": "numerical value",
  "unit": "unit",
  "year": "year",
  "source": "filename",
  "confidence": "high/medium/low",
  "reasoning": "brief explanation"
}}
"""
        )
        
        # --- FIXED: Use LCEL Pipe instead of LLMChain ---
        self.chain = self.prompt | self.llm
        logger.info(f" {self.name} initialized successfully")
    
    def validate_extraction(self, response: Any) -> Dict[str, Any]:
        """Handles both string and object responses from LLM."""
        try:
            # If response is already a dict (some Ollama integrations do this)
            if isinstance(response, dict):
                return response
                
            # Clean up response string
            text_response = str(response).strip()
            if text_response.startswith("```"):
                text_response = text_response.split("```")[1]
                if text_response.startswith("json"):
                    text_response = text_response[4:]
            
            return json.loads(text_response)
        
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON: {e}")
            return {"status": "error", "message": "Invalid JSON format"}

    def extract_kpi(self, question: str, k: int = None) -> Dict[str, Any]:
        k = k or AGENT_A_SEARCH_K
        
        try:
            logger.info(f"Extracting KPI: {question}")
            
            # Retrieve from FAISS
            results = self.vectorstore.similarity_search_with_score(question, k=k)
            
            if not results:
                return {"status": "not_found", "question": question}
            
            # Build context
            context_parts = []
            for doc, score in results:
                source = doc.metadata.get("source", "unknown")
                page = doc.metadata.get("page", "?")
                context_parts.append(f"[Source: {source} (Page {page})]\n{doc.page_content}")
            
            context = "\n\n---\n\n".join(context_parts)
            
            # --- FIXED: Use .invoke() instead of .run() ---
            raw_response = self.chain.invoke({
                "context": context,
                "question": question
            })
            
            return self.validate_extraction(raw_response)
        
        except Exception as e:
            logger.error(f"Extraction error: {e}")
            return {"status": "error", "message": str(e)}

    def extract_all_kpis(self, kpi_questions: List[str] = None) -> Dict[str, Any]:
        kpi_questions = kpi_questions or KPI_CATEGORIES
        all_extractions = []
        successful = 0
        
        for i, question in enumerate(kpi_questions, 1):
            logger.info(f"[{i}/{len(kpi_questions)}] {question}")
            res = self.extract_kpi(question)
            all_extractions.append({"question": question, "extraction": res})
            if res.get("status") == "success":
                successful += 1
                
        return {
            "agent": self.name,
            "total_kpis": len(kpi_questions),
            "successful": successful,
            "extractions": all_extractions
        }

if __name__ == "__main__":
    # Ensure config values exist or provide defaults
    try:
        embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
        vectorstore = FAISS.load_local(
            VECTORSTORE_PATH, 
            embeddings, 
            allow_dangerous_deserialization=True
        )
        
        llm = Ollama(
            model=LLM_MODEL, 
            temperature=LLM_TEMPERATURE, 
            format="json"
        )
        
        agent_a = AgentA_Extractor(vectorstore, llm)
        
        test_questions = ["Total electricity usage?", "Carbon footprint?"]
        results = agent_a.extract_all_kpis(test_questions)
        print(json.dumps(results, indent=2))
        
    except Exception as e:
        print(f"Pipeline failed: {e}")