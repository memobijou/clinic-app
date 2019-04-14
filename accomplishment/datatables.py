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
                Q(Q(name__icontains=search_value) | Q(subject_areas__title__icontains=search_value) |
                  Q(users__first_name__icontains=search_value) | Q(users__last_name__icontains=search_value) |
                  Q(full_score__icontains=search_value))).distinct()

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
            subject_areas_string = ""
            subject_areas = query.subject_areas.all()
            for subject_area in subject_areas:
                subject_areas_string += subject_area.title + "<br/>"
            users_string = ""
            for user in query.users.all():
                users_string += str(user) + "<br/>"
            data["results"].append([
                f'<a href="{reverse_lazy("accomplishment:edit", kwargs={"pk": query.pk})}">Bearbeiten</a>',
                query.name, query.full_score, subject_areas_string, users_string])
        return data
