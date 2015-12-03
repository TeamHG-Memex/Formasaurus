#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This is a Formasaurus command-line utility for annotating HTML forms,
training a classifier based on annotated data and evaluating its quality.

Usage:
    formasaurus add <url> [--data-folder <path>]
    formasaurus train <modelfile> [--data-folder <path>]
    formasaurus run <modelfile> <url> [--threshold <probability>]
    formasaurus check-data [--data-folder <path>]
    formasaurus evaluate [--test-size <ratio>] [--cv <n_folds>] [--data-folder <path>]
    formasaurus -h | --help
    formasaurus --version

Options:
    --data-folder <path>       path to the data folder
    --test-size <ratio>        ratio of data to use for evaluation, from 0 to 1.0 [default: 0.25]
    --cv <n_folds>             use <n_folds> for cross-validation [default: 10]
    --threshold <probability>  don't display predictions with probability below this threshold [default: 0.01]

To annotate new pages use "add" command.
It downloads a web page, displays all HTML forms and for each form asks
user about form type. The result is saved on disk: web page is stored
as a html file and the URL and the annotation results are added
to index.json file.

To train an extractor for HTML form classification use "train" command.

To classify forms from an URL using a saved extractor use "run" command.

To check the storage for consistency and print some stats use "check-data" command.

To check the expected quality of the default model trained on the
training data provided use "evaluate" command.
"""
from __future__ import absolute_import, print_function
import os
from collections import Counter

import docopt

import formasaurus
from formasaurus.annotation import (
    annotate_forms,
    check_annotated_data,
    load_data,
    print_form_html
)
from formasaurus.extractor import FormExtractor
from formasaurus.storage import Storage
from formasaurus.html import load_html
from formasaurus import evaluation, formtype_model


def main():
    args = docopt.docopt(__doc__, version=formasaurus.__version__)

    if args['--data-folder'] is None:
        # by default, use 'data' folder relative to this file
        args['--data-folder'] = os.path.join(os.path.dirname(__file__), 'data')

    if args['add']:
        annotate_forms(
            data_folder=args['--data-folder'],
            url_argument=args["<url>"],
        )

    elif args['check-data']:
        check_annotated_data(args['--data-folder'])

    elif args['train']:
        ex = FormExtractor.trained_on(
            data_folder=args["--data-folder"],
            train_ratio=1.0,
        )
        ex.save(args["<modelfile>"])

    elif args['run']:
        threshold = float(args['--threshold'])
        print("Loading the extractor..")
        ex = FormExtractor.load(args["<modelfile>"])
        print("Downloading data...")
        data, url = load_data(args["<url>"])
        tree = load_html(data, url)

        result = ex.extract_forms_proba(tree, threshold)
        if not result:
            print("No forms found.")
            return

        for form, probs in result:
            print("-"*40)
            print_form_html(form)
            print("")
            for tp, prob in Counter(probs).most_common():
                tp_full = ex.form_types_inv[tp]
                print("%s %0.1f%%" % (tp_full, prob * 100), end='    ')

            print("")

    elif args['evaluate']:
        n_folds = int(args["--cv"])
        ratio = float(args['--test-size'])

        store = Storage(args["--data-folder"])
        form_types, form_types_inv, na_name = store.get_form_types()
        model = formtype_model.get_model()

        annotations = store.iter_annotations(verbose=True, leave=True)
        X, y = zip(*((a.form, a.type) for a in annotations))

        test_size = int(len(y) * ratio)
        train_size = len(y) - test_size
        X_train, X_test = X[:train_size], X[train_size:]
        y_train, y_test = y[:train_size], y[train_size:]

        evaluation.print_metrics(model, X, y, X_train, X_test, y_train, y_test,
                                 ipython=False, cv=n_folds, short_matrix=True,
                                 class_map=form_types_inv)


if __name__ == '__main__':
    main()
