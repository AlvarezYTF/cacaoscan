"""
ML views module.
"""
from .calibration_views import (
    CalibrationStatusView,
    CalibrationView,
    CalibratedScanMeasureView,
)
from .incremental_views import (
    IncrementalTrainingStatusView,
    IncrementalTrainingView,
    IncrementalDataUploadView,
    IncrementalModelVersionsView,
    IncrementalDataVersionsView,
)
from .metrics_crud_views import (
    ModelMetricsListView,
    ModelMetricsDetailView,
    ModelMetricsCreateView,
    ModelMetricsUpdateView,
    ModelMetricsDeleteView,
)
from .metrics_analysis_views import (
    ModelMetricsStatsView,
    ModelPerformanceTrendView,
    BestModelsView,
    ProductionModelsView,
)
from .metrics_comparison_views import (
    ModelComparisonView,
)
from .model_views import (
    ModelsStatusView,
    DatasetValidationView,
    LoadModelsView,
    AutoInitializeView,
    LatestMetricsView,
    PromoteModelView,
    AutoTrainView,
)
from .training_views import (
    TrainingJobListView,
    TrainingJobCreateView,
    TrainingJobStatusView,
)

__all__ = [
    'CalibrationStatusView',
    'CalibrationView',
    'CalibratedScanMeasureView',
    'IncrementalTrainingStatusView',
    'IncrementalTrainingView',
    'IncrementalDataUploadView',
    'IncrementalModelVersionsView',
    'IncrementalDataVersionsView',
    'ModelMetricsListView',
    'ModelMetricsDetailView',
    'ModelMetricsCreateView',
    'ModelMetricsUpdateView',
    'ModelMetricsDeleteView',
    'ModelMetricsStatsView',
    'ModelPerformanceTrendView',
    'ModelComparisonView',
    'BestModelsView',
    'ProductionModelsView',
    'ModelsStatusView',
    'DatasetValidationView',
    'LoadModelsView',
    'AutoInitializeView',
    'LatestMetricsView',
    'PromoteModelView',
    'AutoTrainView',
    'TrainingJobListView',
    'TrainingJobCreateView',
    'TrainingJobStatusView',
]

