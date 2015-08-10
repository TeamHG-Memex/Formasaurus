# -*- coding: utf-8 -*-
from __future__ import absolute_import
import os

from sklearn.externals import joblib

from formasaurus.storage import Storage
from formasaurus.model import get_model
from formasaurus.utils import dependencies_string


at_root = lambda *args: os.path.join(os.path.dirname(__file__), *args)


DEFAULT_DATA_PATH = at_root('data')


class FormExtractor(object):
    """
    FormExtractor detects HTML form types.
    """
    def __init__(self, model=None):
        self.model = model

    @classmethod
    def load(cls, filename=None, create=True):
        """
        Load model from disk file ``filename``.

        If the file is missing and ``create`` option is True (default),
        the model is created. If ``filename`` is None default model file
        name is used.

        Example - load the default extractor::

            ex = FormExtractor.load()

        """
        if filename is None:
            filename = _cached_model_path()

        if create and not os.path.exists(filename):
            ex = cls.trained_on(DEFAULT_DATA_PATH)
            ex.save(filename)
            return ex

        return joblib.load(filename)

    @classmethod
    def trained_on(cls, data_folder, train_ratio=1.0):
        """ Return a FormExtracted trained on data from data_folder """
        ex = cls()
        ex.train(data_folder=data_folder, train_ratio=train_ratio)
        return ex

    def save(self, filename):
        if self.model is None:
            raise ValueError("FormExtractor is not trained")
        joblib.dump(self, filename, compress=3)

    def train(self, data_folder, train_ratio=1.0):
        """ Train the model using data from ``data_folder``. """
        store = Storage(data_folder)
        X, y = store.get_Xy(drop_duplicates=True, verbose=True, leave=True)
        train_size = int(len(y) * train_ratio)
        X, y = X[:train_size], y[:train_size]

        model = get_model()
        print("Training on %d example(s)..." % len(y))
        model.fit(X, y)
        self.model = model

    def classify(self, form):
        """
        Return form class.
        ``form`` should be an lxml HTML <form> element.
        """
        return self.model.predict([form])[0]

    def classify_proba(self, form, threshold=0.0):
        """
        Return probabilities of ``form`` belongs to various form classes.
        ``form`` should be an lxml HTML <form> element.
        Only classes with probability >= threshold are returned.
        """
        probs = self.model.predict_proba([form])[0]
        return self._probs2dict(probs, threshold)

    def extract_forms(self, tree):
        """
        Given a lxml tree, return a list of (form_elem, form_type) tuples.
        """
        forms = tree.xpath("//form")
        if not forms:
            return []
        return list(zip(forms, self.model.predict(forms)))

    def extract_forms_proba(self, tree, threshold=0.0):
        """
        Given a lxml tree, return a list of (form_elem, probs) tuples where
        ``form_elem`` is a lxml <form> element and ``probs`` is a dictionary
        ``{type: probability}``.
        """
        forms = tree.xpath("//form")
        if not forms:
            return []
        probs = self.model.predict_proba(forms)
        prob_dicts = [self._probs2dict(p, threshold) for p in probs]
        return list(zip(forms, prob_dicts))

    def _probs2dict(self, probs, threshold):
        classes = self.classes
        res = dict(zip(classes, probs))
        return {cls: prob for cls, prob in res.items() if prob >= threshold}

    @property
    def _classifier(self):
        if self.model is None:
            raise ValueError("FormExtractor is not trained")
        return self.model.steps[-1][1]

    @property
    def classes(self):
        return self._classifier.classes_


def _cached_model_path():
    env_path = os.environ.get("FORMASAURUS_MODEL")
    if env_path:
        return os.path.expanduser(env_path)
    path = "formasaurus-%s.joblib" % dependencies_string()
    return at_root(path)
