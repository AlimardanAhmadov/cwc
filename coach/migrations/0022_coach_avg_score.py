# Generated by Django 4.0.5 on 2022-07-15 10:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coach', '0021_coach_paid_coach_rating'),
    ]

    operations = [
        migrations.AddField(
            model_name='coach',
            name='avg_score',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
    ]