"""
Agent A: The KPI Extractor
Role: Finds and extracts specific ESG KPIs from the vectorstore
"""
import json
from typing import List, Dict, Any, Optional

from langchain_core.prompts import PromptTemplate
from langchain_community.vectorstores import FAISS

from backend.core.config import (
    AGENT_A_SEARCH_K,
    AGENT_A_CONFIDENCE_THRESHOLD,
    KPI_CATEGORIES,
    setup_logging,
)

logger = setup_logging(__name__)


class AgentA_Extractor:
    def __init__(self, vectorstore: FAISS, llm):
        self.vectorstore = vectorstore
        self.llm = llm
        self.name = "Agent A - KPI Extractor"
        self.role = "ESG Data Extraction Specialist"
        
        logger.info(f"Initializing {self.name}")
        
        self.prompt = PromptTemplate(
            input_variables=["context", "question"],
            template="""You are Agent A - The KPI Extractor, a specialized ESG data extraction expert.

Context from ESG documents:
{context}

Question to answer:
{question}

EXTRACTION INSTRUCTIONS (CRITICAL):
1. FIND the EXACT numerical data requested in the context.
2. EXTRACT: metric, value, unit, year, source document.
3. NUMERICAL VALUE ONLY: The `value` field MUST ONLY CONTAIN NUMBERS (e.g., '1000' not '1,000' or '1000 MWh'). No text strings.
4. STRICT FILTERING: If the context talks about the metric but does NOT provide an exact number or unit, you MUST return "status": "not_found".
5. UNIT ALIGNMENT & CONVERSION: Ensure the 'value' and 'unit' are consistent. 
   - If the text says '1,088,486 kWh', convert it to MWh by dividing by 1000 (value: '1088.486', unit: 'MWh').
   - Normalize areas to 'm²' and emissions to 'tCO2e'. 
6. If data is completely missing, explicitly state "NOT_FOUND".
7. Return ONLY valid JSON. No preamble. No markdown code blocks.

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
        
        self.chain = self.prompt | self.llm
        logger.info(f" {self.name} initialized successfully")
    
    def validate_extraction(self, response: Any) -> Dict[str, Any]:
        try:
            if isinstance(response, dict):
                return response
            text_response = str(response).strip()
            if text_response.startswith("```"):
                text_response = text_response.split("```")[1]
                if text_response.startswith("json"):
                    text_response = text_response[4:]
            return json.loads(text_response)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON: {e}")
            return {"status": "error", "message": "Invalid JSON format"}

    def extract_kpi(self, question: str, k: Optional[int] = None) -> Dict[str, Any]:
        k = k or AGENT_A_SEARCH_K
        try:
            logger.info(f"Extracting KPI: {question}")
            results = self.vectorstore.similarity_search_with_score(question, k=k)
            if not results:
                return {"status": "not_found", "question": question}
            
            context_parts = []
            for doc, score in results:
                source = doc.metadata.get("source", "unknown")
                page = doc.metadata.get("page", "?")
                context_parts.append(f"[Source: {source} (Page {page})]\n{doc.page_content}")
            
            context = "\n\n---\n\n".join(context_parts)
            
            raw_response = self.chain.invoke({
                "context": context,
                "question": question
            })
            
            return self.validate_extraction(raw_response)
        except Exception as e:
            logger.error(f"Extraction error: {e}")
            return {"status": "error", "message": str(e)}

    def extract_all_kpis(self, kpi_questions: Optional[List[str]] = None) -> Dict[str, Any]:
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
