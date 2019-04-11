from django.urls import path

from subject_area.datatables import SubjectAreaDatatables

urlpatterns = [
    path(r'subject-areas-datatables/', SubjectAreaDatatables.as_view(), name="subject_area_datatables"),
]
