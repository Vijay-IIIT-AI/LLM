def detect_language_and_count(text):
    # Ensure the value is a string, if not, convert it to an empty string
    if not isinstance(text, str):
        text = ""
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
