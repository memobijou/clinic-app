from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.views import generic

from taskmanagement.forms import CreateTaskForm, EditTaskForm
from taskmanagement.models import Task, UserTask
# Create your views here.
from account.models import Group
from django.urls import reverse_lazy


class TaskListView(LoginRequiredMixin, generic.ListView):
    template_name = "taskmanagement/task_list.html"
    paginate_by = 15
    queryset = Task.objects.all()
    form = CreateTaskForm()

    def get_form(self):
        if self.request.method == "POST":
            self.form = CreateTaskForm(data=self.request.POST)
        return self.form

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = self.get_form()
        return context


class TaskCreateView(LoginRequiredMixin, generic.CreateView):
    success_url = reverse_lazy("taskmanagement:tasks_list")
    form_class = CreateTaskForm
    template_name = "taskmanagement/task_list.html"

    def form_valid(self, form):
        users = form.cleaned_data.pop("users")
        new_groups = form.cleaned_data.get("groups")
        instance = form.save()

        for new_group in new_groups:
            instance.groups_list.add(new_group)
        print(new_groups)
        group_users = User.objects.filter(Q(groups_list__in=new_groups) | Q(id__in=users)).distinct()
        UserTask.objects.bulk_create([UserTask(user=user, task=instance) for user in group_users])
        return super().form_valid(form)


class TaskUpdateView(LoginRequiredMixin, generic.UpdateView):
    template_name = "taskmanagement/task_detail.html"
    form_class = EditTaskForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context = {**context, **self.get_context()}
        return context

    def get_context(self):
        context = {"user_tasks": self.get_object().usertasks.all()}
        return context

    def get_object(self, queryset=None):
        return get_object_or_404(Task, pk=self.kwargs.get("pk"))

    def get_success_url(self):
        return reverse_lazy("taskmanagement:edit_task", kwargs={"pk": self.get_object().pk})
