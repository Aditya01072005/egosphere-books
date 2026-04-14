"""
All REST API views for the books application.
GET  /api/books/              - List all books
GET  /api/books/<id>/         - Book detail
GET  /api/books/<id>/recommend/ - Related book recommendations
POST /api/books/scrape/       - Trigger scraping
POST /api/books/ask/          - RAG Q&A
GET  /api/books/qa-history/   - Past Q&A sessions
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from .models import Book, QAHistory
from .serializers import (
    BookListSerializer, BookDetailSerializer,
    QAHistorySerializer, AskQuestionSerializer, ScrapeSerializer
)
from ai.insights import get_recommendations
from ai.rag import answer_question


class BookListView(APIView):
    """GET /api/books/ — returns paginated list of all books."""

    def get(self, request):
        books = Book.objects.all()

        # Optional filters
        genre = request.query_params.get('genre')
        search = request.query_params.get('search')
        if genre:
            books = books.filter(genre__icontains=genre)
        if search:
            books = books.filter(title__icontains=search)

        serializer = BookListSerializer(books, many=True)
        return Response({
            "count": books.count(),
            "books": serializer.data
        })


class BookDetailView(APIView):
    """GET /api/books/<id>/ — returns full book details including AI insights."""

    def get(self, request, pk):
        book = get_object_or_404(Book, pk=pk)
        serializer = BookDetailSerializer(book)
        return Response(serializer.data)


class BookRecommendView(APIView):
    """GET /api/books/<id>/recommend/ — returns related book recommendations."""

    def get(self, request, pk):
        book = get_object_or_404(Book, pk=pk)
        all_books = Book.objects.all()
        recommended = get_recommendations(book, all_books, top_n=5)
        serializer = BookListSerializer(recommended, many=True)
        return Response({
            "book": book.title,
            "recommendations": serializer.data
        })


class ScrapeView(APIView):
    """
    POST /api/books/scrape/
    Triggers the Selenium scraper to collect books from books.toscrape.com.
    Body: { "num_pages": 5 }
    """

    def post(self, request):
        serializer = ScrapeSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        num_pages = serializer.validated_data['num_pages']

        try:
            # Import here to avoid loading Selenium at startup
            from scraper.scrape_books import scrape_books
            result = scrape_books(num_pages=num_pages)
            return Response({
                "message": "Scraping completed successfully.",
                "scraped": result['scraped'],
                "new_books_added": result['new']
            })
        except Exception as e:
            return Response(
                {"error": f"Scraping failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AskQuestionView(APIView):
    """
    POST /api/books/ask/
    RAG pipeline endpoint.
    Body: { "question": "...", "book_id": null }
    Caches identical questions to avoid repeated LLM calls.
    """

    def post(self, request):
        serializer = AskQuestionSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        question = serializer.validated_data['question']
        book_id = serializer.validated_data.get('book_id')

        # Cache check — return existing answer if same question was asked before
        cached = QAHistory.objects.filter(question__iexact=question).first()
        if cached and not book_id:
            return Response({
                "question": question,
                "answer": cached.answer,
                "sources": cached.sources,
                "cached": True
            })

        # Run RAG pipeline
        result = answer_question(question, book_id=book_id)

        # Save to history (cache)
        QAHistory.objects.create(
            question=question,
            answer=result['answer'],
            sources=result['sources']
        )

        return Response({
            "question": question,
            "answer": result['answer'],
            "sources": result['sources'],
            "cached": False
        })


class QAHistoryView(APIView):
    """GET /api/books/qa-history/ — returns past Q&A sessions."""

    def get(self, request):
        history = QAHistory.objects.all()[:50]
        serializer = QAHistorySerializer(history, many=True)
        return Response(serializer.data)


class GenreListView(APIView):
    """GET /api/books/genres/ — returns all unique genres."""

    def get(self, request):
        genres = Book.objects.values_list('genre', flat=True).distinct()
        genres = [g for g in genres if g]
        return Response({"genres": sorted(genres)})
