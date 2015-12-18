# -*- coding: utf-8 -*-
"""
A module for working with annotation data storage.
"""
from __future__ import absolute_import
import os
import json
import copy
import collections
from six.moves.urllib import parse as urlparse

from tqdm import tqdm

from formasaurus.annotation import AnnotationSchema, FormAnnotation
from formasaurus.formhash import get_form_hash
from formasaurus.utils import get_domain, inverse_mapping
from formasaurus.html import (
    load_html,
    get_forms,
    get_fields_to_annotate,
    get_field_names,
)


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

    def initialize(self, config, index=None):
        """ Create folders and files for a new storage """
        with open(os.path.join(self.folder, 'config.json'), 'wb') as f:
            f.write(json.dumps(config).encode('utf8'))
        self.write_index(index or {})
        os.mkdir(os.path.join(self.folder, 'html'))

    def get_index(self):
        """ Read an index """
        with open(os.path.join(self.folder, "index.json"), "rb") as f:
            data = f.read().decode('utf8')
            return json.loads(data)

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

        with open(os.path.join(self.folder, "index.json"), "wb") as f:
            data = json.dumps(index, ensure_ascii=True, indent=4)
            f.write(data.encode('utf8'))

    def get_config(self):
        """ Read meta information, including form and field types """
        with open(os.path.join(self.folder, "config.json"), "r") as f:
            return json.load(f)

    def get_field_schema(self):
        """
        Return :class:`AnnotationSchema` instance. `r.types` is an
        OrderedDict with field type names {full_name: short_name};
        `r.types_inv` is a {short_name: full_name} dict;
        `r.na_value` is a short name of type name used for unannotated fields.
        """
        return self._get_schema('field_types')

    def get_form_schema(self):
        """
        Return :class:`AnnotationSchema` instance. `r.types` is an
        OrderedDict with form type names {full_name: short_name};
        `r.types_inv` is a {short_name: full_name} dict;
        `r.na_value` is a short name of type name used for unannotated forms;
        `r.skip_value` is a short name of a type name which should be skipped.
        """
        return self._get_schema('form_types')

    def _get_schema(self, key):
        config = self.get_config()
        na_value = config[key]['NA_value']
        skip_value = config[key]['skip_value']
        simplify_map = config[key]['simplify_map']
        types = collections.OrderedDict([
            (f['full'], f['short']) for f in config[key]['types']
        ])
        types_inv = inverse_mapping(types)
        return AnnotationSchema(types, types_inv, na_value, skip_value, simplify_map)

    def add_result(self, html, url, form_answers=None,
                   visible_html_fields=None, index=None,
                   add_empty=True):
        """
        Save HTML source and its <form> and form field types.
        """
        forms = get_forms(load_html(html))
        if not add_empty:
            if not len(forms):
                return

            if all(len(get_fields_to_annotate(form)) == 0 for form in forms):
                return

        if form_answers is None:
            form_schema = self.get_form_schema()
            form_answers = [form_schema.na_value for _ in forms]
        else:
            assert len(form_answers) == len(forms)

        if visible_html_fields is None:
            field_schema = self.get_field_schema()
            visible_html_fields = [{
                name: field_schema.na_value
                for name in get_field_names(get_fields_to_annotate(form))
            } for form in forms]

        filename = self.generate_filename(url)
        path = os.path.relpath(filename, self.folder)
        if index is None:
            index = self.get_index()
        index[path] = {
            "url": url,
            "forms": form_answers,
            "visible_html_fields": visible_html_fields,
        }
        with open(filename, 'wb') as f:
            if not isinstance(html, bytes):
                html = html.encode('utf8')
            f.write(html)
        self.write_index(index)
        return path

    def iter_annotations(self, index=None,
                         drop_duplicates=True, drop_na=True, drop_skipped=True,
                         simplify_form_types=False, simplify_field_types=False,
                         verbose=False, leave=False):
        """
        Return an iterator over :class:`FormAnnotation` objects.
        """
        form_schema = self.get_form_schema()
        field_schema = self.get_field_schema()
        trees = self.iter_trees(index=index)

        if verbose:
            trees = tqdm(trees, "Loading", mininterval=0,
                         leave=leave, ascii=True, ncols=80, unit=' files')

        seen = set()
        for path, tree, info in trees:
            for idx, (form, tp) in enumerate(zip(get_forms(tree), info["forms"])):
                if simplify_form_types:
                    tp = form_schema.simplify_map.get(tp, tp)

                if drop_na and tp == form_schema.na_value:
                    continue

                if drop_skipped and tp == form_schema.skip_value:
                    continue

                if drop_duplicates:
                    fp = self.get_fingerprint(form)
                    if fp in seen:
                        continue
                    seen.add(fp)

                if simplify_field_types:
                    info = copy.deepcopy(info)
                    for fields in info['visible_html_fields']:
                        for k, v in fields.items():
                            fields[k] = field_schema.simplify_map.get(v, v)

                yield FormAnnotation(form, tp, idx, info, path,
                                     form_schema, field_schema)

        if verbose and leave:
            print("")

    def iter_trees(self, index=None):
        """
        Return an iterator over ``(filename, tree, info)`` tuples
        where ``filename`` is a relative file name, ``tree`` is a lxml tree
        and ``info`` is a dictionary with annotation data.
        """
        if index is None:
            index = self.get_index()
        sorted_items = sorted(
            index.items(),
            key=lambda it: (get_domain(it[1]["url"]), it[0])
        )
        for path, info in sorted_items:
            tree = self.get_tree(path, info)
            yield path, tree, info

    def get_tree(self, path, info=None):
        """
        Load a single tree.
        ``path`` is a relative path to a file (key in index.json file),
        ``info`` is annotation data (value in index.json file).
        """
        if info is None:
            info = self.get_index()[path]
        with open(os.path.join(self.folder, path), "rb") as f:
            return load_html(f.read(), info["url"])

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

            if 'visible_html_fields' not in info:
                errors += 1
                print("No fields data for entry {!r}".format(fn))
            else:
                fields = info['visible_html_fields']
                if len(fields) != len(doc.xpath('//form')):
                    errors += 1
                    print("Invalid number of form field annotations for entry {!r}".format(fn))
                else:
                    for idx, (form, fields_info) in enumerate(zip(doc.xpath('//form'), fields)):
                        elems = get_fields_to_annotate(form)
                        names = {elem.name for elem in elems}
                        if names != set(fields_info.keys()):
                            errors += 1
                            print("Invalid field names for form #{}, "
                                  "entry {!r}. Expected: {}, found: {}".format(
                                idx, fn, names, set(fields_info.keys())
                            ))

        if not errors:
            print("Status: OK")
        else:
            print("Status: %d error(s) found" % errors)

        return errors

    def get_fingerprint(self, form):
        """
        Return form fingerprint (a string that can be used for deduplication).
        """
        return get_form_hash(form, only_visible=True)

    def get_form_type_counts(self, drop_duplicates=True, drop_na=True,
                             simplify=False,
                             verbose=True):
        """ Return a {formtype: count} collections.Counter """
        annotations = self.iter_annotations(verbose=verbose,
                                            drop_duplicates=drop_duplicates,
                                            drop_na=drop_na,
                                            simplify_form_types=simplify)
        return collections.Counter(ann.type for ann in annotations)

    def print_form_type_counts(self, simplify=False):
        """ Print the number annotations of each form types in this storage """
        if simplify:
            print("Annotated HTML forms (simplified classes):\n")
        else:
            print("Annotated HTML forms (detailed classes):\n")
        schema = self.get_form_schema()
        type_counts = self.get_form_type_counts(simplify=simplify)
        for shortcut, count in type_counts.most_common():
            type_name = schema.types_inv[shortcut]
            print("%-5d %-25s (%s)" % (count, type_name, shortcut))
        print("\nTotal form count: %d" % (sum(type_counts.values())))

    def generate_filename(self, url):
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
