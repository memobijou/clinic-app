from django.db.models import Q
from phonebook.serializers import PhoneBookSerializer, CategorySerializer
from phonebook.models import PhoneBook, Category
from uniklinik.mixins import DatatablesMixin
from django.db.models.functions import Lower
from django.urls import reverse_lazy


class PhoneBookDatatables(DatatablesMixin):
    queryset = PhoneBook.objects.all().order_by("first_name")
    serializer_class = PhoneBookSerializer

    def __init__(self):
        super().__init__()
        self.records_total = None
        self.page_number = None
        self.page_size = None

    def get_filtered_queryset(self):
        search_value = self.request.GET.get("search[value]")
        if search_value != "" and search_value is not None:
            self.queryset = self.queryset.filter(
                Q(Q(title__icontains=search_value) | Q(phone_number__icontains=search_value) |
                  Q(first_name__icontains=search_value) | Q(last_name__icontains=search_value)
                  | Q(mobile_number__icontains=search_value)))
        return self.queryset

    def get_ordered_queryset(self):
        order_column_index = self.request.GET.get("order[0][column]")
        asc_or_desc = self.request.GET.get("order[0][dir]")

        if order_column_index == "1":
            if asc_or_desc == "asc":
                self.queryset = self.queryset.extra(
                    select={'lower_last_name': 'lower(last_name)'}).order_by('lower_last_name')
            else:
                self.queryset = self.queryset.extra(
                    select={'lower_last_name': 'lower(last_name)'}).order_by('-lower_last_name')
        if order_column_index == "2":
            if asc_or_desc == "asc":
                self.queryset = self.queryset.extra(
                    select={'lower_first_name': 'lower(first_name)'}).order_by('lower_first_name')
            else:
                self.queryset = self.queryset.extra(
                    select={'lower_first_name': 'lower(first_name)'}).order_by('-lower_first_name')
        if order_column_index == "3":
            if asc_or_desc == "asc":
                self.queryset = self.queryset.extra(
                    select={'lower_title': 'lower(title)'}).order_by('lower_title')
            else:
                self.queryset = self.queryset.extra(
                    select={'lower_title': 'lower(title)'}).order_by('-lower_title')
        if order_column_index == "4":
            if asc_or_desc == "asc":
                self.queryset = self.queryset.order_by('phone_number')
            else:
                self.queryset = self.queryset.order_by('-phone_number')
        if order_column_index == "5":
            if asc_or_desc == "asc":
                self.queryset = self.queryset.order_by('mobile_number')
            else:
                self.queryset = self.queryset.order_by('-mobile_number')
        return self.queryset

    def get_data(self, page):
        data = {"results": [[f'<a href="{reverse_lazy("phonebook:edit", kwargs={"pk": query.pk})}">Bearbeiten</a>',
                             query.last_name, query.first_name, query.title, query.phone_number, query.mobile_number]
                            for query in page],
                "records_total": self.queryset.count()}
        return data


class CategoryDatatables(DatatablesMixin):
    queryset = Category.objects.all().order_by("title")
    serializer_class = CategorySerializer

    def __init__(self):
        super().__init__()
        self.records_total = None
        self.page_number = None
        self.page_size = None

    def get_filtered_queryset(self):
        search_value = self.request.GET.get("search[value]")
        if search_value != "" and search_value is not None:
            self.queryset = self.queryset.filter(
                Q(Q(title__icontains=search_value)))
        return self.queryset

    def get_ordered_queryset(self):
        order_column_index = self.request.GET.get("order[0][column]")
        asc_or_desc = self.request.GET.get("order[0][dir]")

        if order_column_index == "1":
            if asc_or_desc == "asc":
                self.queryset = self.queryset.extra(
                    select={'lower_title': 'lower(title)'}).order_by('lower_title')
            else:
                self.queryset = self.queryset.extra(
                    select={'lower_title': 'lower(title)'}).order_by('-lower_title')
        return self.queryset

    def get_data(self, page):
        data = {"results": [[
            f'<a href="{reverse_lazy("phonebook:category-edit", kwargs={"pk": query.pk})}">Bearbeiten</a>', query.title]
                            for query in page],
                "records_total": self.queryset.count()}
        return data
