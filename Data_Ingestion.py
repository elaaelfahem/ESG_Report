import json
import os
# Modern 2026 Imports
from langchain_core.prompts import PromptTemplate
from langchain_ollama import OllamaLLM 

class AgentC_Writer:
    def __init__(self, llm: OllamaLLM):
        self.llm = llm
        self.name = "Agent C - Report Writer"
        
        self.prompt = PromptTemplate(
            input_variables=["audit_results", "topic"],
            template="""You are Agent C - The Professional ESG Report Writer.
Your task is to write a formal section for a Sustainability Report based on audited data.

TOPIC: {topic}
AUDITED DATA:
{audit_results}

WRITING RULES:
1. TONE: Objective, professional, and transparent.
2. STRUCTURE: Start with a brief narrative overview.
3. DATA: Follow with a clean Markdown table.
4. CITATION: Use the source filename in the table.

Output your response in Markdown format.
"""
        )
        # Using the modern Pipe operator
        self.chain = self.prompt | self.llm

    def write_section(self, topic: str, audit_results: list):
        print(f"\n[WORKING] {self.name} is drafting the {topic} section...")
        
        response = self.chain.invoke({
            "topic": topic,
            "audit_results": json.dumps(audit_results, indent=2)
        })
        
        return response

if __name__ == "__main__":
    # --- UPDATED TO USE YOUR DOWNLOADED MODEL ---
    llm = OllamaLLM(model="llama3.2", temperature=0.7) 
    
    agent_c = AgentC_Writer(llm)
    
    # Test data representing what Agent B would give us
    test_data = [
        {
            "question": "Electricity Usage",
            "audit": {
                "is_compliant": True,
                "score": 9,
                "audit_remarks": "Data is clear and cited."
            }
        }
    ]
    
    report_content = agent_c.write_section("Environmental Impact", test_data)
    print("\n--- TEST REPORT OUTPUT ---")
    print(report_content)