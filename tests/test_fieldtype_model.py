# -*- coding: utf-8 -*-
from sklearn.metrics import accuracy_score

from formasaurus.fieldtype_model import (
    get_realistic_form_labels
)


def test_get_realistic_formtypes(storage):
    annotations = list(storage.iter_annotations())
    y_true = [a.type_full for a in annotations]
    y_pred = get_realistic_form_labels(annotations, n_folds=5)
    score = accuracy_score(y_true, y_pred)
    assert 0.7 < score < 0.98
