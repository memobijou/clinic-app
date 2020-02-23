from django.urls import path

from poll.datatables import PollDatatables
from poll.views import PollListView, PollUpdateView, OptionUpdateView, OptionDeleteView

urlpatterns = [
    path(r"", PollListView.as_view(), name="list"),
    path(r"<int:pk>/edit", PollUpdateView.as_view(), name="edit"),
    path(r"<int:pk>/option/<int:option_pk>/edit", OptionUpdateView.as_view(), name="edit-option"),
    path(r"<int:pk>/option/<int:option_pk>/delete", OptionDeleteView.as_view(), name="delete-option"),
    path(r'datatables', PollDatatables.as_view(), name="datatables"),
]
