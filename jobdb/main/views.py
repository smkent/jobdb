from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from .models import Application, Company, Posting


@login_required
def index(request: HttpRequest) -> HttpResponse:
    your_apps = Application.objects.filter(user=request.user)
    return render(
        request,
        "main/index.html",
        {
            "company": Company.objects.all(),
            "posting": Posting.objects.all(),
            "application": Application.objects.all(),
            "your_apps": your_apps,
        },
    )
