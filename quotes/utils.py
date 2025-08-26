import re
import string

def normalize_text(text: str) -> str:
    if not text:
        return ""

    text = text.lower()

    punctuation_to_remove = string.punctuation + '«»“”‘’—…'

    translator = str.maketrans('', '', punctuation_to_remove)
    text = text.translate(translator)

    text = re.sub(r'\s+', ' ', text)

    text = text.strip()

    return text