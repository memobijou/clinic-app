# Generated by Django 2.1.7 on 2020-05-03 02:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('proposal', '0004_auto_20200224_0401'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='proposal',
            options={'ordering': ('-pk',)},
        ),
    ]
