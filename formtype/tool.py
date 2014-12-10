#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
HTML form annotation tool.

It downloads a web page, displays all HTML forms and for each form asks
user about form type. The result is saved on disk: web page is stored
as a html file and the URL and the annotation results are added
to index.json file.

To annotate new pages use "forms" command; to check the storage for
consistency and print some stats use "check" command.

Usage:
    tool.py forms <url> [--data-folder <path>]
    tool.py check [--data-folder <path>]
    tool.py -h | --help
    tool.py --version

Options:
    --data-folder <path>   path to the data folder [default: data]

"""
from __future__ import absolute_import
import sys
import os
import urllib2

import docopt
import lxml.html
from lxml.html.clean import Cleaner

from formtype.storage import Storage, FORM_TYPES, load_html


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
        return urllib2.urlopen(url_or_path).read(), url_or_path


def print_form_html(form):
    """ Print a cleaned up version of <form> HTML contents """
    cleaner = Cleaner(
        forms=False,
        javascript=True,
        scripts=True,
        style=True,
        allow_tags={'form', 'input', 'textarea', 'label', 'option', 'select', 'submit', 'a'},

        remove_unknown_tags=False,
    )
    html = cleaner.clean_html(lxml.html.tostring(form, pretty_print=True))
    lines = [line.strip() for line in html.splitlines(False) if line.strip()]
    print("\n".join(lines))


def print_form_types(types):
    print("\nAllowed form types and their shortcuts:")
    for full_name, shortcuts in types.items():
        print("  %s %s" % (shortcuts, full_name))
    print("")


def annotate_forms(doc, form_types=None):
    """
    For each form element ask user whether it is a login form or not.
    Return an array with True/False answers.
    """
    forms = doc.xpath("//form")
    if not forms:
        print("Page has no forms.")
        return []
    else:
        print("Page has %d form(s)" % len(forms))

    if form_types is None:
        form_types = FORM_TYPES

    print_form_types(form_types)
    shortcuts = "/".join(form_types.values())

    res = []
    for idx, form in enumerate(forms, 1):
        # xpath = "//form[%d]" % idx
        # print(xpath)
        print_form_html(form)

        while True:
            tp = raw_input("\nPlease enter the form type (%s) or ? for help: " % shortcuts).strip()
            if tp == '?':
                print_form_types(form_types)
                continue
            if tp not in set(shortcuts):
                print("Please enter one of the following letters: %s. You entered %r" % (shortcuts, tp))
                continue
            res.append(tp)
            break

        print("="*40)
    return res


def main():
    args = docopt.docopt(__doc__)

    if args['forms']:
        storage = Storage(args['--data-folder'])
        html, url = load_data(args["<url>"])
        doc = load_html(html, url)
        answers = annotate_forms(doc)
        if answers:
            storage.store_result(html, answers, url)

    elif args['check']:
        storage = Storage(args['--data-folder'])
        ok = storage.check()
        storage.print_type_counts()
        if not ok:
            sys.exit(1)


if __name__ == '__main__':
    main()
