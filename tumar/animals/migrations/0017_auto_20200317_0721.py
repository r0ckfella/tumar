# Generated by Django 2.1.15 on 2020-03-17 01:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("animals", "0016_calf_active"),
    ]

    operations = [
        migrations.AlterField(
            model_name="calf",
            name="wean_date",
            field=models.DateTimeField(null=True, verbose_name="Date of weaning"),
        ),
    ]
