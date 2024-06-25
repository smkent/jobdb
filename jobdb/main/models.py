from __future__ import annotations

import binascii
import os
from typing import Any

from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import connection
from django.db.models import (
    CASCADE,
    PROTECT,
    CharField,
    DateTimeField,
    ForeignKey,
    IntegerChoices,
    IntegerField,
    Model,
    Q,
    QuerySet,
    TextField,
    UniqueConstraint,
    URLField,
)
from django_extensions.db.models import TimeStampedModel  # type: ignore

from .fields import AppliedDateField, URLArray


class User(AbstractUser):
    phone: CharField = CharField("Phone number", max_length=10, blank=True)
    linkedin: URLField = URLField(
        "LinkedIn Profile", max_length=2048, blank=True
    )


class APIKey(TimeStampedModel):
    key: CharField = CharField("Key", max_length=40, primary_key=True)
    user: ForeignKey = ForeignKey(User, on_delete=CASCADE)
    comment: CharField = CharField("Comment", max_length=250, blank=True)

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


class PostingQuerySet(QuerySet):
    def _by_url_filter(self, url: str) -> Q:
        if connection.vendor == "sqlite":
            q_jb_urls = Q(job_board_urls__icontains=url)
        else:
            q_jb_urls = Q(job_board_urls__contains=url)
        return Q(url=url) | q_jb_urls

    def by_url(self, url: str) -> QuerySet:
        return self.filter(self._by_url_filter(url))


class Posting(TimeStampedModel):
    company: ForeignKey = ForeignKey(Company, on_delete=PROTECT)
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

    def _check_duplicate_urls(self) -> None:
        for url in [self.url] + (self.job_board_urls or []):
            if self.__class__.objects.by_url(url).count() > 0:  # type: ignore
                raise ValidationError(
                    f"A posting containing URL {url} already exists"
                )

    def save(self, *args: Any, **kwargs: Any) -> None:
        self._check_duplicate_urls()
        super().save(*args, **kwargs)

    objects = PostingQuerySet.as_manager()

    class Meta:
        verbose_name = "Job posting"


class BonaFide(IntegerChoices):
    HIGH = 1, "High"
    MEDIUM = 2, "Medium"
    LOW = 3, "Low"
    NEED_LICENSE = 4, "License or certification needed"


class Application(Model):
    user: ForeignKey = ForeignKey(User, on_delete=PROTECT)
    posting: ForeignKey = ForeignKey(Posting, on_delete=PROTECT)
    bona_fide: IntegerField = IntegerField(
        choices=BonaFide.choices,
        null=True,
        blank=True,
        verbose_name="Bona Fide rating",
    )
    applied: AppliedDateField = AppliedDateField(verbose_name="Date Applied")
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
