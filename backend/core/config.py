"""
Configuration for ESG Multi-Agent System (Backend)
"""
import os
import torch
import logging

# ============================================================================
# BASE PATH - All paths are relative to the project root (parent of backend/)
# ============================================================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ============================================================================
# PATHS & DIRECTORIES
# ============================================================================
DATA_FOLDER = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "output_md")
VECTORSTORE_PATH = os.path.join(BASE_DIR, "vectorstore")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
ES_DB_PATH = os.path.join(BASE_DIR, "esg_db")
LOGS_DIR = os.path.join(BASE_DIR, "logs")

# JSON intermediate files
EXTRACTED_DOCS_FILE = os.path.join(BASE_DIR, "extracted_documents_pages.json")
CHUNKS_FILE = os.path.join(BASE_DIR, "chunks.json")

# Create directories
for dir_path in [DATA_FOLDER, REPORTS_DIR, LOGS_DIR, OUTPUT_DIR, ES_DB_PATH]:
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
EXTRACT_TABLES = True
TABLE_FORMAT = "markdown"
SKIP_EMPTY_PAGES = True
MIN_PAGE_LENGTH = 50

PDF_EXTENSIONS = [".pdf"]
SKIP_PATTERNS = [".tmp", "~$", "__pycache__"]
MAX_PDFS_PER_RUN = None

# ============================================================================
# CHUNKING CONFIGURATION
# ============================================================================
CHUNK_SIZE = 800
CHUNK_OVERLAP = 100
MIN_CHUNK_LENGTH = 50
CHUNK_SEPARATORS = ["\n\n", "\n", " ", ""]
SKIP_DUPLICATE_CHUNKS = True
SIMILARITY_THRESHOLD = 0.95

# ============================================================================
# EMBEDDING CONFIGURATION
# ============================================================================
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
EMBEDDING_DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
EMBEDDING_BATCH_SIZE = 32
NORMALIZE_EMBEDDINGS = True

# ============================================================================
# VECTORSTORE CONFIGURATION
# ============================================================================
VECTORSTORE_TYPE = "FAISS"
VECTORSTORE_ALLOW_REBUILD = True
VECTORSTORE_BACKUP = True
SIMILARITY_SEARCH_K = 5
SIMILARITY_SCORE_THRESHOLD = 0.3

# ============================================================================
# LLM CONFIGURATION
# ============================================================================
LLM_MODEL = "llama3.2"
LLM_TEMPERATURE = 0.1
LLM_MAX_TOKENS = 2048
LLM_TIMEOUT = 120
LLM_RETRY_ATTEMPTS = 3
LLM_RETRY_DELAY = 5

# ============================================================================
# AGENT A: KPI EXTRACTOR CONFIGURATION
# ============================================================================
AGENT_A_SEARCH_K = 3
AGENT_A_CONFIDENCE_THRESHOLD = 0.7
AGENT_A_CONTEXT_WINDOW = 2500

# ============================================================================
# AGENT B: COMPLIANCE MAPPER CONFIGURATION
# ============================================================================
AGENT_B_FRAMEWORK_PRIORITY = ["GRI", "SASB", "ESRS"]
AGENT_B_INCLUDE_GAPS = True

# KPI Categories for Agent A
KPI_CATEGORIES = [
    "Electricity usage total energy consumption MWh kWh",
    "Renewable energy production sources percentage solar wind",
    "GHG emissions Scope 1 2 3 CO2 footprint",
    "Water withdrawal consumption discharge m3",
    "Waste weight recycling treatment disposal tons",
    "Smart building area implementation certifications",
    "Sustainability funding budget allocation",
    "Campus green space area hectares coverage",
    "Employee gender age minority diversity statistics",
    "Workplace health safety injury incidents",
    "Employee training hours per year average",
    "Board composition independence diversity",
    "Anti-corruption ethics policies training coverage",
    "Social community programs development count"
]

