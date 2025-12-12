"""
URLs para el módulo de reportes.
"""
from django.urls import path
# Import from the views package which exports views from both views.py and views/ subdirectory
from . import views

app_name = 'reports'

urlpatterns = [
    # Endpoints de generación de reportes PDF
    path('reports/quality/', views.GenerateQualityReportView.as_view(), name='quality-report'),
    path('reports/defects/', views.GenerateDefectsReportView.as_view(), name='defects-report'),
    path('reports/performance/', views.GeneratePerformanceReportView.as_view(), name='performance-report'),
    
    # Endpoint de estadísticas para preview
    path('reports/stats/', views.ReportStatsView.as_view(), name='report-stats'),
]


