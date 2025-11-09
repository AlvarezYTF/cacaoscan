"""
URLs para el módulo de reportes.
"""
from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    # Endpoints de generación de reportes PDF
    path('quality/', views.GenerateQualityReportView.as_view(), name='quality-report'),
    path('defects/', views.GenerateDefectsReportView.as_view(), name='defects-report'),
    path('performance/', views.GeneratePerformanceReportView.as_view(), name='performance-report'),
    
    # Endpoint de estadísticas para preview
    path('stats/', views.ReportStatsView.as_view(), name='report-stats'),
]


