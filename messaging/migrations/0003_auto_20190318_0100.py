# Generated by Django 2.1.7 on 2019-03-18 01:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('messaging', '0002_textmessage_created_datetime'),
    ]

    operations = [
        migrations.AlterField(
            model_name='textmessage',
            name='created_datetime',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
    ]
