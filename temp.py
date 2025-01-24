from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import models
import numpy as np
from datetime import datetime
import json

# Models
class SpaceEmbeddingProgress(models.Model):
    emb_id = models.AutoField(primary_key=True)
    space_name = models.CharField(max_length=255, unique=True)
    embedding_status = models.CharField(max_length=50, choices=[('Completed', 'Completed'), ('Failed', 'Failed'), ('In-Progress', 'In-Progress')])
    total_pages_to_embed = models.IntegerField()
    current_embedding_page = models.IntegerField(default=0)
    embedding_completed_page_ids = models.JSONField(default=list)  # List of dicts with page_id and timestamp
    embedding_failed_page_ids = models.JSONField(default=list)    # List of dicts with page_id and timestamp
    embedding_message = models.TextField(null=True, blank=True)
    last_embedded_time = models.DateTimeField(auto_now=True)

class PageEmbedding(models.Model):
    chunk_id = models.AutoField(primary_key=True)
    page_id = models.IntegerField()
    space_name = models.ForeignKey(SpaceEmbeddingProgress, on_delete=models.CASCADE, related_name='page_embeddings')
    last_embedded_time = models.DateTimeField(auto_now=True)
    content = models.TextField()
    encoded_data = models.JSONField(default=dict)  # Simulated embedding data
    meta_data = models.JSONField(default=dict)
    type_of_data = models.CharField(max_length=100, null=True, blank=True)

# Dummy data for pages
dummy_pages = [
    {"page_id": 1, "content": "Page 1 content"},
    {"page_id": 2, "content": "Page 2 content"},
    {"page_id": 3, "content": "Page 3 content"},
    {"page_id": 4, "content": "Page 4 content"},
    {"page_id": 5, "content": "Page 5 content"},
]

# DRF-based API: Start Embedding
class StartEmbeddingAPIView(APIView):
    def post(self, request):
        try:
            space_name = request.data.get('space_name')
            force_embed = request.data.get('force_embed', False)

            if not space_name:
                return Response({'error': 'space_name is required'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                space = SpaceEmbeddingProgress.objects.get(space_name=space_name)

                if space.embedding_status == 'Completed' and not force_embed:
                    return Response({
                        'message': 'Embedding already completed',
                        'status': space.embedding_status,
                        'last_embedded_time': space.last_embedded_time
                    })

                if space.embedding_status == 'Failed' and not force_embed:
                    failed_pages = space.embedding_failed_page_ids
                    dummy_pages_to_embed = [page for page in dummy_pages if page['page_id'] in [p['page_id'] for p in failed_pages]]
                else:
                    dummy_pages_to_embed = dummy_pages

            except SpaceEmbeddingProgress.DoesNotExist:
                space = SpaceEmbeddingProgress.objects.create(
                    space_name=space_name,
                    embedding_status='In-Progress',
                    total_pages_to_embed=len(dummy_pages),
                )
                dummy_pages_to_embed = dummy_pages

            space.embedding_completed_page_ids = []
            space.embedding_failed_page_ids = []
            space.current_embedding_page = 0

            for page in dummy_pages_to_embed:
                page_id = page['page_id']
                content = page['content']

                encoded_data = {f"embedding_dim_{i}": np.random.rand() for i in range(5)}

                try:
                    PageEmbedding.objects.create(
                        page_id=page_id,
                        space_name=space,
                        content=content,
                        encoded_data=encoded_data,
                        meta_data={"source": "dummy"},
                        type_of_data="text",
                    )

                    space.embedding_completed_page_ids.append({"page_id": page_id, "time": str(datetime.now())})
                except Exception as e:
                    space.embedding_failed_page_ids.append({"page_id": page_id, "time": str(datetime.now())})
                    space.embedding_message = str(e)

                space.current_embedding_page += 1

            space.embedding_status = 'Failed' if space.embedding_failed_page_ids else 'Completed'
            space.save()

            return Response({'message': 'Embedding started', 'space_id': space.emb_id}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# DRF-based API: Polling Embedding Status
class PollEmbeddingStatusAPIView(APIView):
    def get(self, request):
        space_name = request.query_params.get('space_name')

        if not space_name:
            return Response({'error': 'space_name is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            space = SpaceEmbeddingProgress.objects.get(space_name=space_name)
            response = {
                'space_name': space.space_name,
                'embedding_status': space.embedding_status,
                'total_pages_to_embed': space.total_pages_to_embed,
                'current_embedding_page': space.current_embedding_page,
                'embedding_completed_page_ids': space.embedding_completed_page_ids,
                'embedding_failed_page_ids': space.embedding_failed_page_ids,
                'embedding_message': space.embedding_message,
                'last_embedded_time': space.last_embedded_time,
            }
            return Response(response, status=status.HTTP_200_OK)

        except SpaceEmbeddingProgress.DoesNotExist:
            return Response({'error': 'space_name not found'}, status=status.HTTP_404_NOT_FOUND)

# URLs
from django.urls import path

urlpatterns = [
    path('start-embedding/', StartEmbeddingAPIView.as_view(), name='start_embedding'),
    path('poll-embedding-status/', PollEmbeddingStatusAPIView.as_view(), name='poll_embedding_status'),
]
