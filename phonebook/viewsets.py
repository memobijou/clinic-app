from rest_framework import viewsets
from phonebook.models import PhoneBook
from phonebook.serializers import PhoneBookSerializer
from rest_framework import mixins


class PhoneBookViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = PhoneBookSerializer
    queryset = PhoneBook.objects.all()
