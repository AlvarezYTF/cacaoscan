"""
Centralized validators for CacaoScan API.
Contains reusable validation functions following DRY and KISS principles.
"""
import re
from typing import Dict, Any, Optional
from rest_framework import serializers


class PasswordValidationError(Exception):
    """Custom exception for password validation errors."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


def validate_password_strength(password: str, raise_serializer_error: bool = True) -> str:
    """
    Validates password strength requirements.
    
    Requirements:
    - Minimum 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one number
    
    Args:
        password: Password string to validate
        raise_serializer_error: If True, raises serializers.ValidationError (for serializers).
                               If False, raises PasswordValidationError (for services).
        
    Returns:
        str: Validated password
        
    Raises:
        serializers.ValidationError: If password doesn't meet requirements and raise_serializer_error=True
        PasswordValidationError: If password doesn't meet requirements and raise_serializer_error=False
    """
    if len(password) < 8:
        error_msg = "La contraseña debe tener al menos 8 caracteres."
        if raise_serializer_error:
            raise serializers.ValidationError(error_msg)
        raise PasswordValidationError(error_msg)
    
    if not any(c.isupper() for c in password):
        error_msg = "La contraseña debe contener al menos una letra mayúscula."
        if raise_serializer_error:
            raise serializers.ValidationError(error_msg)
        raise PasswordValidationError(error_msg)
    
    if not any(c.islower() for c in password):
        error_msg = "La contraseña debe contener al menos una letra minúscula."
        if raise_serializer_error:
            raise serializers.ValidationError(error_msg)
        raise PasswordValidationError(error_msg)
    
    if not any(c.isdigit() for c in password):
        error_msg = "La contraseña debe contener al menos un número."
        if raise_serializer_error:
            raise serializers.ValidationError(error_msg)
        raise PasswordValidationError(error_msg)
    
    return password


def validate_passwords_match(password: str, password_confirm: str, field_name: str = 'confirm_password') -> None:
    """
    Validates that two passwords match.
    
    Args:
        password: First password
        password_confirm: Confirmation password
        field_name: Name of the confirmation field for error message
        
    Raises:
        serializers.ValidationError: If passwords don't match
    """
    if password != password_confirm:
        raise serializers.ValidationError({
            field_name: 'Las contraseñas no coinciden.'
        })


def validate_password_different(old_password: str, new_password: str) -> None:
    """
    Validates that new password is different from old password.
    
    Args:
        old_password: Current password
        new_password: New password
        
    Raises:
        serializers.ValidationError: If passwords are the same
    """
    if old_password == new_password:
        raise serializers.ValidationError({
            'new_password': 'La nueva contraseña debe ser diferente a la contraseña actual.'  # noqa: S2068
        })


def validate_latitude(lat: Optional[float]) -> Optional[float]:
    """
    Validates GPS latitude value.
    
    Args:
        lat: Latitude value to validate
        
    Returns:
        Optional[float]: Validated latitude
        
    Raises:
        serializers.ValidationError: If latitude is out of valid range
    """
    if lat is not None and (lat < -90 or lat > 90):
        raise serializers.ValidationError("La latitud debe estar entre -90 y 90 grados.")
    return lat


def validate_longitude(lng: Optional[float]) -> Optional[float]:
    """
    Validates GPS longitude value.
    
    Args:
        lng: Longitude value to validate
        
    Returns:
        Optional[float]: Validated longitude
        
    Raises:
        serializers.ValidationError: If longitude is out of valid range
    """
    if lng is not None and (lng < -180 or lng > 180):
        raise serializers.ValidationError("La longitud debe estar entre -180 y 180 grados.")
    return lng


def validate_coordinates_pair(lat: Optional[float], lng: Optional[float]) -> None:
    """
    Validates that if coordinates are provided, both latitude and longitude are present.
    
    Args:
        lat: Latitude value
        lng: Longitude value
        
    Raises:
        serializers.ValidationError: If only one coordinate is provided
    """
    if (lat is not None and lng is None) or (lat is None and lng is not None):
        raise serializers.ValidationError("Debe proporcionar tanto latitud como longitud, o ninguna.")


def validate_coordinates(attrs: Dict[str, Any], lat_field: str = 'coordenadas_lat', lng_field: str = 'coordenadas_lng') -> Dict[str, Any]:
    """
    Complete validation for GPS coordinates.
    Validates individual coordinates and ensures both are provided together.
    
    Args:
        attrs: Dictionary of attributes containing coordinates
        lat_field: Name of the latitude field
        lng_field: Name of the longitude field
        
    Returns:
        Dict[str, Any]: Validated attributes dictionary
        
    Raises:
        serializers.ValidationError: If coordinates are invalid
    """
    lat = attrs.get(lat_field)
    lng = attrs.get(lng_field)
    
    # Validate individual coordinates
    if lat is not None:
        validate_latitude(lat)
    if lng is not None:
        validate_longitude(lng)
    
    # Validate that both are provided together
    validate_coordinates_pair(lat, lng)
    
    return attrs

