import tempfile
import os
from pptx import Presentation

def remove_slides(file_path, slide_ids, output_folder):
    """Remove specified slides from a PowerPoint file and save the result with a temporary suffix."""
    prs = Presentation(file_path)
    slides = prs.slides._sldIdLst  # Access slide ID list
    slide_elements = list(slides)  # Convert to list for modification
    
    # Remove slides in reverse order to avoid indexing issues
    for slide_id in sorted(slide_ids, reverse=True):
        if 0 <= slide_id < len(slide_elements):
            slides.remove(slide_elements[slide_id])

    # Ensure the output directory exists
    os.makedirs(output_folder, exist_ok=True)

    # Extract original file name without extension
    original_filename = os.path.basename(file_path).rsplit(".", 1)[0]

    # Create a temporary file name with the original filename as a prefix
    temp_file = tempfile.NamedTemporaryFile(
        delete=False, 
        dir=output_folder, 
        prefix=f"{original_filename}_",  # Prefix the original filename
        suffix=".pptx"
    )
    
    prs.save(temp_file.name)
    temp_file.close()
    
    return temp_file.name

# Define paths
output_folder = r"C:\Users\Vijay\Desktop\PPT"  # Output folder path
slide_ids_to_remove = [100]  # Slide indices to remove (0-based index)
file_path = r"C:\Users\Vijay\Desktop\PPT\LLM추천.pptx"

# Call function
result = remove_slides(file_path, slide_ids_to_remove, output_folder)
print(f"Modified PPT saved at: {result}")
