# Generated by Django 2.1.7 on 2019-05-19 22:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('taskmanagement', '0017_auto_20190518_1254'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='task',
            options={'ordering': ('-pk',)},
        ),
    ]