# Generated by Django 2.1.7 on 2020-03-19 18:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('messaging', '0020_chatpushhistory'),
    ]

    operations = [
        migrations.AddField(
            model_name='chatpushhistory',
            name='unread_notifications',
            field=models.IntegerField(blank=True, default=0),
        ),
    ]
