from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("queue", views.QueueHTMxTableView.as_view(), name="queue_htmx"),
]
