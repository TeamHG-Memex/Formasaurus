Install
=======

Formasaurus requires Python 2.7+ or 3.3+ and the following Python packages:

* scipy_
* numpy_
* scikit-learn_ 0.17+
* sklearn-crfsuite_
* lxml_

.. _numpy: https://github.com/numpy/numpy
.. _scipy: https://github.com/scipy/scipy
.. _scikit-learn: https://github.com/scikit-learn/scikit-learn
.. _sklearn-crfsuite: https://github.com/TeamHG-Memex/sklearn-crfsuite
.. _lxml: https://github.com/lxml/lxml

First, make sure numpy_ is installed. Then, to install Formasaurus with all
its other dependencies run

::

    pip install formasaurus[with_deps]

These packages may require extra steps to install, so the command above may
fail. In this case install dependencies manually, on by one (follow their
install instructions), then run::

    pip install formasaurus

After installation it is convenient to execute ``formasaurus init`` command:
it ensures all necessary initialization is done. Without it Formasaurus
may have to do CPU and memory-heavy model training on a first import.
