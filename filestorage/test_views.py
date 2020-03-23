from django.http import HttpResponse
from filestorage.models import File
from filestorage.serializers import send_file_messages_through_firebase


def test_pushes_view(request):
    send_file_messages_through_firebase(File.objects.first(), is_new=False)
    html = "<html><body>It is now %s.</body></html>"
    return HttpResponse(html)
