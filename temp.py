# Install necessary libraries (run this in a Jupyter notebook or a Python script with shell access)
!pip install torch transformers

# Import required libraries
import torch
from transformers import AutoTokenizer, AutoModelWithLMHead

# Load tokenizer and model
tokenizer = AutoTokenizer.from_pretrained('t5-base')
model = AutoModelWithLMHead.from_pretrained('t5-base', return_dict=True)

# Define the input sequence (a Wikipedia passage about Data Science)
sequence = (
    "Data science is an interdisciplinary field[10] focused on extracting knowledge from typically large data sets and "
    "applying the knowledge and insights from that data to solve problems in a wide range of application domains.[11] "
    "The field encompasses preparing data for analysis, formulating data science problems, analyzing data, developing "
    "data-driven solutions, and presenting findings to inform high-level decisions in a broad range of application domains. "
    "As such, it incorporates skills from computer science, statistics, information science, mathematics, data visualization, "
    "information visualization, data sonification, data integration, graphic design, complex systems, communication and business.[12][13] "
    "Statistician Nathan Yau, drawing on Ben Fry, also links data science to human–computer interaction: users should be able "
    "to intuitively control and explore data.[14][15] In 2015, the American Statistical Association identified database management, "
    "statistics and machine learning, and distributed and parallel systems as the three emerging foundational professional communities.[16]"
)

# Tokenize the input for summarization
inputs = tokenizer.encode(
    "summarize: " + sequence,
    return_tensors='pt',
    max_length=512,
    truncation=True
)

# Generate summary
output = model.generate(inputs, min_length=80, max_length=100)

# Decode and print the summary
summary = tokenizer.decode(output[0], skip_special_tokens=True)
print(summary)
