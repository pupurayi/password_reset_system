# Generated by Django 5.2.1 on 2025-06-06 14:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reset_system', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='is_ict_admin',
            field=models.BooleanField(default=False),
        ),
    ]
