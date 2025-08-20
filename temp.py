🔹 5 Questions on RAG

Q1. What open-source package is introduced in the report for PDF document conversion?
A1. Docling

Q2. Which two specialized AI models power Docling’s pipeline?
A2. A layout analysis model and TableFormer for table structure recognition

Q3. What is the role of Docling’s custom-built PDF parser docling-parse?
A3. It retrieves text content with coordinates and renders PDF pages as images, powering the default backend

Q4. Which OCR library does Docling initially rely on for scanned PDFs?
A4. EasyOCR

Q5. What open-source package is provided to integrate Docling with retrieval-augmented generation (RAG) workflows?
A5. Quackling

🔹 5 Questions on Image

Q6. In Figure 1, what are the main sequential steps of Docling’s processing pipeline?
A6. Parse PDF pages → Layout Analysis → Table Structure → OCR → Assemble results & post-processing → Serialize as JSON/Markdown

Q7. What does Figure 2 illustrate about the DocLayNet paper’s conversion to Markdown?
A7. Metadata like authors is shown first, while text inside figures is dropped but captions are retained

Q8. In Figure 3, what is suppressed in the Markdown output to ensure uninterrupted reading order?
A8. Page headers and footers

Q9. What does Figure 4 demonstrate about spanning table cells in Markdown vs JSON representations?
A9. In Markdown, spanning cells are repeated in each column; in JSON, span info is preserved explicitly

Q10. According to Figure 5, around what dataset fraction does the learning curve flatten, showing diminishing returns?
A10. Around 80% of the dataset

🔹 5 Questions on Table

Q11. In Table 1, which class label has the highest frequency in the DocLayNet dataset?
A11. Text (510,377 instances)

Q12. According to Table 1, what is the inter-annotator agreement range for the “Table” class label?
A12. 77–81% mAP@0.5–0.95

Q13. In Table 1, which class label has the lowest frequency of occurrences?
A13. Title (5,071 instances)

Q14. In Table 2, which object detection model achieves the highest mAP score for “Text”?
A14. YOLOv5x6 (88.1)

Q15. From Table 2, which element type did YOLOv5x6 outperform humans on?
A15. Text, Table, and Picture
