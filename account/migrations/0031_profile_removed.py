# Generated by Django 2.1.7 on 2019-05-17 05:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0030_auto_20190513_2310'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='removed',
            field=models.BooleanField(default=False),
        ),
    ]
