# Generated by Django 5.0.2 on 2024-02-29 12:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rabbiq_api', '0004_alter_performanceappraisal_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='status',
            field=models.BooleanField(default=False),
        ),
    ]
