# -*- coding: utf-8 -*-
from __future__ import absolute_import


def test_data_ok(storage, capsys):
    errors = storage.check()
    assert errors == 0
    out, err = capsys.readouterr()
    assert 'OK' in out
    assert not err


def test_type_counts(storage, capsys):
    storage.print_form_type_counts()
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
    assert len(list(st.iter_annotations(drop_na=False))) == 1

    errors = st.check()
    assert errors == 0
