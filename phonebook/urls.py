from django.urls import path
from phonebook.views import PhoneBookCreateView, PhoneBookListView, PhoneBookUpdateView, CategoryCreateView, \
    CategoryUpdateView

urlpatterns = [
    path('', PhoneBookListView.as_view(), name="list"),
    path('new', PhoneBookCreateView.as_view(), name="create"),
    path('<int:pk>/edit', PhoneBookUpdateView.as_view(), name="edit"),
    path('categories', CategoryCreateView.as_view(), name="category-list"),
    path('categories/<int:pk>/edit', CategoryUpdateView.as_view(), name="category-edit"),
]
