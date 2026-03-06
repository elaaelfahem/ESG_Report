# ESG_Report: Multi-Agent ESG Reporting Tool

**ESG_Report** is an AI-powered, multi-agent full-stack application designed to analyze sustainability reports, extract Environmental, Social, and Governance (ESG) Key Performance Indicators (KPIs), detect potential greenwashing, and generate professional, actionable ESG reports and roadmaps.

## 🌟 Key Features

- **Automated Data Ingestion**: Seamlessly ingest and process sustainability reports from PDFs.
- **Advanced RAG Pipeline**: Uses LangChain, FAISS vector storage, and HuggingFace embeddings for accurate and reliable Retrieval-Augmented Generation.
- **Multi-Agent Architecture**: Employs local Ollama models through distinct agents (Agent A, Agent B, Agent C) to handle specific extraction, analysis, and validation tasks.
- **KPI Extraction**: Intelligently extracts structured ESG KPIs and formats them into well-structured JSON data.
- **Greenwashing Detection**: Analyzes reports for inconsistencies or repetitive AI filler to ensure data reliability and credibility.
- **Full-Stack Interface**: Features a modern Vite + React frontend coupled with a robust FastAPI backend.
- **Comprehensive Reporting**: Generates formatted markdown (`Final_ESG_Report.md`) and professional PDF reports.

## 🏗️ Project Structure

- `backend/`: FastAPI backend handling the core logic, API endpoints, and orchestrating the AI agents.
- `frontend/`: React + Vite frontend application for interacting with the tool.
- `data/` & `esg_db/`: Local storage for uploaded PDFs, extracted data, and vector stores.
- `services/`: Contains the logic for the different AI agents (`agent_a`, `agent_b`, `agent_c`).
- `vectorstore/`: FAISS index storage for semantic search.
- `reports/` & `output_md/`: Generated ESG reports.

## ⚙️ Tech Stack

- **Backend**: Python, FastAPI, LangChain, Uvicorn
- **AI/ML**: Ollama (local LLMs), HuggingFace Embeddings, FAISS
- **Frontend**: React, Vite, Tailwind CSS / Vanilla CSS
- **Data Processing**: pdfplumber, Pandas

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- Node.js & npm
- [Ollama](https://ollama.ai/) installed and running locally with the necessary models pulled.

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/elaaelfahem/ESG_Report.git
   cd ESG_Report
   ```

2. **Backend Setup:**
   ```bash
   # Create and activate a virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`

   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Frontend Setup:**
   ```bash
   cd frontend
   npm install
   ```

### Running the Application

1. **Start the Backend:**
   In the root directory with the virtual environment activated:
   ```bash
   uvicorn backend.main:app --reload
   ```

2. **Start the Frontend:**
   In the `frontend` directory:
   ```bash
   npm run dev
   ```

3. **Access the application:**
   Open your browser and navigate to the local URL provided by Vite (typically `http://localhost:5173`).

## 🤝 Contributing

Contributions to improve the report accuracy, agents' logic, or frontend design are welcome. Please ensure that you test your changes locally before submitting a pull request.
