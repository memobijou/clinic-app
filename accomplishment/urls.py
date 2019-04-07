from django.urls import path

from accomplishment.datatables import AccomplishmentDatatables

# Routers provide an easy way of automatically determining the URL conf.
from accomplishment.views import AccomplishmentListView, AccomplishmentUpdateView


urlpatterns = [
    path(r'datatables', AccomplishmentDatatables.as_view(), name="datatables"),
    path(r"", AccomplishmentListView.as_view(), name="list"),
    path(r"<int:pk>/edit", AccomplishmentUpdateView.as_view(), name="edit")
]

