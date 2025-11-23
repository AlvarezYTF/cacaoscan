"""
Report generation services module.
"""
from .excel import ExcelAgricultoresService, ExcelUsuariosService, ExcelAnalisisService
from .pdf_generator import CacaoReportPDFGenerator
from .report_generation_service import ReportGenerationService
from .report_management_service import ReportManagementService

# Backward compatibility: Create a combined service that delegates to individual services
from api.services.base import BaseService, ServiceResult


class ReportService(BaseService):
    """
    Combined report service for backward compatibility.
    Delegates to individual specialized services.
    """
    
    def __init__(self):
        super().__init__()
        self.generation_service = ReportGenerationService()
        self.management_service = ReportManagementService()
    
    # Generation methods
    def generate_analysis_report(self, user, report_data) -> ServiceResult:
        """Delegates to ReportGenerationService."""
        return self.generation_service.generate_analysis_report(user, report_data)
    
    # Management methods
    def get_user_reports(self, user, page=1, page_size=20, filters=None) -> ServiceResult:
        """Delegates to ReportManagementService."""
        return self.management_service.get_user_reports(user, page, page_size, filters)
    
    def get_report_details(self, report_id, user) -> ServiceResult:
        """Delegates to ReportManagementService."""
        return self.management_service.get_report_details(report_id, user)
    
    def delete_report(self, report_id, user) -> ServiceResult:
        """Delegates to ReportManagementService."""
        return self.management_service.delete_report(report_id, user)
    
    def get_report_statistics(self, user, filters=None) -> ServiceResult:
        """Delegates to ReportManagementService."""
        return self.management_service.get_report_statistics(user, filters)

__all__ = [
    'ExcelAgricultoresService',
    'ExcelUsuariosService',
    'ExcelAnalisisService',
    'CacaoReportPDFGenerator',
    'ReportGenerationService',
    'ReportManagementService',
    'ReportService',  # For backward compatibility
]

