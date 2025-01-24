class StartEmbeddingView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)

            # Validate space_name
            space_name = data.get('space_name')
            if not space_name or not isinstance(space_name, str) or len(space_name) > 255:
                return JsonResponse({'error': 'Invalid or missing space_name'}, status=400)

            # Validate force_embed
            force_embed = data.get('force_embed', False)
            if not isinstance(force_embed, bool):
                return JsonResponse({'error': 'force_embed must be a boolean value'}, status=400)

            # Check if dummy_pages exists
            if not dummy_pages:
                return JsonResponse({'error': 'No pages available for embedding'}, status=500)

            try:
                space = SpaceEmbeddingProgress.objects.get(space_name=space_name)

                if space.embedding_status == 'Completed' and not force_embed:
                    return JsonResponse({
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

            if not dummy_pages_to_embed:
                return JsonResponse({'error': 'No pages to embed'}, status=400)

            # Simulate embedding process
            space.embedding_completed_page_ids = []
            space.embedding_failed_page_ids = []
            space.current_embedding_page = 0

            for page in dummy_pages_to_embed:
                page_id = page['page_id']
                content = page['content']

                try:
                    # Simulate encoding
                    encoded_data = {f"embedding_dim_{i}": np.random.rand() for i in range(5)}

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

            # Finalize embedding status
            space.embedding_status = 'Failed' if space.embedding_failed_page_ids else 'Completed'
            space.save()

            return JsonResponse({'message': 'Embedding started', 'space_id': space.emb_id}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON payload'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

class PollEmbeddingStatusView(View):
    def get(self, request):
        try:
            space_name = request.GET.get('space_name')

            if not space_name:
                return JsonResponse({'error': 'space_name is required'}, status=400)

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
                return JsonResponse(response, status=200)

            except SpaceEmbeddingProgress.DoesNotExist:
                return JsonResponse({'error': 'space_name not found'}, status=404)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

