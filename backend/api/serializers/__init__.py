"""
Serializers for CacaoScan API.
Re-exports all serializers for backward compatibility.
"""
# Common serializers
from .common_serializers import (
    ErrorResponseSerializer,
    DatasetStatsSerializer,
    NotificationSerializer,
    NotificationListSerializer,
    NotificationCreateSerializer,
    NotificationStatsSerializer,
    SystemSettingsSerializer,
)

# Auth serializers
from .auth_serializers import (
    LoginSerializer,
    RegisterSerializer,
    ChangePasswordSerializer,
    EmailVerificationSerializer,
    ResendVerificationSerializer,
    UserSerializer,
    UserProfileSerializer,
    SendOtpSerializer,
    VerifyOtpSerializer,
)

# Image serializers
from .image_serializers import (
    ConfidenceSerializer,
    DebugInfoSerializer,
    ScanMeasureResponseSerializer,
    CacaoImageSerializer,
    CacaoPredictionSerializer,
    CacaoImageDetailSerializer,
    ImagesListResponseSerializer,
    ImagesStatsResponseSerializer,
)

# Finca serializers
from .finca_serializers import (
    FincaSerializer,
    FincaListSerializer,
    FincaDetailSerializer,
    FincaStatsSerializer,
    LoteSerializer,
    LoteListSerializer,
    LoteDetailSerializer,
    LoteStatsSerializer,
)

# ML serializers
from .ml_serializers import (
    ModelsStatusSerializer,
    LoadModelsResponseSerializer,
    TrainingJobSerializer,
    TrainingJobCreateSerializer,
    TrainingJobStatusSerializer,
    AutoTrainConfigSerializer,
    ModelMetricsSerializer,
    ModelMetricsListSerializer,
    ModelMetricsCreateSerializer,
    ModelMetricsUpdateSerializer,
    ModelMetricsStatsSerializer,
    ModelPerformanceTrendSerializer,
    ModelComparisonSerializer,
)

__all__ = [
    # Common
    'ErrorResponseSerializer',
    'DatasetStatsSerializer',
    'NotificationSerializer',
    'NotificationListSerializer',
    'NotificationCreateSerializer',
    'NotificationStatsSerializer',
    'SystemSettingsSerializer',
    # Auth
    'LoginSerializer',
    'RegisterSerializer',
    'ChangePasswordSerializer',
    'EmailVerificationSerializer',
    'ResendVerificationSerializer',
    'UserSerializer',
    'UserProfileSerializer',
    'SendOtpSerializer',
    'VerifyOtpSerializer',
    # Image
    'ConfidenceSerializer',
    'DebugInfoSerializer',
    'ScanMeasureResponseSerializer',
    'CacaoImageSerializer',
    'CacaoPredictionSerializer',
    'CacaoImageDetailSerializer',
    'ImagesListResponseSerializer',
    'ImagesStatsResponseSerializer',
    # Finca
    'FincaSerializer',
    'FincaListSerializer',
    'FincaDetailSerializer',
    'FincaStatsSerializer',
    'LoteSerializer',
    'LoteListSerializer',
    'LoteDetailSerializer',
    'LoteStatsSerializer',
    # ML
    'ModelsStatusSerializer',
    'LoadModelsResponseSerializer',
    'TrainingJobSerializer',
    'TrainingJobCreateSerializer',
    'TrainingJobStatusSerializer',
    'AutoTrainConfigSerializer',
    'ModelMetricsSerializer',
    'ModelMetricsListSerializer',
    'ModelMetricsCreateSerializer',
    'ModelMetricsUpdateSerializer',
    'ModelMetricsStatsSerializer',
    'ModelPerformanceTrendSerializer',
    'ModelComparisonSerializer',
]

