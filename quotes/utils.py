import re

_space_re = re.compile(r"\s+", re.UNICODE)

def normalize_text(s: str) -> str:
    if not s:
        return ""
    s = s.strip().lower()
    s = _space_re.sub(" ", s)
    s = s.replace("«", "").replace("»", "").replace('"', "").replace("'", "")
    return s
