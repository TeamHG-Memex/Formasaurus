# -*- coding: utf-8 -*-
"""
This module provides scikit-learn transformers
for extracting features from HTML forms.
"""
from __future__ import absolute_import

import collections
from six.moves.urllib import parse as urlparse

import lxml.html
from sklearn.base import BaseEstimator, TransformerMixin


def _add_scheme_if_missing(url):
    if "//" not in url:
        url = "http://%s" % url
    return url


def _get_type_counts(form):
    typecount = collections.defaultdict(int)
    for x in form.inputs:
        if isinstance(x, lxml.html.InputElement):
            type_ = x.type
        elif isinstance(x, lxml.html.TextareaElement):
            type_ = "textarea"
        elif isinstance(x, lxml.html.SelectElement):
            type_ = "select"
        else:
            type_ = "other"
        typecount[type_] += 1
    return typecount


class BaseFormFeatureExtractor(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        return [self.get_form_features(form) for form in X]

    def get_form_features(self, form):
        raise NotImplementedError()


class FormElements(BaseFormFeatureExtractor):
    """
    Features based on form HTML elements: counts of elements
    of different types, GET/POST form method.
    """
    def get_form_features(self, form):
        typecounts = _get_type_counts(form)
        return {
            'has <textarea>': typecounts['textarea'] > 0,
            'has <input type=radio>': typecounts['radio'] > 0,
            'has <select>': typecounts['select'] > 0,
            'has <input type=checkbox>': typecounts['checkbox'] > 0,
            'has <input type=email>': typecounts['email'] > 0,

            '2 or 3 inputs': len(form.inputs.keys()) in {2, 3},

            'no <input type=password>': typecounts['password'] == 0,
            'exactly one <input type=password>': typecounts['password'] == 1,
            'exactly two <input type=password>': typecounts['password'] == 2,

            'no <input type=text>': typecounts['text'] == 0,
            'exactly one <input type=text>': typecounts['text'] == 1,
            'exactly two <input type=text>': typecounts['text'] == 2,
            '3 or more <input type=text>': typecounts['text'] >= 3,

            '<form method': form.method.lower().strip() or "MISSING",
        }


class Bias(BaseFormFeatureExtractor):
    """ The same as clf.intercept_ """
    def get_form_features(self, form):
        return {'bias': 1}


class FormText(BaseFormFeatureExtractor):
    """
    Text contents inside the form.
    """
    def get_form_features(self, form):
        return " ".join(form.xpath(".//text()"))


class FormInputNames(BaseFormFeatureExtractor):
    """
    Names of all non-hidden <input> elements, joined to a single string.
    """
    def get_form_features(self, form):
        names = " ".join(form.xpath('.//input[not(@type="hidden")]/@name'))
        return names.replace("_", "").replace("[", "").replace("]", "")


class FormInputHiddenNames(BaseFormFeatureExtractor):
    """
    Names of all <input type=hidden> elements, joined to a single string.
    """
    def get_form_features(self, form):
        names = " ".join(form.xpath('.//input[@type="hidden"]/@name'))
        return names.replace("_", "").replace("[", "").replace("]", "")


class FormLinksText(BaseFormFeatureExtractor):
    """
    Text of all links inside the form.
    It is helpful because e.g. registration links
    inside login forms are common.
    """
    def get_form_features(self, form):
        return " ".join(form.xpath(".//a//text()"))


class SubmitText(BaseFormFeatureExtractor):
    """
    Text of all <submit> buttons, joined to a single string.
    """
    def get_form_features(self, form):
        return " ".join(form.xpath('.//input[@type="submit"]/@value'))


class FormUrl(BaseFormFeatureExtractor):
    """ <form action> value """
    def get_form_features(self, form):
        url = form.get("action", "")
        if not url:
            return url
        url = _add_scheme_if_missing(url)
        p = urlparse.urlparse(url)
        parts = [
            self._normalize(part)
            for part in [p.path, p.params, p.query, p.fragment]
        ]
        return "%s%s%s#%s" % tuple(parts)

    def _normalize(self, part):
        return part.replace("/", "").replace("_", "").replace("-", "")


class FormCss(BaseFormFeatureExtractor):
    """ Form CSS classes and ID """
    def get_form_features(self, form):
        return " ".join([
            form.get("class", ""),
            form.get("id", ""),
        ])


class FormInputTitle(BaseFormFeatureExtractor):
    """ <input title=...> values """
    def get_form_features(self, form):
        return " ".join(form.xpath('.//input[not(@type="hidden")]/@title'))


class FormLabelText(BaseFormFeatureExtractor):
    """ <label> values """
    def get_form_features(self, form):
        return " ".join(form.xpath('.//label//text()'))


class FormInputCss(BaseFormFeatureExtractor):
    """ CSS classes and IDs of <input> elemnts """
    def get_form_features(self, form):
        inputs = form.xpath('.//input[not(@type="hidden")]')
        return " ".join([
            "%s %s" % (inp.get("class", ""), inp.get("id", ""))
            for inp in inputs
        ])


class OldLoginformFeatures(BaseFormFeatureExtractor):
    """ Features that loginform library used. """
    def get_form_features(self, form):
        return loginform_features(form)


def loginform_features(form):
    """ A dict with features from loginform library """
    typecount = _get_type_counts(form)
    res = {
        '2_or_3_inputs': len(form.inputs.keys()) in {2, 3},
        'typecount_text_gt1': (typecount['text'] > 1),
        'typecount_text_0': (typecount['text'] == 0),
        'typecount_password_eq1': (typecount['password'] == 1),
        'typecount_password_0': (typecount['password'] == 0),
        'typecount_checkbox_gt1': (typecount['checkbox'] > 1),
        'typecount_radio_gt0': (typecount['radio'] > 0),
    }
    return res

