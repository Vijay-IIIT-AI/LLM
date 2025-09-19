from django.http import HttpResponse, Http404
from django.views.decorators.http import require_http_methods
from django.conf import settings
from .minio_client import get_minio

@require_http_methods(["GET"])
def proxy_minio_file(request, object_path):
    """Proxy MinIO files through Django on port 8000"""
    try:
        client = get_minio()
        
        # Parse bucket/key from object_path
        if "/" in object_path:
            bucket, key = object_path.split("/", 1)
        else:
            bucket = settings.MINIO_BUCKET
            key = object_path
            
        # Get object from MinIO
        response = client.get_object(bucket, key)
        
        # Create Django response
        file_data = response.read()
        response.close()
        response.release_conn()
        
        django_response = HttpResponse(file_data, content_type='application/octet-stream')
        django_response['Content-Disposition'] = f'attachment; filename="{key.split("/")[-1]}"'
        return django_response
        
    except Exception as e:
        raise Http404(f"File not found: {str(e)}")


def generate_download_url(object_path: str) -> str:
    """Return a URL for downloading the object/file.
    MinIO => Django proxy URL; Local => /local/<path>
    """
    if settings.USE_MINIO:
        # Return Django proxy URL instead of presigned MinIO URL
        return f"/files/download/{object_path}"
    # Local: return application route path
    return f"/local/{object_path}"
