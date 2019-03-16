from django.contrib import admin
from messaging.models import TextMessage


class TextMessageAdmin(admin.ModelAdmin):
    pass


admin.site.register(TextMessage, TextMessageAdmin)
