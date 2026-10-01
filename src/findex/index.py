import time
import tracemalloc
import pickle
import json
from collections import defaultdict, Counter
from dataclasses import dataclass, field
from pathlib import Path
from findex.corpus import iter_documents
from findex.tokenize import tokenize

@dataclass(frozen=True, slots=True)
class Posting:
    doc_id: str
    freq: int

@dataclass(frozen=True, slots=True)
class DocMeta:
    doc_id: str
    path: str
    length: int

@dataclass
class InvertedIndex:
    index: dict[str, list[Posting]] = field(default_factory=dict)
    documents: dict[str, DocMeta] = field(default_factory=dict)

def build_index(root: Path) -> InvertedIndex:
    raw_index = defaultdict(list)
    doc_meta_map = {}

    for doc in iter_documents(root):
        tokens = list(tokenize(doc.text))
        doc_length = len(tokens)
        
        doc_meta_map[doc.doc_id] = DocMeta(
            doc_id=doc.doc_id,
            path=str(doc.path),
            length=doc_length
        )

        token_counts = Counter(tokens)
        for term, freq in token_counts.items():
            raw_index[term].append(Posting(doc_id=doc.doc_id, freq=freq))

    sorted_index = {}
    for term, postings in raw_index.items():
        sorted_postings = sorted(postings, key=lambda p: p.doc_id)
        sorted_index[term] = sorted_postings

    return InvertedIndex(index=sorted_index, documents=doc_meta_map)

def save_index(index: InvertedIndex, path: Path):
    with open(path, "wb") as f:
        pickle.dump(index, f)

def load_index(path: Path) -> InvertedIndex:
    with open(path, "rb") as f:
        return pickle.load(f)

def save_index_json(index: InvertedIndex, path: Path):
    data = {
        "documents": {doc_id: {"doc_id": m.doc_id, "path": m.path, "length": m.length} for doc_id, m in index.documents.items()},
        "index": {term: [{"doc_id": p.doc_id, "freq": p.freq} for p in postings] for term, postings in index.index.items()}
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_index_json(path: Path) -> InvertedIndex:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    documents = {doc_id: DocMeta(**meta) for doc_id, meta in data["documents"].items()}
    index = {term: [Posting(**p) for p in postings] for term, postings in data["index"].items()}
    return InvertedIndex(index=index, documents=documents)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Build and save inverted index.")
    parser.add_argument("data_dir", type=Path, help="Path to corpus directory")
    parser.add_argument("--out", type=Path, required=True, help="Output index file")
    args = parser.parse_args()

    tracemalloc.start()
    start_time = time.perf_counter()

    print("Building index...")
    inv_index = build_index(args.data_dir)
    save_index(inv_index, args.out)

    end_time = time.perf_counter()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    print(f"Index successfully built and saved to {args.out}")
    print(f"Documents indexed: {len(inv_index.documents)}")
    print(f"Unique terms: {len(inv_index.index)}")
    print(f"Time: {end_time - start_time:.4f} seconds")
    print(f"Peak memory: {peak / 1024 / 1024:.2f} MB")