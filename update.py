import threading
import time
import random
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

# Dummy SpaceEmbeddingProgress object for simulation
class SpaceEmbeddingProgress:
    def __init__(self, space_name, embedding_status="Not Started", total_pages_to_embed=0):
        self.space_name = space_name
        self.embedding_status = embedding_status
        self.total_pages_to_embed = total_pages_to_embed
        self.current_embedding_page = 0
        self.embedding_completed_page_ids = []
        self.embedding_failed_page_ids = []
        self.embedding_message = None
        self.last_embedded_time = None

# Simulated database for spaces
space_db = {}

# Simulated PageEmbedding database
page_embeddings = []


def generate_pages(space):
    """
    Simulate a time-consuming page generation process (e.g., scraping).
    Generates a random number of pages, with a 5-second delay for each page.
    Replace this logic with your actual scraping or page retrieval code.
    """
    n_pages_max = 10  # Maximum number of pages to generate
    n_pages = random.randint(1, n_pages_max)  # Randomly decide the number of pages
    generated_pages = []

    for i in range(1, n_pages + 1):
        time.sleep(5)  # Simulate a 5-second delay per page generation
        generated_pages.append({
            "page_id": i,
            "content": f"Page {i} content generated for space: {space.space_name}"
        })

    return generated_pages


def embed_pages_in_background(space, pages_to_embed):
    """
    Function to simulate embedding pages in the background.
    """
    try:
        for page in pages_to_embed:
            page_id = page["page_id"]
            content = page["content"]

            # Simulate embedding logic with a small delay
            time.sleep(2)
            encoded_data = {f"embedding_dim_{i}": random.random() for i in range(5)}

            # Simulate successful embedding
            page_embeddings.append({
                "page_id": page_id,
                "space_name": space.space_name,
                "content": content,
                "encoded_data": encoded_data,
            })
            space.embedding_completed_page_ids.append({"page_id": page_id, "time": time.time()})
            space.current_embedding_page += 1

        space.embedding_status = "Completed"
        space.last_embedded_time = time.time()

    except Exception as e:
        space.embedding_status = "Failed"
        space.embedding_message = str(e)


class StartEmbeddingAPIView(APIView):
    """
    API endpoint to start embedding pages.
    """
    def post(self, request):
        space_name = request.data.get('space_name')
        force_embed = request.data.get('force_embed', False)

        if not space_name:
            return Response({'error': 'space_name is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Get or create space object
        space = space_db.get(space_name)
        if not space:
            space = SpaceEmbeddingProgress(space_name=space_name, embedding_status="In-Progress")
            space_db[space_name] = space

        if space.embedding_status == "Completed" and not force_embed:
            return Response({'message': 'Embedding already completed', 'status': space.embedding_status})

        # Start page generation in a thread
        def start_embedding():
            try:
                pages_to_embed = generate_pages(space)
                space.total_pages_to_embed = len(pages_to_embed)
                embed_pages_in_background(space, pages_to_embed)
            except Exception as e:
                space.embedding_status = "Failed"
                space.embedding_message = str(e)

        threading.Thread(target=start_embedding).start()
        return Response({'message': 'Embedding started in background', 'space_name': space_name}, status=status.HTTP_200_OK)


class PollEmbeddingStatusAPIView(APIView):
    """
    API endpoint to poll embedding status.
    """
    def get(self, request):
        space_name = request.query_params.get('space_name')
        if not space_name:
            return Response({'error': 'space_name is required'}, status=status.HTTP_400_BAD_REQUEST)

        space = space_db.get(space_name)
        if not space:
            return Response({'error': 'space_name not found'}, status=status.HTTP_404_NOT_FOUND)

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


# URL Configuration
from django.urls import path

urlpatterns = [
    path('start-embedding/', StartEmbeddingAPIView.as_view(), name='start_embedding'),
    path('poll-embedding-status/', PollEmbeddingStatusAPIView.as_view(), name='poll_embedding_status'),
]
