# Generated by Django 3.2.14 on 2022-08-30 10:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0016_happeningsurvey_protected_area'),
    ]

    operations = [
        migrations.AddField(
            model_name='form',
            name='question_mapping',
            field=models.JSONField(blank=True, default=dict, verbose_name='Question mapping'),
        ),
    ]