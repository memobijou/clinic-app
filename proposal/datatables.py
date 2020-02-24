from django.db.models import Q
from django.db.models.functions import Lower
from django.urls import reverse_lazy
from proposal.models import Type
from proposal.serializers import TypeSerializer
from uniklinik.mixins import DatatablesMixin


class TypeDatatables(DatatablesMixin):
    queryset = Type.objects.all()
    serializer_class = TypeSerializer

    def __init__(self):
        super().__init__()
        self.records_total = None
        self.page_number = None
        self.page_size = None

    def get_filtered_queryset(self):
        self.filter_by_search_value()
        return self.queryset

    def filter_by_search_value(self):
        whole_search_value = self.request.GET.get("search[value]")
        search_values = whole_search_value.split(" ")
        for search_value in search_values:
            if search_value != "" and search_value is not None:
                self.queryset = self.queryset.filter(
                    Q(Q(title__icontains=search_value))).distinct()

    def get_ordered_queryset(self):
        order_column_index = self.request.GET.get("order[0][column]")
        asc_or_desc = self.request.GET.get("order[0][dir]")
        if order_column_index == "1":
            if asc_or_desc == "asc":
                self.queryset = self.queryset.order_by(Lower("title"))
            else:
                self.queryset = self.queryset.annotate(lower_title=Lower('title')).order_by("-lower_title")
        return self.queryset

    def get_data(self, page):
        data = {"results": [], "records_total": self.queryset.count()}
        for query in page:
            data["results"].append([
                f'<a href="">Bearbeiten</a>',
                # f'<a href="{reverse_lazy("poll:edit", kwargs={"pk": query.pk})}">Bearbeiten</a>',
                query.title])
        return data
