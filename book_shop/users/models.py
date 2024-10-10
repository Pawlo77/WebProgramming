from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser, Group
from django.db import models
from django.utils.translation import gettext_lazy as _


class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifier
    for authentication instead of usernames.
    """

    def create_user(
        self,
        username,
        email,
        password=None,
        first_name=None,
        last_name=None,
        **extra_fields,
    ):
        """
        Create and save a regular user with the given email, username, and password.
        """
        extra_fields.setdefault("role", CustomUser.USER)
        extra_fields.setdefault("is_superuser", False)
        extra_fields.setdefault("is_staff", False)

        if not username:
            raise ValueError(_("The username must be set"))
        if not email:
            raise ValueError(_("The Email must be set"))
        if not first_name:
            raise ValueError(_("The first name must be set"))
        if not last_name:
            raise ValueError(_("The last name must be set"))

        email = self.normalize_email(email)
        user = self.model(
            email=email,
            username=username,
            first_name=first_name,
            last_name=last_name,
            **extra_fields,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password, **extra_fields):
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_staff", True)
        return self.create_admin(username, email, password, **extra_fields)

    def create_admin(self, username, email, password=None, **extra_fields):
        """
        Create and save an admin user with the given email and password.
        """
        extra_fields.setdefault("role", CustomUser.ADMIN)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_staff", True)

        user = self.create_user(username, email, password, **extra_fields)
        self._assign_groups(user, ["Admin", "Staff"])
        return user

    def create_manager(self, username, email, password=None, **extra_fields):
        """
        Create and save a manager user with the given email and password.
        """
        extra_fields.setdefault("role", CustomUser.MANAGER)
        extra_fields.setdefault("is_superuser", False)
        extra_fields.setdefault("is_staff", True)

        user = self.create_user(username, email, password, **extra_fields)
        self._assign_groups(user, ["Staff"])
        return user

    def _assign_groups(self, user, group_names):
        """
        Assign the user to the specified groups.
        """
        for group_name in group_names:
            try:
                group = Group.objects.get(name=group_name)
                user.groups.add(group)
            except Group.DoesNotExist:
                raise ValueError(_(f"Group '{group_name}' does not exist."))


class CustomUser(AbstractUser):
    USER = "user"
    MANAGER = "manager"
    ADMIN = "admin"

    ROLE_CHOICES = [
        (USER, "User"),
        (MANAGER, "Manager"),
        (ADMIN, "Admin"),
    ]
    role = models.CharField(
        max_length=10, choices=ROLE_CHOICES, default=USER, null=False, blank=False
    )

    UNEDUCATED = "uneducated"
    PRIMARY = "primary"
    MIDDLE = "middle"
    HIGH = "high"
    EDUCATION_CHOICES = [
        (UNEDUCATED, "Uneducated"),
        (PRIMARY, "Primary"),
        (MIDDLE, "Middle"),
        (HIGH, "High"),
    ]
    education = models.CharField(
        max_length=10, choices=EDUCATION_CHOICES, null=True, blank=True
    )

    email = models.EmailField(_("email address"), unique=True, null=False, blank=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    first_name = models.CharField(max_length=30, blank=False, null=False)
    last_name = models.CharField(max_length=30, blank=False, null=False)
    date_of_birth = models.DateField(null=True, blank=True)
    date_updated = models.DateTimeField(auto_now=True)

    objects = CustomUserManager()

    def save(self, *args, **kwargs):
        if self.role == self.ADMIN:
            self.is_superuser = True
            self.is_staff = True
        elif self.role == self.MANAGER:
            self.is_superuser = False
            self.is_staff = True
        else:
            self.is_superuser = False
            self.is_staff = False
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username
