# -*- coding: utf-8 -*-
"""
This module defines which features and which classifier the default
form type detection model uses.
"""
from __future__ import absolute_import, division

import numpy as np
from sklearn.model_selection import cross_val_predict, GroupKFold
from sklearn.feature_extraction import DictVectorizer
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.metrics import classification_report, accuracy_score
from sklearn.pipeline import make_pipeline, FeatureUnion, Pipeline
from sklearn.linear_model import SGDClassifier, LogisticRegression
from sklearn.svm import LinearSVC

from formasaurus.utils import get_domain
from formasaurus import formtype_features as features


# a list of 3-tuples with default features:
# (feature_name, form_transformer, vectorizer)
FEATURES = [
    (
        "form elements",
        features.FormElements(),
        DictVectorizer()
    ),
    (
        "<input type=submit value=...>",
        features.SubmitText(),
        CountVectorizer(ngram_range=(1,2), min_df=1, binary=True)
    ),
    # (
    #     "<form> TEXT </form>",
    #     features.FormText(),
    #     TfidfVectorizer(ngram_range=(1,2), min_df=5, stop_words='english',
    #                     binary=True)
    # ),

    (
        "<a> TEXT </a>",
        features.FormLinksText(),
        TfidfVectorizer(ngram_range=(1,2), min_df=4, binary=True,
                        stop_words={'and', 'or', 'of'})
    ),
    (
        "<label> TEXT </label>",
        features.FormLabelText(),
        TfidfVectorizer(ngram_range=(1,2), min_df=3, binary=True,
                        stop_words="english")
    ),

    (
        "<form action=...>",
        features.FormUrl(),
        TfidfVectorizer(ngram_range=(5,6), min_df=4, binary=True,
                        analyzer="char_wb")
    ),
    (
        "<form class=... id=...>",
        features.FormCss(),
        TfidfVectorizer(ngram_range=(4,5), min_df=3, binary=True,
                        analyzer="char_wb")
    ),
    (
        "<input class=... id=...>",
        features.FormInputCss(),
        TfidfVectorizer(ngram_range=(4,5), min_df=5, binary=True,
                        analyzer="char_wb")
    ),
    (
        "<input name=...>",
        features.FormInputNames(),
        TfidfVectorizer(ngram_range=(5,6), min_df=3, binary=True,
                        analyzer="char_wb")
    ),
    (
        "<input title=...>",
        features.FormInputTitle(),
        TfidfVectorizer(ngram_range=(5,6), min_df=3, binary=True,
                        analyzer="char_wb")
    ),
]


if hasattr(Pipeline, 'get_feature_names'):
    _PipelineWithFeatureNames = Pipeline
else:
    class _PipelineWithFeatureNames(Pipeline):
        def get_feature_names(self):
            return self.steps[-1][1].get_feature_names()


def _create_feature_union(features):
    """
    Create a FeatureUnion.
    Each "feature" is a 3-tuple: (name, feature_extractor, vectorizer).
    """
    return FeatureUnion([
        (name, _PipelineWithFeatureNames([('fe', fe), ('vec', vec)]))
        for name, fe, vec in features
    ])


def get_model(prob=True):
    """
    Return a default model.
    """
    # XXX: fit_intercept is False for easier model debugging.
    # Intercept is included as a regular feature ("Bias").

    if prob:
        # clf = SGDClassifier(
        #     penalty='elasticnet',
        #     loss='log',
        #     alpha=0.0002,
        #     n_iter=50,
        #     shuffle=True,
        #     random_state=0,
        #     fit_intercept=False,
        # )
        clf = LogisticRegression(penalty='l2', C=5, fit_intercept=True)
    else:
        clf = LinearSVC(C=0.5, random_state=0, fit_intercept=True)

    fe = _create_feature_union(FEATURES)
    return make_pipeline(fe, clf)


def train(annotations, model=None, full_type_names=False):
    """ Train form type detection model on annotation data """
    if model is None:
        model = get_model()
    X, y = get_Xy(annotations, full_type_names)
    return model.fit(X, y)


def get_Xy(annotations, full_type_names):
    X = [a.form for a in annotations]

    if full_type_names:
        y = np.asarray([a.type_full for a in annotations])
    else:
        y = np.asarray([a.type for a in annotations])

    return X, y


def get_realistic_form_labels(annotations, n_splits=10, model=None,
                              full_type_names=True):
    """
    Return form type labels which form type detection model
    is likely to produce.
    """
    if model is None:
        model = get_model()

    X, y = get_Xy(annotations, full_type_names)
    group_kfold = GroupKFold(n_splits=n_splits)
    groups = [get_domain(ann.url) for ann in annotations]
    return cross_val_predict(model, X, y, cv=group_kfold, groups=groups)


def print_classification_report(annotations, n_splits=10, model=None):
    """ Evaluate model, print classification report """
    if model is None:
        # FIXME: we're overfitting on hyperparameters - they should be chosen
        # using inner cross-validation, not set to fixed values beforehand.
        model = get_model()

    X, y = get_Xy(annotations, full_type_names=True)
    group_kfold = GroupKFold(n_splits=n_splits)
    groups = [get_domain(ann.url) for ann in annotations]
    y_pred = cross_val_predict(model, X, y, cv=group_kfold, groups=groups)

    # hack to format report nicely
    all_labels = list(annotations[0].form_schema.types.keys())
    labels = sorted(set(y_pred), key=lambda k: all_labels.index(k))
    print(classification_report(y, y_pred, digits=2,
                                labels=labels, target_names=labels))

    print("{:0.1f}% forms are classified correctly.".format(
        accuracy_score(y, y_pred) * 100
    ))
