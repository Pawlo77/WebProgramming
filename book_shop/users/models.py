from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser, Group
from django.db import models
from django.utils.translation import gettext_lazy as _


class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """

    def create_user(
        self, username, email, password, first_name, last_name, **extra_fields
    ):
        """
        Create and save a user with the given email and password.
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
            **extra_fields
        )
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, **extra_fields):
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_staff", True)

        return self.create_admin(first_name="Admin", last_name="Admin", **extra_fields)

    def create_admin(self, username, email, password, **extra_fields):
        """
        Create and save an admin user with the given email and password.
        """
        extra_fields.setdefault("role", CustomUser.ADMIN)
        extra_fields.setdefault("is_superuser", False)
        extra_fields.setdefault("is_staff", True)

        # Ensure the role is set correctly for an admin user
        if extra_fields.get("role") != CustomUser.ADMIN:
            raise ValueError(_("Admin must have role=CustomUser.ADMIN."))

        user = self.create_user(
            username=username, email=email, password=password, **extra_fields
        )

        staff_group = Group.objects.get(name="Staff")
        user.groups.add(staff_group)
        admin_gruop = Group.objects.get(name="Admin")
        user.groups.add(admin_gruop)

        return user

    def create_manager(self, username, email, password, **extra_fields):
        """
        Create and save a manager with the given email and password.
        """
        extra_fields.setdefault("role", CustomUser.MANAGER)
        extra_fields.setdefault("is_superuser", False)
        extra_fields.setdefault("is_staff", True)

        if extra_fields.get("role") != CustomUser.MANAGER:
            raise ValueError(_("Admin must have role=CustomUser.MANAGER."))
        user = self.create_user(
            username=username, email=email, password=password, **extra_fields
        )
        staff_group = Group.objects.get(name="Staff")
        user.groups.add(staff_group)

        return user


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
        max_length=10, choices=ROLE_CHOICES, default=USER, null=False, blank=True
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
    date_joined = models.DateTimeField(auto_now_add=True, null=False, blank=True)

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
