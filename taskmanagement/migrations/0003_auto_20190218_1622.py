# Generated by Django 2.1.7 on 2019-02-18 16:22

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('taskmanagement', '0002_usertaks'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='UserTaks',
            new_name='UserTasks',
        ),
    ]