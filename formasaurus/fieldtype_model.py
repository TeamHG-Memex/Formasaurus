# -*- coding: utf-8 -*-
"""
Field type detection model is two-stage:

1. First, we train Formasaurus form type detector.
2. Second, we use form type detector results to improve quality of
   field type detection.

We have correct form types available directly in training data,
but in reality form type detecor will make mistakes at prediction time.
So we have two options:

1. Use correct form labels in training, rely on noisy form
   labels at test/prediction time.
2. Use noisy (predicted) labels both at train and test time.

Strategy (2) leads to more regularized models which account for form
type detector mistakes; strategy (1) uses more information.

Based on held-out dataset it looks like (1) produces better results.

We need noisy form type labels anyways, to check prediction quality.
To get these 'realistic' noisy form type labels we split data into 10 folds,
and then for each fold we predict its labels using form type detector
trained on the rest 9 folds.
"""
from __future__ import absolute_import, division
import warnings

import scipy.stats
import numpy as np
from sklearn.grid_search import RandomizedSearchCV
from sklearn.metrics import make_scorer
from sklearn.cross_validation import cross_val_predict
from sklearn_crfsuite import CRF
from sklearn_crfsuite.metrics import (
    flat_f1_score,
    flat_accuracy_score,
    flat_classification_report,
    sequence_accuracy_score
)
from sklearn_crfsuite.utils import flatten

from formasaurus import formtype_model
from formasaurus.html import get_fields_to_annotate, get_text_around_elems
from formasaurus.text import (normalize, tokenize, ngrams, number_pattern,
    token_ngrams)
from formasaurus.annotation import get_annotation_folds


scorer = make_scorer(flat_f1_score, average='micro')
""" Default scorer for grid search. We're optimizing for micro-averaged F1. """


def train(annotations,
          use_precise_form_types=True,
          optimize_hyperparameters_iters=0,
          optimize_hyperparameters_folds=5,
          optimize_hyperparameters_jobs=-1,
          full_form_type_names=False,
          full_field_type_names=True,
          verbose=True):

    def log(msg):
        if verbose:
            print(msg)

    annotations = [
        a for a in annotations
        if a.fields_annotated and (a.form_annotated or not use_precise_form_types)
    ]
    log("Training on {} forms".format(len(annotations)))

    if use_precise_form_types:
        log("Using precise form types")
        if full_form_type_names:
            form_types = np.asarray([a.type_full for a in annotations])
        else:
            form_types = np.asarray([a.type for a in annotations])
    else:
        log("Computing realistic form types")
        form_types = formtype_model.get_realistic_form_labels(
            annotations=annotations,
            n_folds=10,
            full_type_names=full_form_type_names
        )

    log("Extracting features")
    X, y = get_Xy(
        annotations=annotations,
        form_types=form_types,
        full_type_names=full_field_type_names,
    )

    crf = get_model(use_precise_form_types)

    if optimize_hyperparameters_iters != 0:
        if optimize_hyperparameters_iters < 50:
            warnings.warn(
                "RandomizedSearchCV n_iter is low, results may be unstable. "
                "Consider increasing optimize_hyperparameters_iters."
            )

        log("Finding best hyperparameters using randomized search")
        params_space = {
            'c1': scipy.stats.expon(scale=0.5),
            'c2': scipy.stats.expon(scale=0.05),
        }

        rs = RandomizedSearchCV(crf, params_space,
            cv=get_annotation_folds(annotations, optimize_hyperparameters_folds),
            verbose=verbose,
            n_jobs=optimize_hyperparameters_jobs,
            n_iter=optimize_hyperparameters_iters,
            iid=False,
            scoring=scorer
        )
        rs.fit(X, y)
        crf = rs.best_estimator_
        log("Best hyperparameters: c1={:0.5f}, c2={:0.5f}".format(crf.c1, crf.c2))
    else:
        crf.fit(X, y)

    return crf


def get_Xy(annotations, form_types, full_type_names=False):
    """
    Return training data for field type detection.
    """
    forms = [a.form for a in annotations]
    X = [
        get_form_features(form, form_type)
        for form, form_type in zip(forms, form_types)
    ]
    if full_type_names:
        y = [a.field_types_full for a in annotations]
    else:
        y = [a.field_types for a in annotations]
    return X, y


