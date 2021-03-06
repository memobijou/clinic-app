# Generated by Django 2.1.7 on 2020-02-22 21:22

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('poll', '0005_auto_20200222_2120'),
    ]

    operations = [
        migrations.AddField(
            model_name='option',
            name='user_options',
            field=models.ManyToManyField(through='poll.UserOption', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='useroption',
            name='option',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='poll.Option'),
        ),
    ]
