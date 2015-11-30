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

from tqdm import tqdm

from formasaurus.formhash import get_form_hash
from formasaurus.utils import get_domain, inverse_mapping
from formasaurus.html import load_html, get_forms


FormAnnotation = collections.namedtuple('FormAnnotation', 'form type index info key')


class Storage(object):
    """
    A wrapper class for HTML forms annotation data storage.
    The goal is to store the type of each <form> element from a web page.
    The data is stored in a folder with the following structure::

        config.json
        index.json
        html/
            example.org-0.html
            example.org-1.html
            foo.example.org-0.html
            ...

    ``html`` folders contains raw contents of the webpages.
    :file:`index.json` file contains a JSON dict with the following records::

        "RELATIVE-PATH-TO-HTML-FILE": {
            "url": "URL",
            "forms": ["type1", "type2", ...],
            "visible_html_fields": [
                {"name1": "type1", "name2": "type2", ...},
                ...
            ],
        }

    Key is the relative path to a file with page contents
    (e.g. "html/example.org-1.html"). Values:

    * "url" is an URL the webpage is downloaded from.
    * "forms" contains an array of form type identifiers.
      There must be an identifier per each ``<form>`` element on a web page.
    * "visible_html_fields" contains an array of objects, one object per
      ``<form>`` element; each object is a mapping from field name to
      field type identifier.

    Possible form and field types are stored in :file:`config.json` file;
    you can read them using :meth:`get_form_types` and :meth:`get_field_types`.
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
        for k, info in index.items():
            index[k] = collections.OrderedDict()
            index[k]['url'] = info['url']
            index[k]['forms'] = info['forms']
            if 'visible_html_fields' in info:
                index[k]['visible_html_fields'] = [
                    collections.OrderedDict(sorted(row.items()))
                    for row in info['visible_html_fields']
                ]

        with open(os.path.join(self.folder, "index.json"), "w") as f:
            json.dump(index, f, ensure_ascii=False, indent=4)

    def get_config(self):
        """ Read meta information, including form and field types """
        with open(os.path.join(self.folder, "config.json"), "r") as f:
            return json.load(f)

    def get_field_types(self):
        """
        Return (types, types_inv, na_value) tuple. `types` is an
        OrderedDict with field type names {full_name: short_name};
        `types_inv` is a {short_name: full_name} dict;
        `na_value` is a short name of type name used for unannotated fields.
        """
        return self._get_types('field_types')

    def get_form_types(self):
        """
        Return (types, types_inv, na_value) tuple. `types` is an
        OrderedDict with form type names {full_name: short_name};
        `types_inv` is a {short_name: full_name} dict;
        `na_value` is a short name of type name used for unannotated forms.
        """
        return self._get_types('form_types')

    def _get_types(self, key):
        config = self.get_config()
        na_value = config[key]['NA_value']
        types = collections.OrderedDict([
            (f['full'], f['short']) for f in config[key]['types']
        ])
        types_inv = inverse_mapping(types)
        return types, types_inv, na_value

    def store_result(self, html, url, form_answers):
        """
        Save the downloaded HTML file and its <form> types.
        FIXME: it doesn't handle field type annotations
        """
        index = self.get_index()
        filename = self._generate_filename(url)
        rel_filename =  os.path.relpath(filename, self.folder)
        index[rel_filename] = {
            "url": url,
            "forms": form_answers,
        }
        with open(filename, 'wb') as f:
            f.write(html)
        self.write_index(index)

    def iter_annotations(self, index=None, drop_duplicates=True, drop_na=True,
                         verbose=False, leave=False):
        """
        Return an iterator over (form, type, index, info, path) tuples.
        """
        form_types, form_types_inv, na_value = self.get_form_types()
        trees = self.iter_trees(index=index)

        if verbose:
            trees = tqdm(trees, "Loading", mininterval=0,
                         leave=leave, ascii=True, ncols=80, unit=' files')

        seen = set()
        for path, tree, info in trees:
            for idx, (form, tp) in enumerate(zip(get_forms(tree), info["forms"])):
                if drop_na and tp == na_value:
                    continue

                if drop_duplicates:
                    fp = self.get_fingerprint(form)
                    if fp in seen:
                        continue
                    seen.add(fp)

                yield FormAnnotation(form, tp, idx, info, path)

        if verbose and leave:
            print("")

    def iter_trees(self, index=None):
        """ Return an iterator over (filename, tree, info) tuples """
        if index is None:
            index = self.get_index()
        sorted_items = sorted(
            index.items(),
            key=lambda it: (get_domain(it[1]["url"]), it[0])
        )
        for path, info in sorted_items:
            tree = self.get_tree(path, info)
            yield path, tree, info

    def get_tree(self, path, info):
        """ Load a single tree """
        with open(os.path.join(self.folder, path), "rb") as f:
            return load_html(f.read(), info["url"])

    def get_Xy(self, drop_duplicates=True, verbose=False, leave=False):
        """ Return X,y suitable for scikit-learn training """
        X, y, indices, info_records, info_keys = zip(*self.iter_annotations(
            drop_duplicates=drop_duplicates,
            verbose=verbose,
            leave=leave,
        ))
        return X, y

    def check(self):
        """
        Check that items in storage are correct; print the problems found.
        Return the number of errors found.
        """
        index = self.get_index()
        items = list(index.items())
        errors = 0
        for fn, info in tqdm(items, "Checking", leave=True, mininterval=0,
                             ascii=True, ncols=80, unit=' files'):
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
        form_types, form_types_inv, na_value = self.get_form_types()
        X, y = self.get_Xy(drop_duplicates=True, verbose=verbose, leave=leave)
        return {self.get_fingerprint(form): tp
                for form, tp in zip(X, y) if tp != na_value}

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
        form_types, form_types_inv, na_value = self.get_form_types()
        type_counts = self.get_form_type_counts()
        for shortcut, count in type_counts.most_common():
            type_name = form_types_inv[shortcut]
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
