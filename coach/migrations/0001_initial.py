# Generated by Django 3.2.7 on 2022-07-27 12:09

import coach.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Coach',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('profile_picture', models.ImageField(blank=True, upload_to=coach.models.user_directory_path)),
                ('phone_number', phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, region=None)),
                ('about', models.TextField(blank=True, null=True)),
                ('available_days', models.CharField(blank=True, max_length=400, null=True)),
                ('category', models.CharField(blank=True, max_length=100, null=True)),
                ('timing', models.CharField(blank=True, max_length=200, null=True)),
                ('full_name', models.CharField(blank=True, max_length=250, null=True)),
                ('location', models.CharField(blank=True, max_length=250, null=True)),
                ('rating', models.DecimalField(blank=True, decimal_places=1, default=0.0, max_digits=5)),
                ('image_url', models.TextField(blank=True, null=True)),
                ('address', models.TextField(blank=True, null=True)),
                ('paid', models.BooleanField(default=False)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='coach', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Coach',
                'verbose_name_plural': 'Coaches',
            },
        ),
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('service_title', models.CharField(max_length=550)),
                ('service_description', models.TextField()),
                ('created', models.DateField(auto_now_add=True)),
                ('related_coach', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='coach.coach')),
            ],
            options={
                'ordering': ['created'],
            },
        ),
        migrations.AddIndex(
            model_name='service',
            index=models.Index(fields=['related_coach'], name='coach_servi_related_a80a6b_idx'),
        ),
        migrations.AddIndex(
            model_name='coach',
            index=models.Index(fields=['user', 'id', 'paid', 'category', 'full_name', 'location'], name='coach_coach_user_id_54f7ae_idx'),
        ),
    ]