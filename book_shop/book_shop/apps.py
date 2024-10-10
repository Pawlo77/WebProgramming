from django.apps import AppConfig


class ProjectConfig(AppConfig):
    name = "book_shop"

    def ready(self):
        import book_shop.signals
