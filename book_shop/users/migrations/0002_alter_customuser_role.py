# Generated by Django 5.1.1 on 2024-10-08 07:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="customuser",
            name="role",
            field=models.CharField(
                blank=True,
                choices=[("user", "User"), ("manager", "Manager"), ("admin", "Admin")],
                default="user",
                max_length=10,
            ),
        ),
    ]
