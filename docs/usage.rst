Usage
=====

Basic Usage
-----------

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

.. note::

    To detect form and field types Formasaurus needs to train prediction
    models on user machine. This is done automatically on first call;
    models are saved to a file and then reused.

:func:`formasaurus.extract_forms <formasaurus.classifiers.extract_forms>`
returns a list of (form, info) tuples, one tuple for each ``<form>``
element on a page. ``form`` is a lxml Element for a form,
``info`` dict contains form and field types.

Only fields which are

1. visible to user;
2. have non-empty ``name`` attribute

are returned - other fields usually should be either submitted as-is
(hidden fields) or not sent to the server at all (fields without
``name`` attribute).

There are edge cases like fields filled with JS or fields which are made
invisible using CSS, but all bets are off if page uses JS heavily and all
we have is HTML source.

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

Form Types
----------

By default, Formasaurus detects these form types:

* ``search``
* ``login``
* ``registration``
* ``password/login recovery``
* ``contact/comment``
* ``join mailing list``
* ``order/add to cart``
* all other forms are classified as ``other``.

Field Types
-----------

By deafult, Formasaurus detects these field types:

* ``username``
* ``password``
* ``password confirmation`` - "enter the same password again"
* ``email``
* ``email confirmation`` - "enter the same email again"
* ``username or email`` - a field where both username and email are accepted
* ``captcha`` - image captcha or a puzzle to solve
* ``honeypot`` - this field usually should be left blank
* ``TOS confirmation`` - "I agree with Terms of Service",
  "I agree to follow website rules", "It is OK to process my personal info", etc.
* ``receive emails confirmation`` - a checkbox which means
  "yes, it is ok to send me some sort of emails"
* ``remember me checkbox`` - common on login forms
* ``submit button`` - a button user should click to submit this form
* ``cancel button``
* ``reset/clear button``
* ``first name``
* ``last name``
* ``middle name``
* ``full name``
* ``organization name``
* ``gender``
* ``day``
* ``month``
* ``year``
* ``full date``
* ``time zone``
* ``DST`` - Daylight saving time preference
* ``country``
* ``city``
* ``state``
* ``address`` - other address information
* ``postal code``
* ``phone`` - phone number or its part
* ``fax``
* ``url``
* ``OpenID``
* ``about me text``
* ``comment text``
* ``comment title or subject``
* ``security question`` - "mother's maiden name"
* ``answer to security question``
* ``search query``
* ``search category / refinement`` - search parameter, filtering option
* ``product quantity``
* ``style select`` - style/theme select, common on forums
* ``sorting option`` - asc/desc order, items per page
* ``other number``
* ``other read-only`` - field with information user shouldn't change
* all other fields are classified as ``other``.
