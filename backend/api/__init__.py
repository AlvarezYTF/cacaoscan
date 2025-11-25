"""
API module for CacaoScan.

This module does not import views to avoid circular dependencies during Django setup.
All views should be imported directly from api.views or specific view modules.

For example:
    from api.views import LoginView, RegisterView
    from api.views.ml import CalibrationView
"""
# No views are imported here to avoid circular dependencies during Django setup.
# All code should import views directly from api.views or specific view modules.
# The api/urls.py file already imports directly from .views, so this is safe.

