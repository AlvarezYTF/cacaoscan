"""
Tests for create_admin_user management command.
"""
from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.core.management import call_command
from django.core.management.base import CommandError
from django.contrib.auth.models import User
from io import StringIO


class CreateAdminUserCommandTest(TestCase):
    """Tests for create_admin_user command."""

    def setUp(self):
        """Set up test fixtures."""
        self.stdout = StringIO()
        self.stderr = StringIO()

    def test_create_admin_user_new(self):
        """Test creating a new admin user."""
        call_command(
            'create_admin_user',
            '--username', 'testadmin',
            '--email', 'testadmin@test.com',
            '--password', 'testpass123',
            '--first-name', 'Test',
            '--last-name', 'Admin',
            '--no-input',
            stdout=self.stdout
        )

        user = User.objects.get(username='testadmin')
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_active)
        self.assertEqual(user.email, 'testadmin@test.com')

    def test_create_admin_user_update_existing(self):
        """Test updating an existing user to admin."""
        User.objects.create_user(
            username='existinguser',
            email='existing@test.com',
            password='oldpass',
            is_superuser=False,
            is_staff=False
        )

        call_command(
            'create_admin_user',
            '--username', 'existinguser',
            '--email', 'updated@test.com',
            '--password', 'newpass123',
            '--first-name', 'Updated',
            '--last-name', 'User',
            '--no-input',
            stdout=self.stdout
        )

        user = User.objects.get(username='existinguser')
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
        self.assertEqual(user.email, 'updated@test.com')

    def test_create_admin_user_email_conflict(self):
        """Test creating admin user with existing email."""
        User.objects.create_user(
            username='existing',
            email='conflict@test.com',
            password='pass123'
        )

        with self.assertRaises(CommandError):
            call_command(
                'create_admin_user',
                '--username', 'newuser',
                '--email', 'conflict@test.com',
                '--password', 'pass123',
                '--no-input',
                stdout=self.stdout,
                stderr=self.stderr
            )

    def test_create_admin_user_default_values(self):
        """Test creating admin user with default values."""
        call_command('create_admin_user', '--no-input', stdout=self.stdout)

        user = User.objects.get(username='admin')
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
        self.assertEqual(user.email, 'admin@cacaoscan.com')

