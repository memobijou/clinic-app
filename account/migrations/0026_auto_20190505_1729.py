# Generated by Django 2.1.7 on 2019-05-05 15:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0025_auto_20190505_1728'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='color',
            field=models.CharField(max_length=200, null=True, verbose_name='Farbe'),
        ),
    ]
