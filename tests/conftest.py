# -*- coding: utf-8 -*-
from __future__ import absolute_import
import io
import json

import lxml.html
import pytest

import formasaurus
from formasaurus.extractor import DEFAULT_DATA_PATH
from formasaurus.storage import Storage


LOGIN_PAGE = b'''
<html>
    <body>
        <form method=POST action="/login">
            Username: <input name="username" type="text">
            Password: <input name="password" type="password">
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


@pytest.fixture
def storage():
    return Storage(DEFAULT_DATA_PATH)


@pytest.fixture
def empty_storage(tmpdir):
    storage = Storage(str(tmpdir))
    config = {
        "form_types": {
            "types": [
                {"short": "s", "full": "search"},
                {"short": "l", "full": "login"},
                {"short": "X", "full": "NOT ANNOTATED"}
            ],
            "NA_value": "X"
        },

        "field_types": {
            "types": [
                {"short": "us", "full": "username"},
                {"short": "p1", "full": "password"},
                {"short": "qq", "full": "search query"},
                {"short": "XX", "full": "NOT ANNOTATED"}
            ],
            "NA_value": "XX"
        }
    }
    storage.initialize(config)
    return storage
