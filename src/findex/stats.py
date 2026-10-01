import time
import tracemalloc
from collections import Counter
from pathlib import Path
from findex.corpus import iter_documents
from findex.tokenize import tokenize

def analyze_corpus(root: Path):
    tracemalloc.start()
    start_time = time.perf_counter()

    doc_count = 0
    total_tokens = 0
    token_counter = Counter()

    for doc in iter_documents(root):
        doc_count += 1
        tokens = list(tokenize(doc.text))
        total_tokens += len(tokens)
        token_counter.update(tokens)

    end_time = time.perf_counter()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    elapsed_time = end_time - start_time
    peak_mb = peak / 1024 / 1024

    print(f"Documents processed: {doc_count}")
    print(f"Total tokens: {total_tokens}")
    print(f"Unique tokens (vocabulary size): {len(token_counter)}")
    print(f"Execution time: {elapsed_time:.4f} seconds")
    print(f"Peak memory usage: {peak_mb:.2f} MB")
    
    print("\nTop 50 terms:")
    for term, freq in token_counter.most_common(50):
        print(f"  {term}: {freq}")

if __name__ == "__main__":
    data_dir = Path("data")
    analyze_corpus(data_dir)