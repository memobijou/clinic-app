from django.core.paginator import InvalidPage
from rest_framework.exceptions import NotFound
from rest_framework.pagination import PageNumberPagination

from rest_framework.response import Response
from rest_framework import mixins
from rest_framework import generics
from collections import OrderedDict
from django.utils import six
from abc import ABCMeta, abstractmethod


class DatatablesPagination(PageNumberPagination):
    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('data', data.get("results")),
            ("recordsTotal", data.get("records_total")),
            ("recordsFiltered", data.get("records_total")),

        ]))

    def paginate_queryset_datatables(self, queryset, page_number, page_size):
        """
        Paginate a queryset if required, either returning a
        page object, or `None` if pagination is not configured for this view.
        """

        paginator = self.django_paginator_class(queryset, page_size)

        if page_number in self.last_page_strings:
            page_number = paginator.num_pages

        try:
            page = paginator.page(page_number)
        except InvalidPage as exc:
            msg = self.invalid_page_message.format(
                page_number=page_number, message=six.text_type(exc)
            )
            raise NotFound(msg)

        if paginator.num_pages > 1 and self.template is not None:
            # The browsable API should display pagination controls.
            self.display_page_controls = True
        return list(page)


class DatatablesMixin(mixins.ListModelMixin, generics.GenericAPIView, metaclass=ABCMeta):
    @property
    @abstractmethod
    def queryset(self):
        pass

    @property
    @abstractmethod
    def serializer_class(self):
        pass

    pagination_class = DatatablesPagination

    def __init__(self):
        super().__init__()
        self.records_total = None
        self.page_number = None
        self.page_size = None

    def paginate_queryset(self, queryset):
        """
        Return a single page of results, or `None` if pagination is disabled.
        """
        if self.paginator is None:
            return None
        return self.paginator.paginate_queryset_datatables(queryset,  self.page_number, self.page_size)

    def list(self, request, *args, **kwargs):
        start = int(request.GET.get("start"))
        length = int(request.GET.get("length"))
        page_number = 1

        while start > 0:
            start -= length
            page_number += 1
            if start == 0:
                break

        self.page_number = page_number
        self.page_size = length

        print(f"Page: {page_number}")
        self.filter_queryset(self.queryset)
        self.get_filtered_queryset()
        queryset = self.get_ordered_queryset()
        page = self.paginate_queryset(queryset)
        print(f"haack: {page}")
        if page is not None:
            data = self.get_data(page)

            return self.get_paginated_response(data)
        # hier checken was passiert wenn der queryset leer ist !
        serializer = self.get_serializer(queryset, many=True)
        print(f"???: {serializer.data}")
        return Response(serializer.data)

    @abstractmethod
    def get_data(self, page):
        pass

    @abstractmethod
    def get_filtered_queryset(self):
        pass

    @abstractmethod
    def get_ordered_queryset(self):
        pass

    def get(self, request, *args, **kwargs):
        response = self.list(request, *args, **kwargs)
        print(response)
        return response
