from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import  generic

from taskmanagement.forms import GroupTaskFormMixin, UserTaskFormMixin
from taskmanagement.models import Task, UserTask
# Create your views here.
from account.models import Group
from django.urls import reverse_lazy


class TaskListView(LoginRequiredMixin, generic.ListView):
    template_name = "taskmanagement/task_list.html"
    paginate_by = 15
    queryset = Task.objects.all()
    form = GroupTaskFormMixin()

    def get_form(self):
        if self.request.method == "POST":
            self.form = GroupTaskFormMixin(data=self.request.POST)
        return self.form

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = self.get_form()
        return context


class TaskCreateView(LoginRequiredMixin, generic.CreateView):
    success_url = reverse_lazy("taskmanagement:tasks_list")
    form_class = GroupTaskFormMixin

    def form_valid(self, form):
        instance = form.save()
        new_groups = form.cleaned_data.get("groups")
        for new_group in new_groups:
            instance.groups_list.add(new_group)
        print(new_groups)
        users = User.objects.filter(groups_list__in=new_groups).distinct()
        UserTask.objects.bulk_create([UserTask(user=user, task=instance) for user in users])
        return super().form_valid(form)


class UserTaskUpdateView(LoginRequiredMixin, generic.UpdateView):
    form_class = UserTaskFormMixin
    template_name = "taskmanagement/task_detail.html"
    group = None
    object = None

    def get_object(self, queryset=None):
        self.group = Group.objects.get(pk=self.kwargs.get("group_pk"))
        self.object = Task.objects.get(pk=self.kwargs.get("task_pk"))
        return self.object

    def get_success_url(self):
        return reverse_lazy(
            "taskmanagement:edit_task", kwargs={"pk": self.object.pk}
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
        assigned_users_tasks = UserTask.objects.filter(
            user__in=users, task=instance, user__groups_list__in=[self.group])
        unassigned_users_tasks = UserTask.objects.filter(
            ~Q(user__in=users) & Q(task=instance, user__groups_list__in=[self.group])
        )
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
                form = UserTaskFormMixin(instance=self.object, group=instance, data=self.request.POST)
            else:
                form = UserTaskFormMixin(instance=task, group=instance)
            forms.append(form)
        return list(zip(tasks, forms))


class TaskDetailView(LoginRequiredMixin, generic.UpdateView):
    template_name = "taskmanagement/task_detail.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context())

    def get_context(self):
        instance = Task.objects.get(pk=self.kwargs.get("pk"))
        context = {"instance": instance, "tasks": self.get_tasks(instance)}
        return context

    def get_tasks(self, instance):
        groups = instance.groups_list.all()
        forms = [UserTaskFormMixin(instance=instance, group=group, prefix=f"{group.pk}") for group in groups]
        user_tasks = [UserTask.objects.filter(user__in=group.users.all(), task=instance) for group in groups]
        print(user_tasks)
        return list(zip(groups, user_tasks, forms))
