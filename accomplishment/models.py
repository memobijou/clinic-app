from django.contrib.auth.models import User
from django.db import models
from django.db.models import Sum, Case, When, F


class Accomplishment(models.Model):
    name = models.CharField(max_length=200, null=True, blank=False, verbose_name="Bezeichnung")
    full_score = models.IntegerField(null=True, blank=False, verbose_name="Gesamtpunktezahl")
    users = models.ManyToManyField(User, blank=True, through="accomplishment.UserAccomplishment",
                                   related_name="accomplishments", verbose_name="Benutzer")
    subject_areas = models.ManyToManyField("subject_area.SubjectArea", blank=True, related_name="accomplishments",
                                           verbose_name="Fachrichtungen")

    def get_current_score_percentage(self, subject_area_users):
        users_count = len(subject_area_users)
        full_score = users_count * self.full_score
        if full_score == 0:
            return 0
        scores = self.user_accomplishments.filter(user__in=subject_area_users).aggregate(
            total_scores=Sum(Case(When(completed=True, then=self.full_score),
                                  When(score__lte=self.full_score, then=F("score")),
                                  default=F("accomplishment__full_score"))))["total_scores"] or 0
        print(f"hey: {scores} - {full_score}")
        return int((scores/full_score)*100)

    def get_subject_area_users_scores(self, subject_area_users, user_accomplishments):
        user_accomplishments = user_accomplishments.select_related("accomplishment").filter(
            user__in=subject_area_users)
        user_scores = []
        for user_accomplishment in user_accomplishments:
            if user_accomplishment.completed is True:
                current_score = 100
            else:
                current_score = int((user_accomplishment.score/self.full_score)*100)
            user_scores.append((user_accomplishment, current_score))
        return user_scores

    def get_non_subject_area_users_scores(self, subject_area_users, user_accomplishments):
        user_accomplishments = user_accomplishments.exclude(user__in=subject_area_users)
        user_scores = []
        for user_accomplishment in user_accomplishments:
            current_score = int((user_accomplishment.score/self.full_score)*100)
            user_scores.append((user_accomplishment, current_score))
        return user_scores


class UserAccomplishment(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL,
                             related_name="user_accomplishments")
    accomplishment = models.ForeignKey(Accomplishment, null=True, blank=True, on_delete=models.SET_NULL,
                                       related_name="user_accomplishments")
    score = models.IntegerField(null=True, blank=True)
    completed = models.NullBooleanField(blank=True, null=True, verbose_name="Abgeschloßen")

    def get_score_of(self):
        if self.completed is True:
            return f"{self.score}/{self.score}"
        else:
            return f"{self.score}/{self.accomplishment.full_score}"
