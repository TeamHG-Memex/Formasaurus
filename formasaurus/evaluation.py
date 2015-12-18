# -*- coding: utf-8 -*-
"""
This module provides helper functions for evaluating formasaurus quality.
"""
from __future__ import absolute_import, print_function

import numpy as np
from sklearn.metrics import confusion_matrix


def print_sparsity(clf):
    """
    Print a number of classifier non-zero coefficients.
    FIXME: it does not take intercept into account.
    """
    n_classes, n_features = clf.coef_.shape
    n_active = (clf.coef_ != 0).sum()
    n_possible = n_features * n_classes
    print("Active features: %d out of possible %d" % (n_active, n_possible))


def df_confusion_matrix(y_test, y_pred, class_labels=None):
    """
    Return the confusion matrix as pandas.DataFrame.
    """
    import pandas as pd
    return pd.DataFrame(
        confusion_matrix(y_test, y_pred),
        columns=class_labels,
        index=class_labels,
    )


def print_confusion_matrix(y_test, y_pred, class_labels=None, ipython=False):
    print("\nConfusion matrix (rows=>true values, columns=>predicted values):")
    df = df_confusion_matrix(y_test, y_pred, class_labels)
    if ipython:
        from IPython.display import display
        display(df)
    else:
        print(df)
