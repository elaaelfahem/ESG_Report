import json
from langchain_text_splitters import RecursiveCharacterTextSplitter
from config import (
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    MIN_CHUNK_LENGTH,
    CHUNK_SEPARATORS,
    SKIP_DUPLICATE_CHUNKS,
    EXTRACTED_DOCS_FILE,
    CHUNKS_FILE,
    setup_logging,
)

logger = setup_logging(__name__)


def validate_chunk(chunk: dict) -> bool:
    """Validate chunk has required fields and minimum length."""
    return (
        "id" in chunk and
        "text" in chunk and
        len(chunk["text"]) >= MIN_CHUNK_LENGTH and
        "metadata" in chunk
    )


def is_duplicate_chunk(chunk_text: str, existing_chunks: list, threshold: float = 0.95) -> bool:
    """Simple duplicate detection by checking exact text match."""
    if not SKIP_DUPLICATE_CHUNKS:
        return False
    
    for existing_chunk in existing_chunks:
        if existing_chunk["text"] == chunk_text:
            logger.debug(f"Detected duplicate chunk (first {50} chars: {chunk_text[:50]}...)")
            return True
    return False


def chunk_page_documents(documents, chunk_size=None, overlap=None):
    """
    Chunk page documents with configuration and validation.
    
    Expects structure:
    [
        {
            "source": "file.pdf",
            "pages": [
                {"page": 1, "content": "..."},
                ...
            ]
        }
    ]
    """
    # Use config defaults if not provided
    chunk_size = chunk_size or CHUNK_SIZE
    overlap = overlap or CHUNK_OVERLAP
    
    if overlap >= chunk_size:
        raise ValueError(f"CHUNK_OVERLAP ({overlap}) must be < CHUNK_SIZE ({chunk_size})")
    
    all_chunks = []
    duplicates_skipped = 0
    short_chunks_skipped = 0
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap,
        separators=CHUNK_SEPARATORS
    )

    for doc in documents:
        source = doc["source"]

        for page_obj in doc.get("pages", []):
            page_num = page_obj["page"]
            text = page_obj.get("content", "") or ""

            if not text.strip():
                logger.debug(f"Skipping empty page {page_num} from {source}")
                continue

            page_chunks = text_splitter.split_text(text)

            for chunk_id, chunk_text in enumerate(page_chunks):
                # Check for duplicates
                if is_duplicate_chunk(chunk_text, all_chunks):
                    duplicates_skipped += 1
                    continue
                
                # Skip short chunks
                if len(chunk_text) < MIN_CHUNK_LENGTH:
                    logger.debug(f"Skipping short chunk ({len(chunk_text)} < {MIN_CHUNK_LENGTH} chars)")
                    short_chunks_skipped += 1
                    continue
                
                # Calculate approximate positions for metadata
                start_pos = text.find(chunk_text[:50]) if len(chunk_text) > 50 else text.find(chunk_text)
                end_pos = start_pos + len(chunk_text) if start_pos != -1 else -1

                chunk = {
                    "id": f"{source}::p{page_num}::c{chunk_id}",
                    "text": chunk_text,
                    "metadata": {
                        "source": source,
                        "page": page_num,
                        "chunk_id": chunk_id,
                        "start_pos": start_pos,
                        "end_pos": end_pos,
                        "citation": f"{source} (Page {page_num})"
                    }
                }
                
                # Validate chunk before adding
                if validate_chunk(chunk):
                    all_chunks.append(chunk)
                else:
                    logger.warning(f"Chunk validation failed: {chunk['id']}")

    logger.info(f"Chunking complete: {len(all_chunks)} valid chunks")
    if duplicates_skipped > 0:
        logger.info(f"Skipped {duplicates_skipped} duplicate chunks")
    if short_chunks_skipped > 0:
        logger.info(f"Skipped {short_chunks_skipped} short chunks")
    
    return all_chunks


def load_documents(input_file=None):
    """Load documents from JSON file (uses config default if not provided)."""
    input_file = input_file or EXTRACTED_DOCS_FILE
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            documents = json.load(f)
        logger.info(f"📂 Loaded {len(documents)} documents from {input_file}")
        return documents
    except FileNotFoundError:
        logger.error(f"Input file '{input_file}' not found")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in '{input_file}': {e}")
        raise


def save_chunks(chunks, output_file=None):
    """Save chunks to JSON file (uses config default if not provided)."""
    output_file = output_file or CHUNKS_FILE
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2, ensure_ascii=False)
    logger.info(f"💾 Saved {len(chunks)} chunks to {output_file}")


if __name__ == "__main__":
    try:
        logger.info("="*60)
        logger.info("TEXT CHUNKING STARTED")
        logger.info("="*60)
        
        documents = load_documents()

        logger.info(f"Chunking documents with size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP}...")
        chunks = chunk_page_documents(documents, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP)

        save_chunks(chunks)

        logger.info(f"\n{'='*60}")
        logger.info("CHUNKING SUMMARY")
        logger.info(f"{'='*60}")
        logger.info(f"Total documents: {len(documents)}")
        logger.info(f"Total chunks: {len(chunks)}")

        if documents:
            avg = len(chunks) / len(documents)
            logger.info(f"Average chunks per document: {avg:.1f}")

        logger.info(f"\n{'='*60}")
        logger.info("PREVIEW - First Chunk")
        logger.info(f"{'='*60}")

        if chunks:
            first = chunks[0]
            logger.info(f"ID: {first['id']}")
            logger.info(f"Source: {first['metadata']['source']}")
            logger.info(f"Page: {first['metadata']['page']}")
            logger.info(f"Length: {len(first['text'])} characters")
            logger.info(f"\nText Preview:\n{first['text'][:300]}...")
        
        logger.info("="*60)
        
    except Exception as e:
        logger.error(f"Chunking failed: {e}", exc_info=True)
        raise
