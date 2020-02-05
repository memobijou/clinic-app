from django.urls import path
from phonebook.datatables import PhoneBookDatatables, CategoryDatatables
from rest_framework import routers
from phonebook.viewsets import PhoneBookViewSet
from django.urls import include


router = routers.DefaultRouter()
router.register(r'phone-books', PhoneBookViewSet)

urlpatterns = [
    path(r'', include(router.urls)),
    path(r'phone-books-datatables/', PhoneBookDatatables.as_view(), name="phonebook_datatables"),
    path(r'phone-books-categories-datatables/', CategoryDatatables.as_view(), name="phonebook-categories_datatables"),
]
