# Generated by Django 4.0.5 on 2022-07-21 07:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coach', '0027_remove_coach_coach_coach_user_id_21652d_idx_and_more'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='service',
            index=models.Index(fields=['related_coach'], name='coach_servi_related_a80a6b_idx'),
        ),
    ]