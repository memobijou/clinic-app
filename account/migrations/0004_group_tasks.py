# Generated by Django 2.1.7 on 2019-02-18 15:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('taskmanagement', '0001_initial'),
        ('account', '0003_auto_20190216_2332'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='tasks',
            field=models.ManyToManyField(blank=True, related_name='groups_list', to='taskmanagement.Task'),
        ),
    ]
