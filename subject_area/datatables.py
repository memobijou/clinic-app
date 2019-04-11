from subject_area.models import SubjectArea
from subject_area.serializers import SubjectAreaSerializer
from uniklinik.mixins import DatatablesMixin
from django.urls import reverse_lazy


class SubjectAreaDatatables(DatatablesMixin):
    queryset = SubjectArea.objects.all()
    serializer_class = SubjectAreaSerializer

    def __init__(self):
        super().__init__()
        self.records_total = None
        self.page_number = None
        self.page_size = None

    def get_filtered_queryset(self):
        search_value = self.request.GET.get("search[value]")
        if search_value != "" and search_value is not None:
            self.queryset = self.queryset.filter(title__icontains=search_value)
        return self.queryset

    def get_ordered_queryset(self):
        order_column_index = self.request.GET.get("order[0][column]")
        asc_or_desc = self.request.GET.get("order[0][dir]")

        if order_column_index == "1":
            if asc_or_desc == "asc":
                self.queryset = self.queryset.extra(select={'lower_title': 'lower(title)'}).order_by('lower_title')
            else:
                self.queryset = self.queryset.extra(select={'lower_title': 'lower(title)'}).order_by('-lower_title')

        return self.queryset

    def get_data(self, page):
        data = {"results": [[f'<a href="{reverse_lazy("subject_area:edit", kwargs={"pk": query.pk})}">Bearbeiten</a>',
                             getattr(query, "title", "")] for query in page],
                "records_total": self.queryset.count()}
        return data
