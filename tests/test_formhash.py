# -*- coding: utf-8 -*-
import pytest
from formasaurus.formhash import get_form_hash

FORM_HIDDEN1 = """
<form>
    <input type='text' name='foo'/>
    <input type='hidden' name='mytoken' value='shdgfhsgf'/>
    <input type='submit' value='go'/>
</form>
"""

FORM_HIDDEN2 = """
<form>
    <input type='text' name='foo'></input>
    <input type='hidden' name='mytoken' value='zxmcnvbnbv'/>
    <input type='submit' value='go'/>
</form>
"""


@pytest.mark.parametrize(["form1", "form2"], [
    [
        "<form>Hello!</form>",
        "<FORM>Hello!</FORM>"
    ],
    pytest.param(
        "<form>Hello world</form>",
        "<FORM>Hello  world</FORM>",
        marks=pytest.mark.xfail,
    ),
    pytest.param(
        "<form action='/' method='GET'>Hello!</form>",
        "<FORM method='GET' action='/'>Hello!</FORM>",
        marks=pytest.mark.xfail,
    ),
    pytest.param(
        "<form method='get' action='/'>Hello!</form>",
        "<FORM method='GET' action='/'>Hello!</FORM>",
        marks=pytest.mark.xfail,
    ),
    pytest.param(
        "<form action='/'>Hello!</form>",
        "<FORM method='GET' action='/'>Hello!</FORM>",
        marks=pytest.mark.xfail,
    ),
    [
        """
        <form>
            <input type='text' name='foo'></input>
            <input type='submit' value='go'/>
        </form>
        """,
        """
        <form>
            <input type='text' name='foo'></input>
            <input type='submit' value='go'/>
        </form>
        """,
    ],
    [FORM_HIDDEN1, FORM_HIDDEN2],

])
def test_formhash_equal(form1, form2):
    assert get_form_hash(form1) == get_form_hash(form2)



@pytest.mark.parametrize(["form1", "form2"], [
    [
        "<form>Hello!</form>",
        "<form>Hello</FORM>"
    ],
    [
        """
        <form>
            <input type='text' name='foo'></input>
            <input type='submit' value='go'/>
        </form>
        """,
        """
        <form>
            <input type='text' name='bar'></input>
            <input type='submit' value='go'/>
        </form>
        """,
    ],
])
def test_formhash_not_equal(form1, form2):
    assert get_form_hash(form1) != get_form_hash(form2)


def test_formhash_hidden():
    hash1 = get_form_hash(FORM_HIDDEN1, only_visible=False)
    hash2 = get_form_hash(FORM_HIDDEN2, only_visible=False)
    assert hash1 != hash2
