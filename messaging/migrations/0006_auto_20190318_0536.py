# Generated by Django 2.1.7 on 2019-03-18 05:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('messaging', '0005_auto_20190318_0534'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='textmessage',
            options={'ordering': ('-created_datetime',)},
        ),
    ]
