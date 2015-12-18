#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Formasaurus command-line utility.

Usage:
    formasaurus train <modelfile> [--data-folder <path>]
    formasaurus run <modelfile> <url> [--threshold <probability>]
    formasaurus check-data [--data-folder <path>]
    formasaurus evaluate (forms|fields|all) [--cv <n_folds>] [--data-folder <path>]
    formasaurus -h | --help
    formasaurus --version

Options:
    --data-folder <path>       path to the data folder
    --cv <n_folds>             use <n_folds> for cross-validation [default: 20]
    --threshold <probability>  don't display predictions with probability below this threshold [default: 0.01]

To train an extractor for HTML form classification use "train" command.

To classify forms from an URL using a saved extractor use "run" command.

To check the storage for consistency and print some stats use "check-data" command.

To check the estimated quality of the default form and form fields model
use "evaluate" command.
"""
from __future__ import absolute_import, print_function
import sys
from collections import Counter

import docopt

import formasaurus
from formasaurus.utils import download
from formasaurus.storage import Storage
from formasaurus.html import load_html, get_cleaned_form_html
from formasaurus import formtype_model, fieldtype_model
from formasaurus.classifiers import DEFAULT_DATA_PATH


def main():
    args = docopt.docopt(__doc__, version=formasaurus.__version__)

    data_folder = args['--data-folder']
    if data_folder is None:
        data_folder = DEFAULT_DATA_PATH

    storage = Storage(data_folder)

    if args['check-data']:
        errors = storage.check()
        storage.print_form_type_counts(simplify=False)
        storage.print_form_type_counts(simplify=True)
        print("Errors:", errors)
        if errors:
            sys.exit(1)

    elif args['train']:
        ex = formasaurus.FormFieldClassifier.trained_on(data_folder)
        ex.save(args["<modelfile>"])

    elif args['run']:
        threshold = float(args['--threshold'])
        print("Loading the extractor..")
        ex = formasaurus.FormFieldClassifier.load(args["<modelfile>"])
        print("Downloading data...")
        data = download(args["<url>"])
        tree = load_html(data, args['<url>'])

        result = ex.extract_forms(tree, proba=True, threshold=threshold)
        if not result:
            print("No forms found.")
            return

        for form, probs in result:
            print("-"*40)
            print(get_cleaned_form_html(form))
            print("")
            for tp, prob in Counter(probs).most_common():
                tp_full = ex.form_types_inv[tp]
                print("%s %0.1f%%" % (tp_full, prob * 100), end='    ')

            print("")

    elif args['evaluate']:
        n_folds = int(args["--cv"])
        annotations = list(
            storage.iter_annotations(verbose=True, leave=True,
                                     simplify_form_types=True,
                                     simplify_field_types=True)
        )

        if args['forms'] or args['all']:
            print("Evaluating form classifier...")
            formtype_model.print_classification_report(annotations,
                                                       n_folds=n_folds)
            print("")

        if args['fields'] or args['all']:
            print("Evaluating form field classifier...")
            fieldtype_model.print_classification_report(annotations,
                                                        n_folds=n_folds)


if __name__ == '__main__':
    main()
