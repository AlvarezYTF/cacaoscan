"""
Security utilities for input validation and sanitization.
"""
import os
import re
from pathlib import Path
from typing import Optional


def sanitize_filename(filename: str, default: str = "file") -> str:
    """
    Sanitizes a filename to prevent path traversal and other security issues.
    
    Args:
        filename: Original filename from user input
        default: Default filename if sanitization results in empty string
        
    Returns:
        Sanitized filename safe for use in file operations
        
    Raises:
        ValueError: If filename is invalid or contains dangerous patterns
    """
    if not filename or not isinstance(filename, str):
        raise ValueError("Filename must be a non-empty string")
    
    # Remove any path components (directory separators)
    filename = os.path.basename(filename)
    
    # Remove path traversal attempts
    if ".." in filename:
        raise ValueError("Filename cannot contain path traversal sequences (..)")
    
    # Remove dangerous characters (Windows and Unix)
    # Null bytes, control characters, and special filesystem characters
    dangerous_chars = r'[<>:"|?*\x00-\x1f]'
    if re.search(dangerous_chars, filename):
        # Replace dangerous characters with underscore
        filename = re.sub(dangerous_chars, '_', filename)
    
    # Remove leading/trailing whitespace and dots
    filename = filename.strip(' .')
    
    # Check if empty after sanitization
    if not filename or len(filename) == 0:
        if default:
            filename = default
        else:
            raise ValueError("Filename cannot be empty after sanitization")
    
    # Limit filename length (filesystem limit is typically 255)
    if len(filename) > 255:
        # Try to preserve extension
        name_part, ext = os.path.splitext(filename)
        max_name_length = 255 - len(ext)
        if max_name_length > 0:
            filename = name_part[:max_name_length] + ext
        else:
            filename = filename[:255]
    
    return filename


def validate_filename(filename: str) -> bool:
    """
    Validates that a filename is safe (no path traversal or dangerous characters).
    
    Args:
        filename: Filename to validate
        
    Returns:
        True if filename is safe, False otherwise
    """
    if not filename or not isinstance(filename, str):
        return False
    
    # Check for path traversal attempts
    if ".." in filename:
        return False
    
    # Check for directory separators
    if "/" in filename or "\\" in filename:
        return False
    
    # Check for null bytes
    if "\0" in filename:
        return False
    
    # Check for dangerous characters
    dangerous_chars = r'[<>:"|?*\x00-\x1f]'
    if re.search(dangerous_chars, filename):
        return False
    
    # Filename should not be empty or only whitespace
    if not filename.strip():
        return False
    
    return True


def secure_path_join(base_path: Path, *path_parts: str) -> Path:
    """
    Safely joins path components and ensures the result is within base_path.
    
    This function prevents path traversal attacks by ensuring all joined paths
    resolve to locations within the base_path directory.
    
    Args:
        base_path: Base directory path (must be absolute)
        *path_parts: Additional path components to join
        
    Returns:
        Absolute Path object within base_path
        
    Raises:
        ValueError: If resulting path is outside base_path or invalid
    """
    if not base_path.is_absolute():
        raise ValueError("base_path must be an absolute path")
    
    # Sanitize each path part
    sanitized_parts = []
    for part in path_parts:
        if not part:
            continue
        # Remove any path separators from parts
        part = part.replace("/", "_").replace("\\", "_")
        # Remove path traversal
        part = part.replace("..", "_")
        if part:
            sanitized_parts.append(part)
    
    # Join and resolve
    try:
        result_path = base_path
        for part in sanitized_parts:
            result_path = result_path / part
        
        # Resolve to absolute path (removes .. and . components)
        result_path = result_path.resolve()
        
        # Ensure result is within base_path
        try:
            result_path.relative_to(base_path.resolve())
        except ValueError:
            raise ValueError(
                f"Path {result_path} is outside allowed base path {base_path}"
            )
        
        return result_path
    except Exception as e:
        raise ValueError(f"Invalid path construction: {str(e)}") from e


def escape_html(text: str) -> str:
    """
    Escapes HTML special characters to prevent XSS attacks.
    
    Args:
        text: Text to escape
        
    Returns:
        Escaped HTML string
    """
    if not text:
        return ""
    
    if not isinstance(text, str):
        text = str(text)
    
    escape_map = {
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#x27;",
    }
    
    # Use a list comprehension for better performance
    return "".join(escape_map.get(char, char) for char in text)

