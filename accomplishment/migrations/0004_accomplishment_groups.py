# Generated by Django 2.1.7 on 2019-03-09 18:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0006_profile_device_token'),
        ('accomplishment', '0003_useraccomplishment'),
    ]

    operations = [
        migrations.AddField(
            model_name='accomplishment',
            name='groups',
            field=models.ManyToManyField(to='account.Group'),
        ),
    ]