from django.contrib import admin
from .models import Book, BookChunk, QAHistory


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'rating', 'genre', 'ai_processed', 'created_at']
    list_filter = ['genre', 'ai_processed']
    search_fields = ['title', 'author']


@admin.register(BookChunk)
class BookChunkAdmin(admin.ModelAdmin):
    list_display = ['book', 'chunk_index']
    list_filter = ['book']


@admin.register(QAHistory)
class QAHistoryAdmin(admin.ModelAdmin):
    list_display = ['question', 'created_at']
