from django.contrib.auth.models import Group, Permission
from django.db.models.signals import post_migrate
from django.dispatch import receiver


@receiver(post_migrate)
def create_staff_group(sender, **kwargs):
    group_name = "Staff"
    group, created = Group.objects.get_or_create(name=group_name)

    if created:
        permissions = Permission.objects.filter(
            content_type__app_label="items",
            codename__in=[
                "view_award",
                "add_award",
                "change_award",
                "delete_award",
                "view_book",
                "add_book",
                "change_book",
                "delete_book",
            ],
        )
        group.permissions.add(*permissions)

        permissions = Permission.objects.filter(
            content_type__app_label="people",
            codename__in=[
                "view_author",
                "add_author",
                "change_author",
                "delete_author",
                "view_critic",
                "add_critic",
                "change_critic",
                "delete_critic",
            ],
        )
        group.permissions.add(*permissions)

        permissions = Permission.objects.filter(
            content_type__app_label="reviews",
            codename__in=[
                "view_review",
                "add_review",
                "change_review",
                "delete_review",
                "view_reaction",
                "delete_reaction",
            ],
        )
        group.permissions.add(*permissions)

        print(f'Group "{group_name}" created successfully.')


@receiver(post_migrate)
def create_admin_group(sender, **kwargs):
    group_name = "Admin"
    group, created = Group.objects.get_or_create(name=group_name)

    if created:
        permissions = Permission.objects.filter(
            content_type__app_label="users",
            codename__in=[
                "add_customuser",
                "view_customuser",
            ],
        )
        group.permissions.add(*permissions)

        print(f'Group "{group_name}" created successfully.')
