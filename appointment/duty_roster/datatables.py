from django.db.models import Q
from django.db.models.functions import Lower
from appointment.duty_roster.serializers import DutyRosterSerializer
from appointment.models import DutyRoster
from uniklinik.mixins import DatatablesMixin
from django.template.defaultfilters import date


class DutyRosterDatatables(DatatablesMixin):
    queryset = DutyRoster.objects.all()
    serializer_class = DutyRosterSerializer

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
        data = {"results": [[
            f'<p style="margin:0;padding:0;"><input type="checkbox" style="cursor:pointer;" '
            f'name="item" value={query.pk}></p>',
            f'{date(query.calendar_week_date, "F")} {query.calendar_week_date.year}', self.get_pdf(query)]
            for query in page if query.file and query.calendar_week_date
        ],
                "records_total": self.queryset.count()}
        return data

    def get_pdf(self, query):
        return f'''
        <a href="{query.file.url}">Herunterladen</a>
                '''
