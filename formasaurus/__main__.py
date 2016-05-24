#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Formasaurus command-line utility.

Usage:
    formasaurus init
    formasaurus train <modelfile> [--data-folder <path>]
    formasaurus run <url> [modelfile] [--threshold <probability>]
    formasaurus check-data [--data-folder <path>]
    formasaurus evaluate (forms|fields|all) [--cv <n_folds>] [--data-folder <path>]
    formasaurus -h | --help
    formasaurus --version

Options:
    --data-folder <path>       path to the data folder
    --cv <n_folds>             use <n_folds> for cross-validation [default: 20]
    --threshold <probability>  don't display predictions with probability below
                               this threshold [default: 0.05]

Formasaurus trains a model on a first call, and then caches it.
You can request training&caching explicitly using `formasaurus init` command.

To train a custom extractor for HTML form classification use
"formsasaurus train" command.

To classify forms from an URL using a saved extractor use
"formasaurus run" command.

To check the storage for consistency and print some stats use
"formasaurus check-data" command.

To check the estimated quality of the default form and form fields model
use "formasaurus evaluate" command.
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

    elif args['init']:
        formasaurus.FormFieldClassifier.load()

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

        for form, info in result:
            print("\n")
            print("="*60)
            print(get_cleaned_form_html(form))
            print("-"*60)
            print("Form type:    ", end="")
            for form_tp, prob in Counter(info['form']).most_common():
                print("%s %0.1f%%" % (form_tp, prob * 100), end='    ')

            print("\n\nField types:")
            for field_name, probs in info['fields'].items():
                print(field_name, end=':  ')
                for field_tp, prob in Counter(probs).most_common():
                    print("%s %0.1f%%" % (field_tp, prob * 100), end='  ')
                print("")

            print("")

    elif args['evaluate']:
        n_folds = int(args["--cv"])
        annotations = list(
            storage.iter_annotations(verbose=True, leave=True,
                                     simplify_form_types=True,
                                     simplify_field_types=True)
        )

        if args['forms'] or args['all']:
            print("Evaluating form classifier...\n")
            formtype_model.print_classification_report(annotations,
                                                       n_folds=n_folds)
            print("")

        if args['fields'] or args['all']:
            print("Evaluating form field classifier...\n")
            fieldtype_model.print_classification_report(annotations,
                                                        n_folds=n_folds)


if __name__ == '__main__':
    main()
