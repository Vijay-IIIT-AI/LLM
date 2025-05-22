text = (
    "summarize: Data science is an interdisciplinary field focused on extracting knowledge from large data sets "
    "and applying that knowledge to solve problems across various domains. It combines skills from statistics, "
    "computer science, mathematics, and domain expertise."
)

# Generate summary
summary = summarizer(text, max_length=100, min_length=30, clean_up_tokenization_spaces=True)

# Print the summarized text
print(summary[0]['generated_text'])
