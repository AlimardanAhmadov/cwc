# Generated by Django 4.0.5 on 2022-07-08 17:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subscription', '0004_customsubscriptionplan_created'),
    ]

    operations = [
        migrations.AddField(
            model_name='customsubscriptionplan',
            name='slug_field',
            field=models.SlugField(blank=True, unique=True),
        ),
    ]