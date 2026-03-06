import os
import json
import shutil
from typing import List, Dict, Any
from datetime import datetime

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

from config import (
    EMBEDDING_MODEL,
    EMBEDDING_DEVICE,
    EMBEDDING_BATCH_SIZE,
    NORMALIZE_EMBEDDINGS,
    VECTORSTORE_PATH,
    VECTORSTORE_ALLOW_REBUILD,
    VECTORSTORE_BACKUP,
    SIMILARITY_SEARCH_K,
    SIMILARITY_SCORE_THRESHOLD,
    MIN_CHUNKS_REQUIRED,
    CHUNKS_FILE,
    setup_logging,
    validate_config,
    get_device_info,
)

logger = setup_logging(__name__)


def load_chunks(input_file: str = None) -> List[Dict[str, Any]]:
    """Load chunks from JSON file with validation."""
    input_file = input_file or CHUNKS_FILE
    
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            chunks = json.load(f)
        
        if not chunks:
            raise ValueError(f"No chunks found in {input_file}")
        
        if len(chunks) < MIN_CHUNKS_REQUIRED:
            logger.warning(f"Only {len(chunks)} chunks loaded (minimum recommended: {MIN_CHUNKS_REQUIRED})")
        
        logger.info(f"📂 Loaded {len(chunks)} chunks from {input_file}")
        return chunks
    
    except FileNotFoundError:
        logger.error(f"Chunk file '{input_file}' not found")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in '{input_file}': {e}")
        raise


def build_embeddings_model(model_name: str = None, device: str = None) -> HuggingFaceEmbeddings:
    """Create embeddings model with consistent settings."""
    model_name = model_name or EMBEDDING_MODEL
    device = device or EMBEDDING_DEVICE
    
    logger.info(f"Loading embedding model: {model_name}")
    logger.info(f"Using device: {device}")
    
    return HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs={"device": device},
        encode_kwargs={"normalize_embeddings": NORMALIZE_EMBEDDINGS},
    )


def create_vectorstore(
    chunks: List[Dict[str, Any]],
    model_name: str = None,
    device: str = None,
) -> FAISS:
    """
    Convert text chunks into embeddings and create a FAISS vector store.
    Expects chunk format:
      {"id": "...", "text": "...", "metadata": {...}}
    
    Supports batch processing for large chunk sets.
    """
    model_name = model_name or EMBEDDING_MODEL
    device = device or EMBEDDING_DEVICE
    
    logger.info(f"\n🧠 Creating embeddings using {model_name} on {device}...")
    logger.info(f"   Processing {len(chunks)} chunks...")

    # Extract texts, metadatas, and ids
    texts = [c["text"] for c in chunks]
    metadatas = [c["metadata"] for c in chunks]
    ids = [c["id"] for c in chunks]

    embeddings = build_embeddings_model(model_name=model_name, device=device)

    logger.info("   Building FAISS vector store...")
    
    # Process in batches if chunks are large
    if len(chunks) > 1000:
        logger.info(f"   Using batch processing (batch size: {EMBEDDING_BATCH_SIZE})")
        # Create vectorstore with batch processing
        vectorstore = FAISS.from_texts(
            texts=texts,
            embedding=embeddings,
            metadatas=metadatas,
            ids=ids,
        )
    else:
        # Single batch for smaller datasets
        vectorstore = FAISS.from_texts(
            texts=texts,
            embedding=embeddings,
            metadatas=metadatas,
            ids=ids,
        )

    logger.info("✓ Vector store created successfully!")
    return vectorstore


def save_vectorstore(vectorstore: FAISS, output_dir: str = None) -> None:
    """Save the vector store to disk with optional backup."""
    output_dir = output_dir or VECTORSTORE_PATH
    
    # Backup existing vectorstore if configured
    if os.path.exists(output_dir) and VECTORSTORE_BACKUP:
        backup_dir = f"{output_dir}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        logger.info(f"Creating backup: {backup_dir}")
        shutil.copytree(output_dir, backup_dir)
        logger.info(f"✓ Backup created: {backup_dir}")
    
    os.makedirs(output_dir, exist_ok=True)
    vectorstore.save_local(output_dir)
    logger.info(f"💾 Vector store saved to '{output_dir}/'")


