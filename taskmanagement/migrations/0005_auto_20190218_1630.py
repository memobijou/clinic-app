# Generated by Django 2.1.7 on 2019-02-18 16:30

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('taskmanagement', '0004_auto_20190218_1624'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='users',
            field=models.ManyToManyField(blank=True, through='taskmanagement.UserTask', to=settings.AUTH_USER_MODEL),
        ),
    ]
