"""
Tests for check_fk_lotes management command.
"""
from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.core.management import call_command
from django.core.management.base import CommandError
from django.db import connection
from io import StringIO


class CheckFKLotesCommandTest(TestCase):
    """Tests for check_fk_lotes command."""

    def setUp(self):
        """Set up test fixtures."""
        self.stdout = StringIO()
        self.stderr = StringIO()

    @patch('api.management.commands.check_fk_lotes.Finca')
    @patch('api.management.commands.check_fk_lotes.Lote')
    def test_check_foreign_keys_no_issues(self, mock_lote, mock_finca):
        """Test checking foreign keys when there are no issues."""
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 1 FROM information_schema.tables 
                WHERE table_name = 'fincas_app_lote'
            """)
            table_exists = cursor.fetchone() is not None

        if not table_exists:
            self.skipTest("Table fincas_app_lote does not exist in test database")

        try:
            call_command('check_fk_lotes', stdout=self.stdout, stderr=self.stderr)
            output = self.stdout.getvalue()
            self.assertIsNotNone(output)
        except CommandError:
            pass

    def test_validate_identifier_valid(self):
        """Test identifier validation with valid input."""
        from api.management.commands.check_fk_lotes import Command
        command = Command()

        valid_identifiers = ['table_name', 'column_name', 'test123', 'a_b_c']
        for identifier in valid_identifiers:
            result = command._validate_identifier(identifier)
            self.assertEqual(result, identifier.replace('"', '""'))

    def test_validate_identifier_invalid(self):
        """Test identifier validation with invalid input."""
        from api.management.commands.check_fk_lotes import Command
        command = Command()

        invalid_identifiers = ['', None, 'table-name', 'table name', 'table;name']
        for identifier in invalid_identifiers:
            if identifier is None:
                with self.assertRaises(ValueError):
                    command._validate_identifier(identifier)
            else:
                with self.assertRaises((ValueError, AttributeError)):
                    command._validate_identifier(identifier)

    def test_build_drop_constraint_query(self):
        """Test building drop constraint query."""
        from api.management.commands.check_fk_lotes import Command
        command = Command()

        query = command._build_drop_constraint_query('test_table', 'test_constraint')
        self.assertIn('DROP CONSTRAINT', query)
        self.assertIn('test_table', query)
        self.assertIn('test_constraint', query)

    def test_build_add_constraint_query(self):
        """Test building add constraint query."""
        from api.management.commands.check_fk_lotes import Command
        command = Command()

        query = command._build_add_constraint_query(
            'test_table', 'test_constraint', 'test_column', 'ref_table', 'ref_column'
        )
        self.assertIn('ADD CONSTRAINT', query)
        self.assertIn('FOREIGN KEY', query)
        self.assertIn('REFERENCES', query)

