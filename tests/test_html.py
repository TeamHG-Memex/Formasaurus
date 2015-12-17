# -*- coding: utf-8 -*-
import pytest

from formasaurus.html import (
    html_tostring,
    html_escape,
    remove_by_xpath,
    load_html,
    html_tostring,
    get_forms,
    get_cleaned_form_html,
    get_field_names,
    get_fields_to_annotate,
    escaped_with_field_highlighted,
    highlight_fields,
    add_text_after,
    add_text_before,
    get_text_around_elems,
)


FORM1 = """
<form>
    <input name='foo'/>
    <input type='text' value='hello'>
    <input type='text' value='spam' name=''>
    <select name='bar'>
        <option value='hi'>hi</option>
    </select>
    <input type='radio' name='ch' value='v1'>
    <input type='radio' name='ch' value='v2'>
    <textarea name='baz'></textarea>
    <input type='submit' name='go'>
    <input type='button' name='cancel'>
    <input type='hidden' name='spam' value='123'>
    <input type='HIDDEN' name='spam2' value='123'>
</form>
"""


def test_html_tostring():
    src = "<form><input value='hello'><input type='submit'></form>"
    tree = load_html(src)
    assert html_tostring(tree) == """<form>
<input value="hello"><input type="submit">
</form>
"""


def test_load_html():
    html = b"<div><b></b><b></b></div>"
    tree = load_html(html)
    assert len(tree.xpath('//b')) == 2

    tree2 = load_html(html.decode('ascii'))
    assert len(tree2.xpath('//b')) == 2

    tree3 = load_html(tree)
    assert tree3 is tree


def test_get_forms():
    forms = get_forms(load_html("""
    <p>some text</p>
    <form action="/go">hi</form>
    <FORM method='post'><input name='foo'></FORM>
    """))
    assert len(forms) == 2
    assert forms[0].action == "/go"
    assert forms[1].method == "POST"


def test_get_fields_to_annotate():
    tree = load_html(FORM1)
    form = get_forms(tree)[0]
    elems = get_fields_to_annotate(form)
    assert all(getattr(el, 'name', None) for el in elems)
    names = get_field_names(elems)
    assert names == ['foo', 'bar', 'ch', 'baz', 'go', 'cancel']
    assert set(names) == {el.name for el in elems}


def test_add_text_after():
    tree = load_html("<p>hello,<br/>world</p>")
    add_text_after(tree.xpath('//br')[0], "brave new ")
    add_text_after(tree.xpath('//p')[0], "!")
    assert html_tostring(tree).strip() == "<p>hello,<br>brave new world</p>!"


def test_add_text_before():
    tree = load_html("<div><p>hello<br/>world</p><i>X</i></div>")
    add_text_before(tree.xpath('//br')[0], ",")
    add_text_before(tree.xpath('//p')[0], "!")
    add_text_before(tree.xpath('//i')[0], "1")
    assert html_tostring(tree).strip() == "<div>!<p>hello,<br>world</p>1<i>X</i>\n</div>"


@pytest.mark.xfail()
def test_add_text_before_root():
    tree = load_html("<p>hello<br/>world</p>")
    add_text_before(tree.xpath('//p')[0], "!")
    assert html_tostring(tree).strip() == "!<p>hello<br>world</p>"


def test_get_text_around_elems():
    tree = load_html("""
        <form>
            <h1>Login</h1>
            Please <b>enter</b> your details
            <p>
                Username: <input name='username'/> required
                <div>Email:</div> <input type='text' name='email'> *
            </p>
            Thanks!
        </form>
    """)
    elems = get_fields_to_annotate(tree)
    user, email = elems
    before, after = get_text_around_elems(tree, elems)
    assert len(before) == 2
    assert before[user] == 'Login  Please  enter  your details  Username:'
    assert before[email] == 'required  Email:'

    assert len(after) == 2
    assert after[user] == 'required  Email:'
    assert after[email] == '* Thanks!'

    get_text_around_elems(tree, []) == {}, {}
