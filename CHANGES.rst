Changes
=======

0.8 (2016-05-24)
----------------

* more annotated data for captchas;
* ``formasaurus init`` command which trains & caches the model.

0.7.2 (2016-04-18)
------------------

* pip bug with ``pip install formasaurus[with-deps]`` is worked around;
  it should work now as ``pip install formasaurus[with_deps]``.

0.7.1 (2016-03-03)
------------------

* fixed API documentation at readthedocs.org

0.7 (2016-03-03)
----------------

* more annotated data;
* new ``form_classes`` and ``field_classes`` attributes of FormFieldClassifer;
* more robust web page encoding detection in ``formasaurus.utils.download``;
* bug fixes in annotation widgets;

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
