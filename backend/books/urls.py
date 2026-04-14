from django.urls import path
from .views import (
    BookListView, BookDetailView, BookRecommendView,
    ScrapeView, AskQuestionView, QAHistoryView, GenreListView
)

urlpatterns = [
    path('books/', BookListView.as_view(), name='book-list'),
    path('books/scrape/', ScrapeView.as_view(), name='book-scrape'),
    path('books/ask/', AskQuestionView.as_view(), name='book-ask'),
    path('books/qa-history/', QAHistoryView.as_view(), name='qa-history'),
    path('books/genres/', GenreListView.as_view(), name='genre-list'),
    path('books/<int:pk>/', BookDetailView.as_view(), name='book-detail'),
    path('books/<int:pk>/recommend/', BookRecommendView.as_view(), name='book-recommend'),
]
