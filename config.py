"""
Configuration for ESG Multi-Agent System
"""
import os
import torch
import logging

# ============================================================================
# PATHS & DIRECTORIES
# ============================================================================
DATA_FOLDER = "data"
OUTPUT_DIR = "output_md"
VECTORSTORE_PATH = "vectorstore"
REPORTS_DIR = "reports"
ES_DB_PATH = "esg_db"
LOGS_DIR = "logs"

# JSON intermediate files
EXTRACTED_DOCS_FILE = "extracted_documents_pages.json"
CHUNKS_FILE = "chunks.json"

# Create directories
for dir_path in [REPORTS_DIR, LOGS_DIR, OUTPUT_DIR, ES_DB_PATH]:
    os.makedirs(dir_path, exist_ok=True)

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================
LOG_LEVEL = logging.INFO
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FILE = os.path.join(LOGS_DIR, "esg_system.log")

# ============================================================================
# DATA INGESTION CONFIGURATION
# ============================================================================
# PDF extraction
EXTRACT_TABLES = True
TABLE_FORMAT = "markdown"  # or "plain", "html"
SKIP_EMPTY_PAGES = True
MIN_PAGE_LENGTH = 50  # chars

# File processing
PDF_EXTENSIONS = [".pdf"]
SKIP_PATTERNS = [".tmp", "~$", "__pycache__"]
MAX_PDFS_PER_RUN = None  # None = all, or set limit for testing

# ============================================================================
# CHUNKING CONFIGURATION
# ============================================================================
CHUNK_SIZE = 800
CHUNK_OVERLAP = 100
MIN_CHUNK_LENGTH = 50  # Reject chunks shorter than this
CHUNK_SEPARATORS = ["\n\n", "\n", " ", ""]
SKIP_DUPLICATE_CHUNKS = True
SIMILARITY_THRESHOLD = 0.95  # For duplicate detection

# ============================================================================
# EMBEDDING CONFIGURATION
# ============================================================================
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # Fast, lightweight
# EMBEDDING_MODEL = "sentence-transformers/all-mpnet-base-v2"  # Better quality, slower
# EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"  # Multilingual

EMBEDDING_DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
EMBEDDING_BATCH_SIZE = 32
NORMALIZE_EMBEDDINGS = True

# ============================================================================
# VECTORSTORE CONFIGURATION
# ============================================================================
VECTORSTORE_TYPE = "FAISS"  # or "Chroma", "Pinecone"
VECTORSTORE_ALLOW_REBUILD = True  # Overwrite existing vectorstore
VECTORSTORE_BACKUP = True  # Keep backup before rebuild
SIMILARITY_SEARCH_K = 5  # Default number of results
SIMILARITY_SCORE_THRESHOLD = 0.3  # Min relevance score to return

# ============================================================================
# LLM CONFIGURATION
# ============================================================================
LLM_MODEL = "llama3.2"  # Local Ollama model
# LLM_MODEL = "gpt-4"
# LLM_MODEL = "claude-3-sonnet-20240229"

LLM_TEMPERATURE = 0.1  # Low = deterministic, High = creative
LLM_MAX_TOKENS = 2048
LLM_TIMEOUT = 120  # seconds
LLM_RETRY_ATTEMPTS = 3
LLM_RETRY_DELAY = 5  # seconds

# ============================================================================
# AGENT A: KPI EXTRACTOR CONFIGURATION
# ============================================================================
AGENT_A_SEARCH_K = 5  # Number of documents to retrieve per KPI
AGENT_A_CONFIDENCE_THRESHOLD = 0.7  # Min confidence for returned KPIs
AGENT_A_CONTEXT_WINDOW = 2500  # Max chars of context per query

# ============================================================================
# AGENT B: COMPLIANCE MAPPER CONFIGURATION
# ============================================================================
AGENT_B_FRAMEWORK_PRIORITY = ["GRI", "SASB", "ESRS"]
AGENT_B_INCLUDE_GAPS = True  # Report missing KPIs per framework

# KPI Categories for Agent A to extract
KPI_CATEGORIES = [
    "Total electricity usage and energy consumption",
    "Renewable energy production and sources",
    "Greenhouse gas emissions (Scope 1, 2, 3) and carbon footprint",
    "Water withdrawal, consumption, and discharge",
    "Waste generation, recycling, and treatment",
    "Smart building area and implementation",
    "Transportation vehicles and emissions",
    "Sustainability budget and funding",
    "Campus area and green space coverage",
    "Student and staff population numbers"
]

