# -*- coding: utf-8 -*-
from __future__ import absolute_import
import os

import six
from sklearn.externals import joblib

from formasaurus import formtype_model, fieldtype_model
from formasaurus.html import get_forms, get_fields_to_annotate, load_html
from formasaurus.storage import Storage
from formasaurus.utils import dependencies_string, at_root, thresholded

DEFAULT_DATA_PATH = at_root('data')


def extract_forms(tree_or_html, proba=False, threshold=0.05, fields=True):
    """
    Given a lxml tree or HTML source code, return a list of
    ``(form_elem, form_info)`` tuples.

    ``form_info`` dicts contain results of :meth:`classify` or
    :meth:`classify_proba`` calls, depending on ``proba`` parameter.

    When ``fields`` is False, field type information is not computed.
    """
    return get_instance().extract_forms(
        tree_or_html=tree_or_html,
        proba=proba,
        threshold=threshold,
        fields=fields,
    )


def classify(form, fields=True):
    """
    Return ``{'form': 'type', 'fields': {'name': 'type', ...}}``
    dict with form type and types of its visible submittable fields.

    If ``fields`` argument is False, only information about form type is
    returned: ``{'form': 'type'}``.
    """
    return get_instance().classify(form, fields=fields)


def classify_proba(form, threshold=0.0, fields=True):
    """
    Return dict with probabilities of ``form`` and its fields belonging
    to various form and field classes::

        {
            'form': {'type1': prob1, 'type2': prob2, ...},
            'fields': {
                'name': {'type1': prob1, 'type2': prob2, ...},
                ...
            }
        }

    ``form`` should be an lxml HTML <form> element.
    Only classes with probability >= ``threshold`` are preserved.

    If ``fields`` is False, only information about the form is returned::

        {
            'form': {'type1': prob1, 'type2': prob2, ...}
        }

    """
    return get_instance().classify_proba(
        form=form,
        threshold=threshold,
        fields=fields,
    )


