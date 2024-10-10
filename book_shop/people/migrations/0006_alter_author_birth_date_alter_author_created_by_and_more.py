# Generated by Django 5.1.1 on 2024-10-10 19:27

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("people", "0005_alter_author_photo_alter_critic_photo"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name="author",
            name="birth_date",
            field=models.DateField(help_text="Birth date of the person (required)."),
        ),
        migrations.AlterField(
            model_name="author",
            name="created_by",
            field=models.ForeignKey(
                blank=True,
                help_text="User who created this author entry.",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="author_created_by",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="author",
            name="description",
            field=models.TextField(
                blank=True,
                help_text="Brief biography or description of the person.",
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="author",
            name="first_name",
            field=models.CharField(
                help_text="First name of the person (required).", max_length=100
            ),
        ),
        migrations.AlterField(
            model_name="author",
            name="last_name",
            field=models.CharField(
                help_text="Last name of the person (required).", max_length=100
            ),
        ),
        migrations.AlterField(
            model_name="author",
            name="nationality",
            field=models.CharField(
                blank=True,
                help_text="Nationality or country of origin of the person.",
                max_length=100,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="author",
            name="photo",
            field=models.ImageField(
                blank=True,
                help_text="Photograph of the person.",
                null=True,
                upload_to="person_photos/",
            ),
        ),
        migrations.AlterField(
            model_name="author",
            name="updated_by",
            field=models.ForeignKey(
                blank=True,
                help_text="User who last updated this author entry.",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="author_updated_by",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="author",
            name="website",
            field=models.URLField(
                blank=True, help_text="Official website or portfolio link.", null=True
            ),
        ),
        migrations.AlterField(
            model_name="critic",
            name="birth_date",
            field=models.DateField(help_text="Birth date of the person (required)."),
        ),
        migrations.AlterField(
            model_name="critic",
            name="created_by",
            field=models.ForeignKey(
                blank=True,
                help_text="User who created this critic entry.",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="critic_created_by",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="critic",
            name="description",
            field=models.TextField(
                blank=True,
                help_text="Brief biography or description of the person.",
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="critic",
            name="expertise_area",
            field=models.CharField(
                help_text="Critic's area of expertise (e.g., literature, film).",
                max_length=255,
            ),
        ),
        migrations.AlterField(
            model_name="critic",
            name="first_name",
            field=models.CharField(
                help_text="First name of the person (required).", max_length=100
            ),
        ),
        migrations.AlterField(
            model_name="critic",
            name="last_name",
            field=models.CharField(
                help_text="Last name of the person (required).", max_length=100
            ),
        ),
        migrations.AlterField(
            model_name="critic",
            name="nationality",
            field=models.CharField(
                blank=True,
                help_text="Nationality or country of origin of the person.",
                max_length=100,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="critic",
            name="photo",
            field=models.ImageField(
                blank=True,
                help_text="Photograph of the person.",
                null=True,
                upload_to="person_photos/",
            ),
        ),
        migrations.AlterField(
            model_name="critic",
            name="updated_by",
            field=models.ForeignKey(
                blank=True,
                help_text="User who last updated this critic entry.",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="critic_updated_by",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="critic",
            name="website",
            field=models.URLField(
                blank=True, help_text="Official website or portfolio link.", null=True
            ),
        ),
    ]
