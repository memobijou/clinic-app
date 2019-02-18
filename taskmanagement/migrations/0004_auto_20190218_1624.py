# Generated by Django 2.1.7 on 2019-02-18 16:24

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('taskmanagement', '0003_auto_20190218_1622'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='UserTasks',
            new_name='UserTask',
        ),
        migrations.AddField(
            model_name='task',
            name='users',
            field=models.ManyToManyField(through='taskmanagement.UserTask', to=settings.AUTH_USER_MODEL),
        ),
    ]
