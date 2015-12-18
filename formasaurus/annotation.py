# -*- coding: utf-8 -*-
"""
HTML forms interactive annotation utilities.
"""
from __future__ import absolute_import, print_function
import sys

from sklearn.cross_validation import LabelKFold

from formasaurus.html import get_cleaned_form_html
from formasaurus.utils import get_domain
from formasaurus.storage import Storage


def check_annotated_data(data_folder):
    """
    Check that annotated data is correct; exit with code 1 if it is not.
    """
    storage = Storage(data_folder)
    errors = storage.check()
    storage.print_form_type_counts(simplify=False)
    storage.print_form_type_counts(simplify=True)
    print("Errors:", errors)
    if errors:
        sys.exit(1)


def print_form_html(form):
    """ Print a cleaned up version of <form> HTML contents """
    print(get_cleaned_form_html(form))


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
