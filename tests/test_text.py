# -*- coding: utf-8 -*-
import pytest

from formasaurus.text import (
    normalize_whitespaces,
    normalize,
    ngrams,
    token_ngrams,
    tokenize,
)


@pytest.mark.parametrize(["text", "tokenized"], [
    ["Hello, world!", ["Hello", "world"]],
    ["I am hungry", ["I", "am", "hungry"]],
])
def test_tokenize(text, tokenized):
    assert tokenize(text) == tokenized


@pytest.mark.parametrize(["seq", "min_n", "max_n", "result"], [
    ["Hello", 2, 3, ["He", "el", "ll", "lo", "Hel", "ell", "llo"]],
    [["I", "am", "hungry"], 1, 2, [["I"], ["am"], ["hungry"], ["I", "am"], ["am", "hungry"]]],
])
def test_ngrams(seq, min_n, max_n, result):
    assert ngrams(seq, min_n, max_n) == result



@pytest.mark.parametrize(["seq", "min_n", "max_n", "result"], [
    [["I", "am", "hungry"], 1, 2, ["I", "am", "hungry", "I am", "am hungry"]],
])
def test_token_ngrams(seq, min_n, max_n, result):
    assert token_ngrams(seq, min_n, max_n) == result



@pytest.mark.parametrize(["text", "result"], [
    ["Hello    \tworld!", "Hello world!"],
    ["\nI\nam\n\r  hungry  ", " I am hungry "],
])
def test_normalize_whitespaces(text, result):
    assert normalize_whitespaces(text) == result


def test_normalize():
    assert normalize("Hello,\n  world!") == "hello, world!"
