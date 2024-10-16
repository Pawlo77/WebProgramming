# Generated by Django 5.1.1 on 2024-10-10 08:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("people", "0003_remove_author_people_auth_first_p_f95cca_idx_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="author",
            name="view_count",
            field=models.PositiveIntegerField(
                blank=True,
                default=0,
                help_text="Number of times the item has been viewed on the website.",
            ),
        ),
        migrations.AlterField(
            model_name="critic",
            name="view_count",
            field=models.PositiveIntegerField(
                blank=True,
                default=0,
                help_text="Number of times the item has been viewed on the website.",
            ),
        ),
    ]
