import pytest

import formasaurus
from formasaurus import classifiers
from formasaurus.html import get_forms


def test_extract_forms(tree):
    forms = formasaurus.extract_forms(tree)
    assert len(forms) == 1
    assert forms[0][1] == {
        "form": "login",
        "fields": {"password": "password", "username": "username"},
    }


def test_extract_forms_no_fields(tree):
    forms = formasaurus.extract_forms(tree, fields=False)
    assert len(forms) == 1
    assert forms[0][1] == {"form": "login"}


def test_extract_forms_no_fields_direct(tree):
    ex = classifiers.get_instance()
    forms = ex.form_classifier.extract_forms(tree)
    assert len(forms) == 1
    assert forms[0][1] == "login"


def test_classes():
    ex = classifiers.get_instance()
    assert "registration" in ex.form_classes
    assert "password" in ex.field_classes


@pytest.mark.parametrize(["fields"], [[True], [False]])
def test_extract_forms_proba(tree, fields):
    forms = formasaurus.extract_forms(tree, proba=True, threshold=0, fields=fields)
    assert len(forms) == 1
    probs = forms[0][1]["form"]
    assert probs["login"] > 0.5
    assert probs["contact/comment"] < 0.4
    assert probs["search"] < 0.4
    assert probs["registration"] < 0.4
    assert probs["join mailing list"] < 0.4
    assert probs["other"] < 0.4
    assert probs["password/login recovery"] < 0.4

    if fields:
        field_probs = forms[0][1]["fields"]
        assert sorted(field_probs.keys()) == ["password", "username"]
        assert field_probs["password"]["password"] > 0.9
        assert field_probs["username"]["username"] > 0.9

        assert 1.0 - 1e-6 < sum(field_probs["password"].values()) < 1.0 + 1e-6
        assert 1.0 - 1e-6 < sum(field_probs["username"].values()) < 1.0 + 1e-6


def test_extract_forms_proba_threshold(tree):
    forms = formasaurus.extract_forms(tree, proba=True, threshold=0.3)
    assert len(forms) == 1
    probs = forms[0][1]["form"]
    assert list(probs.keys()) == ["login"]


def test_classify(tree):
    form = get_forms(tree)[0]
    assert formasaurus.classify(form) == {
        "form": "login",
        "fields": {"password": "password", "username": "username"},
    }


def test_classify_proba(tree):
    form = get_forms(tree)[0]
    res1 = formasaurus.classify_proba(form, threshold=0.05)
    res2 = formasaurus.extract_forms(tree, proba=True, threshold=0.05)[0][1]
    assert res1 == res2
