from assertpy import add_extension #type: ignore
from django import forms, http

def contains_form(self, form_type: type[forms.Form]):
    response: http.HttpResponse = self.val
    form = form_type()

    for field in form.fields:
        field_id = f"id=\"{form[field].auto_id}\""
        if field_id.encode(response.charset) not in response.content:
            self.error(f"{field} is not in response!")

    return self

def contains_formset(self, formset_type: type[forms.BaseFormSet]):
    response: http.HttpResponse = self.val
    formset = formset_type()
    management = formset.management_form

    for field in management.fields:
        field_id = f"id=\"{management[field].auto_id}\""
        if field_id.encode(response.charset) not in response.content:
            self.error(f"{field} is not in response!")

    for form in formset:
        for field in form.fields:
            field_id = f"id=\"{form[field].auto_id}\""
            if field_id.encode(response.charset) not in response.content:
                self.error(f"{field} is not in response!")

    return self

add_extension(contains_form)
add_extension(contains_formset)