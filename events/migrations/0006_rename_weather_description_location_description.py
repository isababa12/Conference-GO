# Generated by Django 4.0.3 on 2022-11-11 00:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0005_rename_temperature_location_temp'),
    ]

    operations = [
        migrations.RenameField(
            model_name='location',
            old_name='weather_description',
            new_name='description',
        ),
    ]
