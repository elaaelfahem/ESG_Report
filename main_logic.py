import os
import shutil
from pathlib import Path
from dotenv import load_dotenv
from docling.document_converter import DocumentConverter
from llama_index.core import VectorStoreIndex, StorageContext, Document
from llama_index.core.node_parser import SemanticSplitterNodeParser
from llama_index.llms.google_genai import GoogleGenAI
from llama_index.embeddings.google_genai import GoogleGenAIEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core.agent import ReActAgent
import chromadb

load_dotenv()

# --- Layer 1: Ingestion ---
def process_to_markdown(pdf_path):
    converter = DocumentConverter()
    result = converter.convert(pdf_path)
    return result.document.export_to_markdown()

# --- Layer 2: Knowledge Base ---
def build_vector_db(markdown_text):
    db = chromadb.PersistentClient(path="./esg_db")
    chroma_collection = db.get_or_create_collection("esg_reports")
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    
    embed_model = GoogleGenAIEmbedding(model_name="models/embedding-001")
    splitter = SemanticSplitterNodeParser(buffer_size=1, embed_model=embed_model)
    
    nodes = splitter.get_nodes_from_documents([Document(text=markdown_text)])
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    return VectorStoreIndex(nodes, storage_context=storage_context, embed_model=embed_model)

# --- Layer 3: Multi-Agent Workflow ---
def generate_report_section(index, topic):
    llm = GoogleGenAI(model="models/gemini-1.5-flash")
    query_engine = index.as_query_engine(llm=llm, similarity_top_k=5)
    
    data_tool = query_engine.as_query_tool(name="data_search", description="Search ESG metrics")
    agent = ReActAgent.from_tools([data_tool], llm=llm)
    
    prompt = f"Find 2025 data for {topic} and write a formal GRI-compliant report section with tables."
    return agent.chat(prompt).response

# --- Utility: Cleanup ---
def clear_all_data():
    folders = ['data', 'esg_db', 'output_md']
    for f in folders:
        if os.path.exists(f):
            shutil.rmtree(f)
        os.makedirs(f)