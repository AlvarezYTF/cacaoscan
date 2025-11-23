"""
Serializers para la API de CacaoScan.
DEPRECATED: Este archivo se mantiene solo para retrocompatibilidad.
Todos los serializers han sido movidos a backend/api/serializers/
Por favor, use imports desde backend/api/serializers/ en código nuevo.
"""
# Re-export all serializers from the new modular structure
# Import from serializers package (directory) instead of serializers module
from .serializers import (  # noqa: F401, F403
    # Common
    ErrorResponseSerializer,
    DatasetStatsSerializer,
    NotificationSerializer,
    NotificationListSerializer,
    NotificationCreateSerializer,
    NotificationStatsSerializer,
    SystemSettingsSerializer,
    # Auth
    LoginSerializer,
    RegisterSerializer,
    ChangePasswordSerializer,
    EmailVerificationSerializer,
    ResendVerificationSerializer,
    UserSerializer,
    UserProfileSerializer,
    SendOtpSerializer,
    VerifyOtpSerializer,
    # Image
    ConfidenceSerializer,
    DebugInfoSerializer,
    ScanMeasureResponseSerializer,
    CacaoImageSerializer,
    CacaoPredictionSerializer,
    CacaoImageDetailSerializer,
    ImagesListResponseSerializer,
    ImagesStatsResponseSerializer,
    # Finca
    FincaSerializer,
    FincaListSerializer,
    FincaDetailSerializer,
    FincaStatsSerializer,
    LoteSerializer,
    LoteListSerializer,
    LoteDetailSerializer,
    LoteStatsSerializer,
    # ML
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
