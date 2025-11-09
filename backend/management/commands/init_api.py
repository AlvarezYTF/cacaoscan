"""
Comando Django para inicializar la API de CacaoScan.
"""
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from pathlib import Path

from ml.prediction.predict import load_artifacts
from ml.utils.logs import get_ml_logger


logger = get_ml_logger("cacaoscan.ml.commands")


class Command(BaseCommand):
    help = 'Inicializa la API de CacaoScan cargando modelos y verificando configuración'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--skip-models',
            action='store_true',
            help='Saltar carga de modelos (solo verificar configuración)'
        )
        parser.add_argument(
            '--check-artifacts',
            action='store_true',
            help='Verificar que todos los artefactos estén disponibles'
        )
    
    def handle(self, *args, **options):
        """Maneja la ejecución del comando."""
        self.stdout.write(
            self.style.SUCCESS("Inicializando API de CacaoScan...")
        )
        
        try:
            # 1. Verificar configuración
            self._check_configuration()
            
            # 2. Verificar directorios
            self._check_directories()
            
            # 3. Verificar artefactos si se solicita
            if options['check_artifacts']:
                self._check_artifacts()
            
            # 4. Cargar modelos si no se saltan
            if not options['skip_models']:
                self._load_models()
            
            # 5. Mostrar información de la API
            self._show_api_info()
            
            self.stdout.write(
                self.style.SUCCESS("... API inicializada exitosamente!")
            )
            
        except Exception as e:
            raise CommandError(f"Error inicializando API: {e}")
    
    def _check_configuration(self):
        """Verifica la configuración de Django."""
        self.stdout.write("Verificando configuración...")
        
        # Verificar settings
        required_settings = [
            'MEDIA_ROOT',
            'MEDIA_URL',
            'DEBUG',
            'ALLOWED_HOSTS'
        ]
        
        for setting in required_settings:
            if not hasattr(settings, setting):
                raise CommandError(f"Setting requerido no encontrado: {setting}")
        
        self.stdout.write("  " Configuración Django OK")
    
    def _check_directories(self):
        """Verifica que los directorios necesarios existan."""
        self.stdout.write("Verificando directorios...")
        
        # Directorios requeridos
        required_dirs = [
            settings.MEDIA_ROOT,
            Path(settings.MEDIA_ROOT) / "cacao_images",
            Path(settings.MEDIA_ROOT) / "cacao_images" / "crops_runtime",
            Path(settings.MEDIA_ROOT) / "datasets",
            Path(settings.BASE_DIR) / "ml" / "artifacts" / "regressors",
            Path(settings.BASE_DIR) / "logs"
        ]
        
        for dir_path in required_dirs:
            if not dir_path.exists():
                self.stdout.write(
                    self.style.WARNING(f"  [WARN] Directorio faltante: {dir_path}")
                )
                dir_path.mkdir(parents=True, exist_ok=True)
                self.stdout.write(f"  " Creado: {dir_path}")
            else:
                self.stdout.write(f"  " Existe: {dir_path}")
        
        self.stdout.write("  " Directorios OK")
    
    def _check_artifacts(self):
        """Verifica que los artefactos de ML estén disponibles."""
        self.stdout.write("Verificando artefactos de ML...")
        
        artifacts_dir = Path(settings.BASE_DIR) / "ml" / "artifacts" / "regressors"
        
        # Modelos requeridos
        required_models = ['alto.pt', 'ancho.pt', 'grosor.pt', 'peso.pt']
        required_scalers = ['alto_scaler.pkl', 'ancho_scaler.pkl', 'grosor_scaler.pkl', 'peso_scaler.pkl']
        
        all_found = True
        
        # Verificar modelos
        for model_file in required_models:
            model_path = artifacts_dir / model_file
            if model_path.exists():
                self.stdout.write(f"  " Modelo encontrado: {model_file}")
            else:
                self.stdout.write(
                    self.style.WARNING(f"  [WARN] Modelo faltante: {model_file}")
                )
                all_found = False
        
        # Verificar escaladores
        for scaler_file in required_scalers:
            scaler_path = artifacts_dir / scaler_file
            if scaler_path.exists():
                self.stdout.write(f"  " Escalador encontrado: {scaler_file}")
            else:
                self.stdout.write(
                    self.style.WARNING(f"  [WARN] Escalador faltante: {scaler_file}")
                )
                all_found = False
        
        if all_found:
            self.stdout.write("  " Todos los artefactos encontrados")
        else:
            self.stdout.write(
                self.style.WARNING("  [WARN] Algunos artefactos faltan. Ejecutar entrenamiento primero.")
            )
    
    def _load_models(self):
        """Carga los modelos de ML."""
        self.stdout.write("Cargando modelos de ML...")
        
        try:
            success = load_artifacts()
            
            if success:
                self.stdout.write("  " Modelos cargados exitosamente")
            else:
                self.stdout.write(
                    self.style.WARNING("  [WARN] Error cargando modelos")
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.WARNING(f"  [WARN] Error cargando modelos: {e}")
            )
    
    def _show_api_info(self):
        """Muestra información de la API."""
        self.stdout.write("\n" + "="*50)
        self.stdout.write("INFORMACI"N DE LA API")
        self.stdout.write("="*50)
        
        self.stdout.write(f"URLs disponibles:")
        self.stdout.write(f"  - Swagger UI: http://localhost:8000/swagger/")
        self.stdout.write(f"  - ReDoc: http://localhost:8000/redoc/")
        self.stdout.write(f"  - API Base: http://localhost:8000/api/v1/")
        
        self.stdout.write(f"\nEndpoints principales:")
        self.stdout.write(f"  - POST /api/v1/scan/measure/ - Medir grano de cacao")
        self.stdout.write(f"  - GET /api/v1/models/status/ - Estado de modelos")
        self.stdout.write(f"  - POST /api/v1/models/load/ - Cargar modelos")
        self.stdout.write(f"  - GET /api/v1/dataset/validation/ - Validar dataset")
        
        self.stdout.write(f"\nDirectorios importantes:")
        self.stdout.write(f"  - Media: {settings.MEDIA_ROOT}")
        self.stdout.write(f"  - Logs: {Path(settings.BASE_DIR) / 'logs'}")
        self.stdout.write(f"  - Artefactos: {Path(settings.BASE_DIR) / 'ml' / 'artifacts'}")
        
        self.stdout.write(f"\nPara probar la API:")
        self.stdout.write(f"  - python example_api_usage.py")
        self.stdout.write(f"  - curl -X POST -F 'image=@test.jpg' http://localhost:8000/api/v1/scan/measure/")
        
        self.stdout.write("="*50)


