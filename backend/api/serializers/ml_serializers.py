"""
ML serializers for CacaoScan API.
"""
from rest_framework import serializers
from ..utils.model_imports import get_models_safely
from training.models import ModelMetrics

# Import models safely
models = get_models_safely({
    'TrainingJob': 'training.models.TrainingJob'
})
TrainingJob = models['TrainingJob']

# Field source constants
CREATED_BY_USERNAME_SOURCE = 'created_by.username'


class ModelsStatusSerializer(serializers.Serializer):
    """
    Serializer for ML model status.
    UPDATED to reflect the single Hybrid model.
    """
    status = serializers.CharField()
    device = serializers.CharField()
    model = serializers.CharField()
    model_details = serializers.DictField()
    scalers = serializers.CharField()

    def validate(self, data):
        # The get_model_info() function now returns this structure
        errors = []
        if 'status' not in data:
            errors.append("El campo 'status' es requerido.")
        if 'model' not in data:
            errors.append("El campo 'model' es requerido.")
        
        if errors:
            raise serializers.ValidationError(errors)
        return data


class LoadModelsResponseSerializer(serializers.Serializer):
    """Serializer for model loading response."""
    message = serializers.CharField(required=False)
    error = serializers.CharField(required=False)
    status = serializers.CharField()


class TrainingJobSerializer(serializers.ModelSerializer):
    """Serializer for training jobs."""
    duration_formatted = serializers.ReadOnlyField()
    is_active = serializers.ReadOnlyField()
    created_by_username = serializers.CharField(source=CREATED_BY_USERNAME_SOURCE, read_only=True)
    training_time = serializers.SerializerMethodField()
    
    class Meta:
        model = TrainingJob
        fields = (
            'id', 'job_id', 'job_type', 'status', 'created_by', 'created_by_username',
            'model_name', 'dataset_size', 'epochs', 'batch_size', 'learning_rate',
            'config_params', 'metrics', 'model_path', 'logs', 'created_at',
            'started_at', 'completed_at', 'error_message', 'progress_percentage',
            'duration_formatted', 'is_active', 'training_time'
        )
        read_only_fields = (
            'id', 'job_id', 'created_by', 'created_at', 'started_at', 'completed_at',
            'duration_formatted', 'is_active'
        )
    
    def validate_epochs(self, value):
        if value <= 0 or value > 1000:
            raise serializers.ValidationError("Los epochs deben estar entre 1 y 1000.")
        return value
    
    def validate_batch_size(self, value):
        if value <= 0 or value > 128:
            raise serializers.ValidationError("El batch size debe estar entre 1 y 128.")
        return value
    
    def validate_learning_rate(self, value):
        if value <= 0 or value > 1.0:
            raise serializers.ValidationError("El learning rate debe estar entre 0 y 1.0.")
        return value
    
    def validate_dataset_size(self, value):
        if value <= 0:
            raise serializers.ValidationError("El tamaño del dataset debe ser mayor a 0.")
        return value
    
    def get_training_time(self, obj):
        """Calculate training time in minutes."""
        duration = obj.duration
        if duration is None:
            return 0
        return int(duration / 60)  # Convert seconds to minutes


class TrainingJobCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating training jobs."""
    
    class Meta:
        model = TrainingJob
        fields = (
            'job_type', 'model_name', 'dataset_size', 'epochs', 'batch_size',
            'learning_rate', 'config_params'
        )
    
    def validate_job_type(self, value):
        valid_types = ['regression', 'vision', 'incremental']
        if value not in valid_types:
            raise serializers.ValidationError(f"Tipo de trabajo inválido. Use: {', '.join(valid_types)}")
        return value
    
    def validate_model_name(self, value):
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError("El nombre del modelo no puede estar vacío.")
        return value.strip()


class TrainingJobStatusSerializer(serializers.ModelSerializer):
    """Simplified serializer for job status."""
    duration_formatted = serializers.ReadOnlyField()
    is_active = serializers.ReadOnlyField()
    created_by_username = serializers.CharField(source=CREATED_BY_USERNAME_SOURCE, read_only=True)
    
    class Meta:
        model = TrainingJob
        fields = (
            'id', 'job_id', 'job_type', 'status', 'created_by_username',
            'model_name', 'progress_percentage', 'created_at', 'started_at',
            'completed_at', 'duration_formatted', 'is_active'
        )


class AutoTrainConfigSerializer(serializers.Serializer):
    """
    Basic configuration for triggering automatic training.
    """
    epochs = serializers.IntegerField(required=False, min_value=1, max_value=500, default=50)
    batch_size = serializers.IntegerField(required=False, min_value=1, max_value=128, default=16)
    learning_rate = serializers.FloatField(required=False, min_value=1e-6, max_value=1.0, default=1e-4)
    model_type = serializers.CharField(required=False, default='hybrid')

    def validate_model_type(self, value: str) -> str:
        value = value or 'hybrid'
        allowed = {'hybrid'}
        if value not in allowed:
            raise serializers.ValidationError(f"Tipo de modelo inválido. Opciones permitidas: {', '.join(sorted(allowed))}.")
        return value


class ModelMetricsSerializer(serializers.ModelSerializer):
    """Serializer for model metrics."""
    accuracy_percentage = serializers.ReadOnlyField()
    training_time_formatted = serializers.ReadOnlyField()
    performance_summary = serializers.ReadOnlyField()
    dataset_summary = serializers.ReadOnlyField()
    model_summary = serializers.ReadOnlyField()
    comparison_with_previous = serializers.SerializerMethodField()
    created_by_username = serializers.CharField(source=CREATED_BY_USERNAME_SOURCE, read_only=True)
    
    class Meta:
        model = ModelMetrics
        fields = [
            'id', 'model_name', 'model_type', 'target', 'version',
            'created_by', 'created_by_username',
            'metric_type', 'mae', 'mse', 'rmse', 'r2_score', 'mape',
            'additional_metrics', 'dataset_size', 'train_size',
            'validation_size', 'test_size', 'epochs', 'batch_size',
            'learning_rate', 'model_params', 'training_time_seconds',
            'inference_time_ms', 'stability_score', 'knowledge_retention',
            'notes', 'is_best_model', 'is_production_model',
            'created_at', 'updated_at',
            # Calculated fields
            'accuracy_percentage', 'training_time_formatted',
            'performance_summary', 'dataset_summary', 'model_summary',
            'comparison_with_previous'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_comparison_with_previous(self, obj):
        """Get comparison with previous version."""
        try:
            comparison = obj.get_comparison_with_previous()
            return comparison if comparison is not None else {}
        except AttributeError:
            # If method doesn't exist, return empty dict
            return {}


class ModelMetricsListSerializer(serializers.ModelSerializer):
    """Simplified serializer for model metrics listing."""
    accuracy_percentage = serializers.ReadOnlyField()
    training_time_formatted = serializers.ReadOnlyField()
    created_by_username = serializers.CharField(source=CREATED_BY_USERNAME_SOURCE, read_only=True)
    
    class Meta:
        model = ModelMetrics
        fields = [
            'id', 'model_name', 'model_type', 'target', 'version',
            'metric_type', 'mae', 'rmse', 'r2_score', 'accuracy_percentage',
            'training_time_formatted', 'is_best_model', 'is_production_model',
            'created_by_username', 'created_at'
        ]


class ModelMetricsCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating model metrics."""
    
    class Meta:
        model = ModelMetrics
        fields = [
            'model_name', 'model_type', 'target', 'version',
            'metric_type', 'mae', 'mse', 'rmse',
            'r2_score', 'mape', 'additional_metrics', 'dataset_size',
            'train_size', 'validation_size', 'test_size', 'epochs',
            'batch_size', 'learning_rate', 'model_params',
            'training_time_seconds', 'inference_time_ms',
            'stability_score', 'knowledge_retention', 'notes',
            'is_best_model', 'is_production_model'
        ]
    
    def validate(self, data):
        """Validate serializer data."""
        errors = []
        
        # Validate that dataset_size equals the sum of train, validation and test
        dataset_size = data.get('dataset_size', 0)
        train_size = data.get('train_size', 0)
        validation_size = data.get('validation_size', 0)
        test_size = data.get('test_size', 0)
        
        if dataset_size != (train_size + validation_size + test_size):
            errors.append("El tamaño del dataset debe ser igual a la suma de train_size + validation_size + test_size")
        
        # Validate main metrics
        r2_score = data.get('r2_score')
        if r2_score is not None and (r2_score < 0 or r2_score > 1):
            errors.append("R² score debe estar entre 0 y 1")
        
        mae = data.get('mae')
        if mae is not None and mae < 0:
            errors.append("MAE debe ser mayor o igual a 0")
        
        mse = data.get('mse')
        if mse is not None and mse < 0:
            errors.append("MSE debe ser mayor o igual a 0")
        
        rmse = data.get('rmse')
        if rmse is not None and rmse < 0:
            errors.append("RMSE debe ser mayor o igual a 0")
        
        if errors:
            raise serializers.ValidationError(errors)
        
        return data


class ModelMetricsUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating model metrics."""
    
    class Meta:
        model = ModelMetrics
        fields = [
            'mae', 'mse', 'rmse', 'r2_score', 'mape', 'additional_metrics',
            'training_time_seconds', 'inference_time_ms', 'stability_score',
            'knowledge_retention', 'notes', 'is_best_model', 'is_production_model'
        ]
    
    def _validate_metric_value(self, value: float, metric_name: str, min_value: float = None, max_value: float = None) -> str | None:
        """Validate a single metric value. Returns error message or None."""
        if value is None:
            return None
        
        if min_value is not None and value < min_value:
            return f"{metric_name} debe ser mayor o igual a {min_value}"
        
        if max_value is not None and value > max_value:
            return f"{metric_name} debe ser menor o igual a {max_value}"
        
        return None
    
    def validate(self, data):
        """Validate serializer data."""
        errors = []
        
        # Validate main metrics
        r2_error = self._validate_metric_value(data.get('r2_score'), "R² score", min_value=0, max_value=1)
        if r2_error:
            errors.append(r2_error)
        
        mae_error = self._validate_metric_value(data.get('mae'), "MAE", min_value=0)
        if mae_error:
            errors.append(mae_error)
        
        mse_error = self._validate_metric_value(data.get('mse'), "MSE", min_value=0)
        if mse_error:
            errors.append(mse_error)
        
        rmse_error = self._validate_metric_value(data.get('rmse'), "RMSE", min_value=0)
        if rmse_error:
            errors.append(rmse_error)
        
        if errors:
            raise serializers.ValidationError(errors)
        
        return data


class ModelMetricsStatsSerializer(serializers.Serializer):
    """Serializer for model metrics statistics."""
    total_models = serializers.IntegerField()
    models_by_type = serializers.DictField()
    models_by_target = serializers.DictField()
    best_models_count = serializers.IntegerField()
    production_models_count = serializers.IntegerField()
    average_r2_score = serializers.FloatField()
    best_r2_score = serializers.FloatField()
    worst_r2_score = serializers.FloatField()
    recent_models = serializers.ListField()


class ModelPerformanceTrendSerializer(serializers.Serializer):
    """Serializer for model performance trend."""
    model_name = serializers.CharField()
    target = serializers.CharField()
    metric_type = serializers.CharField()
    trend_data = serializers.ListField()
    current_performance = serializers.DictField()
    improvement_trend = serializers.CharField()


class ModelComparisonSerializer(serializers.Serializer):
    """Serializer for model comparison."""
    model_a = ModelMetricsSerializer()
    model_b = ModelMetricsSerializer()
    comparison_metrics = serializers.DictField()
    winner = serializers.CharField()
    improvement_percentage = serializers.FloatField()

