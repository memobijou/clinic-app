# Generated by Django 2.1.7 on 2019-04-26 13:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('filestorage', '0011_auto_20190317_2104'),
    ]

    operations = [
        migrations.AddField(
            model_name='filedirectory',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='child_directories', to='filestorage.FileDirectory'),
        ),
    ]
