from django.db.models import Q
from django.db.models.functions import Lower
from django.urls import reverse_lazy
from proposal.models import Type, Proposal
from proposal.serializers import TypeSerializer
from uniklinik.mixins import DatatablesMixin


class ProposalDatatables(DatatablesMixin):
    queryset = Proposal.objects.all()
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
                    Q(Q(user__first_name__icontains=search_value) | Q(user_last_name__icontains=search_value))
                ).distinct()

    def get_ordered_queryset(self):
        order_column_index = self.request.GET.get("order[0][column]")
        asc_or_desc = self.request.GET.get("order[0][dir]")
        if order_column_index == "1":
            if asc_or_desc == "asc":
                self.queryset = self.queryset.order_by(Lower("user__first_name"))
            else:
                self.queryset = self.queryset.annotate(
                    lower_first_name=Lower('user__first_name')).order_by("-lower_first_name")
        if order_column_index == "2":
            if asc_or_desc == "asc":
                self.queryset = self.queryset.order_by(Lower("user__last_name"))
            else:
                self.queryset = self.queryset.annotate(
                    lower_last_name=Lower('user__last_name')).order_by("-lower_last_name")
        return self.queryset

    def get_data(self, page):
        data = {"results": [], "records_total": self.queryset.count()}
        for query in page:
            title = ""
            type_ = query.type
            if type_:
                title = type_.title
            confirmation = ""
            if query.confirmed is True:
                confirmation = '<span class="glyphicon glyphicon-ok" style="color:green;"></span>'
            elif query.confirmed is False:
                confirmation = '<span class="glyphicon glyphicon-remove" style="color:red;"></span>'
            else:
                confirmation = "?"

            data["results"].append([
                f'<a href="{reverse_lazy("proposal:edit", kwargs={"pk": query.pk})}">Bearbeiten</a>'
                f'<br/><input type="checkbox" name="item" style="cursor:pointer;" value="{query.pk}"/>',
                # f'<a href="{reverse_lazy("poll:edit", kwargs={"pk": query.pk})}">Bearbeiten</a>',
                query.user.first_name, query.user.last_name, title, query.start_date, query.end_date,
                confirmation])
        return data


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
                f'<a href="{reverse_lazy("proposal:edit-type", kwargs={"pk": query.pk})}">Bearbeiten</a>',
                # f'<a href="{reverse_lazy("poll:edit", kwargs={"pk": query.pk})}">Bearbeiten</a>',
                query.title])
        return data
