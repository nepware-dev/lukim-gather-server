# Generated by Django 3.2.13 on 2022-06-28 11:54

import ckeditor.fields
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('support', '0003_emailtemplate'),
    ]

    operations = [
        migrations.CreateModel(
            name='ResourceTag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('order', models.PositiveIntegerField(db_index=True, editable=False, verbose_name='order')),
                ('title', models.CharField(max_length=50, verbose_name='title')),
                ('created_by', models.ForeignKey(blank=True, default=None, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('updated_by', models.ForeignKey(blank=True, default=None, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('order',),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Resource',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('order', models.PositiveIntegerField(db_index=True, editable=False, verbose_name='order')),
                ('title', models.TextField(max_length=255, verbose_name='title')),
                ('title_en', models.TextField(max_length=255, null=True, verbose_name='title')),
                ('title_ho', models.TextField(max_length=255, null=True, verbose_name='title')),
                ('title_tpi', models.TextField(max_length=255, null=True, verbose_name='title')),
                ('description', ckeditor.fields.RichTextField(verbose_name='description')),
                ('description_en', ckeditor.fields.RichTextField(null=True, verbose_name='description')),
                ('description_ho', ckeditor.fields.RichTextField(null=True, verbose_name='description')),
                ('description_tpi', ckeditor.fields.RichTextField(null=True, verbose_name='description')),
                ('resource_type', models.CharField(choices=[('attachment', 'Attachment'), ('video', 'Video')], max_length=10, verbose_name='resource type')),
                ('video_url', models.URLField(blank=True, default=None, null=True, verbose_name='video url')),
                ('attachment', models.FileField(blank=True, default=None, null=True, upload_to='', verbose_name='attachment')),
                ('created_by', models.ForeignKey(blank=True, default=None, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('tags', models.ManyToManyField(related_name='resources', to='support.ResourceTag', verbose_name='resource tags')),
                ('updated_by', models.ForeignKey(blank=True, default=None, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('order',),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='FrequentlyAskedQuestion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('order', models.PositiveIntegerField(db_index=True, editable=False, verbose_name='order')),
                ('question', models.TextField(verbose_name='question')),
                ('question_en', models.TextField(null=True, verbose_name='question')),
                ('question_ho', models.TextField(null=True, verbose_name='question')),
                ('question_tpi', models.TextField(null=True, verbose_name='question')),
                ('answer', ckeditor.fields.RichTextField(verbose_name='answer')),
                ('answer_en', ckeditor.fields.RichTextField(null=True, verbose_name='answer')),
                ('answer_ho', ckeditor.fields.RichTextField(null=True, verbose_name='answer')),
                ('answer_tpi', ckeditor.fields.RichTextField(null=True, verbose_name='answer')),
                ('created_by', models.ForeignKey(blank=True, default=None, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('updated_by', models.ForeignKey(blank=True, default=None, editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('order',),
                'abstract': False,
            },
        ),
    ]
