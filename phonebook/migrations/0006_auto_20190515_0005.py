# Generated by Django 2.1.7 on 2019-05-15 00:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('phonebook', '0005_auto_20190506_0002'),
    ]

    operations = [
        migrations.AlterField(
            model_name='phonebook',
            name='title',
            field=models.CharField(blank=True, help_text='*Um die Leistungen für die Nutzer auszublenden tragen Sie "SPERRE" für die Bezeichnung ein', max_length=200, null=True, verbose_name='Bezeichnung'),
        ),
    ]
