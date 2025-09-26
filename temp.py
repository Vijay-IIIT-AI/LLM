http://localhost:8000/download_by_url?url=http://127.0.0.1:9000/data/report_comprehensive_2406211642.pdf


# views.py
import io
from urllib.parse import urlparse, quote
from django.http import StreamingHttpResponse, HttpResponse, JsonResponse
from minio import Minio
from minio.error import S3Error

# MinIO configuration
MINIO_ENDPOINT = "127.0.0.1:9000"
MINIO_ACCESS_KEY = "minioadmin"
MINIO_SECRET_KEY = "minioadmin"
MINIO_SECURE = False
CHUNK_SIZE = 1024 * 1024  # 1 MB

minio_client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=MINIO_SECURE
)

import re
_range_re = re.compile(r"bytes=(\d*)-(\d*)")

def parse_range_header(range_header, file_size):
    if not range_header:
        return None
    m = _range_re.match(range_header)
    if not m:
        return None
    start_str, end_str = m.groups()
    if start_str == "" and end_str == "":
        return None
    if start_str == "":
        suffix_len = int(end_str)
        start = max(0, file_size - suffix_len)
        end = file_size - 1
    elif end_str == "":
        start = int(start_str)
        end = file_size - 1
    else:
        start = int(start_str)
        end = int(end_str)
    if start > end or start >= file_size:
        return None
    end = min(end, file_size - 1)
    return start, end

# Optional auth
def check_auth(bucket, obj_path):
    return True

# ------------------------
# Download view
# ------------------------
def download_by_url(request):
    minio_url = request.GET.get("url")
    if not minio_url:
        return JsonResponse({"error": "url query parameter required"}, status=400)

    try:
        parsed = urlparse(minio_url)
        path_parts = parsed.path.lstrip("/").split("/", 1)
        if len(path_parts) != 2:
            return JsonResponse({"error": "invalid MinIO URL"}, status=400)
        bucket, obj_path = path_parts
    except Exception:
        return JsonResponse({"error": "invalid MinIO URL"}, status=400)

    if not check_auth(bucket, obj_path):
        return HttpResponse(status=403)

    try:
        stat = minio_client.stat_object(bucket, obj_path)
        file_size = stat.size
        content_type = stat.content_type or "application/octet-stream"
    except S3Error:
        return JsonResponse({"error": "object not found"}, status=404)

    # Range parsing
    range_header = request.headers.get("Range")
    range_parsed = parse_range_header(range_header, file_size)
    if range_parsed:
        start, end = range_parsed
        length = end - start + 1
        status_code = 206
    else:
        start = 0
        end = file_size - 1
        length = file_size
        status_code = 200

    # Generator for streaming
    def stream_generator():
        obj = None
        try:
            obj = minio_client.get_object(bucket, obj_path, offset=start, length=length)
            for chunk in obj.stream(CHUNK_SIZE):
                if not chunk:
                    break
                yield chunk
        finally:
            if obj:
                try:
                    obj.close()
                    obj.release_conn()
                except Exception:
                    pass

    filename = obj_path.split("/")[-1]
    filename_encoded = quote(filename)
    content_disposition = f"attachment; filename*=UTF-8''{filename_encoded}"

    response = StreamingHttpResponse(
        stream_generator(),
        content_type=content_type,
        status=status_code
    )
    response["Content-Length"] = str(length)
    response["Content-Disposition"] = content_disposition
    response["Accept-Ranges"] = "bytes"
    if range_parsed:
        response["Content-Range"] = f"bytes {start}-{end}/{file_size}"

    return response
