"""
Tests for normalize_migrations_encoding script.
"""
import pytest
import tempfile
import os
from pathlib import Path

from normalize_migrations_encoding import normalize_file_encoding, main


def test_normalize_file_encoding_utf8_file():
    """Test normalizing a UTF-8 file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
        f.write('# Test file\nprint("Hello")\n')
        file_path = Path(f.name)
    
    try:
        success, message = normalize_file_encoding(file_path)
        
        assert success is True
        assert 'UTF-8' in message
    finally:
        os.unlink(file_path)


def test_normalize_file_encoding_with_bom():
    """Test normalizing a file with BOM."""
    with tempfile.NamedTemporaryFile(mode='wb', suffix='.py', delete=False) as f:
        # Write UTF-8 with BOM
        f.write(b'\xef\xbb\xbf# Test file\nprint("Hello")\n')
        file_path = Path(f.name)
    
    try:
        success, message = normalize_file_encoding(file_path)
        
        assert success is True
        # BOM should be removed
        with open(file_path, 'rb') as f:
            content = f.read()
            assert not content.startswith(b'\xef\xbb\xbf')
    finally:
        os.unlink(file_path)


def test_normalize_file_encoding_with_problematic_byte():
    """Test normalizing a file with problematic byte."""
    with tempfile.NamedTemporaryFile(mode='wb', suffix='.py', delete=False) as f:
        f.write(b'# Test file\nprint("Hello")\xf3\n')
        file_path = Path(f.name)
    
    try:
        success, message = normalize_file_encoding(file_path)
        
        assert success is True
        # Problematic byte should be removed
        with open(file_path, 'rb') as f:
            content = f.read()
            assert b'\xf3' not in content
    finally:
        os.unlink(file_path)


def test_normalize_file_encoding_adds_newline():
    """Test that normalize adds newline if missing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
        f.write('# Test file\nprint("Hello")')  # No trailing newline
        file_path = Path(f.name)
    
    try:
        success, message = normalize_file_encoding(file_path)
        
        assert success is True
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            assert content.endswith('\n')
    finally:
        os.unlink(file_path)


def test_normalize_file_encoding_adds_encoding_header():
    """Test that normalize adds encoding header for non-ASCII content."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
        f.write('# Test file\nprint("Hola")\n')  # Has non-ASCII
        file_path = Path(f.name)
    
    try:
        success, message = normalize_file_encoding(file_path)
        
        assert success is True
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            assert 'coding' in content.lower() or 'encoding' in content.lower()
    finally:
        os.unlink(file_path)


def test_normalize_file_encoding_invalid_file():
    """Test normalizing an invalid file."""
    with tempfile.NamedTemporaryFile(mode='wb', suffix='.py', delete=False) as f:
        # Write invalid bytes
        f.write(b'\xff\xfe\x00\x00')  # Invalid UTF-8
        file_path = Path(f.name)
    
    try:
        success, message = normalize_file_encoding(file_path)
        
        # Should handle gracefully
        assert isinstance(success, bool)
    finally:
        os.unlink(file_path)


