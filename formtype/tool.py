#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This is a tool for annotating HTML forms, training a classifier
based on annotated data and evaluating its quality.

To annotate new pages use "add" command.
It downloads a web page, displays all HTML forms and for each form asks
user about form type. The result is saved on disk: web page is stored
as a html file and the URL and the annotation results are added
to index.json file.

To check the storage for consistency and print some stats use "check" command.

To train an extractor for HTML form classification use "train" command.

To classify forms from an URL using a saved extractor use "run" command.


Usage:
    tool.py run <modelfile> <url> [--threshold <probability>]
    tool.py add <url> [--data-folder <path>]
    tool.py check-data [--data-folder <path>]
    tool.py train <modelfile> [--data-folder <path>]
    tool.py evaluate [--test-size <ratio>] [--cv <n_folds>] [--data-folder <path>]
    tool.py -h | --help
    tool.py --version

Options:
    --data-folder <path>       path to the data folder [default: data]
    --test-size <ratio>        ratio of data to use for evaluation, from 0 to 1.0 [default: 0.3]
    --cv <n_folds>             use <n_folds> for cross-validation [default: 10]
    --threshold <probability>  don't display predictions with probability below this threshold [default: 0.01]

"""
from __future__ import absolute_import, print_function
from collections import Counter

import docopt

from formtype.annotation import (
    annotate_forms,
    check_annotated_data,
    load_data,
    print_form_html
)
from formtype.extractor import FormExtractor
from formtype.storage import load_html, FORM_TYPES_INV


def main():
    args = docopt.docopt(__doc__)

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
            train_ratio=float(args["--test-size"])
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
                tp_full = FORM_TYPES_INV[tp]
                print("%s %0.1f%%" % (tp_full, prob*100), end='    ')

            print("")


if __name__ == '__main__':
    main()
