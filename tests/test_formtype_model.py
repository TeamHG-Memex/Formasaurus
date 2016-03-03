# -*- coding: utf-8 -*-
from __future__ import absolute_import, division
import itertools

from sklearn.metrics import accuracy_score

from formasaurus.formtype_model import get_realistic_form_labels


def test_get_realistic_formtypes(storage):
    annotations = list(itertools.islice(storage.iter_annotations(), 0, 300))
    y_true = [a.type_full for a in annotations]
    y_pred = get_realistic_form_labels(annotations, n_folds=3)
    score = accuracy_score(y_true, y_pred)
    assert 0.7 < score < 0.98

