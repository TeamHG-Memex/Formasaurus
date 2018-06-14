# -*- coding: utf-8 -*-
from __future__ import absolute_import


def test_data_ok(storage, capsys):
    errors = storage.check(verbose=False)
    assert errors == 0
    out, err = capsys.readouterr()
    assert 'OK' in out
    assert not err


def test_type_counts(storage, capsys):
    storage.print_form_type_counts(verbose=False)
    out, err = capsys.readouterr()
    assert not err
    assert 'search' in out
    assert 'login' in out
    assert 'Total' in out


def test_storage_add_result(empty_storage):
    st = empty_storage
    assert list(st.iter_trees()) == []

    html = b"""
    <html>
        <body>
            <form>
                <input type='text' name='q'/>
                <input type='submit' value='Search'>
            </form>
        </body>
    </html>
    """
    st.add_result(html=html, url="http://example.com")

    assert len(list(st.iter_trees())) == 1
    assert list(st.iter_annotations()) == []

    all_annotations = list(st.iter_annotations(drop_na=False))
    assert len(all_annotations) == 1

    ann = all_annotations[0]
    assert ann.url == "http://example.com"
    assert ann.fields == {'q': 'XX'}
    assert ann.field_types == ['XX']
    assert ann.field_types_full == ['NOT ANNOTATED']
    assert ann.type == 'X'
    assert ann.type_full == 'NOT ANNOTATED'
    assert not ann.fields_annotated
    assert not ann.fields_partially_annotated

    assert len(ann.field_elems) == 1
    assert ann.field_elems[0].type == 'text'
    assert ann.field_elems[0].name == 'q'

    errors = st.check()
    assert errors == 0
