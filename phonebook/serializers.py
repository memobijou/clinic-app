from rest_framework import serializers
from phonebook.models import PhoneBook


class PhoneBookSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhoneBook
        fields = ('pk', 'title', 'phone_number',)
