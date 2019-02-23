from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import  generic

from taskmanagement.forms import GroupTaskForm, UserTaskForm
from taskmanagement.models import Task, UserTask
# Create your views here.
from account.models import Group
from django.urls import reverse_lazy


class TaskListView(LoginRequiredMixin, generic.ListView):
    template_name = "taskmanagement/task_list.html"
    paginate_by = 15
    queryset = Task.objects.all()
    form = GroupTaskForm()

    def get_form(self):
        if self.request.method == "POST":
            self.form = GroupTaskForm(data=self.request.POST)
        return self.form

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = self.get_form()
        return context


class TaskCreateView(LoginRequiredMixin, generic.CreateView):
    success_url = reverse_lazy("taskmanagement:tasks_list")
    form_class = GroupTaskForm

    def form_valid(self, form):
        instance = form.save()
        new_groups = form.cleaned_data.get("groups")
        for new_group in new_groups:
            instance.groups_list.add(new_group)
        return super().form_valid(form)


class UserTaskCreateView(LoginRequiredMixin, generic.UpdateView):
    form_class = UserTaskForm
    template_name = "taskmanagement/task_detail.html"
    group = None
    object = None

    def get_object(self, queryset=None):
        self.group = Group.objects.get(pk=self.kwargs.get("group_pk"))
        self.object = Task.objects.get(pk=self.kwargs.get("task_pk"))
        return self.object

    def get_success_url(self):
        return reverse_lazy(
            "taskmanagement:edit_task", kwargs={"pk": self.kwargs.get("group_pk")}
        )

    def get_form(self, form_class=None):
        if self.request.method == "POST":
            form = self.form_class(instance=self.object, group=self.group, data=self.request.POST)
        else:
            form = self.form_class(instance=self.object, group=self.group)
        return form

    def form_valid(self, form):
        instance = self.object
        users = form.cleaned_data.get("users")
        assigned_users_tasks = UserTask.objects.filter(user__in=users, task=instance)
        unassigned_users_tasks = UserTask.objects.filter(~Q(user__in=users) & Q(task=instance))
        unassigned_users_tasks.delete()
        users = users.exclude(id__in=assigned_users_tasks.values_list("user_id", flat=True))

        if users.count() > 0:
            bulk_instances = [UserTask(user=user, task=instance) for user in users]
            UserTask.objects.bulk_create(bulk_instances)
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = {**context, **self.get_context()}
        return context

    def get_context(self):
        instance = self.group
        context = {"instance": instance, "tasks": self.get_tasks(instance)}
        return context

    def get_tasks(self, instance):
        tasks = instance.tasks.all()
        forms = []
        for task in tasks:
            if self.request.method == "POST" and task.pk == int(self.kwargs.get("task_pk")):
                print(f"{task.pk} - {self.kwargs.get('task_pk')}")
                form = UserTaskForm(instance=self.object, group=instance, data=self.request.POST)
            else:
                form = UserTaskForm(instance=task, group=instance)
            forms.append(form)
        return list(zip(tasks, forms))



class GroupTaskDetailView(LoginRequiredMixin, generic.UpdateView):
    template_name = "taskmanagement/task_detail.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context())

    def get_context(self):
        instance = Group.objects.get(pk=self.kwargs.get("pk"))
        context = {"instance": instance, "tasks": self.get_tasks(instance)}
        return context

    def get_tasks(self, instance):
        tasks = instance.tasks.all()
        forms = [UserTaskForm(instance=task, group=instance) for task in tasks]
        return list(zip(tasks, forms))