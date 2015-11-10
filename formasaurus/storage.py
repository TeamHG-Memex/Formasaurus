# -*- coding: utf-8 -*-
"""
A module for working with annotation data storage.
"""
from __future__ import absolute_import
import os
import json
import collections
from itertools import chain
from six.moves.urllib import parse as urlparse

import lxml.html
from tqdm import tqdm

from formasaurus.formhash import get_form_hash
from formasaurus.utils import get_domain


FORM_TYPES = collections.OrderedDict([
    ('search', 's'),
    ('login', 'l'),
    ('registration', 'r'),
    ('password/login recovery', 'p'),
    ('contact', 'c'),
    ('join mailing list', 'm'),
    ('other', 'o'),
    ('NOT ANNOTATED', 'X'),
])

FORM_TYPES_INV = {v: k for k, v in FORM_TYPES.items()}


def load_html(data, base_url):
    """ Parse HTML data to a lxml tree """
    return lxml.html.fromstring(data, base_url=base_url)


class Storage(object):
    """
    A wrapper class for HTML forms annotation data storage.
    The goal is to store the type of each <form> element from a web page.
    The data is stored in a folder with the following structure::

        index.json
        html/
            example.org-0.html
            example.org-1.html
            foo.example.org-0.html
            ...

    ``html`` folders contains raw contents of the webpages.
    ``index.json`` file contains a JSON dict with the following records::

        "RELATIVE-PATH-TO-HTML-FILE": {
            "url": "URL",
            "forms": [...]
        }

    Key is the relative path to a file with page contents
    (e.g. "html/example.org-1.html"); ``URL`` is an URL the webpage is
    downloaded from; "forms" contains an array of form type identifiers.
    There must be an identifier per each ``<form>`` element on a web page.

    Possible form types are listed in a ``storage.FORM_TYPES`` constant.
    """

    def __init__(self, folder):
        self.folder = folder

    def get_index(self):
        """ Read an index """
        with open(os.path.join(self.folder, "index.json"), "r") as f:
            return json.load(f)

    def write_index(self, index):
        """ Save an index """
        index = collections.OrderedDict(sorted(index.items()))
        with open(os.path.join(self.folder, "index.json"), "w") as f:
            json.dump(index, f, ensure_ascii=False, indent=4)

    def store_result(self, html, answers, url):
        """ Save the downloaded HTML file and its <form> types. """
        index = self.get_index()
        filename = self._generate_filename(url)
        rel_filename =  os.path.relpath(filename, self.folder)
        index[rel_filename] = {
            "url": url,
            "forms": answers,
        }
        with open(filename, 'wb') as f:
            f.write(html)
        self.write_index(index)

    def iter_annotations(self, drop_duplicates=True, verbose=False, leave=False):
        """ Return an iterator over (form, type) tuples. """

        sorted_items = sorted(
            self.get_index().items(),
            key=lambda it: get_domain(it[1]["url"])
        )

        if verbose:
            sorted_items = tqdm(sorted_items, "Loading", mininterval=0,
                                leave=leave, ascii=True, ncols=80)

        seen = set()
        for filename, info in sorted_items:
            with open(os.path.join(self.folder, filename), "rb") as f:
                tree = load_html(f.read(), info["url"])

            for form, tp in zip(tree.xpath("//form"), info["forms"]):

                if tp == 'X':
                    continue

                if drop_duplicates:
                    fp = self.get_fingerprint(form)
                    if fp in seen:
                        continue
                    seen.add(fp)

                yield form, tp

        if verbose and leave:
            print("")

    def get_Xy(self, drop_duplicates=True, verbose=False, leave=False):
        """ Return X,y suitable for scikit-learn training """
        return list(zip(*self.iter_annotations(
            drop_duplicates=drop_duplicates,
            verbose=verbose,
            leave=leave,
        )))

    def check(self):
        """
        Check that items in storage are correct; print the problems found.
        Return the number of errors found.
        """
        index = self.get_index()
        items = list(index.items())
        errors = 0
        for fn, info in tqdm(items, "Checking", leave=True, mininterval=0,
                             ascii=True, ncols=80):
            fn_full = os.path.join(self.folder, fn)
            if not os.path.exists(fn_full):
                print("\nFile not found: %r" % fn_full)
                errors += 1
                continue

            with open(fn_full, 'rb') as f:
                data = f.read()

            doc = load_html(data, info['url'])
            if len(doc.xpath("//form")) != len(info["forms"]):
                errors += 1
                msg = "\nInvalid form count for entry %r: expected %d, got %d" % (
                         fn, len(doc.xpath("//form")), len(info["forms"])
                      )
                print(msg)

        if not errors:
            print("Status: OK")
        else:
            print("Status: %d error(s) found" % errors)

        return errors

    def get_fingerprints(self, verbose=True, leave=False):
        """ Return a dict with all fingerprints of the existing forms """
        X, y = self.get_Xy(drop_duplicates=True, verbose=verbose, leave=leave)
        return {self.get_fingerprint(form): tp
                for form, tp in zip(X, y) if tp != 'X'}

    def get_fingerprint(self, form):
        """
        Return form fingerprint (a string that can be used for deduplication).
        """
        return get_form_hash(form, only_visible=True)

    def get_form_type_counts(self, drop_duplicates=True, verbose=True):
        """ Return a {formtype: count} collections.Counter """
        if not drop_duplicates:
            index = self.get_index()
            return collections.Counter(
                chain.from_iterable(v["forms"] for v in index.values())
            )

        X, y = self.get_Xy(drop_duplicates=True, verbose=verbose)
        return collections.Counter(y)

    def print_form_type_counts(self):
        """ Print the number annotations of each form types in this storage """
        print("Annotated HTML forms:\n")
        type_counts = self.get_form_type_counts()
        for shortcut, count in type_counts.most_common():
            type_name = FORM_TYPES_INV[shortcut]
            print("%-5d %-25s (%s)" % (count, type_name, shortcut))
        print("\nTotal form count: %d" % (sum(type_counts.values())))

    def _generate_filename(self, url):
        """ Return a name for a new file """
        p = urlparse.urlparse(url)
        idx = 0
        while True:
            name = "html/%s-%d.html" % (p.netloc, idx)
            path = os.path.join(self.folder, name)
            if os.path.exists(path):
                idx += 1
                continue
            return path
