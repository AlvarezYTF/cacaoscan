"""
Tests for seed_colombia management command.
"""
from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.core.management import call_command
from catalogos.models import Departamento, Municipio
from io import StringIO


class SeedColombiaCommandTest(TestCase):
    """Tests for seed_colombia command."""

    def setUp(self):
        """Set up test fixtures."""
        self.stdout = StringIO()
        self.stderr = StringIO()

    def test_seed_colombia_creates_departments(self):
        """Test that seed command creates departments."""
        initial_count = Departamento.objects.count()
        
        call_command('seed_colombia', stdout=self.stdout)
        
        final_count = Departamento.objects.count()
        self.assertGreater(final_count, initial_count)

    def test_seed_colombia_creates_municipalities(self):
        """Test that seed command creates municipalities."""
        initial_count = Municipio.objects.count()
        
        call_command('seed_colombia', stdout=self.stdout)
        
        final_count = Municipio.objects.count()
        self.assertGreater(final_count, initial_count)

    def test_normalize_text(self):
        """Test text normalization function."""
        from catalogos.management.commands.seed_colombia import _normalize_text

        normal_text = "Test"
        self.assertEqual(_normalize_text(normal_text), "Test")

        non_string = 123
        self.assertEqual(_normalize_text(non_string), 123)

    def test_create_or_update_departamento(self):
        """Test creating or updating a department."""
        from catalogos.management.commands.seed_colombia import Command
        command = Command()

        dept, created = command._create_or_update_departamento('99', 'Test Department')
        self.assertIsNotNone(dept)
        self.assertIsInstance(created, bool)

    def test_create_or_update_municipio(self):
        """Test creating or updating a municipality."""
        from catalogos.management.commands.seed_colombia import Command
        command = Command()

        dept, _ = Departamento.objects.get_or_create(
            codigo='99',
            defaults={'nombre': 'Test Department'}
        )

        created = command._create_or_update_municipio(dept, '001', 'Test Municipality')
        self.assertIsInstance(created, bool)

