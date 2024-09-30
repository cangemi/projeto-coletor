# Generated by Django 5.1.1 on 2024-09-09 17:51

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Device',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mac_address', models.CharField(max_length=17, unique=True)),
                ('name', models.CharField(blank=True, max_length=100)),
                ('description', models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='PhotoData',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('data', models.DateTimeField(auto_now_add=True)),
                ('temperature', models.FloatField()),
                ('pressure', models.FloatField()),
                ('altitude', models.FloatField()),
                ('image_link', models.URLField()),
                ('device', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='photo_data', to='device.device')),
            ],
        ),
    ]
