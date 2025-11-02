"""
URLs para el mÃ³dulo de reportes.
"""
from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    # Endpoints de generaciÃ³n de reportes PDF
    path('quality/', views.GenerateQualityReportView.as_view(), name='quality-report'),
    path('defects/', views.GenerateDefectsReportView.as_view(), name='defects-report'),
    path('performance/', views.GeneratePerformanceReportView.as_view(), name='performance-report'),
    
    # Endpoint de estadÃ­sticas para preview
    path('stats/', views.ReportStatsView.as_view(), name='report-stats'),
]


