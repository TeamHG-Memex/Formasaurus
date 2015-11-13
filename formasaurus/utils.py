# -*- coding: utf-8 -*-
from __future__ import absolute_import
import sys
import tldextract


def dependencies_string():
    """
    Return a string with versions of numpy, scipy and scikit-learn.

    Saved scikit-learn models may be not compatible between different
    numpy/scipy/scikit-learn versions; a string returned by this function
    can be used as a part of file name.
    """
    import numpy
    import scipy
    import sklearn
    py_version = "%s.%s" % sys.version_info[:2]

    return "py%s-numpy%s-scipy%s-sklearn%s" % (
        py_version, numpy.__version__, scipy.__version__, sklearn.__version__
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

