# Generated by Django 5.1.1 on 2024-10-07 22:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("people", "0002_initial"),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name="author",
            name="people_auth_first_p_f95cca_idx",
        ),
        migrations.RemoveIndex(
            model_name="author",
            name="people_auth_last_pu_edb3c6_idx",
        ),
        migrations.RemoveField(
            model_name="author",
            name="first_publication_date",
        ),
        migrations.RemoveField(
            model_name="author",
            name="last_publication_date",
        ),
    ]
