# -*- coding: utf-8 -*-
"""
HTML forms interactive annotation utilities.
"""
from __future__ import absolute_import, print_function
import sys
import os
from six.moves.urllib.request import urlopen
from six.moves import input

from formasaurus.html import get_cleaned_form_html, load_html, get_forms
from formasaurus.storage import Storage


def annotate_forms(data_folder, url_argument):
    """
    Run an interactive HTML form annotation tool.

    The process is to download a web page, display all HTML forms and for
    each form ask user about form type. The result is saved on disk:
    web page is stored as a html file and the URL and the annotation
    results are added to index.json file.
    """
    storage = Storage(data_folder)
    html, url = load_data(url_argument)
    doc = load_html(html, url)
    form_answers = _annotate_forms(storage, doc)
    if form_answers:
        storage.add_result(html, url, form_answers)


def check_annotated_data(data_folder):
    """
    Check that annotated data is correct; exit with code 1 if it is not.
    """
    storage = Storage(data_folder)
    errors = storage.check()
    storage.print_form_type_counts()
    print("Errors:", errors)
    if errors:
        sys.exit(1)


def load_data(url_or_path):
    """
    Load binary data from a local file or an url;
    return (data, url) tuple.
    """
    if os.path.exists(url_or_path):
        raise NotImplementedError("Re-annotation is not supported yet")
        # with open(url_or_path, 'rb') as f:
        #     return f.read(), None
    else:
        return urlopen(url_or_path).read(), url_or_path


def print_form_html(form):
    """ Print a cleaned up version of <form> HTML contents """
    print(get_cleaned_form_html(form))



def print_form_types(form_types):
    print("\nAllowed form types and their shortcuts:")
    for full_name, shortcuts in form_types.items():
        print("  %s %s" % (shortcuts, full_name))
    print("")


def _annotate_forms(storage, tree):
    """
    For each form element ask user whether it is a login form or not.
    Return an array with True/False answers.
    """
    forms = get_forms(tree)
    if not forms:
        print("Page has no forms.")
        return []
    else:
        print("Page has %d form(s)" % len(forms))

    form_types, form_types_inv, na = storage.get_form_types()

    print_form_types(form_types)
    shortcuts = "/".join(form_types.values())
    fingerprints = storage.get_fingerprints()

    res = []
    for idx, form in enumerate(forms, 1):

        fp = storage.get_fingerprint(form)
        if fp in fingerprints:
            xpath = "(//form)[%d]" % idx
            tp = form_types_inv[fingerprints[fp]]
            print("Skipping duplicate form %-10s %r" % (xpath, tp))
            res.append("X")
            continue

        print_form_html(form)

        while True:
            tp = input("\nPlease enter the form type (%s) "
                       "or ? for help: " % shortcuts).strip()
            if tp == '?':
                print_form_types(form_types)
                continue
            if tp not in set(shortcuts):
                print("Please enter one of the following "
                      "letters: %s. You entered %r" % (shortcuts, tp))
                continue
            res.append(tp)
            break

        print("="*40)

    if all(r == 'X' for r in res):
        print("Page has no new forms.")
        return []
    return res
