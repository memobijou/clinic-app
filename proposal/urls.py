
from django.urls import path

from proposal.datatables import TypeDatatables
from proposal.views import TypeListView

urlpatterns = [
    path(r"", TypeListView.as_view(), name="list-type"),
    path(r'datatables', TypeDatatables.as_view(), name="datatables-type"),
]
