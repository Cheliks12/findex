import time
import tracemalloc
from pathlib import Path
from findex.index import load_index, InvertedIndex, Posting, DocMeta
from findex.search import evaluate_query

if __name__ == "__main__":
    index_path = Path("index.bin")
    if not index_path.exists():
        print("Index file not found! Run index.py first.")
        exit(1)

    index = load_index(index_path)
    
    term_counts = [(term, len(postings)) for term, postings in index.index.items()]
    term_counts.sort(key=lambda x: x[1], reverse=True)
    
    frequent_term = term_counts[0][0] if term_counts else "test"
    rare_term = term_counts[-1][0] if term_counts else "test"
    
    query = f"{frequent_term} AND {rare_term}"
    print(f"Running benchmark for query: '{query}'")

    for engine in ["merge", "set"]:
        tracemalloc.start()
        start = time.perf_counter()
        res = evaluate_query(index, query, engine)
        end = time.perf_counter()
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        print(f"Engine [{engine}]: time = {(end - start)*1000:.4f} ms, peak memory = {peak / 1024:.2f} KB, found = {len(res)}")