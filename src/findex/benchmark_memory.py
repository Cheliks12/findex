import tracemalloc
import time
from array import array
from dataclasses import dataclass
from pathlib import Path
from findex.corpus import iter_documents
from findex.tokenize import tokenize
from collections import defaultdict, Counter

@dataclass
class PostingNormal:
    doc_id: str
    freq: int

@dataclass(frozen=True, slots=True)
class PostingSlots:
    doc_id: str
    freq: int

def measure_memory(variant_type, root: Path):
    tracemalloc.start()
    start_time = time.perf_counter()
    
    if variant_type == "normal":
        index = defaultdict(list)
        for doc in iter_documents(root):
            tokens = list(tokenize(doc.text))
            for term, freq in Counter(tokens).items():
                index[term].append(PostingNormal(doc_id=doc.doc_id, freq=freq))
    elif variant_type == "slots":
        index = defaultdict(list)
        for doc in iter_documents(root):
            tokens = list(tokenize(doc.text))
            for term, freq in Counter(tokens).items():
                index[term].append(PostingSlots(doc_id=doc.doc_id, freq=freq))
    elif variant_type == "array":
        index = defaultdict(lambda: {"docs": array('I'), "freqs": array('I')})
        for doc in iter_documents(root):
            tokens = list(tokenize(doc.text))
            doc_num = int(doc.doc_id.replace("test", ""))
            for term, freq in Counter(tokens).items():
                index[term]["docs"].append(doc_num)
                index[term]["freqs"].append(freq)

    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return peak / 1024 / 1024

if __name__ == "__main__":
    data_dir = Path("data")
    print("Memory Benchmark:")
    print(f"1. Normal dataclass peak memory: {measure_memory('normal', data_dir):.4f} MB")
    print(f"2. Slots dataclass peak memory: {measure_memory('slots', data_dir):.4f} MB")
    print(f"3. Array 'I' peak memory: {measure_memory('array', data_dir):.4f} MB")
