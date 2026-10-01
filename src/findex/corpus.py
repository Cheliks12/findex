from pathlib import Path
from typing import Iterator, NamedTuple

class Document(NamedTuple):
    doc_id: str
    path: Path
    text: str

def iter_documents(root: Path) -> Iterator[Document]:
    """Generator that reads text files from a directory one by one."""
    if not root.exists():
        return

    for path in sorted(root.rglob("*.txt")):
        if path.is_file():
            try:
                text = path.read_text(encoding="utf-8", errors="replace")
                yield Document(doc_id=path.stem, path=path, text=text)
            except Exception as e:
                print(f"Warning: failed to read file {path}: {e}")