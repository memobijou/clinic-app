# Generated by Django 2.1.7 on 2020-02-22 18:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('poll', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Option',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('selected', models.BooleanField(default=False)),
            ],
        ),
        migrations.AlterField(
            model_name='poll',
            name='description',
            field=models.TextField(blank=True, null=True, verbose_name='Beschreibung'),
        ),
        migrations.AlterField(
            model_name='poll',
            name='open',
            field=models.BooleanField(default=False, verbose_name='Veröffentlichen'),
        ),
        migrations.AlterField(
            model_name='poll',
            name='title',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='Bezeichnung'),
        ),
    ]
