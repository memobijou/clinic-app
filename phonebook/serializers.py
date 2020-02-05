from rest_framework import serializers
from phonebook.models import PhoneBook, Category


class PhoneBookSerializer(serializers.ModelSerializer):
    class Meta:
        model = PhoneBook
        fields = ('pk', 'last_name', 'first_name', 'title', 'phone_number', "mobile_number", )


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('pk', 'title',)
