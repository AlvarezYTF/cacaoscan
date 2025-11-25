"""
Excel report generation module for CacaoScan.
Provides specialized Excel generators following SRP.
"""
from .excel_base import ExcelBaseGenerator
from .excel_agricultores import ExcelAgricultoresGenerator
from .excel_usuarios import ExcelUsuariosGenerator
from .excel_analisis import ExcelAnalisisGenerator

# Backward compatibility: Create a combined generator that delegates to specialized generators
class CacaoReportExcelGenerator:
    """
    Combined Excel generator for backward compatibility.
    Delegates to individual specialized generators.
    """
    
    def __init__(self):
        self.agricultores_generator = ExcelAgricultoresGenerator()
        self.usuarios_generator = ExcelUsuariosGenerator()
        self.analisis_generator = ExcelAnalisisGenerator()
    
    # Farmers report
    def generate_farmers_report(self) -> bytes:
        """Delegates to ExcelAgricultoresGenerator."""
        return self.agricultores_generator.generate_farmers_report()
    
    # Users report
    def generate_users_report(self) -> bytes:
        """Delegates to ExcelUsuariosGenerator."""
        return self.usuarios_generator.generate_users_report()
    
    # Analysis reports
    def generate_quality_report(self, user, filtros=None) -> bytes:
        """Delegates to ExcelAnalisisGenerator."""
        return self.analisis_generator.generate_quality_report(user, filtros)
    
    def generate_finca_report(self, finca_id, user, filtros=None) -> bytes:
        """Delegates to ExcelAnalisisGenerator."""
        return self.analisis_generator.generate_finca_report(finca_id, user, filtros)
    
    def generate_audit_report(self, user, filtros=None) -> bytes:
        """Delegates to ExcelAnalisisGenerator."""
        return self.analisis_generator.generate_audit_report(user, filtros)
    
    def generate_custom_report(self, user, tipo_reporte, parametros, filtros=None) -> bytes:
        """Delegates to ExcelAnalisisGenerator."""
        return self.analisis_generator.generate_custom_report(user, tipo_reporte, parametros, filtros)

__all__ = [
    'ExcelBaseGenerator',
    'ExcelAgricultoresGenerator',
    'ExcelUsuariosGenerator',
    'ExcelAnalisisGenerator',
    'CacaoReportExcelGenerator',  # For backward compatibility
]

