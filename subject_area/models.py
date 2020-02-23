from django.db import models
from django.urls import reverse_lazy
# Create your models here.
from accomplishment.models import UserAccomplishment


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
        print(f"yes: : : {score_sum} - {full_score_sum}")
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
        for user_accomplishement in UserAccomplishment.objects.all().distinct():
            full_score_sum += user_accomplishement.score
        for user_accomplishement in UserAccomplishment.objects.filter(
                user_id=user_id, accomplishment__categories=self).distinct():
            score = user_accomplishement.score
            score_sum += score
        if full_score_sum > 0 and score_sum > 0:
            return int(score_sum/full_score_sum*100)
        else:
            return 0
