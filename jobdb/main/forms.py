from functools import cached_property
from typing import Any

from crispy_bootstrap5.bootstrap5 import FloatingField  # type: ignore
from crispy_forms.helper import FormHelper  # type: ignore
from crispy_forms.layout import Column, Field, Layout, Row  # type: ignore
from django.forms import (
    BooleanField,
    CharField,
    Form,
    HiddenInput,
    ModelForm,
    Textarea,
    TextInput,
)

from .models import Posting, User


class UserProfileForm(ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "phone", "linkedin"]


class URLTextareaForm(Form):
    tool = CharField(widget=HiddenInput, initial="urls_submitted")
    text = CharField(label="URL(s), one per line", widget=Textarea)


class AddPostingForm(ModelForm):
    include = BooleanField(label="", required=False, initial=True)

    class Meta:
        model = Posting
        fields = [
            "include",
            "url",
            "title",
            "location",
            "wa_jurisdiction",
            "notes",
        ]
        widgets = {"notes": TextInput}

    def __init__(self, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.fields["url"].widget.attrs["readonly"] = True

    @cached_property
    def helper(self) -> FormHelper:
        _helper = FormHelper(self)
        layout_items = []
        for field_name in self.fields.keys():
            if field_name == "include":
                layout_items.append(
                    Column(
                        Field(field_name, css_class="p-3"),
                        css_class="col-auto",
                    )
                )
                continue
            layout_items.append(
                Column(
                    FloatingField(field_name),
                    css_class="col-auto",
                )
            )
            if field_name in "url":
                layout_items.append(
                    Column(
                        Field(
                            "url",
                            template="main/form_url_open_link_widget.html",
                        ),
                        css_class="col-auto",
                    )
                )
        _helper.layout = Layout(Row(*layout_items))
        return _helper

    def is_valid(self) -> bool:
        if self.cleaned_data.get("include") is False:
            self._errors = {}  # type: ignore
            return True
        return super().is_valid()

    def save(self, *args: Any, **kwargs: Any) -> Posting:
        if self.cleaned_data.get("include") is False:
            raise Exception("This posting is excluded and cannot be saved")
        return super().save(*args, **kwargs)  # type: ignore
