#pip install datasets
from unsloth import FastVisionModel
from datasets import load_dataset
from trl import SFTTrainer, SFTConfig
from unsloth.trainer import UnslothVisionDataCollator

# Load model and tokenizer
model, tokenizer = FastVisionModel.from_pretrained(
    "unsloth/Qwen2-VL-72B-Instruct-bnb-4bit",
    load_in_4bit=True,
    use_gradient_checkpointing="unsloth"
)

# Inject LoRA
model = FastVisionModel.get_peft_model(
    model,
    finetune_vision_layers=True,
    finetune_language_layers=True,
    finetune_attention_modules=True,
    finetune_mlp_modules=True,
    r=16, lora_alpha=16, lora_dropout=0, bias="none"
)

# Load and convert dataset
dataset = load_dataset("unsloth/Radiology_mini", split="train")
instruction = "You are a medical expert. What do you observe?"
def convert(sample):
    return {
        "messages": [
            {"role": "user", "content": [
                {"type": "text", "text": instruction},
                {"type": "image", "image": sample["image"]}
            ]},
            {"role": "assistant", "content": [
                {"type": "text", "text": sample["caption"]}
            ]}
        ]
    }
converted_dataset = [convert(x) for x in dataset]

# Training
FastVisionModel.for_training(model)
trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=converted_dataset,
    data_collator=UnslothVisionDataCollator(model, tokenizer),
    args=SFTConfig(
        per_device_train_batch_size=1,
        gradient_accumulation_steps=4,
        max_steps=30,
        learning_rate=2e-4,
        logging_steps=1,
        output_dir="qwen72b_outputs",
        optim="adamw_8bit",
        lr_scheduler_type="linear",
        remove_unused_columns=False,
        dataset_text_field="",
        dataset_kwargs={"skip_prepare_dataset": True},
        max_seq_length=2048,
        report_to="none",
    )
)
trainer.train()

# ✅ Save to disk in 16bit (for vLLM)
model.save_pretrained_merged("qwen72b_merged_fp16", tokenizer, save_method="merged_16bit")
