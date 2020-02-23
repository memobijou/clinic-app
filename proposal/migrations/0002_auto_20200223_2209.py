# Generated by Django 2.1.7 on 2020-02-23 22:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proposal', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Type',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=200, null=True, verbose_name='Bezeichnung')),
            ],
        ),
        migrations.AlterField(
            model_name='proposal',
            name='end_date',
            field=models.DateField(blank=True, null=True, verbose_name='Enddatum'),
        ),
        migrations.AlterField(
            model_name='proposal',
            name='start_date',
            field=models.DateField(blank=True, null=True, verbose_name='Startdatum'),
        ),
    ]
