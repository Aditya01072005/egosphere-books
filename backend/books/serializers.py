from rest_framework import serializers
from .models import Book, BookChunk, QAHistory


class BookChunkSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookChunk
        fields = ['id', 'chunk_index', 'content']


class BookListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing books."""
    class Meta:
        model = Book
        fields = [
            'id', 'title', 'author', 'rating', 'num_reviews',
            'genre', 'price', 'availability', 'book_url',
            'cover_image_url', 'ai_genre', 'ai_sentiment', 'created_at'
        ]


class BookDetailSerializer(serializers.ModelSerializer):
    """Full serializer including AI fields and chunks."""
    chunks = BookChunkSerializer(many=True, read_only=True)

    class Meta:
        model = Book
        fields = '__all__'


class QAHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = QAHistory
        fields = ['id', 'question', 'answer', 'sources', 'created_at']


class AskQuestionSerializer(serializers.Serializer):
    question = serializers.CharField(max_length=1000)
    book_id = serializers.IntegerField(required=False, allow_null=True)


class ScrapeSerializer(serializers.Serializer):
    num_pages = serializers.IntegerField(default=5, min_value=1, max_value=50)
