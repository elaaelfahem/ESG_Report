import json
from langchain_core.prompts import PromptTemplate
from langchain_ollama import OllamaLLM

class AgentB_Auditor:
    def __init__(self, llm: OllamaLLM):
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
  "audit_remarks": "Professional feedback for the reporter",
  "recommendation": "What should the writer do to improve this?"
}}

Return ONLY JSON. No explanation.
"""
        )
        self.chain = self.prompt | self.llm

    def audit_data(self, extraction_results: list, framework: str = "GRI"):
        print(f"\n🕵️ {self.name} is auditing {len(extraction_results)} KPIs...")
        
        audits = []
        for item in extraction_results:
            # We pass the 'extraction' part of Agent A's result
            raw_audit = self.chain.invoke({
                "extraction_data": json.dumps(item['extraction']),
                "framework": framework
            })
            
            # Simple cleanup of potential markdown blocks
            clean_json = str(raw_audit).replace("```json", "").replace("```", "").strip()
            audits.append({
                "question": item['question'],
                "audit": json.loads(clean_json)
            })
            
        return audits

if __name__ == "__main__":
    # Test Logic
    llm = OllamaLLM(model="llama3", temperature=0, format="json") # Or your LLM_MODEL
    agent_b = AgentB_Auditor(llm)
    
    # You would pass the 'extractions' list from Agent A's output here
    # sample_data = results['extractions']
    # print(agent_b.audit_data(sample_data))