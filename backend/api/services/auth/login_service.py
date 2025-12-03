"""
Login service for CacaoScan.
Handles user authentication, login, logout, and token refresh.
"""
import logging
from typing import Optional
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone

from ..base import BaseService, ServiceResult, ValidationServiceError
from audit.models import LoginHistory

logger = logging.getLogger("cacaoscan.services.auth.login")


class LoginService(BaseService):
    """
    Service for handling user login, logout, and token refresh.
    """
    
    def __init__(self):
        super().__init__()
    
    def login_user(self, username: str, password: str, request=None) -> ServiceResult:
        """
        Authenticates a user and generates JWT tokens.
        
        Args:
            username: Username or email
            password: Password
            request: Request object to get IP and user agent
            
        Returns:
            ServiceResult with tokens and user data
        """
        try:
            # Validate required fields
            self.validate_required_fields(
                {'username': username, 'password': password},
                ['username', 'password']
            )
            
            # Authenticate user
            user = authenticate(username=username, password=password)
            
            if not user:
                return ServiceResult.validation_error(
                    "Credenciales inválidas",
                    details={"field": "credentials"}
                )
            
            if not user.is_active:
                return ServiceResult.validation_error(
                    "Cuenta de usuario desactivada",
                    details={"field": "account_status"}
                )
            
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token
            
            # Log user login
            self._log_user_login(user, request)
            
            # Create audit log
            self.create_audit_log(
                user=user,
                action="login",
                resource_type="user",
                resource_id=user.id,
                details={"login_method": "password"}
            )
            
            self.log_info(f"Usuario {user.username} autenticado exitosamente")
            
            return ServiceResult.success(
                data={
                    'access': str(access_token),
                    'refresh': str(refresh),
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'is_staff': user.is_staff,
                        'is_superuser': user.is_superuser,
                        'is_active': user.is_active,
                        'date_joined': user.date_joined.isoformat(),
                        'last_login': user.last_login.isoformat() if user.last_login else None
                    },
                    'access_expires_at': access_token['exp'],
                    'refresh_expires_at': refresh['exp']
                },
                message="Login exitoso"
            )
            
        except ValidationServiceError as e:
            return ServiceResult.error(e)
        except Exception as e:
            self.log_error(f"Error en login: {str(e)}")
            return ServiceResult.error(
                ValidationServiceError("Error interno durante el login", details={"original_error": str(e)})
            )
    
    def logout_user(self, user: User, refresh_token: str = None) -> ServiceResult:
        """
        Logs out a user.
        
        Args:
            user: User to log out
            refresh_token: Refresh token to invalidate
            
        Returns:
            ServiceResult with logout result
        """
        try:
            # Invalidate refresh token if provided
            if refresh_token:
                try:
                    token = RefreshToken(refresh_token)
                    token.blacklist()
                except Exception as e:
                    self.log_warning(f"Error invalidando token: {str(e)}")
            
            # Create audit log
            self.create_audit_log(
                user=user,
                action="logout",
                resource_type="user",
                resource_id=user.id
            )
            
            self.log_info(f"Usuario {user.username} cerró sesión")
            
            return ServiceResult.success(
                message="Logout exitoso"
            )
            
        except Exception as e:
            self.log_error(f"Error en logout: {str(e)}")
            return ServiceResult.error(
                ValidationServiceError("Error interno durante el logout", details={"original_error": str(e)})
            )
    
    def refresh_token(self, refresh_token: str) -> ServiceResult:
        """
        Refreshes an access token.
        
        Args:
            refresh_token: Refresh token
            
        Returns:
            ServiceResult with new access token
        """
        try:
            token = RefreshToken(refresh_token)
            new_access_token = token.access_token
            
            return ServiceResult.success(
                data={
                    'access': str(new_access_token),
                    'access_expires_at': new_access_token['exp']
                },
                message="Token refrescado exitosamente"
            )
            
        except Exception as e:
            self.log_error(f"Error refrescando token: {str(e)}")
            return ServiceResult.error(
                ValidationServiceError("Token de refresh inválido", details={"original_error": str(e)})
            )
    
    def _log_user_login(self, user: User, request=None):
        """Logs user login in history."""
        try:
            ip_address = None
            user_agent = None
            
            if request:
                ip_address = self._get_client_ip(request)
                user_agent = request.META.get('HTTP_USER_AGENT', '')
            
            LoginHistory.objects.create(
                usuario=user,
                ip_address=ip_address,
                user_agent=user_agent,
                login_time=timezone.now(),
                success=True
            )
        except Exception as e:
            self.log_warning(f"Error registrando login: {str(e)}")
    
    def _get_client_ip(self, request):
        """Gets client IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def login(self, username_or_email: str, password: str, request=None) -> ServiceResult:
        """
        Alias for login_user for backward compatibility with tests.
        
        Args:
            username_or_email: Username or email
            password: Password
            request: Request object to get IP and user agent
            
        Returns:
            ServiceResult with tokens and user data
        """
        return self.login_user(username_or_email, password, request)

