from resiliparse.parse.encoding import detect_encoding, bytes_to_str
from resiliparse.extract.html2text import extract_plain_text

def extract_text_from_html_bytes(html_bytes: bytes) -> str | None:

    detected_encoding = detect_encoding(html_bytes)
    extracted_text = bytes_to_str(html_bytes, encoding= detected_encoding, errors='ignore', fallback_encodings=('utf-8', 'cp1252'), strip_bom=True)
    
    text = extract_plain_text(extracted_text)
    return text


