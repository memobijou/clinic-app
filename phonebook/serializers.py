from rest_framework import serializers
from phonebook.models import PhoneBook


class PhoneBookSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhoneBook
        fields = ('pk', 'last_name', 'first_name', 'title', 'phone_number', "mobile_number", )
