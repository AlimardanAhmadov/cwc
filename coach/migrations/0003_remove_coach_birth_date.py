# Generated by Django 4.0.5 on 2022-06-23 12:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('coach', '0002_coach_available_days'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='coach',
            name='birth_date',
        ),
    ]