# Compliance Frameworks for Agent B
FRAMEWORKS = {
    "GRI": {
        "name": "Global Reporting Initiative",
        "standards": {
            "GRI 302/305": "Environmental - Energy & Emissions (Scope 1, 2, 3)",
            "GRI 303/306": "Environmental - Water & Waste management",
            "GRI 401/404": "Social - Employment, Diversity & Training",
            "GRI 403": "Social - Occupational Health and Safety",
            "GRI 205": "Governance - Anti-corruption and Ethics",
            "GRI 2-9": "Governance - Board composition and independence"
        }
    },
    "SASB": {
        "name": "Sustainability Accounting Standards Board",
        "standards": {
            "Environmental": "GHG Emissions, Energy & Water Management, Waste",
            "Social Capital": "Human Rights, Community Relations, Data Security",
            "Human Capital": "Employee Engagement, Diversity & Inclusion, Safety",
            "Leadership & Governance": "Business Ethics, Product Quality & Safety, Competitive Behavior"
        }
    },
    "ESRS": {
        "name": "European Sustainability Reporting Standards",
        "standards": {
            "ESRS E1-E5": "Environmental - Climate Change, Pollution, Water, Circular Economy",
            "ESRS S1": "Social - Own Workforce (Diversity, Working Conditions, Rights)",
            "ESRS G1": "Governance - Business Conduct, Ethics, and Internal Control"
        }
    }
}

# ============================================================================
# VALIDATION & QUALITY THRESHOLDS
# ============================================================================
VALIDATE_CHUNKS = True
VALIDATE_EMBEDDINGS = True
MIN_CHUNKS_REQUIRED = 10
WARN_IF_FEW_CHUNKS = 100

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
    "report_format": ["json", "markdown", "pdf"],
}

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
ORGANIZATION_TYPE = "Higher Education Institution"

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def setup_logging(name: str) -> logging.Logger:
    """Configure logging for a module."""
    logger = logging.getLogger(name)
    logger.setLevel(LOG_LEVEL)
    
    # Avoid duplicate handlers
    if not logger.handlers:
        fh = logging.FileHandler(LOG_FILE)
        fh.setLevel(LOG_LEVEL)
        
        ch = logging.StreamHandler()
        ch.setLevel(LOG_LEVEL)
        
        formatter = logging.Formatter(LOG_FORMAT)
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)
        
        logger.addHandler(fh)
        logger.addHandler(ch)
    
    return logger


def get_full_paths() -> dict:
    return {
        "data": os.path.abspath(DATA_FOLDER),
        "output": os.path.abspath(OUTPUT_DIR),
        "vectorstore": os.path.abspath(VECTORSTORE_PATH),
        "reports": os.path.abspath(REPORTS_DIR),
        "db": os.path.abspath(ES_DB_PATH),
        "logs": os.path.abspath(LOGS_DIR),
    }


def validate_config() -> bool:
    checks = [
        (os.path.isdir(DATA_FOLDER), f"Data folder '{DATA_FOLDER}' must exist"),
        (CHUNK_SIZE > 0, "CHUNK_SIZE must be > 0"),
        (CHUNK_OVERLAP < CHUNK_SIZE, "CHUNK_OVERLAP must be < CHUNK_SIZE"),
        (MIN_CHUNK_LENGTH > 0, "MIN_CHUNK_LENGTH must be > 0"),
        (0 <= AGENT_A_CONFIDENCE_THRESHOLD <= 1, "AGENT_A_CONFIDENCE_THRESHOLD must be 0-1"),
    ]
    
    for check, msg in checks:
        if not check:
            raise ValueError(f"Config validation failed: {msg}")
    
    return True


def get_device_info() -> str:
    return f"Device: {EMBEDDING_DEVICE.upper()}, Model: {EMBEDDING_MODEL}, CUDA Available: {torch.cuda.is_available()}"
