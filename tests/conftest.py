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

