from django.urls import path

from poll.datatables import PollDatatables
from poll.views import PollListView, PollUpdateView


urlpatterns = [
    path(r"", PollListView.as_view(), name="list"),
    path(r"<int:pk>/edit", PollUpdateView.as_view(), name="edit"),
    path(r'datatables', PollDatatables.as_view(), name="datatables"),
]
