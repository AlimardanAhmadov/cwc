# Generated by Django 4.0.5 on 2022-07-08 11:36

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('coach', '0015_alter_service_service_title'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='service',
            options={'ordering': ['created']},
        ),
        migrations.AddField(
            model_name='service',
            name='created',
            field=models.DateField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]