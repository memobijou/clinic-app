# Generated by Django 2.1.7 on 2019-03-10 00:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accomplishment', '0005_auto_20190309_1829'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accomplishment',
            name='full_score',
            field=models.IntegerField(blank=True, null=True, verbose_name='Gesamtpunktezahl'),
        ),
        migrations.AlterField(
            model_name='accomplishment',
            name='groups',
            field=models.ManyToManyField(related_name='accomplishments', to='account.Group', verbose_name='Gruppen'),
        ),
        migrations.AlterField(
            model_name='accomplishment',
            name='name',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='Bezeichnung'),
        ),
    ]
