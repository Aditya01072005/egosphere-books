"""
RAG (Retrieval-Augmented Generation) Pipeline.
Steps:
1. Embed the user question
2. Similarity search across book chunks in ChromaDB
3. Build context from top chunks
4. Send context + question to LM Studio
5. Return answer with source citations
"""
from .embeddings import similarity_search
from .insights import get_lm_client
from django.conf import settings


def answer_question(question, book_id=None, n_chunks=5):
    """
    Full RAG pipeline.
    - question: user's question string
    - book_id: optional, restrict search to a specific book
    - n_chunks: number of chunks to retrieve
    Returns dict with 'answer' and 'sources'.
    """
    # Step 1 & 2: Embed question + similarity search
    hits = similarity_search(question, n_results=n_chunks)

    # Filter by book_id if provided
    if book_id:
        hits = [h for h in hits if h['book_id'] == str(book_id)]

    if not hits:
        return {
            "answer": "I couldn't find relevant information in the book database to answer your question.",
            "sources": []
        }

    # Step 3: Build context from retrieved chunks
    context_parts = []
    sources = []
    seen_books = set()

    for hit in hits:
        context_parts.append(f"[From '{hit['book_title']}']: {hit['content']}")
        if hit['book_title'] not in seen_books:
            sources.append({
                "book_title": hit['book_title'],
                "book_id": hit['book_id'],
                "relevance_score": hit['score']
            })
            seen_books.add(hit['book_title'])

    context = "\n\n".join(context_parts)

    # Step 4: Construct prompt and call LLM
    prompt = (
        "You are a helpful book assistant. Use the following book excerpts to answer the question.\n"
        "Always cite which book(s) your answer comes from.\n\n"
        f"Context:\n{context}\n\n"
        f"Question: {question}\n\n"
        "Answer:"
    )

    try:
        client = get_lm_client()
        response = client.chat.completions.create(
            model=settings.LM_STUDIO_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.3
        )
        answer = response.choices[0].message.content.strip()
    except Exception as e:
        answer = f"LM Studio is not running or unavailable. Error: {str(e)}"

    return {
        "answer": answer,
        "sources": sources
    }
