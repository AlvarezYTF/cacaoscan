"""
Upload and creation views for batch analysis in CacaoScan.
Handles lote/finca creation and image upload for batch processing.
"""
import logging
import time
from pathlib import Path
from datetime import datetime, date
from django.db import transaction, connection as db_conn
from django.conf import settings
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from api.utils.model_imports import get_models_safely
from api.tasks.image_tasks import process_batch_analysis_task
from api.serializers import ErrorResponseSerializer
from api.views.mixins import AdminPermissionMixin

# Import models safely
models = get_models_safely({
    'Lote': 'fincas_app.models.Lote',
    'Finca': 'fincas_app.models.Finca',
})
Lote = models['Lote']
Finca = models['Finca']

logger = logging.getLogger("cacaoscan.api")


class BatchAnalysisView(AdminPermissionMixin, APIView):
    """
    Endpoint for batch analysis of lotes with multiple images.
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    @swagger_auto_schema(
        operation_description="Procesa un lote con múltiples imágenes usando ML",
        operation_summary="Análisis batch de lote",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'name': openapi.Schema(type=openapi.TYPE_STRING, description="Nombre del lote"),
                'farm': openapi.Schema(type=openapi.TYPE_STRING, description="Nombre de la finca"),
                'originPlace': openapi.Schema(type=openapi.TYPE_STRING, description="Lugar de origen"),
                'genetics': openapi.Schema(type=openapi.TYPE_STRING, description="Genética/variedad"),
                'collectionDate': openapi.Schema(type=openapi.TYPE_STRING, format='date', description="Fecha de recolección"),
                'origin': openapi.Schema(type=openapi.TYPE_STRING, description="Origen geográfico"),
                'notes': openapi.Schema(type=openapi.TYPE_STRING, description="Notas adicionales"),
                'images': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_FILE), description="Imágenes del lote"),
            },
            required=['name', 'farm', 'collectionDate', 'genetics', 'images']
        ),
        responses={
            202: openapi.Response(
                description="Análisis batch iniciado (procesamiento asíncrono)",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'task_id': openapi.Schema(type=openapi.TYPE_STRING, description="ID de la tarea Celery para seguimiento"),
                        'lote_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'total_images': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'status': openapi.Schema(type=openapi.TYPE_STRING, description="Estado: 'processing'"),
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                    }
                )
            ),
            400: ErrorResponseSerializer,
            401: ErrorResponseSerializer,
            500: ErrorResponseSerializer,
        },
        tags=['Análisis']
    )
    def post(self, request):
        """
        Processes a lote with multiple images using ML asynchronously.
        
        Returns immediately a task_id that can be used to check the status
        of processing via the endpoint GET /api/v1/tasks/{task_id}/status/
        """
        start_time = time.time()
        
        try:
            # 1. Validate input data
            name = request.data.get('name', '').strip()
            farm_name = request.data.get('farm', '').strip()
            genetics = request.data.get('genetics', '').strip()
            collection_date = request.data.get('collectionDate', '').strip()
            origin_place = request.data.get('originPlace', '').strip()
            origin = request.data.get('origin', '').strip()
            notes = request.data.get('notes', '').strip()
            
            # Validations
            if not name:
                return Response({
                    'error': 'El nombre del lote es requerido',
                    'status': 'error'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if not farm_name:
                return Response({
                    'error': 'La finca es requerida',
                    'status': 'error'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if not genetics:
                return Response({
                    'error': 'La genética es requerida',
                    'status': 'error'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if not collection_date:
                return Response({
                    'error': 'La fecha de recolección es requerida',
                    'status': 'error'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 2. Get or create finca
            finca = self._get_or_create_finca(request, farm_name, origin_place, origin)
            if not finca:
                logger.error(f"Error obteniendo/creando finca '{farm_name}' para usuario {request.user.username}")
                return Response({
                    'error': 'Error al obtener/crear la finca',
                    'status': 'error'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            logger.info(f"Finca obtenida/creada: ID={finca.id}, nombre={finca.nombre}, agricultor={finca.agricultor_id}")
            
            # 3. Get or create lote
            lote = self._get_or_create_lote(
                request, finca, name, genetics, collection_date, notes
            )
            if not lote:
                logger.error(f"Error obteniendo/creando lote '{name}' para finca_id={finca.id if finca else 'None'}")
                return Response({
                    'error': 'Error al obtener/crear el lote',
                    'status': 'error'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 4. Process images
            images = request.FILES.getlist('images')
            if not images:
                return Response({
                    'error': 'No se enviaron imágenes',
                    'status': 'error'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 5. Save images temporarily and prepare data for task
            media_root = Path(settings.MEDIA_ROOT)
            temp_dir = media_root / 'temp' / f'batch_{lote.id}_{int(time.time())}'
            temp_dir.mkdir(parents=True, exist_ok=True)
            
            images_data = []
            for idx, image_file in enumerate(images):
                try:
                    # Save image to temporary location
                    temp_path = temp_dir / f"{idx}_{image_file.name}"
                    with open(temp_path, 'wb+') as destination:
                        for chunk in image_file.chunks():
                            destination.write(chunk)
                    
                    images_data.append({
                        'file_name': image_file.name,
                        'file_size': image_file.size,
                        'file_type': image_file.content_type,
                        'temp_path': str(temp_path)
                    })
                except Exception as e:
                    logger.error(f"Error saving temporary image {idx}: {e}")
                    continue
            
            if not images_data:
                return Response({
                    'error': 'Error guardando imágenes temporalmente',
                    'status': 'error'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # 6. Enqueue Celery task
            task = process_batch_analysis_task.delay(
                user_id=request.user.id,
                lote_id=lote.id,
                images_data=images_data
            )
            
            logger.info(
                f"Batch analysis task enqueued - Task ID: {task.id}, "
                f"Lote ID: {lote.id}, Images: {len(images_data)}"
            )
            
            # 7. Return task_id immediately
            return Response({
                'task_id': task.id,
                'lote_id': lote.id,
                'lote_name': lote.identificador,
                'total_images': len(images_data),
                'status': 'processing',
                'message': 'Análisis batch iniciado. Use el task_id para consultar el estado.'
            }, status=status.HTTP_202_ACCEPTED)
            
        except Exception as e:
            logger.error(f"Error en análisis batch: {e}", exc_info=True)
            return Response({
                'error': f'Error procesando análisis batch: {str(e)}',
                'status': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _get_or_create_finca(self, request, farm_name, origin_place, origin):
        """Get or create finca."""
        try:
            # Search existing finca by name
            if self.is_admin_user(request.user):
                # Admin can see all fincas
                finca = Finca.objects.filter(nombre=farm_name).first()
            else:
                # Farmer only sees their fincas
                finca = Finca.objects.filter(nombre=farm_name, agricultor=request.user).first()
            
            if finca:
                # Verify finca actually exists in DB
                try:
                    finca_verificada = Finca.objects.get(id=finca.id)
                    logger.debug(f"Finca existente encontrada: ID={finca_verificada.id}, nombre={finca_verificada.nombre}, tabla={Finca._meta.db_table}")
                    return finca_verificada
                except Finca.DoesNotExist:
                    logger.warning(f"Finca con ID={finca.id} no existe en BD, creando nueva")
                    finca = None
            
            # Create new finca if doesn't exist
            # IMPORTANT: agricultor always must have a value, cannot be None
            with transaction.atomic():
                finca = Finca.objects.create(
                    nombre=farm_name,
                    agricultor=request.user,  # Always assign current user
                    ubicacion=origin_place if origin_place else 'No especificado',
                    municipio=origin_place if origin_place else 'No especificado',
                    departamento=origin if origin else 'No especificado',
                    hectareas=1.0,  # Default value
                    activa=True
                )
                
                # Verify it saved correctly by refreshing from DB
                finca.refresh_from_db()
                
                # Verify again that it exists in DB
                try:
                    finca_verificada = Finca.objects.get(id=finca.id)
                    logger.info(f"Finca '{farm_name}' creada para usuario {request.user.username} - ID: {finca_verificada.id}")
                    logger.debug(f"Finca guardada: tabla={Finca._meta.db_table}, agricultor_id={finca_verificada.agricultor_id}")
                    return finca_verificada
                except Finca.DoesNotExist:
                    logger.error(f"Finca creada pero no encontrada en BD después de refresh - ID: {finca.id}")
                    return None
            
        except Exception as e:
            logger.error(f"Error obteniendo/creando finca: {e}", exc_info=True)
            return None
    
    def _get_or_create_lote(self, request, finca, name, genetics, collection_date, notes):
        """Get or create lote."""
        try:
            # Search existing lote
            lote = Lote.objects.filter(
                finca=finca,
                identificador=name
            ).first()
            
            if lote:
                logger.debug(f"Lote existente encontrado: ID={lote.id}, identificador={lote.identificador}")
                return lote
            
            # Create new lote
            # Convert date string to date
            fecha_recoleccion = None
            try:
                fecha_recoleccion = datetime.strptime(collection_date, '%Y-%m-%d').date()
            except:
                fecha_recoleccion = date.today()
            
            # Use collection date as planting date (since that's what we have)
            fecha_plantacion = fecha_recoleccion
            
            # Verify finca exists before creating lote
            if not finca or not finca.id:
                logger.error(f"Error: Finca no válida al crear lote. Finca={finca}")
                return None
            
            # Verify finca exists in database and reload it to ensure consistency
            try:
                finca_verificada = Finca.objects.get(id=finca.id)
                logger.debug(f"Finca verificada: ID={finca_verificada.id}, nombre={finca_verificada.nombre}, tabla={Finca._meta.db_table}")
            except Finca.DoesNotExist:
                logger.error(f"Error: Finca con ID={finca.id} no existe en la base de datos. Tabla esperada: {Finca._meta.db_table}")
                return None
            
            # Verify reference table of Lote model
            lote_finca_model = Lote._meta.get_field('finca').remote_field.model
            lote_finca_table = lote_finca_model._meta.db_table
            finca_table = Finca._meta.db_table
            
            if lote_finca_table != finca_table:
                logger.error(
                    f"Error: Desajuste de tablas - Lote referencia '{lote_finca_table}' "
                    f"pero Finca está en '{finca_table}'"
                )
                return None
            
            logger.debug(f"Creando lote con finca_id={finca_verificada.id}, nombre={name}")
            logger.debug(f"Lote tabla: {Lote._meta.db_table}, Finca referencia: {lote_finca_table}")
            
            # Verify once more that finca exists directly in DB using raw SQL
            with db_conn.cursor() as cursor:
                cursor.execute("SELECT id, nombre FROM api_finca WHERE id = %s", [finca_verificada.id])
                finca_row = cursor.fetchone()
                
                if not finca_row:
                    logger.error(f"Error crítico: Finca ID={finca_verificada.id} no existe en tabla api_finca")
                    return None
                
                finca_id_bd, finca_nombre_bd = finca_row
                logger.debug(f"Verificación SQL: Finca ID={finca_id_bd} existe en api_finca: {finca_nombre_bd}")
            
            try:
                with transaction.atomic():
                    # Try with Django ORM first
                    try:
                        lote = Lote.objects.create(
                            finca_id=finca_id_bd,  # Use ID directly from DB
                            identificador=name,
                            variedad=genetics,
                            fecha_plantacion=fecha_plantacion,
                            fecha_cosecha=fecha_recoleccion,
                            area_hectareas=0.1,
                            estado='activo',
                            descripcion=notes if notes else '',
                            activo=True
                        )
                        logger.info(f"Lote '{name}' (ID={lote.id}) creado para finca {finca_nombre_bd} (ID={finca_id_bd})")
                        return lote
                    except Exception as orm_error:
                        # If fails with ORM, verify if it's a foreign key problem
                        error_msg = str(orm_error)
                        if 'foreign key' in error_msg.lower() or 'viola la llave foránea' in error_msg.lower():
                            logger.warning(f"Error con ORM: {error_msg}. Intentando con SQL directo...")
                            
                            # Insert directly with SQL
                            with db_conn.cursor() as cursor:
                                cursor.execute("""
                                    INSERT INTO fincas_app_lote 
                                    (finca_id, identificador, variedad, fecha_plantacion, fecha_cosecha, 
                                     area_hectareas, estado, descripcion, activo, created_at, updated_at)
                                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                                    RETURNING id;
                                """, [
                                    finca_id_bd, name, genetics, fecha_plantacion, fecha_recoleccion,
                                    0.1, 'activo', notes if notes else '', True
                                ])
                                lote_id = cursor.fetchone()[0]
                                
                                # Reload object from DB
                                lote = Lote.objects.get(id=lote_id)
                                logger.info(f"Lote '{name}' (ID={lote.id}) creado con SQL directo para finca {finca_nombre_bd} (ID={finca_id_bd})")
                                return lote
                        else:
                            raise
            except Exception as db_error:
                # Capture specifically foreign key errors
                error_msg = str(db_error)
                if 'foreign key' in error_msg.lower() or 'viola la llave foránea' in error_msg.lower():
                    logger.error(
                        f"Error de foreign key al crear lote: {error_msg}. "
                        f"Finca ID={finca_id_bd} existe en tabla api_finca. "
                        f"Verificando esquema de BD..."
                    )
                    # Verify DB schema directly
                    try:
                        with db_conn.cursor() as cur:
                            cur.execute("""
                                SELECT constraint_name, ccu.table_name
                                FROM information_schema.table_constraints AS tc
                                JOIN information_schema.key_column_usage AS kcu
                                    ON tc.constraint_name = kcu.constraint_name
                                JOIN information_schema.constraint_column_usage AS ccu
                                    ON ccu.constraint_name = tc.constraint_name
                                WHERE tc.constraint_type = 'FOREIGN KEY'
                                    AND tc.table_name = 'fincas_app_lote'
                                    AND kcu.column_name = 'finca_id';
                            """)
                            fk_info = cur.fetchall()
                            for fk_constraint, fk_table in fk_info:
                                logger.error(f"FK en BD: {fk_constraint} -> {fk_table}")
                    except Exception as schema_error:
                        logger.error(f"Error verificando esquema: {schema_error}")
                raise
            
        except Exception as e:
            logger.error(f"Error obteniendo/creando lote: {e}", exc_info=True)
            return None

