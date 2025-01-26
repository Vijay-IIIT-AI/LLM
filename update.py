import threading
import time
from datetime import datetime
import numpy as np
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import SpaceEmbeddingProgress, PageEmbedding


# Function to generate pages (replace with actual scraping logic)
def generate_pages(space, total_pages=None):
    """
    Generate pages with content. This simulates a page generation process.
    total_pages defaults to space.total_pages_to_embed if not provided.
    """
    if total_pages is None:
        total_pages = space.total_pages_to_embed  # Use the space's total_pages_to_embed value

    pages = []
    for i in range(total_pages):
        time.sleep(5)  # Simulate page generation delay (e.g., scraping)
        pages.append({"page_id": i + 1, "content": f"Page {i + 1} content"})
    
    return pages


# Function to simulate embedding pages
def embed_pages_in_background(space_id, pages_to_embed):
    """
    Embed pages and update the database.
    """
    space = get_object_or_404(SpaceEmbeddingProgress, emb_id=space_id)
    space.embedding_status = 'In-Progress'
    space.save()

    for page in pages_to_embed:
        page_id = page['page_id']
        content = page['content']
        encoded_data = {f"embedding_dim_{i}": np.random.rand() for i in range(5)}  # Simulate embedding data

        try:
            # Check if a PageEmbedding entry exists; if yes, update it
            page_embedding, created = PageEmbedding.objects.update_or_create(
                page_id=page_id,
                space_name=space,
                defaults={
                    'content': content,
                    'encoded_data': encoded_data,
                    'meta_data': {"source": "scraped"},
                    'type_of_data': "text"
                }
            )
            if created:
                space.embedding_completed_page_ids.append({"page_id": page_id, "time": str(datetime.now())})
            else:
                space.embedding_updated_page_ids.append({"page_id": page_id, "time": str(datetime.now())})

        except Exception as e:
            space.embedding_failed_page_ids.append({"page_id": page_id, "time": str(datetime.now())})
            space.embedding_message = str(e)

        space.current_embedding_page += 1
        space.save()

    # Mark the space status as completed if no failures occurred
    space.embedding_status = 'Completed' if not space.embedding_failed_page_ids else 'Failed'
    space.save()


# API View: Start Embedding
class StartEmbeddingAPIView(APIView):
    def post(self, request):
        try:
            space_name = request.data.get('space_name')
            force_embed = request.data.get('force_embed', False)

            if not space_name:
                return Response({'error': 'space_name is required'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                # Check if space already exists or needs to be created
                space, created = SpaceEmbeddingProgress.objects.get_or_create(
                    space_name=space_name,
                    defaults={
                        'embedding_status': 'In-Progress',
                        'total_pages_to_embed': 5  # Example total pages
                    }
                )

                if space.embedding_status == 'Completed' and not force_embed:
                    return Response({
                        'message': 'Embedding already completed',
                        'status': space.embedding_status,
                        'last_embedded_time': space.last_embedded_time
                    })

                # Generate pages in the background using threading
                def background_task():
                    pages_to_embed = generate_pages(space)
                    embed_pages_in_background(space.emb_id, pages_to_embed)

                embedding_thread = threading.Thread(target=background_task)
                embedding_thread.start()

                return Response({'message': 'Embedding started in background', 'space_id': space.emb_id}, status=status.HTTP_200_OK)

            except SpaceEmbeddingProgress.DoesNotExist:
                return Response({'error': 'Failed to create or retrieve space'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
