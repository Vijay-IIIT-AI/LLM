"""
Standalone Custom Document Translator with Resilient Batching for Speed
All-in-one file with dependencies on 'requests' and 'tqdm'

- MODIFIED: Removed Mistral/Groq logic to support any custom LLM.
"""
import os
import shutil
import zipfile
import xml.etree.ElementTree as ET
from time import sleep
from tqdm import tqdm
# Note: 'requests' and 'groq' are no longer needed if your custom LLM has a different interface.
# You might need to add other imports depending on your LLM.


# --- Generic Prompts ---

DEFAULT_ROLE_PROMPT = """You are a professional translator, proficient in various languages including English, Chinese, Japanese, Korean, German, French, and Spanish. 
You have expertise in specialized vocabulary across different fields and understand the cultural nuances of each language.
Your translations are accurate, natural, and maintain the original tone and style of the text."""

DEFAULT_USER_PROMPT_BATCH = """
Please translate the following text, which contains multiple segments separated by a special tag: <--!brk!-->
Translate each segment into {target_language} and preserve the <--!brk!--> tag exactly as it is between the translated segments.

# Example
- Input: "Hello world.<--!brk!-->How are you?"
- Your Output: "你好世界。<--!brk!-->你好吗？" (if target language is Chinese)

# Translation Guidelines
1. Maintain the meaning and context for each segment.
2. **Crucially, you must maintain the exact `<--!brk!-->` separator between your translated segments.** Do not add or remove any separators.
3. If a segment is a URL or number, return it as is.

# Output Format
Return only the translated segments, separated by <--!brk!-->. Do not add any extra text, explanations, or introductory phrases.

Input Text: {text}
Your Translated Text:
"""

def get_translation_messages_batch(text: str, target_language: str = 'English') -> list:
    """Get translation messages for batch processing"""
    return [
        {"role": "system", "content": DEFAULT_ROLE_PROMPT},
        {"role": "user", "content": DEFAULT_USER_PROMPT_BATCH.format(
            text=text, target_language=target_language
        )},
    ]

def get_translation_messages(text: str, target_language: str = 'English') -> list:
    """Get translation messages for a single text string."""
    user_prompt = f"Please translate the following text into {target_language}. Return only the translated text.\n\nInput Text: {text}\nYour Translated Text:"
    return [
        {"role": "system", "content": DEFAULT_ROLE_PROMPT},
        {"role": "user", "content": user_prompt}
    ]

# --- IMPORTANT: CUSTOM LLM FUNCTION ---
# --- Replace this function with the code that calls your own LLM ---
def call_your_llm(system_prompt: str, user_prompt: str, max_tokens: int) -> str:
    """
    A placeholder function to call your custom LLM.
    
    Args:
        system_prompt: The system message for the LLM.
        user_prompt: The user message (the text to be translated).
        max_tokens: A suggestion for the maximum number of tokens in the response.

    Returns:
        The translated text as a string.
    """
    # =========================================================================
    # --- START: YOUR CUSTOM LLM INTEGRATION CODE ---
    #
    # Example using a hypothetical API endpoint:
    #
    # import requests
    # try:
    #     api_url = "http://localhost:8080/v1/chat/completions" # Your local API URL
    #     payload = {
    #         "model": "your-model-name",
    #         "messages": [
    #             {"role": "system", "content": system_prompt},
    #             {"role": "user", "content": user_prompt}
    #         ],
    #         "temperature": 0.3,
    #         "max_tokens": max_tokens
    #     }
    #     response = requests.post(api_url, json=payload)
    #     response.raise_for_status()
    #     return response.json()["choices"][0]["message"]["content"].strip()
    # except Exception as e:
    #     print(f"Error calling custom LLM: {e}")
    #     return None # Return None on failure

    # --- END: YOUR CUSTOM LLM INTEGRATION CODE ---
    # =========================================================================
    
    # For demonstration purposes, this returns a placeholder message.
    # **DELETE THIS PART** when you add your own LLM logic above.
    print("--- SIMULATING LLM CALL ---")
    print(f"System: {system_prompt[:80]}...")
    print(f"User: {user_prompt[:80]}...")
    return f"This is a simulated translation for: '{user_prompt.split('Input Text:')[-1].strip()}'"
    

