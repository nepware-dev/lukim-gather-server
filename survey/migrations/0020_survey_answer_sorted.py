# Generated by Django 3.2.20 on 2023-10-09 08:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0019_happeningsurvey_audio_file'),
    ]

    operations = [
        migrations.AddField(
            model_name='survey',
            name='answer_sorted',
            field=models.JSONField(blank=True, default=dict, null=True, verbose_name='Sorted answer'),
        ),
    ]