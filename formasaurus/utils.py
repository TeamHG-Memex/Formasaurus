# -*- coding: utf-8 -*-
from __future__ import absolute_import  
import sys


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
