# Generated by Django 5.1.1 on 2024-11-04 05:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='libro',
            name='disponible',
            field=models.BooleanField(default=True),
        ),
    ]
