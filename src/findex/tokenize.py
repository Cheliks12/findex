import re
import unicodedata
from typing import Iterator

WORD_RE = re.compile(r"\w+(?:[']\w+)?", re.UNICODE)

def tokenize(text: str) -> Iterator[str]:
    """Extracts tokens from text stream-wise using re.finditer."""
    normalized = unicodedata.normalize("NFC", text)
    folded = normalized.casefold()
    for match in WORD_RE.finditer(folded):
        yield match.group()