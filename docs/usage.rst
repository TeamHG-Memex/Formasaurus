Usage
=====

Grab some HTML:

    >>> import requests
    >>> html = requests.get('https://www.github.com/').text

Then use :func:`formasaurus.extract_forms <formasaurus.classifiers.extract_forms>`
to detect form and field types:

    >>> import formasaurus
    >>> formasaurus.extract_forms(html)
    [(<Element form at 0x1150ba0e8>,
      {'fields': {'q': 'search query'}, 'form': 'search'}),
     (<Element form at 0x1150ba138>,
      {'fields': {'user[email]': 'email',
        'user[login]': 'username',
        'user[password]': 'password'},
       'form': 'registration'})]

It returns a list of (form, info) tuples, one tuple for each ``<form>``
element on a page. ``info`` dict contains form and field types.

.. note::

    To detect form and field types Formasaurus needs to train prediction
    models on user machine. This is done automatically on first call;
    models are saved to a file and then reused.

By default, info dict contains only most likely form and field types.
To get probabilities pass ``proba=True``:

    >>> formasaurus.extract_forms(html, proba=True, threshold=0.05)
    [(<Element form at 0x1150db408>,
      {'fields': {'q': {'search query': 0.999129068423436}},
       'form': {'search': 0.99580680143321776}}),
     (<Element form at 0x1150dbae8>,
      {'fields': {'user[email]': {'email': 0.9980438256540791},
        'user[login]': {'username': 0.9877912041558733},
        'user[password]': {'password': 0.9968113886622333}},
       'form': {'login': 0.12481875549840604,
        'registration': 0.86248202363754578}})]

Note that Formasaurus is less certain about the second form type - it thinks
most likely the form is a registration form (0.86%), but the form
also looks similar to a login form (12%).

``threshold`` argument can be used to filter out low-probability options;
we used 0.05 in this example. To get probabilities of all classes use
``threshold=0``.

To classify individual forms use
:func:`formasaurus.classify <formasaurus.classifiers.classify>`
or :func:`formasaurus.classify_proba <formasaurus.classifiers.classify_proba>`.
They accept lxml <form> Elements. Let's load an HTML file using lxml:

    >>> import lxml.html
    >>> tree = lxml.html.parse("http://google.com")

and then classify the first form on this page:

    >>> form = tree.xpath('//form')[0]
    >>> formasaurus.classify(form)
    {'fields': {'btnG': 'submit button',
      'btnI': 'submit button',
      'q': 'search query'},
     'form': 'search'}

    >>> formasaurus.classify_proba(form, threshold=0.1)
    {'fields': {'btnG': {'submit button': 0.9254039698573596},
      'btnI': {'submit button': 0.9642014575642849},
      'q': {'search query': 0.9959819637966439}},
     'form': {'search': 0.98794025545508202}}

In this example the data is loaded from an URL; of course, data may be
loaded from a local file or from an in-memory object, or you may already
have the tree loaded (e.g. with Scrapy).

