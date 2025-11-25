"""
User profile service for CacaoScan.
Handles user profile retrieval and updates.
"""
import logging
from typing import Dict, Any
from django.contrib.auth.models import User

from ..base import BaseService, ServiceResult, ValidationServiceError

logger = logging.getLogger("cacaoscan.services.auth.profile")


class ProfileService(BaseService):
    """
    Service for handling user profile operations.
    """
    
    def __init__(self):
        super().__init__()
    
    def get_user_profile(self, user: User) -> ServiceResult:
        """
        Gets user profile.
        
        Args:
            user: User
            
        Returns:
            ServiceResult with profile data
        """
        try:
            # Get extended profile if exists
            from ...utils.model_imports import get_models_safely
            models = get_models_safely({
                'UserProfile': 'auth_app.models.UserProfile'
            })
            UserProfile = models['UserProfile']
            
            user_profile = None
            try:
                user_profile = user.profile
            except UserProfile.DoesNotExist:
                # If no profile exists, create empty one
                user_profile = UserProfile.objects.create(user=user)
            
            profile_data = {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'full_name': user.get_full_name() or user.username,
                'is_staff': user.is_staff,
                'is_superuser': user.is_superuser,
                'is_active': user.is_active,
                'date_joined': user.date_joined.isoformat(),
                'last_login': user.last_login.isoformat() if user.last_login else None,
                'is_verified': self._check_email_verified(user),
                # Extended profile data
                'phone_number': user_profile.phone_number or '',
                'region': user_profile.region or '',
                'municipality': user_profile.municipality or '',
                'farm_name': user_profile.farm_name or '',
                'years_experience': user_profile.years_experience,
                'farm_size_hectares': float(user_profile.farm_size_hectares) if user_profile.farm_size_hectares else None,
                'preferred_language': user_profile.preferred_language,
                'email_notifications': user_profile.email_notifications,
                'role': user_profile.role
            }
            
            return ServiceResult.success(
                data=profile_data,
                message="Perfil obtenido exitosamente"
            )
            
        except Exception as e:
            self.log_error(f"Error obteniendo perfil: {str(e)}")
            return ServiceResult.error(
                ValidationServiceError("Error interno obteniendo perfil", details={"original_error": str(e)})
            )
    
    def update_user_profile(self, user: User, profile_data: Dict[str, Any]) -> ServiceResult:
        """
        Updates user profile.
        
        Args:
            user: User
            profile_data: Data to update
            
        Returns:
            ServiceResult with updated data
        """
        try:
            # Allowed fields for User model update
            user_allowed_fields = ['first_name', 'last_name', 'email']
            
            # Extended profile fields (UserProfile)
            profile_allowed_fields = ['phone_number']
            
            # Separate User and UserProfile data
            user_data = {}
            profile_data_dict = {}
            
            for field, value in profile_data.items():
                if field in user_allowed_fields:
                    user_data[field] = value
                elif field in profile_allowed_fields:
                    profile_data_dict[field] = value
                else:
                    return ServiceResult.validation_error(
                        f"Campo '{field}' no permitido para actualización",
                        details={
                            "field": field, 
                            "allowed_fields": user_allowed_fields + profile_allowed_fields
                        }
                    )
            
            # Validate unique email if changing
            if 'email' in user_data and user_data['email'] != user.email:
                if User.objects.filter(email=user_data['email']).exclude(id=user.id).exists():
                    return ServiceResult.validation_error(
                        "Este email ya está registrado",
                        details={"field": "email"}
                    )
            
            # Update User model fields
            for field, value in user_data.items():
                setattr(user, field, value)
            
            user.save()
            
            # Update extended profile if exists
            if profile_data_dict:
                from ...utils.model_imports import get_models_safely
                models = get_models_safely({
                    'UserProfile': 'auth_app.models.UserProfile'
                })
                UserProfile = models['UserProfile']
                profile, created = UserProfile.objects.get_or_create(user=user)
                for field, value in profile_data_dict.items():
                    setattr(profile, field, value)
                profile.save()
            
            # Get updated user data
            updated_data = self.get_user_profile(user).data
            
            # Create audit log
            self.create_audit_log(
                user=user,
                action="profile_updated",
                resource_type="user",
                resource_id=user.id,
                details={"updated_fields": list(profile_data.keys())}
            )
            
            self.log_info(f"Perfil actualizado para usuario {user.username}")
            
            return ServiceResult.success(
                data=updated_data,
                message="Perfil actualizado exitosamente"
            )
            
        except ValidationServiceError as e:
            return ServiceResult.error(e)
        except Exception as e:
            self.log_error(f"Error actualizando perfil: {str(e)}")
            return ServiceResult.error(
                ValidationServiceError("Error interno actualizando perfil", details={"original_error": str(e)})
            )
    
    def _check_email_verified(self, user: User) -> bool:
        """Checks if user email is verified."""
        try:
            if hasattr(user, 'auth_email_token'):
                return user.auth_email_token.is_verified
        except:
            pass
        return user.is_active

