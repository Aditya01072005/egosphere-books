"""
Handles embedding generation and ChromaDB vector storage.
Uses sentence-transformers for local embeddings (no API key needed).
"""
import os
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from django.conf import settings

# Load once at module level to avoid reloading on every call
_model = None
_chroma_client = None
_collection = None


def get_embedding_model():
    global _model
    if _model is None:
        _model = SentenceTransformer('all-MiniLM-L6-v2')
    return _model


def get_chroma_collection():
    global _chroma_client, _collection
    if _collection is None:
        persist_dir = getattr(settings, 'CHROMA_PERSIST_DIR', './vector_store')
        os.makedirs(persist_dir, exist_ok=True)
        _chroma_client = chromadb.PersistentClient(path=persist_dir)
        _collection = _chroma_client.get_or_create_collection(
            name="book_chunks",
            metadata={"hnsw:space": "cosine"}
        )
    return _collection


def chunk_text(text, chunk_size=300, overlap=50):
    """
    Smart chunking: splits text into overlapping word windows.
    Overlap ensures context is not lost at chunk boundaries.
    """
    words = text.split()
    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk = ' '.join(words[start:end])
        chunks.append(chunk)
        start += chunk_size - overlap  # sliding window with overlap
    return chunks


def embed_and_store_book(book):
    """
    Chunks a book's text content, generates embeddings,
    and stores them in ChromaDB. Also saves chunks to MySQL via BookChunk model.
    """
    from books.models import BookChunk

    # Combine all text fields for richer context
    full_text = f"{book.title}. {book.description} Genre: {book.genre}."
    full_text = full_text.strip()

    if not full_text or len(full_text) < 20:
        return

    chunks = chunk_text(full_text)
    model = get_embedding_model()
    collection = get_chroma_collection()

    # Remove old chunks for this book (re-processing case)
    BookChunk.objects.filter(book=book).delete()
    existing_ids = [f"book_{book.id}_chunk_{i}" for i in range(len(chunks))]
    try:
        collection.delete(ids=existing_ids)
    except Exception:
        pass

    embeddings = model.encode(chunks, show_progress_bar=False).tolist()

    chroma_ids = []
    documents = []
    metadatas = []
    db_chunks = []

    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        chroma_id = f"book_{book.id}_chunk_{i}"
        chroma_ids.append(chroma_id)
        documents.append(chunk)
        metadatas.append({
            "book_id": str(book.id),
            "book_title": book.title,
            "chunk_index": i
        })
        db_chunks.append(BookChunk(
            book=book,
            chunk_index=i,
            content=chunk,
            chroma_id=chroma_id
        ))

    # Batch upsert into ChromaDB
    collection.upsert(
        ids=chroma_ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas
    )

    # Batch insert into MySQL
    BookChunk.objects.bulk_create(db_chunks)


def similarity_search(query, n_results=5):
    """
    Embeds the query and retrieves the top-n most similar chunks from ChromaDB.
    Returns list of dicts with content, book_title, book_id.
    """
    model = get_embedding_model()
    collection = get_chroma_collection()

    query_embedding = model.encode([query], show_progress_bar=False).tolist()

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=n_results,
        include=["documents", "metadatas", "distances"]
    )

    hits = []
    if results and results['documents']:
        for doc, meta, dist in zip(
            results['documents'][0],
            results['metadatas'][0],
            results['distances'][0]
        ):
            hits.append({
                "content": doc,
                "book_title": meta.get("book_title", ""),
                "book_id": meta.get("book_id", ""),
                "score": round(1 - dist, 4)  # cosine similarity
            })
    return hits
