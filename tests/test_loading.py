import os

import pytest

import formasaurus


def test_non_existing_model(tmpdir):
    model = os.path.join(str(tmpdir), "m.joblib")
    assert not os.path.exists(model)

    with pytest.raises(IOError):
        formasaurus.FormFieldClassifier.load(model, autocreate=False)

    assert not os.path.exists(model)


def test_autocreate_model(tmpdir):
    model = os.path.join(str(tmpdir), "m.joblib")
    formasaurus.FormFieldClassifier.load(model)
    assert os.path.exists(model)


def test_rebuild_model(tmpdir):
    path = os.path.join(str(tmpdir), "m.joblib")
    formasaurus.FormFieldClassifier.load(path)
    mtime1 = os.path.getmtime(path)

    formasaurus.FormFieldClassifier.load(path)
    mtime2 = os.path.getmtime(path)

    formasaurus.FormFieldClassifier.load(path, rebuild=True)
    mtime3 = os.path.getmtime(path)

    assert mtime2 == mtime1
    assert mtime3 > mtime1
