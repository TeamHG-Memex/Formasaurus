# -*- coding: utf-8 -*-
"""
This module defines which features and which classifier the default model uses.
"""
from __future__ import absolute_import

from sklearn.feature_extraction import DictVectorizer
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.pipeline import make_pipeline, make_union
from sklearn.linear_model import SGDClassifier, LogisticRegression
from sklearn.svm import LinearSVC

from formasaurus import features

# a list of 3-tuples with default features: (feature_name, form_transformer, vectorizer)
FEATURES = [
    (
        "bias",
        features.Bias(),
        DictVectorizer(),
    ),
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
    #     TfidfVectorizer(ngram_range=(1,2), min_df=5, stop_words='english', binary=True)
    # ),

    (
        "<a> TEXT </a>",
        features.FormLinksText(),
        TfidfVectorizer(ngram_range=(1,2), min_df=4, stop_words={'and', 'or', 'of'}, binary=True)
    ),
    (
        "<label> TEXT </label>",
        features.FormLabelText(),
        TfidfVectorizer(ngram_range=(1,2), min_df=3, stop_words="english", binary=True)
    ),

    (
        "<form action=...>",
        features.FormUrl(),
        TfidfVectorizer(ngram_range=(5,6), min_df=4, analyzer="char_wb", binary=True)
    ),
    (
        "<form class=... id=...>",
        features.FormCss(),
        TfidfVectorizer(ngram_range=(4,5), min_df=3, analyzer="char_wb", binary=True)
    ),
    (
        "<input class=... id=...>",
        features.FormInputCss(),
        TfidfVectorizer(ngram_range=(4,5), min_df=5, analyzer="char_wb", binary=True)
    ),
    (
        "<input name=...>",
        features.FormInputNames(),
        TfidfVectorizer(ngram_range=(5,6), min_df=3, analyzer="char_wb", binary=True)
    ),
    (
        "<input title=...>",
        features.FormInputTitle(),
        TfidfVectorizer(ngram_range=(5,6), min_df=3, analyzer="char_wb", binary=True)
    ),
]


def _create_feature_union(features):
    """
    Create a FeatureUnion.
    Each "feature" is a 3-tuple: (name, feature_extractor, vectorizer).
    """
    return make_union(*[
        make_pipeline(fe, vec)
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
        clf = LogisticRegression(penalty='l2', C=5, fit_intercept=False)
    else:
        clf = LinearSVC(C=0.5, random_state=0, fit_intercept=False)

    fe = _create_feature_union(FEATURES)
    return make_pipeline(fe, clf)


