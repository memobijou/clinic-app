# Generated by Django 2.1.7 on 2020-03-05 14:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('messaging', '0011_group'),
    ]

    operations = [
        migrations.AddField(
            model_name='grouptextmessage',
            name='group_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='messaging.Group'),
        ),
    ]
