from django.contrib import admin

# Register your models here.
from appointment.models import Appointment
from appointment.models import DutyRoster


class AppointmentAdmin(admin.ModelAdmin):
    pass

class DustyRosterAdmin(admin.ModelAdmin):
    pass

admin.site.register(Appointment, AppointmentAdmin)
admin.site.register(DutyRoster, DustyRosterAdmin)

