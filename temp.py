import torch
import gc

def unload_unsloth_model(model, tokenizer=None):
    """
    Safely unloads the Unsloth model and tokenizer from memory without affecting other CUDA models.
    
    Args:
    - model (torch.nn.Module): The Unsloth model instance.
    - tokenizer (Optional): The tokenizer associated with the model (if applicable).
    """
    if model is not None:
        # Move the model to CPU first to safely free GPU memory
        model.to("cpu")
        
        # Delete model reference
        del model

    if tokenizer is not None:
        # Delete tokenizer reference
        del tokenizer

    # Run garbage collection to free up Python memory
    gc.collect()

    # Free unused GPU memory (won't affect other models in CUDA)
    torch.cuda.empty_cache()
    torch.cuda.ipc_collect()  # Optional: Helps clean inter-process shared memory

# Example usage
unload_unsloth_model(model, tokenizer)
