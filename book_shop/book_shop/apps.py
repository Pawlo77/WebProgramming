from django.apps import AppConfig
from django.db.models.signals import post_migrate


class ProjectConfig(AppConfig):
    name = "book_shop"

    def ready(self):
        from .signals import create_admin_group, create_staff_group

        post_migrate.connect(create_staff_group, sender=self)
        post_migrate.connect(create_admin_group, sender=self)
