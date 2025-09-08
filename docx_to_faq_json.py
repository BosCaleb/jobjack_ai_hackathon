import json
import re
from docx import Document

# Regex pattern to match emojis and symbols
EMOJI_PATTERN = re.compile(
    "["u"\U0001F600-\U0001F64F"  # emoticons
    u"\U0001F300-\U0001F5FF"     # symbols & pictographs
    u"\U0001F680-\U0001F6FF"     # transport & map
    u"\U0001F1E0-\U0001F1FF"     # flags
    u"\u2600-\u26FF"             # misc symbols
    u"\u2700-\u27BF"             # dingbats
    "]+", flags=re.UNICODE
)

def clean_text(text: str) -> str:
    """Remove emojis and extra spaces from text."""
    text = EMOJI_PATTERN.sub(r'', text)  # remove emojis
    return text.strip()

def parse_faq_from_table(docx_path, output_json):
    """Parse FAQ Q&A pairs from Word tables, remove emojis, save JSON."""
    doc = Document(docx_path)
    faq_entries = []

    for table in doc.tables:
        for row in table.rows[1:]:  # skip header row
            cells = [clean_text(cell.text) for cell in row.cells]
            if len(cells) >= 2 and cells[0] and cells[1]:
                faq_entries.append({
                    "question": cells[0],
                    "answer": cells[1]
                })

    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(faq_entries, f, indent=2, ensure_ascii=False)

    print(f"✅ Extracted {len(faq_entries)} clean FAQ entries into {output_json}")


if __name__ == "__main__":
    input_docx = "faq_word_file.docx"   # Replace with your file
    output_json = "faq_data.json"
    parse_faq_from_table(input_docx, output_json)
