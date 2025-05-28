pip install huggingface_hub
from huggingface_hub import hf_hub_download, list_repo_files
import os

model_repo = "unsloth/Llama-3.2-90B-Vision-Instruct-bnb-4bit"
save_dir = "./llama_3_2_90b"

# Create save directory if it doesn't exist
os.makedirs(save_dir, exist_ok=True)

# List all files in the repo
files = list_repo_files(model_repo)
print(f"Files to download: {files}")

# Download each file
for file_name in files:
    print(f"Downloading {file_name}...")
    hf_hub_download(
        repo_id=model_repo,
        filename=file_name,
        cache_dir=save_dir,
        local_dir=save_dir,
        local_dir_use_symlinks=False
    )

print("Download complete!")
