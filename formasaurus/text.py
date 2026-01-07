# -*- coding: utf-8 -*-
from __future__ import absolute_import, division
import re

tokenize = re.compile(r"(?u)\b\w+\b").findall
""" Tokenize text """


def ngrams(seq, min_n, max_n):
    """
    Return min_n to max_n n-grams of elements from a given sequence.
    """
    text_len = len(seq)
    res = []
    for n in range(min_n, min(max_n + 1, text_len + 1)):
        for i in range(text_len - n + 1):
            res.append(seq[i: i + n])
    return res


def token_ngrams(tokens, min_n, max_n):
    """
    Return n-grams given a list of tokens.
    """
    return [' '.join(t) for t in ngrams(tokens, min_n, max_n)]


_replace_white_spaces = re.compile(r"\s\s+").sub
_replace_newlines = re.compile(r'[\n\r]').sub
def normalize_whitespaces(text):
    """ Replace newlines and whitespaces with a single white space """
    text = _replace_newlines(" ", text)
    return _replace_white_spaces(" ", text)


def normalize(text):
    """ Default text normalization function """
    return normalize_whitespaces(text.lower())


def number_pattern(text, ratio=0.3):
    """
    Replace digits with X and letters with C if text contains > ratio
    of digits; return empty string otherwise.
    """
    if not text:
        return ''
    digit_ratio = sum(1 for ch in text if ch.isdigit()) / len(text)

    if digit_ratio >= ratio:
        num_pattern = re.sub('\d', 'X', text)
        return re.sub('[^X\W]', 'C', num_pattern)
    else:
        return ''


