import pandas as pd
import re

# Example dataframe with bilingual content
data = {
    "page_contents": [
        "이 문장은 짧습니다.",  # Short Korean text
        "This content has exactly twenty words. It should stay in the dataframe.",  # Long English content
        "짧은 텍스트입니다.",  # Short Korean text
        "This content contains 한국어와 영어가 섞여 있습니다.",  # Mixed Korean and English
        "이것은 스무 자 이상의 유효한 콘텐츠입니다. It should not be removed."  # Mixed content, long enough
    ],
    "page_id": [101, 102, 103, 104, 105]
}
df = pd.DataFrame(data)

# Step 1: Define a function to handle bilingual cases and detect language
def detect_language_and_count(text):
    # Check for English words
    english_word_count = len(re.findall(r'\b\w+\b', text))
    # Check for Korean characters
    korean_char_count = len(re.findall(r'[\uac00-\ud7a3]', text))
    # Determine language type
    if english_word_count > 0 and korean_char_count > 0:
        language = "bilingual"
    elif english_word_count > 0:
        language = "english"
    elif korean_char_count > 0:
        language = "korean"
    else:
        language = "unknown"
    # Return total word count and language
    return english_word_count + korean_char_count, language

# Step 2: Apply the function to calculate word/character count and detect language
df[["word_count", "source_language"]] = df["page_contents"].apply(
    lambda text: pd.Series(detect_language_and_count(text))
)

# Step 3: Identify rows with fewer than 20 total words/characters
rows_with_few_words = df[df["word_count"] < 20]

# Step 4: Get the `page_id` of rows to remove
page_ids_to_remove = rows_with_few_words["page_id"].tolist()

# Step 5: Drop rows with fewer than 20 total words/characters
df = df[df["word_count"] >= 20].drop(columns=["word_count"])  # Remove helper column if not needed

print("Page IDs to Remove:", page_ids_to_remove)
print("\nUpdated DataFrame:")
print(df)
