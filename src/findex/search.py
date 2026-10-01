from findex.index import Posting, DocMeta, InvertedIndex
import time
import tracemalloc
import argparse
from pathlib import Path
from findex.index import load_index, InvertedIndex, Posting
from findex.tokenize import tokenize

def merge_and(postings1: list[Posting], postings2: list[Posting]) -> list[str]:
    i, j = 0, 0
    result = []
    while i < len(postings1) and j < len(postings2):
        doc1, doc2 = postings1[i].doc_id, postings2[j].doc_id
        if doc1 == doc2:
            result.append(doc1)
            i += 1
            j += 1
        elif doc1 < doc2:
            i += 1
        else:
            j += 1
    return result

def merge_or(postings1: list[Posting], postings2: list[Posting]) -> list[str]:
    i, j = 0, 0
    result = []
    while i < len(postings1) and j < len(postings2):
        doc1, doc2 = postings1[i].doc_id, postings2[j].doc_id
        if doc1 == doc2:
            result.append(doc1)
            i += 1
            j += 1
        elif doc1 < doc2:
            result.append(doc1)
            i += 1
        else:
            result.append(doc2)
            j += 1
    while i < len(postings1):
        result.append(postings1[i].doc_id)
        i += 1
    while j < len(postings2):
        result.append(postings2[j].doc_id)
        j += 1
    return result

def merge_not(postings1: list[Posting], postings2: list[Posting]) -> list[str]:
    docs2 = {p.doc_id for p in postings2}
    result = []
    for p in postings1:
        if p.doc_id not in docs2:
            result.append(p.doc_id)
    return result

def set_search(index: InvertedIndex, terms: list[str], op: str) -> list[str]:
    doc_sets = []
    for term in terms:
        postings = index.index.get(term, [])
        doc_sets.append({p.doc_id for p in postings})
    
    if not doc_sets:
        return []
    
    result_set = doc_sets[0]
    for s in doc_sets[1:]:
        if op == "AND":
            result_set = result_set.intersection(s)
        elif op == "OR":
            result_set = result_set.union(s)
        elif op == "NOT":
            result_set = result_set.difference(s)
    return sorted(list(result_set))

def evaluate_query(index: InvertedIndex, query: str, engine: str) -> list[str]:
    tokens = list(tokenize(query))
    if not tokens:
        return []
    
    upper_query = query.upper()
    op = "AND"
    if "OR" in upper_query:
        op = "OR"
    elif "NOT" in upper_query:
        op = "NOT"
    
    terms = [t for t in tokens if t not in ("and", "or", "not")]
    if len(terms) < 2:
        if terms:
            return [p.doc_id for p in index.index.get(terms[0], [])]
        return []

    term1, term2 = terms[0], terms[1]
    postings1 = index.index.get(term1, [])
    postings2 = index.index.get(term2, [])

    if engine == "set":
        return set_search(index, [term1, term2], op)
    else: 
        if op == "AND":
            return merge_and(postings1, postings2)
        elif op == "OR":
            return merge_or(postings1, postings2)
        elif op == "NOT":
            return merge_not(postings1, postings2)
    return []

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Search the inverted index.")
    parser.add_argument("index_file", type=Path, help="Path to index file")
    parser.add_argument("query", type=str, help="Search query")
    parser.add_argument("--engine", choices=["merge", "set"], default="merge", help="Search engine implementation")
    args = parser.parse_args()

    tracemalloc.start()
    start_time = time.perf_counter()

    index = load_index(args.index_file)
    results = evaluate_query(index, args.query, args.engine)

    end_time = time.perf_counter()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    print(f"Engine: {args.engine}")
    print(f"Found documents: {len(results)}")
    for doc_id in results:
        meta = index.documents.get(doc_id)
        if meta:
            print(f"  - {doc_id} ({meta.path})")
    print(f"Time: {end_time - start_time:.4f} seconds")
    print(f"Peak memory: {peak / 1024 / 1024:.2f} MB")
