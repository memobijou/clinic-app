# Generated by Django 2.1.7 on 2019-03-09 18:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accomplishment', '0004_accomplishment_groups'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accomplishment',
            name='groups',
            field=models.ManyToManyField(related_name='accomplishments', to='account.Group'),
        ),
    ]
