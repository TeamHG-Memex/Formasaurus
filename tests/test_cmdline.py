# -*- coding: utf-8 -*-
from __future__ import absolute_import
import io
import subprocess

import formasaurus


def test_usage():
    out = subprocess.check_output('formasaurus -h', shell=True)
    assert b'Usage' in out
    assert b'Formasaurus' in out


def test_version():
    out = subprocess.check_output('formasaurus --version', shell=True)
    assert formasaurus.__version__ in out.decode('ascii')


def test_check_data():
    out = subprocess.check_output('formasaurus check-data', shell=True)
    assert b'Errors: 0' in out


def test_evaluate():
    out = subprocess.check_output('formasaurus evaluate --cv 3', shell=True)
