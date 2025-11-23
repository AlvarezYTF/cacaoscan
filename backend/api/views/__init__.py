"""
Views module for CacaoScan API.
Organized by domain for better maintainability.
"""
from .auth_views import (
    LoginView,
    RegisterView,
    LogoutView,
    UserProfileView,
    RefreshTokenView,
    ChangePasswordView,
    EmailVerificationView,
    ResendVerificationView,
    PreRegisterView,
    VerifyEmailPreRegistrationView,
    ForgotPasswordView,
    ResetPasswordView
)

from .image_views import (
    ScanMeasureView,
    ImagesListView,
    ImageDetailView,
    ImagesStatsView,
    ImageUpdateView,
    ImageDeleteView,
    ImageDownloadView,
    ImagesExportView,
    AdminImagesListView,
    AdminImageDetailView,
    AdminImageUpdateView,
    AdminImageDeleteView,
    AdminBulkUpdateView,
    AdminDatasetStatsView,
    ImagePermissionMixin
)

from .user_views import (
    UserListView,
    UserUpdateView,
    UserDeleteView,
    UserStatsView,
    AdminStatsView,
    UserDetailView
)

from .training_views import (
    TrainingJobListView,
    TrainingJobCreateView,
    TrainingJobStatusView
)

from .ml_views import (
    ModelsStatusView,
    DatasetValidationView,
    LoadModelsView,
    AutoInitializeView,
    LatestMetricsView,
    PromoteModelView,
    AutoTrainView
)

__all__ = [
    # Auth views
    'LoginView',
    'RegisterView',
    'LogoutView',
    'UserProfileView',
    'RefreshTokenView',
    'ChangePasswordView',
    'EmailVerificationView',
    'ResendVerificationView',
    'PreRegisterView',
    'VerifyEmailPreRegistrationView',
    'ForgotPasswordView',
    'ResetPasswordView',
    # Image views
    'ScanMeasureView',
    'ImagesListView',
    'ImageDetailView',
    'ImagesStatsView',
    'ImageUpdateView',
    'ImageDeleteView',
    'ImageDownloadView',
    'ImagesExportView',
    'AdminImagesListView',
    'AdminImageDetailView',
    'AdminImageUpdateView',
    'AdminImageDeleteView',
    'AdminBulkUpdateView',
    'AdminDatasetStatsView',
    'ImagePermissionMixin',
    # User views
    'UserListView',
    'UserUpdateView',
    'UserDeleteView',
    'UserStatsView',
    'AdminStatsView',
    'UserDetailView',
    # Training views
    'TrainingJobListView',
    'TrainingJobCreateView',
    'TrainingJobStatusView',
    # ML views
    'ModelsStatusView',
    'DatasetValidationView',
    'LoadModelsView',
    'AutoInitializeView',
    'LatestMetricsView',
    'PromoteModelView',
    'AutoTrainView',
]

