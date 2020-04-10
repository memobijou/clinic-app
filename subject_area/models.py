from django.db import models
from django.db.models import Sum
from django.urls import reverse_lazy
# Create your models here.
from accomplishment.models import UserAccomplishment, Accomplishment
from django.contrib.auth.models import User


class SubjectArea(models.Model):
    title = models.CharField(max_length=200, verbose_name="Bezeichnung")

    @staticmethod
    def get_absolute_url():
        return reverse_lazy("subject_area:list")

    def __str__(self):
        return self.title

    def get_user_accomplishment_score(self, user_id):
        score_sum = 0
        full_score_sum = 0
        for category in self.category_set.all():
            print(f"bomba: {category} - {category.accomplishments.all()}")
            for accomplishment in category.accomplishments.all():
                full_score_sum += accomplishment.full_score
                for user_accomplishment in accomplishment.user_accomplishments.filter(user_id=user_id):
                    score_sum += user_accomplishment.score

        if score_sum is None or full_score_sum is None:
            return 0

        if score_sum > 0 and full_score_sum > 0:
            return f"{score_sum}/{full_score_sum}"
        else:
            return "0/0"

    def get_user_accomplishment_percentage(self, user_id):
        score_sum = 0
        full_score_sum = 0
        for category in self.category_set.all():
            print(f"bomba: {category} - {category.accomplishments.all()}")
            for accomplishment in category.accomplishments.all():
                full_score_sum += accomplishment.full_score
                for user_accomplishment in accomplishment.user_accomplishments.filter(user_id=user_id):
                    score_sum += user_accomplishment.score
        print(f"yes: : : {score_sum} - {full_score_sum}")

        if score_sum is None or full_score_sum is None:
            return 0

        if score_sum > 0 and full_score_sum > 0:
            return int((score_sum/full_score_sum)*100)
        else:
            return 0


class Category(models.Model):
    title = models.CharField(max_length=200, verbose_name="Bezeichnung")
    subject_area = models.ForeignKey("subject_area.SubjectArea", null=True, on_delete=models.SET_NULL)

    def __str__(self):
        if self.subject_area.title:
            return f"{self.subject_area.title} - {self.title}"

    def get_user_accomplishment_percentage(self, user_id):
        score_sum = 0
        full_score_sum = 0
        for accomplishment in self.accomplishments.all():
            full_score_sum += accomplishment.full_score
            print(accomplishment.name)
        print(full_score_sum)
        for user_accomplishement in UserAccomplishment.objects.filter(
                user_id=user_id, accomplishment__categories=self).distinct():
            score = user_accomplishement.score
            score_sum += score

        if full_score_sum is None or score_sum is None:
            return 0

        if full_score_sum > 0 and score_sum > 0:
            return int(score_sum/full_score_sum*100)
        else:
            return 0

    def get_user_accomplishment_percentage_related_to_finished(self, user_id):
        score_sum = 0
        full_score_sum = 0

        subject_area_id = User.objects.get(pk=user_id).profile.subject_area_id

        for user_accomplishment in UserAccomplishment.objects.filter(
                user_id=user_id, accomplishment__categories__subject_area_id=subject_area_id).distinct():
            full_score_sum += user_accomplishment.score
        print(full_score_sum)

        for user_accomplishement in UserAccomplishment.objects.filter(
                user_id=user_id, accomplishment__categories=self).distinct():
            score = user_accomplishement.score
            score_sum += score

        if full_score_sum is None or score_sum is None:
            return 0

        if full_score_sum > 0 and score_sum > 0:
            return int(score_sum/full_score_sum*100)
        else:
            return 0

    def get_user_accomplishment_percentage_for_category(self, user_id):
        user_score_sum = 0
        full_score_sum = Accomplishment.objects.filter(categories=self).distinct().aggregate(
            total=Sum("full_score")).get("total", 0)

        for user_accomplishement in UserAccomplishment.objects.filter(
                user_id=user_id, accomplishment__categories=self).distinct():
            score = user_accomplishement.score
            user_score_sum += score

        if full_score_sum is None or user_score_sum is None:
            return 0

        if full_score_sum > 0 and user_score_sum > 0:
            return int((user_score_sum/full_score_sum)*100)
        else:
            return 0
