# Generated by Django 2.1.4 on 2018-12-13 00:25

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('appointment', '0001_initial'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Appoinment',
            new_name='Appointment',
        ),
    ]
