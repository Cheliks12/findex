from findex.tokenize import tokenize

def test_tokenize_basic():
    text = "Hello, world! This is a test string with Python 3.11."
    tokens = list(tokenize(text))
    assert "hello" in tokens
    assert "world" in tokens
    assert "python" in tokens
    assert "3" in tokens

def test_tokenize_unicode_and_apostrophe():
    text = "Five objects, cafe, résumé, o'connor."
    tokens = list(tokenize(text))
    assert "five" in tokens
    assert "cafe" in tokens
    assert "résumé" in tokens
    assert "o'connor" in tokens