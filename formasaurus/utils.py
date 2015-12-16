# -*- coding: utf-8 -*-
from __future__ import absolute_import
import sys

import requests
import tldextract
from sklearn.cross_validation import LabelKFold


def dependencies_string():
    """
    Return a string with versions of formasaurus, numpy, scipy and scikit-learn.

    Saved scikit-learn models may be not compatible between different
    numpy/scipy/scikit-learn versions; a string returned by this function
    can be used as a part of file name.
    """
    import numpy
    import scipy
    import sklearn
    import formasaurus

    py_version = "%s.%s" % sys.version_info[:2]

    return "%s-py%s-numpy%s-scipy%s-sklearn%s" % (
        formasaurus.__version__, py_version,
        numpy.__version__, scipy.__version__, sklearn.__version__
    )


def add_scheme_if_missing(url):
    """
    >>> add_scheme_if_missing("example.org")
    'http://example.org'
    >>> add_scheme_if_missing("https://example.org")
    'https://example.org'
    """
    if "//" not in url:
        url = "http://%s" % url
    return url


def get_domain(url):
    """
    >>> get_domain('example.org')
    'example'
    >>> get_domain('foo.example.co.uk')
    'example'
    """
    return tldextract.extract(url).domain


def inverse_mapping(dct):
    """
    Return reverse mapping:

    >>> inverse_mapping({'x': 5})
    {5: 'x'}
    """
    return {v:k for k,v in dct.items()}


def select_by_index(arr, index):
    """
    Like numpy indexing, but for lists. This is for cases
    conversion to numpy array is problematic.

    >>> select_by_index(['a', 'b', 'c', 'd'], [0, 3])
    ['a', 'd']
    """
    return [arr[i] for i in index]


def get_annotation_folds(annotations, n_folds):
    """
    Return (train_indices, test_indices) folds iterator.
    It is guaranteed forms from the same website can't be both in
    train and test parts.
    """
    return LabelKFold(
        labels=[get_domain(ann.url) for ann in annotations],
        n_folds=n_folds
    )


def get_annotation_train_test_indices(annotations, n_folds=4):
    """
    Split annotations into train and test parts, return train and test indices.
    The size of test part is approximately ``len(annotations)/n_folds``.
    it is guaranteed forms from the same website can't be both
    in train and test parts.
    """
    for idx_train, idx_test in get_annotation_folds(annotations, n_folds):
        break
    return idx_train, idx_test


def download(url):
    """
    Download a web page from url, return its content as unicode.
    """
    return requests.get(url).text
