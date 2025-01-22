from django.db import models
import json

class PageInfo(models.Model):
    page_id = models.IntegerField(primary_key=True)  # Unique identifier for the page
    confluence_last_modified = models.DateTimeField()  # Last modified time fetched from Confluence
    last_embedded_time = models.DateTimeField(null=True, blank=True)  # Last time the embeddings were updated
    embedding_status = models.CharField(
        max_length=50,
        choices=[  # Enum-like choices for status
            ('embedding_in_progress', 'Embedding in Progress'),
            ('embedding_completed', 'Embedding Completed'),
            ('embedding_failed', 'Embedding Failed'),
        ],
        default='embedding_completed',  # Default is 'embedding_completed'
    )
    metadata = models.JSONField(default=dict)  # Additional metadata about the page (optional)

    def __str__(self):
        return f"Page ID: {self.page_id}, Status: {self.embedding_status}"

    class Meta:
        db_table = 'page_info'  # Table name in the database


from django.db import models
import json

class PageChunks(models.Model):
    chunk_id = models.AutoField(primary_key=True)  # Auto-increment unique identifier for each chunk
    page_id = models.ForeignKey(PageInfo, on_delete=models.CASCADE, related_name='chunks')  # Foreign key to PageInfo
    chunk_content = models.TextField()  # The actual content of the chunk (either table or text)
    is_table = models.BooleanField()  # Boolean to indicate whether the chunk is a table
    header = models.TextField(null=True, blank=True)  # Optional markdown header for the chunk
    metadata = models.JSONField(default=dict)  # Optional metadata for the chunk

    def __str__(self):
        return f"Chunk ID: {self.chunk_id}, Page ID: {self.page_id}, Is Table: {self.is_table}"

    class Meta:
        db_table = 'page_chunks'  # Table name in the database
