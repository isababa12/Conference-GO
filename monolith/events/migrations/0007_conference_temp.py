# Generated by Django 4.0.3 on 2022-11-11 01:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0006_rename_weather_description_location_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='conference',
            name='temp',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='temperature', to='events.location'),
        ),
    ]
