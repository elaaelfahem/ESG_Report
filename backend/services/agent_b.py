"""
Agent B: The Compliance Auditor
Role: Audits extracted KPIs against ESG frameworks (GRI, SASB, ESRS)
"""
import json
from langchain_core.prompts import PromptTemplate

from backend.core.config import setup_logging

logger = setup_logging(__name__)


class AgentB_Auditor:
    def __init__(self, llm):
        self.llm = llm
        self.name = "Agent B - Compliance Auditor"
        
        self.prompt = PromptTemplate(
            input_variables=["extraction_data", "framework"],
            template="""You are Agent B - The ESG Compliance Auditor. 
Your role: Audit the following extracted data against the {framework} framework.

DATA TO AUDIT:
{extraction_data}

AUDIT REQUIREMENTS:
1. COMPLETENESS: Does the data have a value, a unit, and a year?
2. FORMAT: Is the metric name clear and professional?
3. CITATION: Is there a clear source file mentioned?

YOUR RESPONSE MUST BE A VALID JSON OBJECT:
{{
  "is_compliant": true/false,
  "score": 1 to 10,
  "missing_elements": ["list", "of", "missing", "items"],
  "thematic_analysis": "A 1-sentence analytical insight about this KPI's value relative to ESG goals",
  "audit_remarks": "Professional feedback for the reporter",
  "recommendation": "What should the writer do to improve this?"
}}

Return ONLY JSON. No explanation.
"""
        )
        self.chain = self.prompt | self.llm

    def audit_data(self, extraction_results: list, framework: str = "GRI"):
        logger.info(f"{self.name} is auditing {len(extraction_results)} KPIs...")
        
        audits = []
        for item in extraction_results:
            raw_audit = self.chain.invoke({
                "extraction_data": json.dumps(item['extraction']),
                "framework": framework
            })
            
            clean_json = str(raw_audit).replace("```json", "").replace("```", "").strip()
            try:
                audit_parsed = json.loads(clean_json)
            except json.JSONDecodeError:
                audit_parsed = {"is_compliant": False, "score": 0, "audit_remarks": "Failed to parse audit response"}
            
            audits.append({
                "question": item['question'],
                "audit": audit_parsed
            })
            
        return audits
