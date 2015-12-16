# -*- coding: utf-8 -*-
from __future__ import absolute_import
import io

import lxml.html
import pytest

from formasaurus.classifiers import DEFAULT_DATA_PATH
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
                {"short": "o", "full": "other"},
                {"short": "X", "full": "NOT ANNOTATED"}
            ],
            "simplify_map": {
                "l": "o",
            },
            "NA_value": "X",
            "skip_value": "-"
        },

        "field_types": {
            "types": [
                {"short": "us", "full": "username"},
                {"short": "p1", "full": "password"},
                {"short": "qq", "full": "search query"},
                {"short": "XX", "full": "NOT ANNOTATED"}
            ],
            "simplify_map": {},
            "NA_value": "XX",
            "skip_value": "--"
        }
    }
    storage.initialize(config)
    return storage
