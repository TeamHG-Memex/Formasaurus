# -*- coding: utf-8 -*-
from __future__ import absolute_import
import io

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


@pytest.fixture
def storage():
    return Storage(DEFAULT_DATA_PATH)
