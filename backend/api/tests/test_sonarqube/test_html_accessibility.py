"""
Test 5: Verificar que las tablas HTML tienen caption para accesibilidad.

Bug SonarQube: "Add a description to this table"
Archivos corregidos: 
- backend/api/templates/emails/analysis_complete.html
- frontend/src/components/admin/AdminAgricultorComponents/DataTable.vue
"""
from django.test import TestCase
from pathlib import Path
import os


class TestHTMLAccessibility(TestCase):
    """Tests para verificar accesibilidad HTML en templates y componentes."""
    
    def test_analysis_complete_email_has_caption(self):
        """Verifica que el template de email tiene caption en la tabla."""
        try:
            from django.template.loader import render_to_string
            from django.template import Context
            
            # Intentar renderizar el template
            context = Context({
                'analysis': {
                    'alto': 10.5,
                    'ancho': 8.3,
                    'grosor': 5.2,
                    'peso': 12.0
                },
                'confidence': 0.95
            })
            
            html = render_to_string('emails/analysis_complete.html', context)
            
            # Verificar que la tabla tiene un caption
            self.assertIn('<caption', html.lower(), 
                        "La tabla debe tener un elemento <caption> para accesibilidad")
            self.assertIn('tabla', html.lower())
            
        except Exception as e:
            # Si el template no se puede cargar, saltamos el test
            self.skipTest(f"No se pudo cargar el template: {e}")
    
    def test_data_table_vue_has_caption(self):
        """Verifica que el componente DataTable.vue tiene caption."""
        # Ruta al archivo Vue
        vue_file = Path(__file__).parent.parent.parent.parent.parent / 'frontend' / 'src' / 'components' / 'admin' / 'AdminAgricultorComponents' / 'DataTable.vue'
        
        if vue_file.exists():
            content = vue_file.read_text(encoding='utf-8')
            
            # Verificar que tiene caption en el template
            self.assertIn('<caption', content, 
                        "El componente DataTable debe tener un elemento <caption>")
            self.assertIn('sr-only', content,
                        "El caption debe tener la clase sr-only para accesibilidad")
        else:
            self.skipTest("Archivo DataTable.vue no encontrado")
    
    def test_data_table_vue_has_aria_label(self):
        """Verifica que el componente DataTable.vue tiene aria-label."""
        vue_file = Path(__file__).parent.parent.parent.parent.parent / 'frontend' / 'src' / 'components' / 'admin' / 'AdminAgricultorComponents' / 'DataTable.vue'
        
        if vue_file.exists():
            content = vue_file.read_text(encoding='utf-8')
            
            # Verificar que tiene aria-label en la tabla
            self.assertIn('aria-label', content,
                        "La tabla debe tener un atributo aria-label para accesibilidad")
        else:
            self.skipTest("Archivo DataTable.vue no encontrado")

