from django.db import models


class Book(models.Model):
    title = models.CharField(max_length=500)
    author = models.CharField(max_length=300, blank=True, default='Unknown')
    rating = models.FloatField(null=True, blank=True)
    num_reviews = models.IntegerField(null=True, blank=True)
    description = models.TextField(blank=True, default='')
    genre = models.CharField(max_length=200, blank=True, default='')
    price = models.CharField(max_length=50, blank=True, default='')
    availability = models.CharField(max_length=100, blank=True, default='')
    book_url = models.URLField(max_length=255, unique=True)
    cover_image_url = models.URLField(max_length=500, blank=True, default='')

    # AI-generated fields
    ai_summary = models.TextField(blank=True, default='')
    ai_genre = models.CharField(max_length=200, blank=True, default='')
    ai_sentiment = models.CharField(max_length=100, blank=True, default='')

    # Cache flag — avoid re-generating AI insights
    ai_processed = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class BookChunk(models.Model):
    """Stores text chunks of a book for RAG pipeline."""
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='chunks')
    chunk_index = models.IntegerField()
    content = models.TextField()
    # ChromaDB document ID for this chunk
    chroma_id = models.CharField(max_length=200, unique=True)

    class Meta:
        ordering = ['chunk_index']

    def __str__(self):
        return f"{self.book.title} - Chunk {self.chunk_index}"


class QAHistory(models.Model):
    """Stores question-answer history for caching and display."""
    question = models.TextField()
    answer = models.TextField()
    sources = models.JSONField(default=list)   # list of book titles used as context
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.question[:80]
