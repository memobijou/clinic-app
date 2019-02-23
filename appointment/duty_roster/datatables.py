from django.db.models import Q
from django.db.models.functions import Lower
from django.urls import reverse_lazy
from appointment.models import DutyRoster
from uniklinik.mixins import DatatablesMixin


class DutyRosterDatatables(DatatablesMixin):
    queryset = DutyRoster.objects.all()
    #serializer_class = DutyRosterSerializer

    def __init__(self):
        super().__init__()
        self.records_total = None
        self.page_number = None
        self.page_size = None

    def get_filtered_queryset(self):
        search_value = self.request.GET.get("search[value]")
        if search_value != "" and search_value is not None:
            self.queryset = self.queryset.filter(Q(name__icontains=search_value))
        return self.queryset

    def get_ordered_queryset(self):
        order_column_index = self.request.GET.get("order[1][column]")
        asc_or_desc = self.request.GET.get("order[1][dir]")
        if order_column_index == "1":
            if asc_or_desc == "asc":
                self.queryset = self.queryset.order_by(Lower("name"))
            else:
                self.queryset = self.queryset.annotate(lower_name=Lower('name')).order_by("-name")
        return self.queryset

    def get_data(self, page):
        data = {"results": [[f'<p><a href="{reverse_lazy("account:edit_group", kwargs={"pk": query.pk})}">Bearbeiten</a></p>',
                             query.name] for query in page],
                "records_total": self.queryset.count()}
        return data