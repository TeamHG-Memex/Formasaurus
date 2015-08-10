# -*- coding: utf-8 -*-
"""
This module provides helper functions for evaluating formasaurus quality.
"""
from __future__ import absolute_import, print_function
from distutils.version import LooseVersion

import numpy as np
import sklearn
from sklearn.cross_validation import cross_val_score
from sklearn.metrics import classification_report, confusion_matrix

from .storage import FORM_TYPES_INV


SKLEARN_VERSION = LooseVersion(sklearn.__version__)


def print_sparsity(clf):
    """
    Print a number of classifier non-zero coefficients.
    FIXME: it does not take intercept into account.
    """
    n_classes, n_features = clf.coef_.shape
    n_active = (clf.coef_ != 0).sum()
    n_possible = n_features*n_classes
    print("Active features: %d out of possible %d" % (n_active, n_possible))


def print_cv_scores(model, X, y, cv=10):
    """ Print cross-validation scores of a classifier """
    scoring = 'f1' if SKLEARN_VERSION < '0.16' else 'f1_weighted'
    cv_scores = cross_val_score(model, X, y, scoring=scoring, cv=cv,
                                verbose=False)
    print(
        u"%d-fold cross-validation F1: %0.3f (±%0.3f)  min=%0.3f  max=%0.3f" % (
        cv, cv_scores.mean(),  cv_scores.std() * 2,
        cv_scores.min(), cv_scores.max())
    )


def fit_and_predict(model, X_train, X_test, y_train):
    model.fit(X_train, y_train)
    return model.predict(X_test)


def print_classification_report(y_train,y_test, y_pred, class_labels=None):
    """ Print the classification report """
    print(
        "\nClassification report (%d training examples, %d testing "
        "examples):\n" % (len(y_train), len(y_test))
    )
    print(classification_report(y_test, y_pred, target_names=class_labels))


def get_class_labels(clf):
    """ Return full names of labels the classifier uses """
    return [FORM_TYPES_INV[c] for c in clf.classes_]


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


def print_metrics(model, X, y, X_train, X_test, y_train, y_test,
                  ipython=False, cv=10, short_matrix=False):
    clf = model.steps[-1][1]
    y_pred = fit_and_predict(model, X_train, X_test, y_train)
    class_labels = get_class_labels(clf)

    print_classification_report(y_train, y_test, y_pred, class_labels)
    print_sparsity(clf)

    if short_matrix:
        class_labels = clf.classes_
    print_confusion_matrix(y_test, y_pred, class_labels, ipython=ipython)

    print("\nRunning cross validation...")
    print_cv_scores(model, X, y, cv=cv)


def get_informative_features(vectorizers, clf, class_labels, N):
    """
    Return text with features with the highest absolute coefficient
    values, per class.
    """
    feature_names = []
    for vec_name, vec in vectorizers:
        feature_names.extend(
            "%30s  %s" % (vec_name, name) for name in vec.get_feature_names()
        )
    features_by_class = []
    for i, class_label in enumerate(class_labels):
        topN = np.argsort(clf.coef_[i])[-N:]
        bottomN = np.argsort(clf.coef_[i])[:N]
        res = []

        for j in reversed(topN):
            coef = clf.coef_[i][j]
            if coef > 0:
                res.append("+%0.4f: %s" % (coef, feature_names[j]))

        if (len(topN) >= N) or (len(bottomN) >= N):
            res.append("   ...")

        for j in reversed(bottomN):
            coef = clf.coef_[i][j]
            if coef < 0:
                res.append("%0.4f: %s" % (coef, feature_names[j]))
        features_by_class.append((class_label, '\n'.join(res)))
    return features_by_class


def print_informative_features(features, clf, top, classes=None):
    vectorizers = [(name, vec) for (name, fe, vec) in features]
    feat_info = get_informative_features(vectorizers, clf, clf.classes_, top)
    for cls, report in feat_info:
        if classes is not None and cls not in classes:
            continue
        print(FORM_TYPES_INV[cls])
        print(report)
        print("-"*80)
