# Generated by Django 2.1.15 on 2019-12-12 13:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_user_phone_num'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='user',
            options={'verbose_name': 'User', 'verbose_name_plural': 'Users'},
        ),
    ]
