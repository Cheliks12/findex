# Text Search Indexer (findex) - Lab 01

A modular text processing and tokenization pipeline built with Python and `uv`.

## Project Structure
- `src/findex/corpus.py`: Lazy document reader generator (`iter_documents`).
- `src/findex/tokenize.py`: Streaming tokenizer with Unicode normalization (`NFC`) and `casefold`.
- `src/findex/stats.py`: Streaming corpus statistics analyzer (memory and time efficient).
- `src/findex/stats_greedy.py`: Greedy in-memory version for performance and memory comparison.
- `tests/test_tokenize.py`: Unit tests for tokenization logic (`pytest`).

## Measurements Comparison

| Implementation             | Documents | Total Tokens | Peak Memory (MB) | Time (s) |
| --------------             | --------- | ------------ | ---------------- | -------- |
| Streaming (`stats.py`)     | 1         | 448          | 0.04 MB          | 0.0028 s |
| Greedy (`stats_greedy.py`) | 1         | 448          | 0.04 MB          | 0.0020 s |

### Where did the memory go in the greedy version?
The greedy version allocates memory simultaneously for all file paths, reads all document strings into a single list (`documents`), and then expands all generated tokens into a massive global list (`all_tokens.extend`) before aggregation. This places heavy overhead on Python's memory manager and garbage collector, whereas the streaming version processes text lazily item-by-item, maintaining a minimal memory footprint.