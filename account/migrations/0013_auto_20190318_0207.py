# Generated by Django 2.1.7 on 2019-03-18 02:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0012_group_discipline'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='group',
            name='discipline',
        ),
        migrations.AddField(
            model_name='group',
            name='type',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='Typ'),
        ),
    ]