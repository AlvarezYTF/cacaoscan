"""
Tests for validators.
"""
import pytest
from rest_framework import serializers

from core.utils.validators import (
    validate_password_strength,
    validate_passwords_match,
    validate_password_different,
    validate_latitude,
    validate_longitude,
    validate_coordinates_pair,
    validate_coordinates,
    PasswordValidationError
)


class TestPasswordValidators:
    """Tests for password validators."""
    
    def test_validate_password_strength_valid(self):
        """Test valid password."""
        password = "ValidPass123"
        result = validate_password_strength(password)
        assert result == password
    
    def test_validate_password_strength_too_short(self):
        """Test password too short."""
        password = "Short1"
        with pytest.raises(serializers.ValidationError):
            validate_password_strength(password, raise_serializer_error=True)
        
        with pytest.raises(PasswordValidationError):
            validate_password_strength(password, raise_serializer_error=False)
    
    def test_validate_password_strength_no_uppercase(self):
        """Test password without uppercase."""
        password = "nopass123"
        with pytest.raises(serializers.ValidationError):
            validate_password_strength(password, raise_serializer_error=True)
        
        with pytest.raises(PasswordValidationError):
            validate_password_strength(password, raise_serializer_error=False)
    
    def test_validate_password_strength_no_lowercase(self):
        """Test password without lowercase."""
        password = "NOPASS123"
        with pytest.raises(serializers.ValidationError):
            validate_password_strength(password, raise_serializer_error=True)
        
        with pytest.raises(PasswordValidationError):
            validate_password_strength(password, raise_serializer_error=False)
    
    def test_validate_password_strength_no_number(self):
        """Test password without number."""
        password = "NoPassword"
        with pytest.raises(serializers.ValidationError):
            validate_password_strength(password, raise_serializer_error=True)
        
        with pytest.raises(PasswordValidationError):
            validate_password_strength(password, raise_serializer_error=False)
    
    def test_validate_passwords_match(self):
        """Test matching passwords."""
        password = "ValidPass123"
        password_confirm = "ValidPass123"
        # Should not raise
        validate_passwords_match(password, password_confirm)
    
    def test_validate_passwords_match_mismatch(self):
        """Test mismatched passwords."""
        password = "ValidPass123"
        password_confirm = "DifferentPass123"
        with pytest.raises(serializers.ValidationError):
            validate_passwords_match(password, password_confirm)
    
    def test_validate_password_different(self):
        """Test different passwords."""
        old_password = "OldPass123"
        new_password = "NewPass123"
        # Should not raise
        validate_password_different(old_password, new_password)
    
    def test_validate_password_different_same(self):
        """Test same passwords."""
        old_password = "SamePass123"
        new_password = "SamePass123"
        with pytest.raises(serializers.ValidationError):
            validate_password_different(old_password, new_password)


class TestCoordinateValidators:
    """Tests for coordinate validators."""
    
    def test_validate_latitude_valid(self):
        """Test valid latitude."""
        lat = 45.5
        result = validate_latitude(lat)
        assert result == lat
    
    def test_validate_latitude_none(self):
        """Test None latitude."""
        result = validate_latitude(None)
        assert result is None
    
    def test_validate_latitude_too_high(self):
        """Test latitude too high."""
        lat = 91.0
        with pytest.raises(serializers.ValidationError):
            validate_latitude(lat)
    
    def test_validate_latitude_too_low(self):
        """Test latitude too low."""
        lat = -91.0
        with pytest.raises(serializers.ValidationError):
            validate_latitude(lat)
    
    def test_validate_latitude_boundary_high(self):
        """Test latitude at upper boundary."""
        lat = 90.0
        result = validate_latitude(lat)
        assert result == lat
    
    def test_validate_latitude_boundary_low(self):
        """Test latitude at lower boundary."""
        lat = -90.0
        result = validate_latitude(lat)
        assert result == lat
    
    def test_validate_longitude_valid(self):
        """Test valid longitude."""
        lng = 120.5
        result = validate_longitude(lng)
        assert result == lng
    
    def test_validate_longitude_none(self):
        """Test None longitude."""
        result = validate_longitude(None)
        assert result is None
    
    def test_validate_longitude_too_high(self):
        """Test longitude too high."""
        lng = 181.0
        with pytest.raises(serializers.ValidationError):
            validate_longitude(lng)
    
    def test_validate_longitude_too_low(self):
        """Test longitude too low."""
        lng = -181.0
        with pytest.raises(serializers.ValidationError):
            validate_longitude(lng)
    
    def test_validate_longitude_boundary_high(self):
        """Test longitude at upper boundary."""
        lng = 180.0
        result = validate_longitude(lng)
        assert result == lng
    
    def test_validate_longitude_boundary_low(self):
        """Test longitude at lower boundary."""
        lng = -180.0
        result = validate_longitude(lng)
        assert result == lng
    
    def test_validate_coordinates_pair_both_none(self):
        """Test coordinates pair with both None."""
        # Should not raise
        validate_coordinates_pair(None, None)
    
    def test_validate_coordinates_pair_both_provided(self):
        """Test coordinates pair with both provided."""
        # Should not raise
        validate_coordinates_pair(45.5, 120.5)
    
    def test_validate_coordinates_pair_only_latitude(self):
        """Test coordinates pair with only latitude."""
        with pytest.raises(serializers.ValidationError):
            validate_coordinates_pair(45.5, None)
    
    def test_validate_coordinates_pair_only_longitude(self):
        """Test coordinates pair with only longitude."""
        with pytest.raises(serializers.ValidationError):
            validate_coordinates_pair(None, 120.5)
    
    def test_validate_coordinates_complete(self):
        """Test complete coordinate validation."""
        attrs = {
            'coordenadas_lat': 45.5,
            'coordenadas_lng': 120.5
        }
        result = validate_coordinates(attrs)
        assert result == attrs
    
    def test_validate_coordinates_both_none(self):
        """Test coordinate validation with both None."""
        attrs = {
            'coordenadas_lat': None,
            'coordenadas_lng': None
        }
        result = validate_coordinates(attrs)
        assert result == attrs
    
    def test_validate_coordinates_invalid_latitude(self):
        """Test coordinate validation with invalid latitude."""
        attrs = {
            'coordenadas_lat': 91.0,
            'coordenadas_lng': 120.5
        }
        with pytest.raises(serializers.ValidationError):
            validate_coordinates(attrs)
    
    def test_validate_coordinates_invalid_longitude(self):
        """Test coordinate validation with invalid longitude."""
        attrs = {
            'coordenadas_lat': 45.5,
            'coordenadas_lng': 181.0
        }
        with pytest.raises(serializers.ValidationError):
            validate_coordinates(attrs)
    
    def test_validate_coordinates_only_latitude(self):
        """Test coordinate validation with only latitude."""
        attrs = {
            'coordenadas_lat': 45.5,
            'coordenadas_lng': None
        }
        with pytest.raises(serializers.ValidationError):
            validate_coordinates(attrs)
    
    def test_validate_coordinates_custom_field_names(self):
        """Test coordinate validation with custom field names."""
        attrs = {
            'lat': 45.5,
            'lng': 120.5
        }
        result = validate_coordinates(attrs, lat_field='lat', lng_field='lng')
        assert result == attrs


