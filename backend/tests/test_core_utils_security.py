"""
Unit tests for core utils security module.
Tests security validation and sanitization functions.
"""
import pytest
from pathlib import Path

from core.utils.security import (
    sanitize_filename,
    validate_filename,
    secure_path_join,
    escape_html
)


class TestSanitizeFilename:
    """Tests for sanitize_filename function."""
    
    def test_sanitize_normal_filename(self):
        """Test sanitizing a normal filename."""
        result = sanitize_filename("test_file.jpg")
        
        assert result == "test_file.jpg"
    
    def test_sanitize_filename_with_dangerous_chars(self):
        """Test sanitizing filename with dangerous characters."""
        result = sanitize_filename("test<file>name.jpg")
        
        assert "<" not in result
        assert ">" not in result
    
    def test_sanitize_filename_with_path_traversal(self):
        """Test that path traversal is rejected."""
        with pytest.raises(ValueError, match="path traversal"):
            sanitize_filename("../../../etc/passwd")
    
    def test_sanitize_filename_with_directory_separator(self):
        """Test that directory separators are removed."""
        result = sanitize_filename("path/to/file.jpg")
        
        assert "/" not in result
        assert "\\" not in result
    
    def test_sanitize_empty_filename_uses_default(self):
        """Test that empty filename uses default."""
        result = sanitize_filename("   ", default="default.jpg")
        
        assert result == "default.jpg"
    
    def test_sanitize_filename_too_long(self):
        """Test that very long filenames are truncated."""
        long_name = "a" * 300 + ".jpg"
        result = sanitize_filename(long_name)
        
        assert len(result) <= 255
    
    def test_sanitize_invalid_input_raises_error(self):
        """Test that invalid input raises ValueError."""
        with pytest.raises(ValueError):
            sanitize_filename(None)
        
        with pytest.raises(ValueError):
            sanitize_filename("")


class TestValidateFilename:
    """Tests for validate_filename function."""
    
    def test_validate_normal_filename(self):
        """Test validating a normal filename."""
        assert validate_filename("test_file.jpg") is True
    
    def test_validate_filename_with_path_traversal(self):
        """Test that path traversal is rejected."""
        assert validate_filename("../../../etc/passwd") is False
    
    def test_validate_filename_with_directory_separator(self):
        """Test that directory separators are rejected."""
        assert validate_filename("path/to/file.jpg") is False
        assert validate_filename("path\\to\\file.jpg") is False
    
    def test_validate_filename_with_null_byte(self):
        """Test that null bytes are rejected."""
        assert validate_filename("test\0file.jpg") is False
    
    def test_validate_filename_with_dangerous_chars(self):
        """Test that dangerous characters are rejected."""
        assert validate_filename("test<file>name.jpg") is False
        assert validate_filename("test:file.jpg") is False
    
    def test_validate_empty_filename(self):
        """Test that empty filename is rejected."""
        assert validate_filename("") is False
        assert validate_filename("   ") is False
    
    def test_validate_invalid_input(self):
        """Test that invalid input returns False."""
        assert validate_filename(None) is False
        assert validate_filename(123) is False


class TestSecurePathJoin:
    """Tests for secure_path_join function."""
    
    def test_secure_path_join_basic(self, tmp_path):
        """Test basic secure path joining."""
        base = Path(tmp_path) / "base"
        base.mkdir()
        
        result = secure_path_join(base, "subdir", "file.txt")
        
        assert result.is_absolute()
        assert "subdir" in str(result)
        assert "file.txt" in str(result)
    
    def test_secure_path_join_prevents_traversal(self, tmp_path):
        """Test that path traversal is prevented."""
        base = Path(tmp_path) / "base"
        base.mkdir()
        
        with pytest.raises(ValueError, match="outside allowed"):
            secure_path_join(base, "..", "etc", "passwd")
    
    def test_secure_path_join_requires_absolute_base(self):
        """Test that base path must be absolute."""
        with pytest.raises(ValueError, match="absolute path"):
            secure_path_join(Path("relative"), "file.txt")
    
    def test_secure_path_join_sanitizes_parts(self, tmp_path):
        """Test that path parts are sanitized."""
        base = Path(tmp_path) / "base"
        base.mkdir()
        
        result = secure_path_join(base, "path/to", "file.txt")
        
        # Directory separators should be replaced
        assert "/" not in result.name
        assert "\\" not in result.name
    
    def test_secure_path_join_with_empty_parts(self, tmp_path):
        """Test path joining with empty parts."""
        base = Path(tmp_path) / "base"
        base.mkdir()
        
        result = secure_path_join(base, "", "file.txt")
        
        assert "file.txt" in str(result)


class TestEscapeHtml:
    """Tests for escape_html function."""
    
    def test_escape_html_basic(self):
        """Test basic HTML escaping."""
        result = escape_html("<script>alert('xss')</script>")
        
        assert "<" not in result
        assert ">" not in result
        assert "&lt;" in result
        assert "&gt;" in result
    
    def test_escape_html_quotes(self):
        """Test escaping HTML quotes."""
        result = escape_html('Text with "quotes" and \'apostrophes\'')
        
        assert "&quot;" in result
        assert "&#x27;" in result
    
    def test_escape_html_ampersand(self):
        """Test escaping ampersand."""
        result = escape_html("A & B")
        
        assert "&amp;" in result
    
    def test_escape_html_empty_string(self):
        """Test escaping empty string."""
        result = escape_html("")
        
        assert result == ""
    
    def test_escape_html_none_returns_empty(self):
        """Test that None returns empty string."""
        result = escape_html(None)
        
        assert result == ""
    
    def test_escape_html_non_string_converts(self):
        """Test that non-string input is converted."""
        result = escape_html(123)
        
        assert isinstance(result, str)
        assert result == "123"

