from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum, Q
from django.shortcuts import render
from django.views import generic
# Create your views here.
from accomplishment.forms import AccomplishmentFormMixin
from accomplishment.models import Accomplishment
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy


class AccomplishmentListView(LoginRequiredMixin, generic.CreateView):
    form_class = AccomplishmentFormMixin
    template_name = "accomplishment/accomplishment_list.html"
    success_url = reverse_lazy("accomplishment:list")


class AccomplishmentUpdateView(LoginRequiredMixin, generic.UpdateView):
    form_class = AccomplishmentFormMixin
    template_name = "accomplishment/edit/edit.html"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.groups = None
        self.users = None
        self.users_accomplishments = None
        self.groups_users = None
        self.non_groups_users = None
        self.non_groups_useraccomplishments = None
        self.groups_useraccomplishments = None
        self.users_scores = []
        self.non_groups_users_scores = []

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.users = self.object.users.all()
        self.groups = self.object.groups.all()
        groups_pks = self.groups.values_list("pk", flat=True)
        print(groups_pks)
        print(self.users)
        self.groups_users = self.users.filter(groups_list__pk__in=groups_pks).distinct()
        print(self.groups_users)
        self.non_groups_users = self.users.filter(~Q(groups_list__pk__in=groups_pks))
        self.users_accomplishments = self.object.user_accomplishments.all().distinct()
        self.non_groups_useraccomplishments = self.get_non_groups_useraccomplishments()
        self.groups_useraccomplishments = self.get_groups_useraccomplishments()
        context["current_score"] = self.get_current_score()
        context["users_scores"] = self.get_users_scores()
        context["non_groups_users_scores"] = self.get_non_groups_users_scores()
        return context

    def get_non_groups_useraccomplishments(self):
        self.non_groups_useraccomplishments = self.users_accomplishments.filter(user__in=self.non_groups_users)
        return self.non_groups_useraccomplishments

    def get_groups_useraccomplishments(self):
        self.groups_useraccomplishments = self.users_accomplishments.filter(user__in=self.groups_users)
        return self.groups_useraccomplishments

    def get_current_score(self):
        users_count = self.groups_users.count()
        full_score = users_count * self.object.full_score
        if full_score == 0:
            return 0
        scores = self.groups_useraccomplishments.aggregate(total_scores=Sum("score"))["total_scores"] or 0
        return int((scores/full_score)*100)

    def get_users_scores(self):
        for user_accomplishment in self.groups_useraccomplishments:
            current_score = int((user_accomplishment.score/self.object.full_score)*100)
            self.users_scores.append((user_accomplishment, current_score))
        return self.users_scores

    def get_non_groups_users_scores(self):
        for user_accomplishment in self.non_groups_useraccomplishments:
            current_score = int((user_accomplishment.score/self.object.full_score)*100)
            self.non_groups_users_scores.append((user_accomplishment, current_score))
        return self.non_groups_users_scores

    def get_object(self, queryset=None):
        return get_object_or_404(Accomplishment, pk=self.kwargs.get("pk"))

    def get_success_url(self):
        return reverse_lazy("accomplishment:edit", kwargs={"pk": self.object.pk})
