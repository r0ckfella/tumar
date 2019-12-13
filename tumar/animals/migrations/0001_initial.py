# Generated by Django 2.1.15 on 2019-12-11 11:13

import django.contrib.gis.db.models.fields
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Animal',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('imei', models.CharField(blank=True, max_length=15, null=True, validators=[django.core.validators.RegexValidator(message="Imei must be entered in the format: '123456789012345'. Up to 15 digits allowed.", regex='^\\d{15}$')])),
                ('cow_code', models.CharField(blank=True, max_length=15, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Farm',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('key', models.CharField(max_length=32)),
                ('name', models.CharField(blank=True, max_length=50, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Geolocation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('position', django.contrib.gis.db.models.fields.PointField(srid=3857)),
                ('time', models.DateTimeField()),
                ('animal', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='geolocation', to='animals.Animal')),
            ],
        ),
        migrations.AddField(
            model_name='animal',
            name='farm',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='animals', to='animals.Farm'),
        ),
        migrations.AlterUniqueTogether(
            name='geolocation',
            unique_together={('animal', 'position', 'time')},
        ),
    ]