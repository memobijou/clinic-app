from django.contrib import admin
# Register your models here.
from taskmanagement.models import Task, UserTask
from account.models import Group


class UsersInline(admin.TabularInline):
    model = UserTask
    can_delete = True
    verbose_name_plural = "Benutzer"


class GroupsInline(admin.TabularInline):
    model = Group.tasks.through
    can_delete = True
    verbose_name_plural = "Gruppen"


class TaskAdmin(admin.ModelAdmin):
    inlines = (UsersInline, GroupsInline, )


admin.site.register(Task, TaskAdmin)
