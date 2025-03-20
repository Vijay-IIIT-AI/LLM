def encode_image(image_path):
    """Convert image to base64 (only needed for local files)."""
    with open(image_path, "rb") as img_file:
        return f"data:image/jpeg;base64,{base64.b64encode(img_file.read()).decode()}"

# List of image paths
image_paths = ["image1.jpg", "image2.jpg", "image3.jpg"]
image_urls = [encode_image(img) for img in image_paths]
