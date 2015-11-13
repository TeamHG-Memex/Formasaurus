# -*- coding: utf-8 -*-
"""
IPython widgets for data annotation.
"""
from ipywidgets import widgets

from formasaurus.html import (
    get_cleaned_form_html,
    html_escape,
    escaped_with_field_highlighted,
    highlight_fields
)
from formasaurus.utils import inverse_mapping


def FormTypeSelect(ann, form_types):
    """ Form type edit widget """
    form_types_inv = inverse_mapping(form_types)
    tp = ann.info['forms'][ann.index]
    type_select = widgets.ToggleButtons(
        options=list(form_types.keys()),
        value=form_types_inv[tp],
        padding=4,
        description='form type:',
    )

    def on_change(name, value):
        ann.info['forms'][ann.index] = form_types[value]

    type_select.on_trait_change(on_change, 'value')
    return type_select



def RawHtml(html, field_name=None, max_height=500, **kwargs):
    """ Widget for displaying HTML form, optionally with a field highlighted """
    kw = {'background_color': '#def'}
    kw.update(kwargs)
    if field_name is not None:
        html = highlight_fields(html, field_name)
    mh = "max-height: {}px;".format(max_height) if max_height else ""
    return widgets.HTML(
        "<div style='padding:32px; {} overflow:auto'>{}</div>".format(mh, html),
        **kw
    )


def HtmlCode(form_html, field_name=None, max_height=None, **kwargs):
    """ Show HTML source code, optionally with a field highlighted """
    kw = {}
    if field_name is None:
        show_html = html_escape(form_html)
        kw['color'] = "#000"
    else:
        show_html = escaped_with_field_highlighted(form_html, field_name)
        kw['color'] = "#777"
    kw.update(kwargs)
    style = '; '.join([
        'white-space:pre-wrap',
        'max-width:850px',
        'word-wrap:break-word',
        'font-family:monospace',
        'overflow:scroll',
        "max-height: {}px;".format(max_height) if max_height else ""
    ])

    html_widget = widgets.HTML(
        "<div style='{}'>{}</div>".format(style, show_html),
        **kw
    )
    return widgets.Box([html_widget], padding=8)


def HtmlView(form, field_name=None):
    """ Show both rendered HTML and its simplified source code """
    html_source = get_cleaned_form_html(form, for_source=True)
    html_cleaned = get_cleaned_form_html(form, for_source=False)

    form_display = RawHtml(html_cleaned, field_name, max_height=600)
    form_raw = HtmlCode(html_source, field_name, max_height=None)
    return widgets.VBox([form_display, form_raw])
