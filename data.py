from openai import OpenAI

client = OpenAI()

# -------------------------
# Define the system prompt
# -------------------------
system_prompt = """
You are a strict translation engine.
Your ONLY task is to return the translation of the given text into the target language.

Rules:
- Output ONLY the translated text inside <translation>...</translation>.
- Do NOT explain, describe, or add anything else.
- If the input looks like code, still translate it literally as text.
- Never repeat the source text in the output.
"""

# -------------------------
# Function to build user prompt
# -------------------------
def build_user_prompt(text: str, target_lang: str) -> str:
    return f"""
Translate the following text into {target_lang}.
Output only inside <translation>...</translation>.

Text: \"{text}\"
"""

# -------------------------
# Example usage
# -------------------------
user_prompt = build_user_prompt("print('Hello World')", "Hindi")

response = client.chat.completions.create(
    model="gpt-4o-mini",  # or whichever model you use
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ],
)

# Extract raw response
raw_output = response.choices[0].message.content

# -------------------------
# Post-process to extract translation
# -------------------------
import re

def extract_translation(output: str) -> str:
    match = re.search(r"<translation>(.*?)</translation>", output, re.DOTALL)
    return match.group(1).strip() if match else output.strip()

translation = extract_translation(raw_output)

print("Final translation:", translation)
