@require_http_methods(["GET"])
def proxy_minio_file(request, object_path):
    """Download from MinIO and serve file content to UI"""
    try:
        client = get_minio()
        
        # Parse bucket/key from object_path
        if "/" in object_path:
            bucket, key = object_path.split("/", 1)
        else:
            bucket = settings.MINIO_BUCKET
            key = object_path
            
        # Download object from MinIO
        response = client.get_object(bucket, key)
        
        # Read file content
        file_data = response.read()
        response.close()
        response.release_conn()
        
        # Determine content type based on file extension
        file_extension = key.split('.')[-1].lower()
        content_type_map = {
            'pdf': 'application/pdf',
            'pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'txt': 'text/plain',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'gif': 'image/gif',
            'mp4': 'video/mp4',
            'mp3': 'audio/mpeg',
            'zip': 'application/zip',
            'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        }
        content_type = content_type_map.get(file_extension, 'application/octet-stream')
        
        # Serve file content directly
        django_response = HttpResponse(file_data, content_type=content_type)
        
        # For downloads, add Content-Disposition
        if request.GET.get('download') == 'true':
            django_response['Content-Disposition'] = f'attachment; filename="{key.split("/")[-1]}"'
        else:
            # For inline viewing in browser
            django_response['Content-Disposition'] = f'inline; filename="{key.split("/")[-1]}"'
            
        return django_response
        
    except Exception as e:
        raise Http404(f"File not found: {str(e)}")