class CustomTranslator:
    """
    Standalone Custom translator that uses a user-defined LLM function.
    """
    
    def __init__(self):
        self.request_delay = 0.1 # Delay between requests to avoid overwhelming your model
        self.ns = {
            'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
            'm': 'http://schemas.openxmlformats.org/officeDocument/2006/math'
        }
        self.batch_separator = "<--!brk!-->"

    def _send_request_to_custom_llm(self, messages: list, max_tokens: int) -> str | None:
        """
        Sends prompts to the custom LLM and handles potential errors.
        """
        try:
            sleep(self.request_delay)
            system_prompt = next((m["content"] for m in messages if m["role"] == "system"), "")
            user_prompt = next((m["content"] for m in messages if m["role"] == "user"), "")

            if not user_prompt:
                return None

            # This is where the call to your custom LLM happens
            translated_text = call_your_llm(system_prompt, user_prompt, max_tokens)
            
            return translated_text

        except Exception as e:
            print(f"\nAn error occurred while calling the custom LLM: {str(e)}")
            return None

    def translate_batch(self, text_batch: list, target_language: str) -> list | None:
        """Translates a batch of texts using the custom LLM."""
        if not text_batch:
            return []
            
        combined_text = self.batch_separator.join(text_batch)
        messages = get_translation_messages_batch(combined_text, target_language)
        
        translated_combined = self._send_request_to_custom_llm(messages, max_tokens=8000)

        if translated_combined is None:
            return None # Signal failure
        
        translated_batch = translated_combined.split(self.batch_separator)

        if len(translated_batch) != len(text_batch):
            print(f"\nBatch length mismatch. Expected {len(text_batch)}, got {len(translated_batch)}. Will retry individually.")
            return None

        return translated_batch

    def translate_text(self, text: str, target_language: str) -> str:
        """Translates a single string of text using the custom LLM."""
        if not text.strip():
            return ""
        messages = get_translation_messages(text, target_language)
        
        translated_text = self._send_request_to_custom_llm(messages, max_tokens=2000)
        
        return translated_text if translated_text is not None else text

    def extract_text(self, element: ET.Element) -> str:
        """Extracts text, skipping any text within mathematical formulas."""
        math_text_nodes = set()
        for math_el in element.findall('.//m:oMath', self.ns) + element.findall('.//m:oMathPara', self.ns):
            for t_node in math_el.iter('{' + self.ns['w'] + '}t'):
                math_text_nodes.add(t_node)

        text_parts = []
        for t_node in element.iter('{' + self.ns['w'] + '}t'):
            if t_node not in math_text_nodes and t_node.text:
                text_parts.append(t_node.text)
        
        return ''.join(text_parts).strip()

    def update_text(self, element: ET.Element, translated_text: str) -> None:
        """Updates an element, overwriting only the original non-math text nodes."""
        if not translated_text.strip():
            return

        math_text_nodes = set()
        for math_el in element.findall('.//m:oMath', self.ns) + element.findall('.//m:oMathPara', self.ns):
            for t_node in math_el.iter('{' + self.ns['w'] + '}t'):
                math_text_nodes.add(t_node)
        
        translatable_nodes = []
        for t_node in element.iter('{' + self.ns['w'] + '}t'):
            if t_node not in math_text_nodes:
                translatable_nodes.append(t_node)

        if not translatable_nodes:
            return

        translatable_nodes[0].text = translated_text
        for t_node in translatable_nodes[1:]:
            t_node.text = ''

    def translate_document(self, input_file: str, output_file: str, target_language: str) -> None:
        """Translate entire document using batching with a single-item fallback."""
        temp_dir = "temp_docx"
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        os.makedirs(temp_dir)

        try:
            with zipfile.ZipFile(input_file, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)

            doc_xml_path = os.path.join(temp_dir, 'word', 'document.xml')
            tree = ET.parse(doc_xml_path)
            root = tree.getroot()

            elements_to_translate = []
            original_texts = []
            
            all_potential_elements = root.findall('.//w:p', self.ns)
            for tbl in root.findall('.//w:tbl', self.ns):
                    all_potential_elements.extend(tbl.findall('.//w:tc', self.ns))

            print("Extracting text from document...")
            for element in all_potential_elements:
                text = self.extract_text(element)
                if text.strip():
                    elements_to_translate.append(element)
                    original_texts.append(text)

            batch_size = 15
            all_translated_texts = []
            
            batch_iterator = tqdm(range(0, len(original_texts), batch_size), desc="Translating Batches")
            for i in batch_iterator:
                batch_texts = original_texts[i:i+batch_size]
                translated_batch = self.translate_batch(batch_texts, target_language)
                
                if translated_batch is None:
                    batch_iterator.set_description(f"Batch {i//batch_size+1} failed. Retrying one by one")
                    
                    fallback_translations = []
                    for text_item in tqdm(batch_texts, desc="Individual Fallback", leave=False):
                        fallback_translations.append(self.translate_text(text_item, target_language))
                    
                    all_translated_texts.extend(fallback_translations)
                    batch_iterator.set_description("Translating Batches") 
                else:
                    all_translated_texts.extend(translated_batch)

            print("Updating document with translations...")
            for element, translated_text in zip(elements_to_translate, all_translated_texts):
                self.update_text(element, translated_text)

            with open(doc_xml_path, 'wb') as f:
                f.write(b'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n')
                tree.write(f, encoding='utf-8')

            print("Rebuilding DOCX file...")
            with zipfile.ZipFile(output_file, 'w') as outzip:
                for foldername, subfolders, filenames in os.walk(temp_dir):
                    for filename in filenames:
                        file_path = os.path.join(foldername, filename)
                        arcname = os.path.relpath(file_path, temp_dir)
                        outzip.write(file_path, arcname)

            print(f"\nTranslation completed! Output saved to: {output_file}")

        finally:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)


def translate_document(input_file: str, output_file: str, target_language: str = 'English') -> str:
    if not input_file.endswith('.docx'):
        raise ValueError("Input file must be a .docx file")
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Input file not found: {input_file}")
    
    print(f"Starting translation...")
    print(f"- Input file: {input_file}")
    print(f"- Output file: {output_file}")
    print(f"- Target language: {target_language}")
    
    translator = CustomTranslator()
    translator.translate_document(input_file, output_file, target_language)
    return output_file


# --- Example Usage ---
if __name__ == "__main__":
    # --- CONFIGURE YOUR TRANSLATION JOB HERE ---
    INPUT_DOCX = r"C:\Users\YourUser\Documents\report.docx"  # <-- IMPORTANT: SET YOUR INPUT FILE PATH
    OUTPUT_DOCX = "translated_document.docx"
    TARGET_LANGUAGE = "Korean"

    if "path/to/your/document.docx" in INPUT_DOCX or "YourUser" in INPUT_DOCX:
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        print("!!! PLEASE UPDATE the INPUT_DOCX variable to a real file.   !!!")
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    else:
        try:
            translate_document(
                input_file=INPUT_DOCX,
                output_file=OUTPUT_DOCX,
                target_language=TARGET_LANGUAGE
            )
        except Exception as e:
            print(f"\nAn unexpected error occurred during the translation process: {e}")
