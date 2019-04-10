from django.db.models import Q
from phonebook.serializers import PhoneBookSerializer
from phonebook.models import PhoneBook
from uniklinik.mixins import DatatablesMixin
from django.db.models.functions import Lower
from django.urls import reverse_lazy


class PhoneBookDatatables(DatatablesMixin):
    queryset = PhoneBook.objects.all()
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
                Q(Q(title__icontains=search_value) | Q(phone_number__icontains=search_value)))
        return self.queryset

    def get_ordered_queryset(self):
        order_column_index = self.request.GET.get("order[0][column]")
        asc_or_desc = self.request.GET.get("order[0][dir]")

        if order_column_index == "1":
            if asc_or_desc == "asc":
                self.queryset = self.queryset.extra(select={'lower_title': 'lower(title)'}).order_by('lower_title')
            else:
                self.queryset = self.queryset.extra(select={'lower_title': 'lower(title)'}).order_by('-lower_title')
        if order_column_index == "2":
            if asc_or_desc == "asc":
                self.queryset = self.queryset.order_by('phone_number')
            else:
                self.queryset = self.queryset.order_by('-phone_number')
        return self.queryset

    def get_data(self, page):
        data = {"results": [[f'<a href="{reverse_lazy("phonebook:edit", kwargs={"pk": query.pk})}">Bearbeiten</a>',
                             query.title, query.phone_number] for query in page],
                "records_total": self.queryset.count()}
        return data