class FormFieldClassifier(object):
    """
    FormFieldClassifier detects HTML form and field types.
    """
    def __init__(self, form_classifier=None, field_model=None):
        self.form_classifier = form_classifier
        self._field_model = field_model

    @classmethod
    def load(cls, filename=None, autocreate=True, rebuild=False):
        """
        Load extractor from file ``filename``.

        If the file is missing and ``autocreate`` option is True (default),
        the model is created using default parameters and training data.
        If ``filename`` is None then default model file name is used.

        Example - load the default extractor::

            ffc = FormFieldClassifier.load()

        """
        if filename is None:
            filename = cls._cached_model_path()

        if rebuild or (autocreate and not os.path.exists(filename)):
            ex = cls.trained_on(DEFAULT_DATA_PATH)
            ex.save(filename)
            return ex

        return joblib.load(filename)

    @classmethod
    def trained_on(cls, data_folder):
        """ Return Formasaurus object trained on data from data_folder """
        store = Storage(data_folder)
        print("Loading training data...")
        annotations = list(store.iter_annotations(
            simplify_form_types=True,
            simplify_field_types=True,
            verbose=True,
            leave=True,
        ))
        ex = cls()
        ex.train(annotations)
        return ex

    def save(self, filename):
        if self.form_classifier is None or self._field_model is None:
            raise ValueError("FormFieldExtractor is not trained")
        joblib.dump(self, filename, compress=3)

    def train(self, annotations):
        """ Train FormFieldExtractor on a list of FormAnnotation objects. """
        print("Training form type detector on %d example(s)..." % len(annotations))
        self.form_classifier = FormClassifier(full_type_names=True)
        self.form_classifier.train(annotations)

        print("Training field type detector...")
        self._field_model = fieldtype_model.train(
            annotations=annotations,
            use_precise_form_types=True,
            full_field_type_names=True,
            full_form_type_names=self.form_classifier.full_type_names,
            verbose=True,
        )

    def classify(self, form, fields=True):
        """
        Return ``{'form': 'type', 'fields': {'name': 'type', ...}}``
        dict with form type and types of its visible submittable fields.

        If ``fields`` argument is False, only information about form type is
        returned: ``{'form': 'type'}``.
        """
        form_type = self.form_classifier.classify(form)
        res = {'form': form_type}
        if fields:
            field_elems = get_fields_to_annotate(form)
            xseq = fieldtype_model.get_form_features(form, form_type, field_elems)
            yseq = self._field_model.predict_single(xseq)
            res['fields'] = {
                elem.name: cls
                for elem, cls in zip(field_elems, yseq)
            }
        return res

    def classify_proba(self, form, threshold=0.0, fields=True):
        """
        Return dict with probabilities of ``form`` and its fields belonging
        to various form and field classes::

            {
                'form': {'type1': prob1, 'type2': prob2, ...},
                'fields': {
                    'name': {'type1': prob1, 'type2': prob2, ...},
                    ...
                }
            }

        ``form`` should be an lxml HTML <form> element.
        Only classes with probability >= ``threshold`` are preserved.

        If ``fields`` is False, only information about the form is returned::

            {
                'form': {'type1': prob1, 'type2': prob2, ...}
            }

        """
        form_types_proba = self.form_classifier.classify_proba(form, threshold)
        res = {'form': form_types_proba}

        if fields:
            form_type = max(form_types_proba, key=lambda p: form_types_proba[p])
            field_elems = get_fields_to_annotate(form)
            xseq = fieldtype_model.get_form_features(form, form_type, field_elems)
            yseq = self._field_model.predict_marginals_single(xseq)
            res['fields'] = {
                elem.name: thresholded(probs, threshold)
                for elem, probs in zip(field_elems, yseq)
            }

        return res

    def extract_forms(self, tree_or_html, proba=False, threshold=0.05,
                      fields=True):
        """
        Given a lxml tree or HTML source code, return a list of
        ``(form_elem, form_info)`` tuples.

        ``form_info`` dicts contain results of :meth:`classify` or
        :meth:`classify_proba`` calls, depending on ``proba`` parameter.

        When ``fields`` is False, field type information is not computed.
        """
        if isinstance(tree_or_html, (six.string_types, bytes)):
            tree = load_html(tree_or_html)
        else:
            tree = tree_or_html
        forms = get_forms(tree)
        if proba:
            return [(form, self.classify_proba(form, threshold, fields))
                    for form in forms]
        else:
            return [(form, self.classify(form, fields)) for form in forms]

    @classmethod
    def _cached_model_path(cls):
        env_path = os.environ.get("FORMASAURUS_MODEL")
        if env_path:
            return os.path.expanduser(env_path)
        path = "formasaurus-%s.joblib" % dependencies_string()
        return at_root(path)

    @property
    def form_classes(self):
        """ Possible form classes """
        return self.form_classifier.classes

    @property
    def field_classes(self):
        """ Possible field classes """
        return self._field_model.classes_


class FormClassifier(object):
    """
    Convenience wrapper for scikit-learn based form type detection model.
    """
    def __init__(self, form_model=None, full_type_names=True):
        self.model = form_model
        self.full_type_names = full_type_names

    def classify(self, form):
        """
        Return form class.
        ``form`` should be an lxml HTML <form> element.
        """
        return self.model.predict([form])[0]

    def classify_proba(self, form, threshold=0.0):
        """
        Return form class.
        ``form`` should be an lxml HTML <form> element.
        """
        probs = self.model.predict_proba([form])[0]
        return self._probs2dict(probs, threshold)

    def train(self, annotations):
        """ Train FormExtractor on a list of FormAnnotation objects. """
        self.model = formtype_model.train(
            annotations=annotations,
            full_type_names=self.full_type_names,
        )

    def extract_forms(self, tree_or_html, proba=False, threshold=0.05):
        """
        Given a lxml tree or HTML source code, return a list of
        ``(form_elem, form_info)`` tuples. ``form_info`` dicts contain results
        of :meth:`classify` or :meth:`classify_proba`` calls, depending on
        ``proba`` parameter.
        """
        forms = get_forms(load_html(tree_or_html))
        if proba:
            return [(form, self.classify_proba(form, threshold))
                    for form in forms]
        else:
            return [(form, self.classify(form)) for form in forms]

    @property
    def classes(self):
        if self.model is None:
            raise ValueError("FormExtractor is not trained")
        return self.model.steps[-1][1].classes_

    def _probs2dict(self, probs, threshold):
        return thresholded(dict(zip(self.classes, probs)), threshold)



_form_field_classifier = None

def get_instance():
    """ Return a shared FormFieldClassifier instance """
    global _form_field_classifier
    if _form_field_classifier is None:
        _form_field_classifier = FormFieldClassifier.load()
    return _form_field_classifier