def get_form_features(form, form_type, field_elems=None):
    """
    Return a list of feature dicts, a dict per visible submittable
    field in a <form> element.
    """
    if field_elems is None:
        field_elems = get_fields_to_annotate(form)
    text_before, text_after = get_text_around_elems(form, field_elems)
    res = [_elem_features(elem) for elem in field_elems]

    for idx, elem_feat in enumerate(res):
        if idx == 0:
            elem_feat['is-first'] = True
        if idx == len(res)-1:
            elem_feat['is-last'] = True

        elem_feat['form-type'] = form_type
        # get text before element
        text = normalize(text_before[field_elems[idx]])
        tokens = tokenize(text)[-6:]
        elem_feat['text-before'] = token_ngrams(tokens, 1, 2)

        # get text after element
        text = normalize(text_after[field_elems[idx]])
        tokens = tokenize(text)[:5]
        elem_feat['text-after'] = token_ngrams(tokens, 1, 2)
        elem_feat['bias'] = 1

    return res


def _elem_features(elem):
    elem_name = normalize(elem.name)
    elem_value = _elem_attr(elem, 'value')
    elem_placeholder = _elem_attr(elem, 'placeholder')
    elem_css_class = _elem_attr(elem, 'class')
    elem_id = _elem_attr(elem, 'id')
    elem_title = _elem_attr(elem, 'title')

    feat = {
        'tag': elem.tag,
        'name': tokenize(elem_name),
        'name-ngrams-3-5': ngrams(elem_name, 3, 5),
        'value': ngrams(elem_value, 5, 5),
        'value-ngrams': ngrams(elem_value, 5, 5),
        'css-class-ngrams': ngrams(elem_css_class, 5, 5),
        'help': tokenize(elem_title + " " + elem_placeholder),
        'id-ngrams': ngrams(elem_id, 4, 4),
        'id': tokenize(elem_id),
    }
    label = elem.label
    if label is not None:
        label_text = normalize(label.text_content())
        feat['label'] = tokenize(label_text)
        feat['label-ngrams-3-5'] = ngrams(label_text, 3, 5)

    if elem.tag == 'input':
        feat['input-type'] = elem.get('type', 'text').lower()

    if elem.tag == 'select':
        feat['option-text'] = [normalize(v) for v in elem.xpath('option//text()')]
        feat['option-value'] = [normalize(el.get('value', '')) for el in elem.xpath('option')]
        feat['option-num-pattern'] = list(
            {number_pattern(v) for v in feat['option-text'] + feat['option-value']}
        )

    return feat


def _elem_attr(elem, attr):
    return normalize(elem.get(attr, ''))


_PRECISE_C1_C2 = 0.1655, 0.0236  # values found by randomized search
_REALISTIC_C1_C2 = 0.247, 0.032  # values found by randomized search


def get_model(use_precise_form_types=True):
    """ Return default CRF model """
    c1, c2 = _PRECISE_C1_C2 if use_precise_form_types else _REALISTIC_C1_C2
    return CRF(
        all_possible_transitions=True,
        max_iterations=100,
        c1=c1,
        c2=c2
    )


def print_classification_report(annotations, n_folds=10, model=None):
    """ Evaluate model, print classification report """
    if model is None:
        # FIXME: we're overfitting on hyperparameters - they should be chosen
        # using inner cross-validation, not set to fixed values beforehand.
        model = get_model(use_precise_form_types=True)

    annotations = [a for a in annotations if a.fields_annotated]
    form_types = formtype_model.get_realistic_form_labels(
        annotations=annotations,
        n_folds=n_folds,
        full_type_names=False
    )

    X, y = get_Xy(
        annotations=annotations,
        form_types=form_types,
        full_type_names=True,
    )
    cv = get_annotation_folds(annotations, n_folds=n_folds)
    y_pred = cross_val_predict(model, X, y, cv=cv, n_jobs=-1)

    all_labels = list(annotations[0].field_schema.types.keys())
    labels = sorted(set(flatten(y_pred)), key=lambda k: all_labels.index(k))
    print(flat_classification_report(y, y_pred, digits=2,
                                     labels=labels, target_names=labels))

    print(
        "{:0.1f}% fields are classified correctly.".format(
            flat_accuracy_score(y, y_pred) * 100
        )
    )
    print(
        "All fields are classified correctly in {:0.1f}% forms.".format(
            sequence_accuracy_score(y, y_pred) * 100
        )
    )
