from functools import cached_property

from crispy_bootstrap5.bootstrap5 import FloatingField  # type: ignore
from crispy_forms.helper import FormHelper  # type: ignore
from crispy_forms.layout import Column, Layout, Row  # type: ignore
from django.forms import CharField, Form, HiddenInput, ModelForm, Textarea

from .models import Posting, User


class UserProfileForm(ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "phone", "linkedin"]


class URLTextareaForm(Form):
    tool = CharField(widget=HiddenInput, initial="urls_submitted")
    text = CharField(label="List of URLs", widget=Textarea)


class AddPostingForm(ModelForm):
    class Meta:
        model = Posting
        fields = ["url", "title", "location", "wa_jurisdiction"]

    @cached_property
    def helper(self) -> FormHelper:
        _helper = FormHelper(self)
        layout_items = []
        for field_name in self.fields.keys():
            layout_items.append(
                Column(
                    FloatingField(field_name),
                    css_class="col-auto",
                )
            )
        _helper.layout = Layout(Row(*layout_items))
        return _helper
