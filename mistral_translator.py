"""
Standalone Custom Document Translator
All-in-one file with no external dependencies except requests
"""
import os
import shutil
import zipfile
import xml.etree.ElementTree as ET
import requests
from time import sleep
from typing import Optional


# Translation prompts
DEFAULT_ROLE_PROMPT = """You are a professional translator, proficient in various languages including English, Chinese, Japanese, Korean, German, French, and Spanish. 
You have expertise in specialized vocabulary across different fields and understand the cultural nuances of each language.
Your translations are accurate, natural, and maintain the original tone and style of the text."""

DEFAULT_USER_PROMPT = """
Please translate the following text into {target_language}, ensuring accurate conveyance of the original meaning while maintaining consistency in style and tone.

# Translation Guidelines
1. Maintain the original meaning and context
2. Use appropriate terminology for the target language
3. Keep the same level of formality
4. Preserve any technical terms or proper nouns
5. Ensure natural flow in the target language
6. Consider cultural context and localization needs
7. If the text contains a URL or number, then directly return the URL or number

# Language-Specific Notes
- For Chinese: Use Simplified Chinese characters and modern standard Mandarin
- For Japanese: Use appropriate keigo (honorific language) when context requires
- For Korean: Use appropriate honorific forms based on context
- For European languages: Maintain proper gender agreement and formal/informal distinctions

# Output Format
Return only the translated text without any additional content or explanation.

Input Text: {text}
Your Translated Text:
"""

def get_translation_messages(text: str, target_language: str = 'English') -> list:
    """Get translation messages for Custom API"""
    return [
        {"role": "system", "content": DEFAULT_ROLE_PROMPT},
        {"role": "user", "content": DEFAULT_USER_PROMPT.format(
            text=text, target_language=target_language
        )},
    ]


