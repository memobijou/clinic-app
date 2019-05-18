from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.views import generic
from taskmanagement.forms import CreateTaskForm, EditTaskForm
from taskmanagement.models import Task
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.views import View


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


class TaskDeleteView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        items = request.POST.getlist("item")
        print(f"abc abc: {items}")
        Task.objects.filter(pk__in=items).delete()
        return HttpResponseRedirect(reverse_lazy("taskmanagement:tasks_list"))
