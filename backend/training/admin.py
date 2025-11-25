"""
Configuración del admin de Django para la app de entrenamiento.
"""
from django.contrib import admin
from .models import TrainingJob, ModelMetrics


@admin.register(TrainingJob)
class TrainingJobAdmin(admin.ModelAdmin):
    """Admin para trabajos de entrenamiento."""
    list_display = ('job_id', 'job_type', 'model_name', 'status', 'created_by', 'created_at', 'duration_formatted')
    list_filter = ('job_type', 'status', 'created_at')
    search_fields = ('job_id', 'model_name', 'created_by__username')
    readonly_fields = ('job_id', 'created_at', 'started_at', 'completed_at', 'duration', 'duration_formatted', 'is_active')
    date_hierarchy = 'created_at'


@admin.register(ModelMetrics)
class ModelMetricsAdmin(admin.ModelAdmin):
    """Admin para métricas de modelos."""
    list_display = ('model_name', 'model_type', 'target', 'version', 'metric_type', 'r2_score', 'rmse', 'is_best_model', 'is_production_model', 'created_at')
    list_filter = ('model_type', 'target', 'metric_type', 'is_best_model', 'is_production_model', 'created_at')
    search_fields = ('model_name', 'version', 'created_by__username')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Información del Modelo', {
            'fields': ('model_name', 'model_type', 'target', 'version', 'created_by')
        }),
        ('Tipo de Métrica', {
            'fields': ('metric_type',)
        }),
        ('Métricas Principales', {
            'fields': ('mae', 'mse', 'rmse', 'r2_score', 'mape')
        }),
        ('Métricas Adicionales', {
            'fields': ('additional_metrics',),
            'classes': ('collapse',)
        }),
        ('Dataset', {
            'fields': ('dataset_size', 'train_size', 'validation_size', 'test_size')
        }),
        ('Parámetros de Entrenamiento', {
            'fields': ('epochs', 'batch_size', 'learning_rate', 'model_params')
        }),
        ('Tiempos', {
            'fields': ('training_time_seconds', 'inference_time_ms')
        }),
        ('Métricas de Calidad', {
            'fields': ('stability_score', 'knowledge_retention')
        }),
        ('Flags', {
            'fields': ('is_best_model', 'is_production_model')
        }),
        ('Notas', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Optimizar queryset con select_related."""
        return super().get_queryset(request).select_related('created_by')
