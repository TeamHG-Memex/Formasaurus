# -*- coding: utf-8 -*-
from __future__ import absolute_import
import os
import sys

import requests
from requests.compat import chardet
from w3lib.encoding import html_to_unicode
import tldextract


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


def at_root(*args):
    """ Return path relative to formasaurus source code """
    return os.path.join(os.path.dirname(__file__), *args)


def thresholded(dct, threshold):
    """
    Return dict ``dct`` without all values less than threshold.

    >>> thresholded({'foo': 0.5, 'bar': 0.1}, 0.5)
    {'foo': 0.5}

    >>> thresholded({'foo': 0.5, 'bar': 0.1, 'baz': 1.0}, 0.6)
    {'baz': 1.0}

    >>> dct = {'foo': 0.5, 'bar': 0.1, 'baz': 1.0, 'spam': 0.0}
    >>> thresholded(dct, 0.0) == dct
    True
    """
    return {k: v for k, v in dct.items() if v >= threshold}


def download(url):
    """
    Download a web page from url, return its content as unicode.
    """
    url = add_scheme_if_missing(url)
    resp = requests.get(url)
    return response2unicode(resp)


def response2unicode(resp):
    """
    Convert requests.Response body to unicode.
    Unlike ``response.text`` it handles <meta> tags in response content.
    """
    enc, html = html_to_unicode(
        content_type_header=resp.headers.get('Content-Type'),
        html_body_str=resp.content,
        auto_detect_fun=_autodetect_encoding
    )
    return html


def _autodetect_encoding(binary_data):
    return chardet.detect(binary_data)['encoding']
