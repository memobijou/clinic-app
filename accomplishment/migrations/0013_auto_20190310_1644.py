# Generated by Django 2.1.7 on 2019-03-10 16:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accomplishment', '0012_auto_20190310_1635'),
    ]

    operations = [
        migrations.AlterField(
            model_name='useraccomplishment',
            name='accomplishment',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='useraccomplishments', to='accomplishment.Accomplishment'),
        ),
    ]
