from transformers.utils import cached_path

model_name = "bert-base-uncased"
model_path = cached_path(f"models--{model_name.replace('/', '--')}/snapshots")
print(model_path)
