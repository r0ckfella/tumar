# Generated by Django 2.1.15 on 2020-02-17 11:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("animals", "0011_animal_image"),
    ]

    operations = [
        migrations.AlterField(
            model_name="animal",
            name="image",
            field=models.ImageField(
                blank=True, max_length=150, null=True, upload_to="animalimages"
            ),
        ),
    ]
