# Generated by Django 4.0.5 on 2022-07-09 08:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coach', '0020_remove_coach_rating'),
    ]

    operations = [
        migrations.AddField(
            model_name='coach',
            name='paid',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='coach',
            name='rating',
            field=models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=5),
        ),
    ]
