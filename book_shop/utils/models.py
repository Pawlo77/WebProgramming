from django.db import models


class Item(models.Model):
    # Auto-generated fields
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    # View count
    view_count = models.PositiveIntegerField(
        default=0,
        blank=True,
        null=False,
        help_text="Number of times the item has been viewed on the website.",
    )

    class Meta:
        abstract = True

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
        request = kwargs.pop("request", None)
        if request and hasattr(request, "user"):
            if not self.pk:
                self.created_by = request.user
            self.updated_by = request.user
        super().save(*args, **kwargs)

    def update_views(self):
        """Method to increment the view count."""
        self.view_count += 1
        self.save()

    def __str__(self):
        return f"Item created at {self.date_created}."

    @staticmethod
    def get_user(kwargs):
        request = kwargs.pop("request", None)
        if request and hasattr(request, "user"):
            return request.user
        return None
