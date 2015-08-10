# -*- coding: utf-8 -*-
from __future__ import absolute_import
import os

import pytest

import formasaurus


def test_non_existing_model(tmpdir):
    model = os.path.join(str(tmpdir), 'm.joblib')
    assert not os.path.exists(model)

    with pytest.raises(IOError):
        ex = formasaurus.FormExtractor.load(model, create=False)

    assert not os.path.exists(model)


def test_create_model(tmpdir):
    model = os.path.join(str(tmpdir), 'm.joblib')
    ex = formasaurus.FormExtractor.load(model)
    assert os.path.exists(model)
