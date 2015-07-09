===========
Formasaurus
===========

.. image:: https://img.shields.io/pypi/v/Formasaurus.svg
   :target: https://pypi.python.org/pypi/Formasaurus
   :alt: PyPI Version

.. image:: https://img.shields.io/travis/TeamHG-Memex/Formasaurus/master.svg
   :target: http://travis-ci.org/TeamHG-Memex/Formasaurus
   :alt: Build Status

Formasaurus is a Python package that tells you the type of an HTML form:
is it a login, search, registration, password recovery, "join mailing list",
contact form or something else. Under the hood it uses machine learning.

Installation
============

Formasaurus requires scipy, numpy, scikit-learn and lxml to work.

First, make sure numpy is installed. Then, to install Formasaurus with all
its other dependencies run

::

    pip install formasaurus[with-deps]

These packages may require extra steps to install, so the command above
may fail. In this case install dependencies manually, on by one, and
then run::

    pip install formasaurus

Usage
=====

Load the form extractor:

    >>> from formasaurus import FormExtractor
    >>> ex = FormExtractor.load()

Most library features are provided by ``formasaurus.FormExtractor`` class.

FormExtractor expects HTML files parsed by lxml as an input.
Load an HTML file using lxml:

    >>> import lxml.html
    >>> tree = lxml.html.parse("http://google.com")

In this example the data is loaded from an URL; of course, data may be
loaded from a local file or from an in-memory object, or you may already
have the tree loaded (e.g. with Scrapy).

To extract all forms from the page use ``extract_forms`` method:

    >>> ex.extract_forms(tree)
    [(<Element form at 0x10bbc5730>, u's')]

It returns a list of (form, cls) tuples, one tuple for each ``<form>``
element on a page.

``cls`` can be one of the following letters:

* **s** - search form;
* **l** - login form;
* **r** - registration form;
* **p** - password or account recovery form;
* **m** - mailing list / newsletter subscription form;
* **c** - contact / feedback form;
* **o** - other form.

FormExtractor can return probabilities of a form being of one of these
classes. Use ``extract_forms_proba`` method for that:

    >>> ex.extract_forms_proba(tree)
    [(<Element form at 0x10bbc5730>,
        {u'c': 0.0013464597746403034,
         u'l': 0.0024144635740943055,
         u'm': 0.0035095665774015081,
         u'o': 0.0048140061900189797,
         u'p': 0.002359130863598229,
         u'r': 0.0019866565416929898,
         u's': 0.98356971647855373})]

This method also returns a list of tuples, but now the second element is
not just the class itself, but a dictionary with probabilities.

There is a shortcut for dropping all classes with low probabilities. Let's
remove all classes with probability < 0.1:

    >>> ex.extract_forms_proba(tree, 0.1)
    [(<Element form at 0x10bbc5730>,
        {u's': 0.98356971647855373})]

Here the extractor is fairily certain the form is a search form,
so only a single item remained.

To classify individual forms use ``classify`` and ``classify_proba`` methods.
They work on individual <form> elements (lxml Element instances):

    >>> form = tree.xpath("//form")[0]
    >>> ex.classify(form)
    u's'
    >>> ex.classify_proba(form, 0.004)  # threshold is also supported here
    {u'o': 0.0048140061900189797, u's': 0.98356971647855373}


Creating Custom Models
======================

Formasaurus uses a ML-based classifier to classify HTML forms.
Default training data is distributed alongside with Formasaurus; default
model is trained on this data the first time ``FormExtractor.load()``
is called, and model file is cached.

To use a custom model file pass its name to ``FormExtractor.load`` method:

    >>> from formasaurus import FormExtractor
    >>> ex = FormExtractor.load("./myextractor.joblib")

If the file doesn't exist it will be created from the default training data.

To train custom models using your own training data use
``formasaurus`` command-line tool::

    $ formasaurus train ./myextractor.joblib --data-path ./my-training-data

Run ``formasaurus --help`` for more information. There are utilities for
annotating HTML pages (adding more training examples), evaluating models,
checking how they work, etc.

Contributing
============

Source code and bug tracker are on github:
https://github.com/TeamHG-Memex/Formasaurus

License is MIT.

The easiest way to improve classification quality is to add more training
examples. Use ``formasaurus add`` command for that.

For more info about the classification model check
"notebooks/Model.ipynb" IPython notebook (see
https://github.com/TeamHG-Memex/Formasaurus/blob/master/notebooks/Model.ipynb );
some experience with machine learning is helpful if you want to improve
the model.

Currently Formasaurus uses a linear classifier (Logistic Regression) and
features like counts of form elements of different types, whether a form is
POST or GET, text on submit buttons, names of CSS classes and IDs,
input labels, presence of certain substrings in URLs, etc.

To make the extractor understand a new type of form (e.g. "order" form
or "forum navigation" form) it is necessary to check all forms that
are marked as "other" in the existing dataset and change their type
when needed, then check the extraction quality (``formasaurus evaluate``
command or an IPython notebook could help) and improve the model if
the quality is not satisfactory.

Extraction Quality
==================

::

    Classification report (480 training examples, 160 testing examples):

                             precision    recall  f1-score   support

                    contact       0.89      0.89      0.89         9
                      login       0.97      0.97      0.97        33
          join mailing list       0.80      0.53      0.64        15
                      other       0.69      0.95      0.80        21
    password/login recovery       1.00      0.94      0.97        16
               registration       1.00      0.81      0.89        21
                     search       0.96      1.00      0.98        45

                avg / total       0.92      0.91      0.90       160

    Active features: 30891 out of possible 30891

    Confusion matrix (rows=>true values, columns=>predicted values):
       c   l  m   o   p   r   s
    c  8   0  0   1   0   0   0
    l  0  32  0   1   0   0   0
    m  0   0  8   5   0   0   2
    o  1   0  0  20   0   0   0
    p  0   0  1   0  15   0   0
    r  0   1  1   2   0  17   0
    s  0   0  0   0   0   0  45

    Running cross validation...
    10-fold cross-validation F1: 0.900 (±0.087)  min=0.828  max=0.953

Dataset was sorted by domain the page is from to prevent overfitting.
Most duplicate forms are removed.

Take the numbers with a grain of salt - it is not a proper estimation
on a held-out dataset because I used these metrics to develop features
and select classification models. Generally F1 stood in ~0.9 when new
unseen data was added, so the numbers shouldn't be too off, but still,
don't take these numbers as a proper quality estimation.
