from django.urls import path
from phonebook.views import PhoneBookCreateView, PhoneBookListView, PhoneBookUpdateView

urlpatterns = [
    path('', PhoneBookListView.as_view(), name="list"),
    path('new', PhoneBookCreateView.as_view(), name="create"),
    path('<int:pk>/edit', PhoneBookUpdateView.as_view(), name="edit")
]
