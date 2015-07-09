# -*- coding: utf-8 -*-
from __future__ import absolute_import
import io
import lxml.html
import pytest
import formasaurus

LOGIN_PAGE = b'''
<html>
    <body>
        <form method=POST action="/login">
            Username: <input name="username" type="text">
            Password: <input name="password" type="passoword">
            <input type="submit" value="Login">
        </form>
    </body>
</html>
'''


@pytest.fixture
def ex():
    return formasaurus.FormExtractor.load()


@pytest.fixture
def tree():
    return lxml.html.parse(io.BytesIO(LOGIN_PAGE))


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
