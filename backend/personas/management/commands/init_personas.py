"""
Comando para inicializar datos básicos de la app personas.
"""
from django.core.management.base import BaseCommand
from personas.models import TipoDocumento, Genero


class Command(BaseCommand):
    help = 'Inicializa datos básicos para la app personas (tipos de documento y géneros)'

    def handle(self, *args, **options):
        # Crear tipos de documento
        tipos_documento = [
            {'codigo': 'CC', 'nombre': 'Cédula de Ciudadanía'},
            {'codigo': 'CE', 'nombre': 'Cédula de Extranjería'},
            {'codigo': 'PA', 'nombre': 'Pasaporte'},
            {'codigo': 'TI', 'nombre': 'Tarjeta de Identidad'},
            {'codigo': 'RC', 'nombre': 'Registro Civil'},
        ]
        
        for tipo in tipos_documento:
            obj, created = TipoDocumento.objects.get_or_create(
                codigo=tipo['codigo'],
                defaults={'nombre': tipo['nombre']}
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Tipo de documento creado: {obj.codigo} - {obj.nombre}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'⊘ Tipo de documento ya existe: {obj.codigo} - {obj.nombre}')
                )
        
        # Crear géneros
        generos = [
            {'codigo': 'M', 'nombre': 'Masculino'},
            {'codigo': 'F', 'nombre': 'Femenino'},
            {'codigo': 'O', 'nombre': 'Otro'},
        ]
        
        for genero in generos:
            obj, created = Genero.objects.get_or_create(
                codigo=genero['codigo'],
                defaults={'nombre': genero['nombre']}
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Género creado: {obj.codigo} - {obj.nombre}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'⊘ Género ya existe: {obj.codigo} - {obj.nombre}')
                )
        
        self.stdout.write(self.style.SUCCESS('\n✓ Inicialización de personas completada'))

