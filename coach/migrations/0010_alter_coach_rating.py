# Generated by Django 4.0.5 on 2022-06-26 07:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coach', '0009_alter_coach_rating'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coach',
            name='rating',
            field=models.DecimalField(decimal_places=2, max_digits=5),
        ),
    ]