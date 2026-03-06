import json
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
1. TONE: Objective, professional, and transparent (No marketing fluff).
2. STRUCTURE: Start with a brief narrative overview.
3. DATA: Follow the narrative with a clean Markdown table of the KPIs.
4. TRANSPARENCY: If the audit found missing data (like a missing year), mention it as a 'Data Limitation' or 'Note'.
5. CITATION: Use the source filename in the table.

Output your response in Markdown format.
"""
        )
        self.chain = self.prompt | self.llm

    def write_section(self, topic: str, audit_results: list):
        print(f"\n {self.name} is drafting the {topic} section...")
        
        # We pass the full combined results of A and B
        response = self.chain.invoke({
            "topic": topic,
            "audit_results": json.dumps(audit_results, indent=2)
        })
        
        return response

if __name__ == "__main__":
    # Test with placeholder data
    llm = OllamaLLM(model="llama3") 
    agent_c = AgentC_Writer(llm)
    print(agent_c.write_section("Environmental Impact", []))