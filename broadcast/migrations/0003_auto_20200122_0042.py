# Generated by Django 2.1.7 on 2020-01-22 00:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('broadcast', '0002_auto_20200121_0110'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='like',
            options={'ordering': ('-like_datetime',)},
        ),
    ]