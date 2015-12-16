# -*- coding: utf-8 -*-
from __future__ import absolute_import

import formasaurus
from formasaurus import classifiers
from formasaurus.html import get_forms


def test_extract_forms(tree):
    forms = formasaurus.extract_forms(tree)
    assert len(forms) == 1
    assert forms[0][1] == {
        'form': 'login',
        'fields': {'password': 'password', 'username': 'username'},
    }


def test_extract_forms_only(tree):
    ex = classifiers.instance()
    forms = ex.form_classifier.extract_forms(tree)
    assert len(forms) == 1
    assert forms[0][1] == 'login'


def test_extract_forms_proba(tree):
    forms = formasaurus.extract_forms(tree, proba=True, threshold=0)
    assert len(forms) == 1
    probs = forms[0][1]['form']
    assert probs['login'] > 0.5
    assert probs['contact/comment'] < 0.4
    assert probs['search'] < 0.4
    assert probs['registration'] < 0.4
    assert probs['join mailing list'] < 0.4
    assert probs['other'] < 0.4
    assert probs['password/login recovery'] < 0.4

    forms = formasaurus.extract_forms(tree, proba=True, threshold=0.3)
    assert len(forms) == 1
    probs = forms[0][1]['form']
    assert list(probs.keys()) == ['login']


def test_classify(tree):
    form = get_forms(tree)[0]
    assert formasaurus.classify(form) == {
        'form': 'login',
        'fields': {'password': 'password', 'username': 'username'},
    }


def test_classify_proba(tree):
    form = get_forms(tree)[0]
    res1 = formasaurus.classify_proba(form, threshold=0.05)
    res2 = formasaurus.extract_forms(tree, proba=True, threshold=0.05)[0][1]
    assert res1 == res2

