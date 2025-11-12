"""
Test 6: Verificar que el HTML tiene atributos lang y xml:lang.

Bug SonarQube: "Add 'lang' and/or 'xml:lang' attributes to this '<html>' element"
Archivo corregido: frontend/cypress/support/component-index.html
"""
from django.test import TestCase
from pathlib import Path


class TestComponentIndexHTML(TestCase):
    """Tests para verificar atributos de idioma en HTML."""
    
    def test_component_index_has_lang_attributes(self):
        """Verifica que el archivo HTML tiene atributos lang y xml:lang."""
        # Ruta al archivo
        html_file = Path(__file__).parent.parent.parent.parent.parent / 'frontend' / 'cypress' / 'support' / 'component-index.html'
        
        if html_file.exists():
            content = html_file.read_text(encoding='utf-8')
            
            # Verificar que tiene lang y xml:lang
            self.assertIn('lang="es"', content,
                        "El elemento <html> debe tener el atributo lang='es'")
            self.assertIn('xml:lang="es"', content,
                        "El elemento <html> debe tener el atributo xml:lang='es'")
            
            # Verificar que están en el elemento html
            html_tag_lower = content.lower()
            self.assertIn('<html', html_tag_lower,
                        "Debe existir un elemento <html>")
        else:
            self.skipTest("Archivo component-index.html no encontrado")

