.. _how-it-works:

How It Works
============

Formasaurus uses two separate ML models for form type detection and for
field type detection. Field type detector uses form type detection results
to improve the quality.

The model is trained on 1000+ annotated web forms - check `data`_ folder
in Formasaurus repository. Most pages to annotate were selected randomly
from `Alexa Top 1M <http://www.alexa.com/topsites>`_ websites.

Form Type Detection
-------------------

To detect HTML form types Formasaurus takes a `<form>` element and
uses a linear classifier (`Logistic Regression`_) to choose its type
from a predefined set of types. Features include:

* counts of form elements of different types,
* whether a form is POST or GET,
* text on submit buttons,
* names and char ngrams of CSS classes and IDs,
* input labels,
* presence of certain substrings in URLs,
* etc.

See `Form Type Detection.ipynb`_ IPython notebook for more detailed description.

.. _Logistic Regression: https://en.wikipedia.org/wiki/Logistic_regression
.. _Form Type Detection.ipynb: https://github.com/TeamHG-Memex/Formasaurus/blob/master/notebooks/Form%20Type%20Detection.ipynb
.. _data: https://github.com/TeamHG-Memex/Formasaurus/tree/master/formasaurus/data

Field Type Detection
--------------------

To detect form field types Formasaurus uses `Conditional Random Field`_ (CRF)
model. All fields in an HTML form is a sequence where order matters; CRF allows
to take field order in account.

Features include

* form type predicted by a form type detector,
* field tag name,
* field value,
* text before and after field,
* field CSS class and ID,
* text of field <label> element,
* field title and placeholder attributes,
* etc.

There are about 50 distinct field types.

To train field type detector we need form type labels.
There are true form types available directly in training data,
but in reality form type detecor will make mistakes at prediction time.
So we have two options:

1. Use correct form labels in training, rely on noisy form
   labels at test/prediction time.
2. Use noisy (predicted) labels both at train and test time.

Strategy (2) leads to more regularized models which account for form
type detector mistakes; strategy (1) uses more information.

Based on held-out dataset it looks like (1) produces better results.

We need noisy form type labels anyways, to check prediction quality.
To get these 'realistic' noisy form type labels we split data into 10 folds,
and then for each fold we predict its labels using form type detector
trained on the rest 9 folds.

.. _Conditional Random Field: https://en.wikipedia.org/wiki/Conditional_random_field

