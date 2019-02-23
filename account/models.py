from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
# Create your models here.


def get_name(self):
    return f"{self.first_name or ''} {self.last_name or ''}"


User.add_to_class("__str__", get_name)


class Group(models.Model):
    name = models.CharField(null=True, blank=False, max_length=200)
    users = models.ManyToManyField(User, blank=True, related_name="groups_list")
    tasks = models.ManyToManyField("taskmanagement.Task", blank=True, related_name="groups_list")

    def __str__(self):
        return f"{self.name}"

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_admin = models.NullBooleanField(verbose_name="Administrations Status")

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    print(f"signal sent")
    print(created)
    print(hasattr(instance, "profile"))
    if created or hasattr(instance, "profile") is False:
        print(f"created!")
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
