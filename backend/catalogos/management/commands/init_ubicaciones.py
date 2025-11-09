from django.core.management.base import BaseCommand
from catalogos.models import Departamento, Municipio


class Command(BaseCommand):
    help = 'Inicializa los departamentos y municipios de Colombia.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Iniciando inicialización de ubicaciones de Colombia...'))

        # Datos iniciales de departamentos y sus municipios
        # Solo incluimos algunos departamentos importantes como ejemplo
        ubicaciones_data = [
            {
                'codigo': '05',
                'nombre': 'Antioquia',
                'municipios': [
                    {'codigo': '001', 'nombre': 'Medellín'},
                    {'codigo': '002', 'nombre': 'Bello'},
                    {'codigo': '003', 'nombre': 'Itagüí'},
                    {'codigo': '004', 'nombre': 'Envigado'},
                    {'codigo': '005', 'nombre': 'Rionegro'},
                ]
            },
            {
                'codigo': '11',
                'nombre': 'Bogotá D.C.',
                'municipios': [
                    {'codigo': '001', 'nombre': 'Bogotá D.C.'},
                ]
            },
            {
                'codigo': '54',
                'nombre': 'Norte de Santander',
                'municipios': [
                    {'codigo': '001', 'nombre': 'Cúcuta'},
                    {'codigo': '002', 'nombre': 'Ocaña'},
                    {'codigo': '003', 'nombre': 'Pamplona'},
                ]
            },
            {
                'codigo': '13',
                'nombre': 'Bolívar',
                'municipios': [
                    {'codigo': '001', 'nombre': 'Cartagena'},
                    {'codigo': '002', 'nombre': 'Magangué'},
                    {'codigo': '003', 'nombre': 'Mompós'},
                ]
            },
            {
                'codigo': '76',
                'nombre': 'Valle del Cauca',
                'municipios': [
                    {'codigo': '001', 'nombre': 'Cali'},
                    {'codigo': '002', 'nombre': 'Palmira'},
                    {'codigo': '003', 'nombre': 'Buenaventura'},
                    {'codigo': '004', 'nombre': 'Yumbo'},
                ]
            },
            {
                'codigo': '95',
                'nombre': 'Guaviare',
                'municipios': [
                    {'codigo': '001', 'nombre': 'San José del Guaviare'},
                    {'codigo': '002', 'nombre': 'Calamar'},
                    {'codigo': '003', 'nombre': 'El Retorno'},
                    {'codigo': '004', 'nombre': 'Miraflores'},
                ]
            },
        ]

        # Crear departamentos y municipios
        for dept_data in ubicaciones_data:
            municipios_data = dept_data.pop('municipios')
            
            # Crear o obtener el departamento
            departamento, created = Departamento.objects.get_or_create(
                codigo=dept_data['codigo'],
                defaults={
                    'nombre': dept_data['nombre']
                }
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'" Departamento creado: {departamento.codigo} - {departamento.nombre}'))
            else:
                self.stdout.write(self.style.WARNING(f'- Departamento ya existe: {departamento.codigo} - {departamento.nombre}'))
            
            # Crear municipios del departamento
            for mun_data in municipios_data:
                municipio, mun_created = Municipio.objects.get_or_create(
                    departamento=departamento,
                    codigo=mun_data['codigo'],
                    defaults={
                        'nombre': mun_data['nombre']
                    }
                )
                
                if mun_created:
                    self.stdout.write(self.style.SUCCESS(f'  " Municipio creado: {municipio.nombre}'))
                else:
                    self.stdout.write(self.style.WARNING(f'  - Municipio ya existe: {municipio.nombre}'))

        self.stdout.write(self.style.SUCCESS('\n" Inicialización de ubicaciones completada'))


