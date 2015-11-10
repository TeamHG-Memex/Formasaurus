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
