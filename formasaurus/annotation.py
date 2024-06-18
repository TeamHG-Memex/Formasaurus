import collections

from formasaurus.html import get_fields_to_annotate

AnnotationSchema = collections.namedtuple(
    "AnnotationSchema", "types types_inv na_value skip_value simplify_map"
)


_FormAnnotation = collections.namedtuple(
    "FormAnnotation", "form type index info key form_schema field_schema"
)


class FormAnnotation(_FormAnnotation):
    """Annotated HTML form"""

    @property
    def url(self):
        return self.info["url"]

    @property
    def fields(self):
        """
        {"field name": "field type"} dict.
        """
        return self.info["visible_html_fields"][self.index]

    @property
    def fields_annotated(self):
        """True if form has fields and all fields are annotated."""
        if not self.fields:
            return False
        return all(v != self.field_schema.na_value for v in self.fields.values())

    @property
    def form_annotated(self):
        return self.type != self.form_schema.na_value

    @property
    def fields_partially_annotated(self):
        """
        True when some fields are annotated and some are not annotated.
        """
        if not self.fields:
            return False
        values = self.fields.values()
        has_na = any(v == self.field_schema.na_value for v in values)
        has_annotated = not all(v == self.field_schema.na_value for v in values)
        return has_na and has_annotated

    @property
    def field_elems(self):
        """
        Return a list of lxml Elements for fields which are annotated.
        Fields are returned in in order they appear in form;
        only visible submittable fields are considered.
        """
        return get_fields_to_annotate(self.form)

    @property
    def field_types(self):
        """
        A list of field types, in order they appear in form.
        Only visible submittable fields are considered.
        """
        fields = self.fields
        return [fields[field.name] for field in self.field_elems]

    @property
    def field_types_full(self):
        """
        A list of long field type names, in order they appear in form.
        Only visible submittable fields are considered.
        """
        return [self.field_schema.types_inv[tp] for tp in self.field_types]

    @property
    def type_full(self):
        """Full form type name"""
        return self.form_schema.types_inv[self.type]

    def __repr__(self):
        return "FormAnnotation(form={!r}, type={!r}, index={!r}, url={!r}, key={!r}, fields={!r})".format(
            self.form, self.type, self.index, self.url, self.key, self.fields
        )
