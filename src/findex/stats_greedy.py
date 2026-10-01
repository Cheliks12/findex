import time
import tracemalloc
from collections import Counter
from pathlib import Path
from findex.tokenize import tokenize

def analyze_corpus_greedy(root: Path):
    tracemalloc.start()
    start_time = time.perf_counter()

    if not root.exists():
        return

    all_paths = list(root.rglob("*.txt"))
    documents = []
    for path in all_paths:
        if path.is_file():
            text = path.read_text(encoding="utf-8", errors="replace")
            documents.append((path.stem, text))

    doc_count = len(documents)
    all_tokens = []
    for _, text in documents:
        tokens = list(tokenize(text))
        all_tokens.extend(tokens)

    total_tokens = len(all_tokens)
    token_counter = Counter(all_tokens)

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
    analyze_corpus_greedy(data_dir)