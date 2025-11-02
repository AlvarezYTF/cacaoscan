from django.core.management.base import BaseCommand
from catalogos.models import Tema, Parametro


class Command(BaseCommand):
    help = 'Inicializa los temas y parÃ¡metros bÃ¡sicos del sistema.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Iniciando inicializaciÃ³n de catÃ¡logos...'))

        # Datos iniciales: Temas y ParÃ¡metros
        temas_data = [
            {
                'codigo': 'TIPO_DOC',
                'nombre': 'Tipo de Documento',
                'descripcion': 'Tipos de documentos de identificaciÃ³n vÃ¡lidos en Colombia',
                'parametros': [
                    {'codigo': 'CC', 'nombre': 'CÃ©dula de CiudadanÃ­a', 'descripcion': 'Documento nacional de identidad para mayores de edad'},
                    {'codigo': 'CE', 'nombre': 'CÃ©dula de ExtranjerÃ­a', 'descripcion': 'Documento para extranjeros residentes en Colombia'},
                    {'codigo': 'PA', 'nombre': 'Pasaporte', 'descripcion': 'Documento de viaje internacional'},
                    {'codigo': 'TI', 'nombre': 'Tarjeta de Identidad', 'descripcion': 'Documento para menores de edad'},
                    {'codigo': 'RC', 'nombre': 'Registro Civil', 'descripcion': 'Documento de registro de nacimiento'},
                ]
            },
            {
                'codigo': 'SEXO',
                'nombre': 'Sexo',
                'descripcion': 'Opciones de gÃ©nero/sexo disponibles',
                'parametros': [
                    {'codigo': 'M', 'nombre': 'Masculino', 'descripcion': 'Sexo masculino'},
                    {'codigo': 'F', 'nombre': 'Femenino', 'descripcion': 'Sexo femenino'},
                    {'codigo': 'O', 'nombre': 'Otro', 'descripcion': 'Otro gÃ©nero'},
                ]
            },
            {
                'codigo': 'ESTADO_CIVIL',
                'nombre': 'Estado Civil',
                'descripcion': 'Estados civiles de las personas',
                'parametros': [
                    {'codigo': 'SOL', 'nombre': 'Soltero', 'descripcion': 'Persona no casada'},
                    {'codigo': 'CAS', 'nombre': 'Casado', 'descripcion': 'Persona casada'},
                    {'codigo': 'DIV', 'nombre': 'Divorciado', 'descripcion': 'Persona divorciada'},
                    {'codigo': 'VIU', 'nombre': 'Viudo', 'descripcion': 'Persona viuda'},
                    {'codigo': 'UNL', 'nombre': 'UniÃ³n Libre', 'descripcion': 'Persona en uniÃ³n libre'},
                ]
            },
            {
                'codigo': 'GENETICA',
                'nombre': 'GenÃ©tica',
                'descripcion': 'Tipos de genÃ©tica del cacao',
                'parametros': [
                    {'codigo': 'FOR', 'nombre': 'Forastero', 'descripcion': 'Tipo de cacao Forastero'},
                    {'codigo': 'TRI', 'nombre': 'Trinitario', 'descripcion': 'Tipo de cacao Trinitario'},
                    {'codigo': 'CRI', 'nombre': 'Criollo', 'descripcion': 'Tipo de cacao Criollo'},
                    {'codigo': 'NAC', 'nombre': 'Nacional', 'descripcion': 'Cacao Nacional'},
                ]
            },
        ]

        # Crear temas y parÃ¡metros
        for tema_data in temas_data:
            parametros_data = tema_data.pop('parametros')
            
            # Crear o obtener el tema
            tema, created = Tema.objects.get_or_create(
                codigo=tema_data['codigo'],
                defaults={
                    'nombre': tema_data['nombre'],
                    'descripcion': tema_data['descripcion'],
                    'activo': True
                }
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'âœ“ Tema creado: {tema.codigo} - {tema.nombre}'))
            else:
                self.stdout.write(self.style.WARNING(f'â€¢ Tema ya existe: {tema.codigo} - {tema.nombre}'))
            
            # Crear parÃ¡metros del tema
            for param_data in parametros_data:
                parametro, param_created = Parametro.objects.get_or_create(
                    tema=tema,
                    codigo=param_data['codigo'],
                    defaults={
                        'nombre': param_data['nombre'],
                        'descripcion': param_data.get('descripcion', ''),
                        'activo': True
                    }
                )
                
                if param_created:
                    self.stdout.write(self.style.SUCCESS(f'  âœ“ ParÃ¡metro creado: {parametro.codigo} - {parametro.nombre}'))
                else:
                    self.stdout.write(self.style.WARNING(f'  â€¢ ParÃ¡metro ya existe: {parametro.codigo}'))

        self.stdout.write(self.style.SUCCESS('\nâœ“ InicializaciÃ³n de catÃ¡logos completada'))


