# from django.contrib.auth import get_user_model
from datetime import date

from django.test import TestCase

from .models import CustomUser


class UsersManagersTests(TestCase):

    def test_create_user(self):
        user = CustomUser.objects.create_user(
            username="user",
            password="testpass123",
            role=CustomUser.USER,
            email="user@example.com",
            first_name="John",
            last_name="Cena",
        )
        self.assertEqual(user.email, "user@example.com")
        self.assertEqual(user.role, CustomUser.USER)
        self.assertEqual(user.first_name, "John")
        self.assertEqual(user.last_name, "Cena")
        self.assertEqual(user.date_joined.date(), date.today())

        with self.assertRaises(TypeError):
            CustomUser.objects.create_user()
        with self.assertRaises(TypeError):
            CustomUser.objects.create_user(email="")
        with self.assertRaises(TypeError):
            CustomUser.objects.create_user(email="", password="")
        with self.assertRaises(TypeError):
            CustomUser.objects.create_user(username="", email="", password="foo")
        with self.assertRaises(TypeError):
            CustomUser.objects.create_user(
                username="", email="", password="foo", first_name=""
            )
        with self.assertRaises(ValueError):
            CustomUser.objects.create_user(
                username="", email="", password="foo", first_name="", last_name=""
            )

    def test_create_admin(self):
        admin_user = CustomUser.objects.create_admin(
            username="admin",
            email="super@user.com",
            password="foo",
            first_name="John",
            last_name="Cena",
        )
        self.assertEqual(admin_user.email, "super@user.com")
        self.assertEqual(admin_user.role, CustomUser.ADMIN)

        with self.assertRaises(ValueError):
            CustomUser.objects.create_admin(
                username="user",
                password="testpass123",
                role=CustomUser.USER,
                email="user@example.com",
                first_name="John",
                last_name="Cena",
            )

    def test_create_manager(self):
        admin_user = CustomUser.objects.create_manager(
            username="manager",
            email="super@user.com",
            password="foo",
            first_name="John",
            last_name="Cena",
        )
        self.assertEqual(admin_user.email, "super@user.com")
        self.assertEqual(admin_user.role, CustomUser.MANAGER)

        with self.assertRaises(ValueError):
            CustomUser.objects.create_manager(
                username="manager",
                password="testpass123",
                role=CustomUser.USER,
                email="user@example.com",
                first_name="John",
                last_name="Cena",
            )
