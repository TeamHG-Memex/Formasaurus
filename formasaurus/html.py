# -*- coding: utf-8 -*-
"""
HTML processing utilities
"""
from doctest import Example
try:
    from html import escape as html_escape  # Python 3
except ImportError:
    from cgi import escape as html_escape  # Python 2

import lxml.html
from lxml.html.clean import Cleaner
from lxml.doctestcompare import LXMLOutputChecker, PARSE_HTML


def remove_by_xpath(tree, xpath):
    """
    Remove all HTML elements which match a given XPath expression.
    """
    for bad in tree.xpath(xpath):
        bad.getparent().remove(bad)


def load_html(data, base_url=None):
    """ Parse HTML data to a lxml tree """
    return lxml.html.fromstring(data, base_url=base_url)


def html_tostring(tree):
    return lxml.html.tostring(tree, pretty_print=True, encoding='unicode')


def get_forms(tree):
    return tree.xpath("//form")


def get_cleaned_form_html(form, for_source=True):
    """
    Return a cleaned up version of <form> HTML contents.
    If `for_source` is True, HTML is cleaned to make
    source code more readable; otherwise it is cleaned to make
    rendered form more safe to render.
    """
    params = dict(
        forms=False,
        javascript=True,
        scripts=True,
        remove_unknown_tags=False,
    )

    if for_source:
        params.update(
            style=True,
            allow_tags={'form', 'input', 'textarea', 'label', 'option',
                        'select', 'submit', 'a'},
        )
    else:
        params.update(style=False)

    cleaner = Cleaner(**params)
    raw_html = lxml.html.tostring(form, pretty_print=True, encoding="unicode")
    html = cleaner.clean_html(raw_html)
    if for_source:
        lines = [line.strip() for line in html.splitlines(False) if line.strip()]
        html = "\n".join(lines)
    return html


def get_field_names(elems):
    """ Return unique name attributes """
    res = []
    seen = set()
    for el in elems:
        if (not getattr(el, 'name', None)) or (el.name in seen):
            continue
        seen.add(el.name)
        res.append(el.name)
    return res


def get_visible_fields(form):
    """
    Return visible form fields (the ones users should fill).
    """
    # FIXME: don't suggest readonly fields
    return form.xpath(
        'descendant::textarea'
        '|descendant::select'
        '|descendant::button'
        '|(descendant::input[(@type!="hidden" and @type!="HIDDEN") or not(@type)])'
    )


def get_fields_to_annotate(form):
    """
    Return fields which should be annotated:

    1. they should be visible to user, and
    2. they should have name (i.e. affect form submission result).

    """
    return [
        f for f in get_visible_fields(form)
        if getattr(f, 'name', None) is not None
    ]


def escaped_with_field_highlighted(form_html, field_name):
    """
    Return escaped HTML source code suitable for displaying;
    fields with name==field_name are highlighted.
    """
    form = load_html(form_html)
    for elem in form.xpath('.//*[@name="{}"]'.format(field_name)):
        add_text_before(elem, '__START__')
        add_text_after(elem, '__END__')
    text = html_tostring(form)
    text = html_escape(text).replace('__START__', '<span style="font-size:large;color:#000">').replace('__END__', '</span>')
    return text


def highlight_fields(html, field_name):
    """
    Return HTML source code with all fields with name==field_name
    highlighted by adding ``formasaurus-field-highlighted`` CSS class.
    """
    tree = load_html(html)
    xpath = './/*[@name="{}"]'.format(field_name)
    for elem in tree.xpath(xpath):
        elem.set('class', elem.get('class', '') + ' formasaurus-field-highlighted')
    return html_tostring(tree)


def add_text_after(elem, text):
    """ Add text after elem """
    tail = elem.tail or ''
    elem.tail = text + tail


def add_text_before(elem, text):
    """ Add text before elem """
    prev = elem.getprevious()
    if prev is not None:
        # not a first child
        prev.tail = (prev.tail or '') + text
    else:
        # first child
        parent = elem.getparent()
        parent.text = (parent.text or '') + text


def assert_html_equal(want, got):
    """ Assert that 2 HTML documents are equal """
    checker = LXMLOutputChecker()
    if not checker.check_output(want, got, PARSE_HTML):
        message = checker.output_difference(Example("", want), got, 0)
        raise AssertionError(message)
