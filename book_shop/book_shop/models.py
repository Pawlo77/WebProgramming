from django.db import models


class Item(models.Model):
    # Auto-generated fields
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    @property
    def created_ago(self):
        """
        Calculates the age of the item from the date it was created.
        Returns the age in days.
        """
        now = timezone.now()
        age_timedelta = now - self.date_created
        return age_timedelta.days

    def save(self, *args, **kwargs):
        user = Item.get_user(kwargs)
        if user is None or not user.is_authenticated:
            raise PermissionDenied("You must be logged in to save this item.")

        if not self.pk:  # If creating a new instance
            self.created_by = request.user
        self.updated_by = request.user

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Item created at {self.date_created}."

    @staticmethod
    def get_user(kwargs):
        request = kwargs.pop("request", None)
        if request and hasattr(request, "user"):
            return request.user
        return None
