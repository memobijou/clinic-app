# Generated by Django 2.1.7 on 2019-03-11 22:04

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0008_auto_20190311_2202'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='mentor',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='mentors', to=settings.AUTH_USER_MODEL),
        ),
    ]
