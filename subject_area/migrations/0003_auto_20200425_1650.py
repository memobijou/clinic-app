# Generated by Django 2.1.7 on 2020-04-25 16:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('subject_area', '0002_category'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='category',
            options={'ordering': ('id',)},
        ),
    ]
