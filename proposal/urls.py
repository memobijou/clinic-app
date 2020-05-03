
from django.urls import path

from proposal.datatables import TypeDatatables, ProposalDatatables
from proposal.views import TypeListView, TypeUpdateView, ProposalListView, ProposalUpdateView, ProposalDeleteView

urlpatterns = [
    path(r"types/", TypeListView.as_view(), name="list-type"),
    path(r"types/<int:pk>/", TypeUpdateView.as_view(), name="edit-type"),
    path(r'datatables-type/', TypeDatatables.as_view(), name="datatables-type"),
    path(r'datatables/', ProposalDatatables.as_view(), name="datatables"),
    path(r'', ProposalListView.as_view(), name="list"),
    path(r'<int:pk>/edit', ProposalUpdateView.as_view(), name="edit"),
    path(r'delete/', ProposalDeleteView.as_view(), name="delete"),
]
