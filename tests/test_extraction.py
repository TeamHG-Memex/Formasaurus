# -*- coding: utf-8 -*-
from __future__ import absolute_import


def test_extract_forms(ex, tree):
    forms = ex.extract_forms(tree)
    assert len(forms) == 1
    assert forms[0][1] == 'l'  # login form


def test_extract_forms_proba(ex, tree):
    forms = ex.extract_forms_proba(tree)
    assert len(forms) == 1
    probs = forms[0][1]
    assert probs['l'] > 0.5
    assert probs['c'] < 0.4
    assert probs['s'] < 0.4
    assert probs['r'] < 0.4
    assert probs['m'] < 0.4
    assert probs['o'] < 0.4
    assert probs['p'] < 0.4

    forms = ex.extract_forms_proba(tree, 0.3)
    assert len(forms) == 1
    probs = forms[0][1]
    assert list(probs.keys()) == ['l']
