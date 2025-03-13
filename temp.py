import torch
import gc

def unload_unsloth_model(model, tokenizer=None):

    if model is not None:
        try:
            # Check if model is quantized (8-bit via bitsandbytes)
            if hasattr(model, "quantization_method") and model.quantization_method == "bitsandbytes":
                print("Detected 8-bit model (bitsandbytes). Using special cleanup.")
                del model  # Directly delete without moving to CPU
            else:
                print("Detected standard PyTorch model. Moving to CPU before deletion.")
                model.to("cpu")
                del model
        except Exception as e:
            print(f"Error during model unloading: {e}")

    if tokenizer is not None:
        del tokenizer

    # Run garbage collection to free memory
    gc.collect()

    # Free only unused GPU memory (won’t affect other models)
    torch.cuda.empty_cache()
    torch.cuda.ipc_collect()

# Example usage:
unload_unsloth_model(model, tokenizer)
