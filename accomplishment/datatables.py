from django.contrib.auth.models import User
from django.db.models import Q
from django.db.models.functions import Lower
from django.urls import reverse_lazy
from accomplishment.models import Accomplishment
from accomplishment.serializers import AccomplishmentSerializer
from uniklinik.mixins import DatatablesMixin


class AccomplishmentDatatables(DatatablesMixin):
    queryset = Accomplishment.objects.all()
    serializer_class = AccomplishmentSerializer

    def __init__(self):
        super().__init__()
        self.records_total = None
        self.page_number = None
        self.page_size = None

    def get_filtered_queryset(self):
        self.filter_by_search_value()
        return self.queryset

    def filter_by_search_value(self):
        search_value = self.request.GET.get("search[value]")
        if search_value != "" and search_value is not None:
            self.queryset = self.queryset.filter(
                Q(Q(name__icontains=search_value)))

    def get_ordered_queryset(self):
        order_column_index = self.request.GET.get("order[0][column]")
        asc_or_desc = self.request.GET.get("order[0][dir]")
        if order_column_index == "0":
            if asc_or_desc == "asc":
                self.queryset = self.queryset.order_by(Lower("name"))
            else:
                self.queryset = self.queryset.annotate(lower_name=Lower('name')).order_by("-lower_name")
        return self.queryset

    def get_data(self, page):
        data = {"results": [], "records_total": self.queryset.count()}
        for query in page:
            groups_string = ""
            groups = query.groups.all()
            for group in query.groups.all():
                groups_string += group.name + "<br/>"
            users_string = ""
            for user in User.objects.filter(groups_list__in=groups).distinct():
                users_string += str(user) + "<br/>"
            data["results"].append([f'<a href="{reverse_lazy("accomplishment:edit", kwargs={"pk": query.pk})}">Bearbeiten</a>', query.name, query.full_score, groups_string, users_string])
        return data