def load_vectorstore(
    vectorstore_dir: str = None,
    model_name: str = None,
    device: str = None,
) -> FAISS:
    """Load a previously saved vector store."""
    vectorstore_dir = vectorstore_dir or VECTORSTORE_PATH
    model_name = model_name or EMBEDDING_MODEL
    device = device or EMBEDDING_DEVICE
    
    if not os.path.exists(vectorstore_dir):
        logger.error(f"Vectorstore directory '{vectorstore_dir}' not found")
        raise FileNotFoundError(f"Vectorstore not found at {vectorstore_dir}")
    
    embeddings = build_embeddings_model(model_name=model_name, device=device)
    
    try:
        vectorstore = FAISS.load_local(
            vectorstore_dir,
            embeddings,
            allow_dangerous_deserialization=True,
        )
        logger.info(f"📂 Vector store loaded from '{vectorstore_dir}/'")
        return vectorstore
    except Exception as e:
        logger.error(f"Failed to load vectorstore from '{vectorstore_dir}': {e}", exc_info=True)
        raise


def test_retrieval(vectorstore: FAISS, query: str, k: int = None) -> None:
    """Test the vector store with a sample query."""
    k = k or SIMILARITY_SEARCH_K
    
    logger.info(f"\n🔍 Query: {query}")
    logger.info("=" * 80)

    results = vectorstore.similarity_search_with_scores(query, k=k)

    for i, (doc, score) in enumerate(results, 1):
        md = doc.metadata or {}
        source = md.get("source", "unknown")
        page = md.get("page", "unknown")
        chunk_id = md.get("chunk_id", "unknown")
        citation = md.get("citation", f"{source} (Page {page})")

        # Skip results below threshold
        if score < SIMILARITY_SCORE_THRESHOLD:
            logger.debug(f"Skipping result {i} (score {score:.4f} < threshold {SIMILARITY_SCORE_THRESHOLD})")
            continue

        logger.info(f"\n[Result {i}] Score: {score:.4f}")
        logger.info(f"Source:   {source}")
        logger.info(f"Page:     {page}")
        logger.info(f"Chunk ID: {chunk_id}")
        logger.info(f"Citation: {citation}")
        logger.info("\nContent preview:")
        logger.info(doc.page_content[:400].replace("\n", " ") + "...")
        logger.info("-" * 80)


if __name__ == "__main__":
    try:
        logger.info("=" * 80)
        logger.info("CREATING EMBEDDINGS FROM CHUNKS (FAISS)")
        logger.info("=" * 80)
        logger.info(get_device_info())
        
        # Validate configuration
        validate_config()

        # Load chunks
        chunks = load_chunks()

        # Create vector store
        vectorstore = create_vectorstore(
            chunks,
            model_name=EMBEDDING_MODEL,
            device=EMBEDDING_DEVICE,
        )

        # Check if we should rebuild (backup existing first)
        if os.path.exists(VECTORSTORE_PATH) and not VECTORSTORE_ALLOW_REBUILD:
            logger.warning(f"Vectorstore already exists at '{VECTORSTORE_PATH}'")
            logger.warning("Set VECTORSTORE_ALLOW_REBUILD=True to overwrite")
        else:
            # Save vector store
            save_vectorstore(vectorstore, VECTORSTORE_PATH)

        # Test retrieval
        logger.info("\nTESTING RETRIEVAL")
        logger.info("=" * 80)
        test_queries = [
            "electricity usage",
            "renewable energy",
            "greenhouse gas emissions",
            "water consumption",
            "Scope 1 emissions",
            "Scope 2 emissions",
        ]

        for q in test_queries:
            test_retrieval(vectorstore, q, k=SIMILARITY_SEARCH_K)

        logger.info("\n✅ EMBEDDINGS COMPLETE!")
        logger.info("=" * 80)
        
    except Exception as e:
        logger.error(f"Embedding pipeline failed: {e}", exc_info=True)
        raise
