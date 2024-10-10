# Generated by Django 5.1.1 on 2024-10-07 21:07

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('people', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='author',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='author_created_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='author',
            name='updated_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='author_updated_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='critic',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='critic_created_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='critic',
            name='updated_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='critic_updated_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddIndex(
            model_name='author',
            index=models.Index(fields=['first_publication_date'], name='people_auth_first_p_f95cca_idx'),
        ),
        migrations.AddIndex(
            model_name='author',
            index=models.Index(fields=['last_publication_date'], name='people_auth_last_pu_edb3c6_idx'),
        ),
    ]
