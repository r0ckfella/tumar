# Generated by Django 2.1.15 on 2020-03-19 13:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('animals', '0017_auto_20200317_0721'),
    ]

    operations = [
        migrations.AlterField(
            model_name='farm',
            name='api_key',
            field=models.CharField(blank=True, help_text='Переводит ваш логин в другой формат для быстрого использования (к примеру, kh001 в ff80808170c314600170c393dace234)', max_length=100, verbose_name='Chinese API key'),
        ),
    ]
