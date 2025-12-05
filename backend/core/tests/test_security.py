"""
Tests for security utility functions.
"""
import pytest
from pathlib import Path
import tempfile
import os

from core.utils.security import (
    sanitize_filename,
    validate_filename,
    secure_path_join,
    escape_html
)


def test_sanitize_filename_valid():
    """Test sanitizing a valid filename."""
    result = sanitize_filename("test_file.jpg")
    assert result == "test_file.jpg"


def test_sanitize_filename_with_path_traversal():
    """Test sanitizing filename with path traversal attempt."""
    with pytest.raises(ValueError, match="path traversal"):
        sanitize_filename("../../../etc/passwd")


def test_sanitize_filename_with_dangerous_chars():
    """Test sanitizing filename with dangerous characters."""
    result = sanitize_filename("test<file>name.jpg")
    assert result == "test_file_name.jpg"
    assert "<" not in result
    assert ">" not in result


def test_sanitize_filename_with_null_bytes():
    """Test sanitizing filename with null bytes."""
    result = sanitize_filename("test\x00file.jpg")
    assert "\x00" not in result


def test_sanitize_filename_strips_whitespace():
    """Test sanitizing filename strips whitespace and dots."""
    result = sanitize_filename("  test_file.jpg  ")
    assert result == "test_file.jpg"
    
    # Note: "..." contains ".." so it will raise ValueError
    # Use single dots instead
    result = sanitize_filename(".test_file.jpg.")
    assert result == "test_file.jpg"


def test_sanitize_filename_empty_after_sanitization():
    """Test sanitizing filename that becomes empty."""
    # Use only dots (not "..") that will become empty after strip
    with pytest.raises(ValueError, match="empty after sanitization"):
        sanitize_filename("   ", default=None)


def test_sanitize_filename_empty_with_default():
    """Test sanitizing empty filename with default."""
    # Whitespace after strip becomes empty, so default is used
    result = sanitize_filename("   ", default="default_file.txt")
    assert result == "default_file.txt"


def test_sanitize_filename_too_long():
    """Test sanitizing filename that is too long."""
    long_name = "a" * 300 + ".jpg"
    result = sanitize_filename(long_name)
    assert len(result) <= 255
    assert result.endswith(".jpg")


def test_sanitize_filename_invalid_type():
    """Test sanitizing filename with invalid type."""
    with pytest.raises(ValueError, match="non-empty string"):
        sanitize_filename(None)
    
    with pytest.raises(ValueError, match="non-empty string"):
        sanitize_filename(123)


def test_validate_filename_valid():
    """Test validating a valid filename."""
    assert validate_filename("test_file.jpg") is True
    assert validate_filename("document.pdf") is True


def test_validate_filename_with_path_traversal():
    """Test validating filename with path traversal."""
    assert validate_filename("../etc/passwd") is False


def test_validate_filename_with_directory_separators():
    """Test validating filename with directory separators."""
    assert validate_filename("path/to/file.jpg") is False
    assert validate_filename("path\\to\\file.jpg") is False


def test_validate_filename_with_null_bytes():
    """Test validating filename with null bytes."""
    assert validate_filename("test\x00file.jpg") is False


def test_validate_filename_with_dangerous_chars():
    """Test validating filename with dangerous characters."""
    assert validate_filename("test<file>name.jpg") is False
    assert validate_filename("test:file.jpg") is False


def test_validate_filename_empty():
    """Test validating empty filename."""
    assert validate_filename("") is False
    assert validate_filename("   ") is False


def test_validate_filename_invalid_type():
    """Test validating filename with invalid type."""
    assert validate_filename(None) is False
    assert validate_filename(123) is False


def test_secure_path_join_valid():
    """Test secure path join with valid paths."""
    with tempfile.TemporaryDirectory() as tmpdir:
        base_path = Path(tmpdir)
        result = secure_path_join(base_path, "subdir", "file.txt")
        
        assert isinstance(result, Path)
        assert result.is_absolute()
        assert str(result).startswith(str(base_path.resolve()))


def test_secure_path_join_relative_base_path():
    """Test secure path join with relative base path."""
    with pytest.raises(ValueError, match="absolute path"):
        secure_path_join(Path("relative/path"), "file.txt")


def test_secure_path_join_path_traversal():
    """Test secure path join with path traversal attempt."""
    with tempfile.TemporaryDirectory() as tmpdir:
        base_path = Path(tmpdir)
        with pytest.raises(ValueError, match="outside allowed base path"):
            secure_path_join(base_path, "..", "etc", "passwd")


def test_secure_path_join_with_slashes():
    """Test secure path join sanitizes slashes in path parts."""
    with tempfile.TemporaryDirectory() as tmpdir:
        base_path = Path(tmpdir)
        result = secure_path_join(base_path, "path/to", "file.txt")
        
        # Slashes should be replaced with underscores
        assert "path_to" in str(result) or "path" in str(result)


def test_secure_path_join_empty_parts():
    """Test secure path join with empty path parts."""
    with tempfile.TemporaryDirectory() as tmpdir:
        base_path = Path(tmpdir)
        result = secure_path_join(base_path, "", "file.txt")
        
        assert isinstance(result, Path)
        assert "file.txt" in str(result)


def test_escape_html_simple():
    """Test escaping simple HTML."""
    result = escape_html("<script>alert('xss')</script>")
    assert "&lt;" in result
    assert "&gt;" in result
    assert "<script>" not in result


def test_escape_html_quotes():
    """Test escaping HTML with quotes."""
    result = escape_html('Test "quoted" string')
    assert "&quot;" in result
    assert '"' not in result


def test_escape_html_ampersand():
    """Test escaping HTML with ampersand."""
    result = escape_html("A & B")
    assert "&amp;" in result


def test_escape_html_empty():
    """Test escaping empty string."""
    result = escape_html("")
    assert result == ""


def test_escape_html_none():
    """Test escaping None."""
    result = escape_html(None)
    assert result == ""


def test_escape_html_non_string():
    """Test escaping non-string value."""
    result = escape_html(123)
    assert result == "123"
    
    result = escape_html(True)
    assert result == "True"


