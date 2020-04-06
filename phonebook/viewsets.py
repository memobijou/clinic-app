from rest_framework import viewsets
from phonebook.models import PhoneBook, Category
from phonebook.serializers import PhoneBookSerializer, CategorySerializer
from rest_framework import mixins
from django.db.models import Q
from rest_framework import pagination
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User


class CustomPagination(pagination.PageNumberPagination):
    page_size = 500


class PhoneBookViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = PhoneBookSerializer
    queryset = PhoneBook.objects.all().order_by("last_name")
    pagination_class = CustomPagination

    def get_queryset(self):
        q = self.request.GET.get("q")
        if q:
            self.queryset = self.queryset.filter(
                Q(Q(last_name__icontains=q) | Q(first_name__icontains=q) | Q(title__icontains=q)
                  | Q(phone_number__icontains=q) | Q(mobile_number__icontains=q))
            )
        category_id = self.request.GET.get("category_id")
        if category_id:
            self.queryset = self.queryset.filter(category_id=category_id)

        user_id = self.request.query_params.get("user_id")

        if user_id:
            user = get_object_or_404(User, pk=user_id)
            profile = user.profile
            profile.phonebook_badges = 0
            profile.save()

        return self.queryset


class CategoryViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = CategorySerializer
    queryset = Category.objects.all().order_by("title")
    pagination_class = CustomPagination

    def get_queryset(self):
        q = self.request.GET.get("q")
        if q:
            self.queryset = self.queryset.filter(
                Q(Q(title__icontains=q))
            )
        return self.queryset
