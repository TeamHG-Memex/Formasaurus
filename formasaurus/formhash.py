# -*- coding: utf-8 -*-
from copy import deepcopy

import six
import lxml.html

from formasaurus.html import remove_by_xpath


def get_form_hash(form, only_visible=True):
    """
    Return a string which is the same for duplicate forms, but different
    for forms which are not the same.

    If only_visible is True, hidden fields are not taken in account.
    """
    if isinstance(form, six.string_types):
        form = lxml.html.fromstring(form)
    else:
        form = deepcopy(form)

    if only_visible:
        remove_by_xpath(form, "input[@type='hidden']")

    html = lxml.html.tostring(form, pretty_print=True, encoding="unicode")
    lines = [line.strip() for line in html.splitlines(False) if line.strip()]

    # return the whole string as a hash, for easier debugging
    return "\n".join(lines)

