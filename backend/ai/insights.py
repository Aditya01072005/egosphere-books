"""
AI Insight Generation using LM Studio (local LLM via OpenAI-compatible API).
Generates: Summary, Genre Classification, Sentiment Analysis.
Includes caching — skips re-generation if already processed.
"""
import json
from openai import OpenAI
from django.conf import settings


def get_lm_client():
    """Returns an OpenAI client pointed at LM Studio's local server."""
    import httpx
    return OpenAI(
        base_url=settings.LM_STUDIO_BASE_URL,
        api_key="lm-studio",
        http_client=httpx.Client()
    )


def _call_llm(prompt, max_tokens=400):
    """Generic LLM call with error handling."""
    try:
        client = get_lm_client()
        response = client.chat.completions.create(
            model=settings.LM_STUDIO_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=0.3
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"AI unavailable: {str(e)}"


def generate_summary(book):
    """Generates a 3-4 sentence summary of the book."""
    prompt = (
        f"Write a concise 3-4 sentence summary for the book titled '{book.title}'. "
        f"Description: {book.description or 'Not available'}. "
        f"Genre: {book.genre or 'Unknown'}. "
        "Focus on what the book is about and who would enjoy it."
    )
    return _call_llm(prompt, max_tokens=200)


def classify_genre(book):
    """Predicts the genre based on title and description."""
    prompt = (
        f"Classify the genre of this book in 1-3 words only.\n"
        f"Title: {book.title}\n"
        f"Description: {book.description or 'Not available'}\n"
        f"Current genre tag: {book.genre or 'Unknown'}\n"
        "Reply with only the genre label, nothing else."
    )
    return _call_llm(prompt, max_tokens=20)


def analyze_sentiment(book):
    """Analyzes the sentiment/tone of the book description."""
    prompt = (
        f"Analyze the sentiment/tone of this book description in one word "
        f"(e.g. Positive, Negative, Neutral, Dark, Uplifting, Mysterious).\n"
        f"Title: {book.title}\n"
        f"Description: {book.description or 'Not available'}\n"
        "Reply with only one word."
    )
    return _call_llm(prompt, max_tokens=10)


def generate_all_insights(book):
    """
    Generates all AI insights for a book.
    Skips if already processed (caching via ai_processed flag).
    """
    if book.ai_processed:
        return  # Already cached, skip LLM calls

    book.ai_summary = generate_summary(book)
    book.ai_genre = classify_genre(book)
    book.ai_sentiment = analyze_sentiment(book)
    book.ai_processed = True
    book.save(update_fields=['ai_summary', 'ai_genre', 'ai_sentiment', 'ai_processed'])


def get_recommendations(book, all_books, top_n=5):
    """
    Recommendation logic: finds books with similar genre or AI genre.
    Falls back to same scraped genre category.
    """
    candidates = all_books.exclude(id=book.id)

    # Match by AI genre first
    if book.ai_genre:
        genre_matches = candidates.filter(ai_genre__icontains=book.ai_genre.split()[0])
        if genre_matches.count() >= top_n:
            return genre_matches[:top_n]

    # Fallback: match by scraped genre tag
    if book.genre:
        genre_matches = candidates.filter(genre__icontains=book.genre)
        if genre_matches.exists():
            return genre_matches[:top_n]

    # Final fallback: top-rated books
    return candidates.order_by('-rating')[:top_n]
