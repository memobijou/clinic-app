# Generated by Django 2.1.7 on 2019-02-19 16:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('filestorage', '0005_auto_20181217_0059'),
    ]

    operations = [
        migrations.AlterField(
            model_name='file',
            name='parent_directory',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='files', to='filestorage.FileDirectory', verbose_name='Ordnerstruktur'),
        ),
    ]
