# -*- coding: utf-8 -*-
"""
IPython widgets for data annotation.
"""
from ipywidgets import widgets
from IPython.display import display

from formasaurus.html import (
    get_cleaned_form_html,
    html_escape,
    escaped_with_field_highlighted,
    highlight_fields,
    get_field_names,
    get_fields_to_annotate
)
from formasaurus.utils import inverse_mapping, download


def AddPageWidget(storage):
    """
    Widget used to add a new web page to dataset.
    """
    url_field = widgets.Text(description='URL:', value='')
    fetch_btn = widgets.Button(description='Add')

    def on_submit(_):
        url = url_field.value.strip()
        html = download(url)
        path = storage.add_result(html, url, add_empty=False)
        if path is None:
            print("No forms at ", url)
        else:
            print("Added:", path, url)
        url_field.value = ""

    fetch_btn.on_click(on_submit)
    url_field.on_submit(on_submit)
    box = widgets.HBox([url_field, fetch_btn], padding=4)
    display(box)


def MultiFormAnnotator(annotations,
                       annotate_fields=True, annotate_types=True,
                       save_func=None):
    """
    A widget with a paginator for annotating multiple forms.
    """
    back, forward, slider = get_pager_elements(0, len(annotations) - 1)
    rendered = {}

    def render(i):
        widget = FormAnnotator(
            ann=annotations[i],
            annotate_fields=annotate_fields,
            annotate_types=annotate_types,
        )
        return widgets.VBox([
            widgets.HBox([back, forward, slider]),
            widget
        ])

    def on_change(name, value):
        for i in rendered:
            rendered[i].close()

        if value not in rendered:
            rendered[value] = render(value)
        else:
            rendered[value].open()

        if save_func:
            save_func()

        display(rendered[value])

    slider.on_trait_change(on_change, 'value')
    on_change('value', slider.value)


def FormAnnotator(ann, annotate_fields=True, annotate_types=True, max_fields=80):
    """
    Widget for annotating a single HTML form.
    """
    assert annotate_fields or annotate_types
    form_types_inv = ann.form_schema.types_inv

    children = []

    if annotate_types:
        children += [FormTypeSelect(ann)]

    tpl = """
    <h4>
        {tp} <a href='{url}'>{url}</a>
        <small>{key} #{index}</small>
    </h4>
    """
    header = widgets.HTML(tpl.format(
        url=ann.url,
        index=ann.index,
        key=ann.key,
        tp=form_types_inv.get(ann.type, '?')
    ))
    children += [header]

    if annotate_fields:
        pages = []
        names = get_field_names(get_fields_to_annotate(ann.form))
        if len(names) > max_fields:
            children += [
                widgets.HTML("<h4>Too many fields ({})</h4>".format(len(names)))
            ]
        else:
            for name in names:
                field_type_select = FieldTypeSelect(ann, name)
                html_view = HtmlView(ann.form, name)
                page = widgets.Box(children=[field_type_select, html_view])
                pages.append(page)

            field_tabs = widgets.Tab(children=pages, padding=4)
            for idx, name in enumerate(names):
                field_tabs.set_title(idx, name)

            children += [field_tabs]
    else:
        children += [HtmlView(ann.form)]

    return widgets.VBox(children, padding=8)


def FormTypeSelect(ann):
    """ Form type edit widget """

    form_types = ann.form_schema.types
    tp = ann.info['forms'][ann.index]
    type_select = widgets.ToggleButtons(
        options=list(form_types.keys()),
        value=ann.form_schema.types_inv[tp],
        padding=4,
        description='form type:',
    )

    def on_change(name, value):
        ann.info['forms'][ann.index] = form_types[value]

    type_select.on_trait_change(on_change, 'value')
    return type_select


def FieldTypeSelect(ann, field_name):
    """ Form field type edit widget """
    field_types = ann.field_schema.types
    field_types_inv = ann.field_schema.types_inv
    tp = ann.fields[field_name]
    type_select = widgets.ToggleButtons(
        options=list(field_types.keys()),
        value=field_types_inv[tp],
    )

    def on_change(name, value):
        ann.fields[field_name] = field_types[value]

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
        'max-width:800px',
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
    html_source = get_cleaned_form_html(form, human_readable=True)
    html_cleaned = get_cleaned_form_html(form, human_readable=False)

    form_display = RawHtml(html_cleaned, field_name, max_height=600)
    form_raw = HtmlCode(html_source, field_name, max_height=None)
    return widgets.VBox([form_display, form_raw])


def get_pager_elements(min, max):
    """
    Return (back, forward, slider) widgets.
    """
    back = widgets.Button(description="<- Prev")
    forward = widgets.Button(description="Next ->")
    slider = widgets.IntSlider(min=min, max=max)

    def on_back(b):
        if slider.value > min:
            slider.value -= 1

    def on_forward(b):
        if slider.value < max:
            slider.value += 1

    back.on_click(on_back)
    forward.on_click(on_forward)

    return back, forward, slider