class CustomTranslator:
    """Standalone Custom translator for document translation"""
    
    def __init__(self, api_key: str, model: str = "mistral-small-latest", base_url: str = "https://api.mistral.ai/v1"):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url
        self.request_delay = 0.1  # Small delay to prevent rate limiting
        self.ns = {
            'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
            'm': 'http://schemas.openxmlformats.org/officeDocument/2006/math'
        }

    def translate_text(self, text: str, target_language: str) -> str:
        """Translate text using Custom API"""
        if not text.strip():
            return ""
            
        messages = get_translation_messages(text, target_language)
        
        try:
            # Small delay to prevent rate limiting
            sleep(self.request_delay)
            url = f"{self.base_url}/chat/completions"
            headers = {"Authorization": f"Bearer {self.api_key}"}
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": 0.3,
                "max_tokens": 2000,
                "top_p": 1.0
            }
            resp = requests.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"].strip()
        except Exception as e:
            print(f"Custom translation error: {str(e)}")
            return text  # Return original text if translation fails

    def is_math_element(self, element: ET.Element) -> bool:
        """Check if element is a math formula"""
        return any(child.tag.startswith('{' + self.ns['m'] + '}') for child in element.iter())

    def extract_text(self, element: ET.Element) -> str:
        """Extract text from XML element"""
        # Skip math formulas
        if self.is_math_element(element):
            return ''
            
        text = []
        for t in element.iter('{' + self.ns['w'] + '}t'):
            if t.text:
                text.append(t.text)
        return ''.join(text).strip()

    def update_text(self, element: ET.Element, translated_text: str) -> None:
        """Update element with translated text"""
        if not translated_text.strip():
            return

        text_elements = list(element.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t'))
        if not text_elements:
            return

        if len(text_elements) == 1:
            text_elements[0].text = translated_text
            return

        # Distribute translated text across multiple text elements
        words = translated_text.split()
        total_words = len(words)
        words_per_element = max(1, total_words // len(text_elements))

        for i, t_element in enumerate(text_elements):
            start_idx = i * words_per_element
            end_idx = start_idx + words_per_element if i < len(text_elements) - 1 else None
            if start_idx < len(words):
                t_element.text = ' '.join(words[start_idx:end_idx])
            else:
                t_element.text = ''

    def process_table(self, table: ET.Element, target_language: str) -> None:
        """Process table cells for translation"""
        for row_idx, row in enumerate(table.findall('.//w:tr', self.ns)):
            for cell_idx, cell in enumerate(row.findall('.//w:tc', self.ns)):
                try:
                    cell_text = ''
                    for para in cell.findall('.//w:p', self.ns):
                        text = self.extract_text(para)
                        if text.strip():
                            cell_text += text + ' '

                    cell_text = cell_text.strip()
                    if cell_text:
                        print(f"Translating cell at row {row_idx+1}, column {cell_idx+1}")
                        translated_text = self.translate_text(cell_text, target_language)
                        if translated_text and translated_text != cell_text:
                            paras = cell.findall('.//w:p', self.ns)
                            if paras:
                                self.update_text(paras[0], translated_text)
                                # Clear other paragraphs
                                for para in paras[1:]:
                                    for t in para.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t'):
                                        t.text = ''
                except Exception as e:
                    print(f"Error processing cell at row {row_idx+1}, column {cell_idx+1}: {str(e)}")

    def translate_document(self, input_file: str, output_file: str, target_language: str) -> None:
        """Translate entire document"""
        temp_dir = "temp_docx"
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        os.makedirs(temp_dir)

        try:
            # Extract DOCX file
            with zipfile.ZipFile(input_file, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)

            # Parse document XML
            doc_xml_path = os.path.join(temp_dir, 'word', 'document.xml')
            tree = ET.parse(doc_xml_path)
            root = tree.getroot()

            # Translate paragraphs
            print("Translating paragraphs...")
            for i, element in enumerate(root.findall('.//w:p', self.ns)):
                text = self.extract_text(element)
                if text.strip():
                    print(f"Translating paragraph {i+1}: {text[:50]}...")
                    translated_text = self.translate_text(text, target_language)
                    if translated_text:
                        self.update_text(element, translated_text)

            # Translate tables
            print("Translating tables...")
            for i, table in enumerate(root.findall('.//w:tbl', self.ns)):
                print(f"Translating table {i+1}...")
                self.process_table(table, target_language)

            # Save modified document
            tree.write(doc_xml_path, encoding='UTF-8', xml_declaration=True)

            # Recreate DOCX file
            with zipfile.ZipFile(output_file, 'w') as outzip:
                for foldername, subfolders, filenames in os.walk(temp_dir):
                    for filename in filenames:
                        file_path = os.path.join(foldername, filename)
                        arcname = os.path.relpath(file_path, temp_dir)
                        outzip.write(file_path, arcname)

            print(f"Translation completed! Output saved to: {output_file}")

        finally:
            # Cleanup
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)


def translate_document(input_file: str, output_file: str, api_key: str, target_language: str = 'English', 
                      model: str = "mistral-small-latest", base_url: str = "https://api.mistral.ai/v1") -> str:
    """
    Main function to translate a document using Custom API
    
    Args:
        input_file (str): Path to input DOCX file
        output_file (str): Path to output translated DOCX file
        api_key (str): Custom API key
        target_language (str): Target language for translation (default: 'English')
        model (str): Custom model to use (default: 'mistral-small-latest')
        base_url (str): Custom API base URL (default: 'https://api.mistral.ai/v1')
    
    Returns:
        str: Path to the translated file
    """
    
    if not input_file.endswith('.docx'):
        raise ValueError("Input file must be a .docx file")
    
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Input file not found: {input_file}")
    
    print(f"Starting translation...")
    print(f"Input file: {input_file}")
    print(f"Output file: {output_file}")
    print(f"Target language: {target_language}")
    print(f"Model: {model}")
    
    # Create translator instance
    translator = CustomTranslator(api_key, model, base_url)
    
    # Translate document
    translator.translate_document(input_file, output_file, target_language)
    
    return output_file


def translate_text(text: str, api_key: str, target_language: str = 'English', 
                  model: str = "mistral-small-latest", base_url: str = "https://api.mistral.ai/v1") -> str:
    """
    Translate text using Custom API
    
    Args:
        text (str): Text to translate
        api_key (str): Custom API key
        target_language (str): Target language for translation (default: 'English')
        model (str): Custom model to use (default: 'mistral-small-latest')
        base_url (str): Custom API base URL (default: 'https://api.mistral.ai/v1')
    
    Returns:
        str: Translated text
    """
    
    translator = CustomTranslator(api_key, model, base_url)
    return translator.translate_text(text, target_language)


# Example usage
if __name__ == "__main__":
    # Example 1: Translate a document
    input_file = r"C:\Users\Vijay\Desktop\Document_Translator\transdoc-main\transdoc-main\docs\Source_English_Docx.docx"
    output_file = "translated_output.docx"
    api_key = "mjLoMvjl6nnvofomLxPNDMWZsvuouvCz"
    target_language = "Korean"
    
    try:
        result = translate_document(
            input_file=input_file,
            output_file=output_file,
            api_key=api_key,
            target_language=target_language
        )
        print(f"Translation completed: {result}")
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 2: Translate text
    text = "Hello, how are you today?"
    translated_text = translate_text(
        text=text,
        api_key=api_key,
        target_language="Chinese"
    )
    print(f"Original: {text}")
    print(f"Translated: {translated_text}")
