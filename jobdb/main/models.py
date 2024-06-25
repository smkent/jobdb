from __future__ import annotations

import binascii
import os
from typing import Any

from django.contrib.auth.models import AbstractUser
from django.db.models import (
    CASCADE,
    CharField,
    DateTimeField,
    ForeignKey,
    IntegerChoices,
    IntegerField,
    Model,
    TextField,
    UniqueConstraint,
    URLField,
)
from django_extensions.db.models import TimeStampedModel  # type: ignore

from .fields import URLArray


class User(AbstractUser):
    phone: CharField = CharField("Phone number", max_length=10, blank=True)
    linkedin: URLField = URLField(
        "LinkedIn Profile", max_length=2048, blank=True
    )


class APIKey(TimeStampedModel):
    key: CharField = CharField("Key", max_length=40, primary_key=True)
    user: ForeignKey = ForeignKey(User, on_delete=CASCADE)

    def save(self, *args: Any, **kwargs: Any) -> APIKey:
        if not self.key:
            self.key = self.generate_key()
        return super().save(*args, **kwargs)  # type: ignore

    @classmethod
    def generate_key(cls) -> str:
        return binascii.hexlify(os.urandom(20)).decode()

    def __str__(self) -> str:
        return f"API Key for {self.user.username}: {self.key}"

    class Meta:
        verbose_name = "API Key"


class Company(TimeStampedModel):
    name: CharField = CharField(
        max_length=500, unique=True, verbose_name="Company name"
    )
    hq: CharField = CharField(
        max_length=250,
        verbose_name="Headquarters",
        help_text="Company headquarters location",
    )
    url: URLField = URLField(
        max_length=2048,
        unique=True,
        verbose_name="URL",
        help_text="Company web site URL",
    )
    careers_url: URLField = URLField(
        max_length=2048,
        unique=True,
        verbose_name="Careers URL",
        help_text="Careers page URL",
    )
    careers_urls: URLArray = URLArray(
        null=True,
        blank=True,
        verbose_name="Additional Careers URLs",
        help_text="Additional careers page URLs",
    )
    employees_est: CharField = CharField(
        max_length=100, verbose_name="Estimated number of employees"
    )
    employees_est_source: CharField = CharField(
        max_length=500, verbose_name="Estimated number of employees source"
    )
    how_found: CharField = CharField(
        max_length=250,
        blank=True,
        verbose_name="How Found",
        help_text="How the company was originally found",
    )
    notes: TextField = TextField(blank=True, verbose_name="Notes")

    def __str__(self) -> str:
        return f"{self.name}"

    class Meta:
        verbose_name_plural = "Companies"


class Posting(TimeStampedModel):
    company: ForeignKey = ForeignKey(Company, on_delete=CASCADE)
    url: URLField = URLField(
        max_length=2048,
        unique=True,
        verbose_name="Posting URL",
        help_text="Job posting URL",
    )
    job_board_urls: URLArray = URLArray(
        null=True,
        blank=True,
        verbose_name="Job Board URLs",
        help_text="Additional posting URLs that link to the main posting URL",
    )
    title: CharField = CharField(max_length=500, verbose_name="Role Title")
    closed: DateTimeField = DateTimeField(
        null=True, blank=True, verbose_name="Date Closed"
    )
    closed_note: CharField = CharField(
        max_length=1000,
        blank=True,
        verbose_name="Closed Note",
        help_text="Optional reason role is closed",
    )
    location: CharField = CharField(
        max_length=500, verbose_name="Role Location"
    )
    wa_jurisdiction: CharField = CharField(
        max_length=2000,
        blank=True,
        verbose_name="WA Jurisdiction",
        help_text="WA jurisdiction if role is remote",
    )
    notes: TextField = TextField(blank=True, verbose_name="Notes and evidence")

    def __str__(self) -> str:
        closed = " (closed)" if self.closed else ""
        return f"{self.company.name} • {self.title} • {self.url}{closed}"

    class Meta:
        verbose_name = "Job posting"


class BonaFide(IntegerChoices):
    HIGH = 1, "High"
    MEDIUM = 2, "Medium"
    LOW = 3, "Low"
    NEED_LICENSE = 4, "License or certification needed"


class Application(Model):
    user: ForeignKey = ForeignKey(User, on_delete=CASCADE)
    posting: ForeignKey = ForeignKey(Posting, on_delete=CASCADE)
    bona_fide: IntegerField = IntegerField(
        choices=BonaFide.choices,
        null=True,
        blank=True,
        verbose_name="Bona Fide rating",
    )
    applied: DateTimeField = DateTimeField(
        auto_now_add=True, verbose_name="Date Applied"
    )
    reported: DateTimeField = DateTimeField(
        null=True, blank=True, verbose_name="Date Reported"
    )
    notes: TextField = TextField(blank=True, verbose_name="Notes")

    def __str__(self) -> str:
        return (
            f"{self.user.username}"
            f" | {self.posting.company.name}"
            f" • {self.posting.title}"
        )

    class Meta:
        verbose_name = "Job application"
        constraints = [
            UniqueConstraint(
                fields=["user", "posting"],
                name="single_application_per_user_posting",
            )
        ]