# Compliance Frameworks for Agent B
FRAMEWORKS = {
    "GRI": {
        "name": "Global Reporting Initiative",
        "standards": {
            "GRI 302": "Energy - Total energy consumption, renewable energy percentage, energy intensity",
            "GRI 305": "Emissions - Direct (Scope 1) GHG emissions, Energy indirect (Scope 2) GHG emissions, Other indirect (Scope 3) GHG emissions",
            "GRI 303": "Water - Total water withdrawal by source, Total water consumption, Total water discharge by destination",
            "GRI 306": "Waste - Total weight of waste generated, Total weight of waste diverted from disposal, Total weight of waste directed to disposal"
        }
    },
    "SASB": {
        "name": "Sustainability Accounting Standards Board",
        "standards": {
            "Energy Management": "Total energy consumed, Percentage grid electricity, Percentage renewable energy",
            "GHG Emissions": "Gross global Scope 1 emissions, Gross global Scope 2 emissions, Discussion of long-term and short-term strategy",
            "Water Management": "Total water withdrawn, Total water consumed, Percentage in regions with high water stress",
            "Waste Management": "Amount of hazardous waste generated, Percentage recycled"
        }
    },
    "ESRS": {
        "name": "European Sustainability Reporting Standards",
        "standards": {
            "ESRS E1": "Climate Change - GHG emissions (Scope 1, 2, 3), Energy consumption and mix, Energy intensity",
            "ESRS E2": "Pollution - Emissions to air, Emissions to water, Emissions to soil, Substances of concern",
            "ESRS E3": "Water and Marine Resources - Water consumption, Water withdrawals, Water discharges",
            "ESRS E5": "Resource Use and Circular Economy - Resource inflows, Resource outflows, Waste"
        }
    }
}

# ============================================================================
# VALIDATION & QUALITY THRESHOLDS
# ============================================================================
VALIDATE_CHUNKS = True
VALIDATE_EMBEDDINGS = True
MIN_CHUNKS_REQUIRED = 10  # Minimum chunks to build vectorstore
WARN_IF_FEW_CHUNKS = 100  # Warning threshold

# ============================================================================
# OUTPUT FORMATS
# ============================================================================
OUTPUT_FORMATS = {
    "kpi_format": {
        "fields": ["metric", "value", "unit", "year", "source", "confidence"],
        "required": ["metric", "value"],
    },
    "compliance_format": {
        "fields": ["framework", "standard", "status", "kpis_covered", "gaps"],
        "required": ["framework", "standard"],
    },
    "report_format": ["json", "markdown", "pdf"],  # Supported formats
}

# JSON Schema for Agent A output (strict format)
AGENT_A_OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "kpis": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "metric": {"type": "string"},
                    "value": {"type": ["number", "string"]},
                    "unit": {"type": "string"},
                    "year": {"type": "integer"},
                    "source": {"type": "string"},
                    "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                },
                "required": ["metric", "value"],
            },
        },
    },
    "required": ["kpis"],
}

# ============================================================================
# ORGANIZATION INFO
# ============================================================================
ORGANIZATION = "University of Carthage"
REPORT_YEAR = "2024-2025"
ORGANIZATION_TYPE = "Higher Education Institution"  # For ESG context

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def setup_logging(name: str) -> logging.Logger:
    """Configure logging for a module."""
    logger = logging.getLogger(name)
    logger.setLevel(LOG_LEVEL)
    
    # File handler
    fh = logging.FileHandler(LOG_FILE)
    fh.setLevel(LOG_LEVEL)
    
    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(LOG_LEVEL)
    
    # Formatter
    formatter = logging.Formatter(LOG_FORMAT)
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    
    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger


def get_full_paths() -> dict:
    """Return absolute paths for all configured directories."""
    return {
        "data": os.path.abspath(DATA_FOLDER),
        "output": os.path.abspath(OUTPUT_DIR),
        "vectorstore": os.path.abspath(VECTORSTORE_PATH),
        "reports": os.path.abspath(REPORTS_DIR),
        "db": os.path.abspath(ES_DB_PATH),
        "logs": os.path.abspath(LOGS_DIR),
    }


def validate_config() -> bool:
    """Validate that all required configs are set and paths exist."""
    checks = [
        (os.path.isdir(DATA_FOLDER), f"Data folder '{DATA_FOLDER}' must exist"),
        (CHUNK_SIZE > 0, "CHUNK_SIZE must be > 0"),
        (CHUNK_OVERLAP < CHUNK_SIZE, "CHUNK_OVERLAP must be < CHUNK_SIZE"),
        (MIN_CHUNK_LENGTH > 0, "MIN_CHUNK_LENGTH must be > 0"),
        (0 <= AGENT_A_CONFIDENCE_THRESHOLD <= 1, "AGENT_A_CONFIDENCE_THRESHOLD must be 0-1"),
        (os.path.exists(LOGS_DIR), f"Logs directory '{LOGS_DIR}' must exist"),
    ]
    
    for check, msg in checks:
        if not check:
            raise ValueError(f"Config validation failed: {msg}")
    
    return True


def get_device_info() -> str:
    """Return current device configuration."""
    return f"Device: {EMBEDDING_DEVICE.upper()}, Model: {EMBEDDING_MODEL}, CUDA Available: {torch.cuda.is_available()}"


# ============================================================================
# ENVIRONMENT DETECTION
# ============================================================================
def is_production() -> bool:
    """Check if running in production mode."""
    return os.environ.get("ENV", "dev").lower() == "prod"


def is_debug() -> bool:
    """Check if debug mode is enabled."""
    return os.environ.get("DEBUG", "false").lower() == "true"