# Generated by Django 2.1.7 on 2019-03-15 19:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('filestorage', '0007_filedirectory_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='file',
            name='version',
            field=models.DecimalField(decimal_places=3, default=1.0, max_digits=10, verbose_name='Version'),
        ),
    ]