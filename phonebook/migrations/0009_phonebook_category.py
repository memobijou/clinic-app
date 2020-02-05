# Generated by Django 2.1.7 on 2020-02-05 12:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('phonebook', '0008_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='phonebook',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='phonebook.Category'),
        ),
    ]