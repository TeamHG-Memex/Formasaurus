Changes
=======

0.6 (2016-01-27)
----------------

* ``fields=False`` argument is supported in ``formasaurus.extract_forms``,
  ``formasaurus.classify``, ``formasaurus.classify_proba`` functions and
   in related ``FormFieldClassifier`` methods. It allows to avoid predicting
   form field types if they are not needed.
* ``formasaurus.classifiers.instance()`` is renamed to
  ``formasaurus.classifiers.get_instance()``.
* Bias is no longer regularized for form type classifier.

0.5 (2015-12-19)
----------------

This is a major backwards-incompatible release.

* Formasaurus now can detect field types, not only form types;
* API is changed - check the updated documentation;
* there are more form types detected;
* evaluation setup is improved;
* annotation UI is rewritten using IPython widgets;
* more training data is added.

0.2 (2015-08-10)
----------------

* Python 3 support;
* fixed model auto-creation.

0.1 (2015-07-09)
----------------

Initial release.
