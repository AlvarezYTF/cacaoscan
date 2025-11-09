"""
Vistas para análisis batch de lotes con ML.
"""
import logging
import time
import io
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

try:
    from fincas_app.models import Lote, Finca
except ImportError:
    Lote = None
    Finca = None

try:
    from images_app.models import CacaoImage, CacaoPrediction
except ImportError:
    CacaoImage = None
    CacaoPrediction = None
from .serializers import ErrorResponseSerializer

logger = logging.getLogger("cacaoscan.api")


class BatchAnalysisView(APIView):
    """
    Endpoint para análisis batch de lotes con múltiples imágenes.
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
            201: openapi.Response(
                description="Análisis batch completado",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'lote_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'total_images': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'processed_images': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'failed_images': openapi.Schema(type=openapi.TYPE_INTEGER),
                        'average_confidence': openapi.Schema(type=openapi.TYPE_NUMBER),
                        'status': openapi.Schema(type=openapi.TYPE_STRING),
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
        Procesa un lote con múltiples imágenes usando ML.
        """
        start_time = time.time()
        
        try:
            # 1. Validar datos de entrada
            name = request.data.get('name', '').strip()
            farm_name = request.data.get('farm', '').strip()
            genetics = request.data.get('genetics', '').strip()
            collection_date = request.data.get('collectionDate', '').strip()
            origin_place = request.data.get('originPlace', '').strip()
            origin = request.data.get('origin', '').strip()
            notes = request.data.get('notes', '').strip()
            
            # Validaciones
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
            
            # 2. Obtener o crear finca
            finca = self._get_or_create_finca(request, farm_name, origin_place, origin)
            if not finca:
                logger.error(f"Error obteniendo/creando finca '{farm_name}' para usuario {request.user.username}")
                return Response({
                    'error': 'Error al obtener/crear la finca',
                    'status': 'error'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            logger.info(f"Finca obtenida/creada: ID={finca.id}, nombre={finca.nombre}, agricultor={finca.agricultor_id}")
            
            # 3. Obtener o crear lote
            lote = self._get_or_create_lote(
                request, finca, name, genetics, collection_date, notes
            )
            if not lote:
                logger.error(f"Error obteniendo/creando lote '{name}' para finca_id={finca.id if finca else 'None'}")
                return Response({
                    'error': 'Error al obtener/crear el lote',
                    'status': 'error'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 4. Procesar imágenes
            images = request.FILES.getlist('images')
            if not images:
                return Response({
                    'error': 'No se enviaron imágenes',
                    'status': 'error'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 5. Procesar cada imagen con ML
            results = self._process_images_batch(request, images, lote)
            
            # 6. Calcular estadísticas
            stats = self._calculate_stats(results)
            
            # 7. Preparar respuesta
            total_time = time.time() - start_time
            logger.info(
                f"Análisis batch completado en {total_time:.2f}s - "
                f"Lote ID: {lote.id}, Imágenes procesadas: {stats['processed_images']}/{stats['total_images']}"
            )
            
            # Preparar resultados individuales para el frontend
            predictions_list = []
            for r in results:
                if r.get('success', False):
                    pred = r.get('prediction', {})
                    predictions_list.append({
                        'image_id': r.get('image_id'),
                        'alto_mm': pred.get('alto_mm', 0),
                        'ancho_mm': pred.get('ancho_mm', 0),
                        'grosor_mm': pred.get('grosor_mm', 0),
                        'peso_g': pred.get('peso_g', 0),
                        'confidences': pred.get('confidences', {}),
                        'crop_url': pred.get('crop_url', ''),
                        'model_version': pred.get('debug', {}).get('models_version', 'v1.0'),
                        'processing_time_ms': pred.get('processing_time_ms', 0)
                    })
                else:
                    predictions_list.append({
                        'image_id': r.get('image_id'),
                        'error': r.get('error', 'Error desconocido'),
                        'success': False
                    })
            
            return Response({
                'lote_id': lote.id,
                'lote_name': lote.identificador,
                'total_images': stats['total_images'],
                'processed_images': stats['processed_images'],
                'failed_images': stats['failed_images'],
                'average_confidence': stats['average_confidence'],
                'average_dimensions': stats['average_dimensions'],
                'total_weight': stats['total_weight'],
                'predictions': predictions_list,  # Resultados individuales
                'status': 'completed',
                'processing_time_seconds': round(total_time, 2)
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Error en análisis batch: {e}", exc_info=True)
            return Response({
                'error': f'Error procesando análisis batch: {str(e)}',
                'status': 'error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _get_or_create_finca(self, request, farm_name, origin_place, origin):
        """Obtener o crear finca."""
        try:
            # Buscar finca existente por nombre
            if request.user.is_superuser or request.user.is_staff:
                # Admin puede ver todas las fincas
                finca = Finca.objects.filter(nombre=farm_name).first()
            else:
                # Agricultor solo ve sus fincas
                finca = Finca.objects.filter(nombre=farm_name, agricultor=request.user).first()
            
            if finca:
                # Verificar que la finca existe realmente en la BD
                try:
                    finca_verificada = Finca.objects.get(id=finca.id)
                    logger.debug(f"Finca existente encontrada: ID={finca_verificada.id}, nombre={finca_verificada.nombre}, tabla={Finca._meta.db_table}")
                    return finca_verificada
                except Finca.DoesNotExist:
                    logger.warning(f"Finca con ID={finca.id} no existe en BD, creando nueva")
                    finca = None
            
            # Crear nueva finca si no existe
            # IMPORTANTE: agricultor siempre debe tener un valor, no puede ser None
            from django.db import transaction
            
            with transaction.atomic():
                finca = Finca.objects.create(
                    nombre=farm_name,
                    agricultor=request.user,  # Siempre asignar el usuario actual
                    ubicacion=origin_place if origin_place else 'No especificado',
                    municipio=origin_place if origin_place else 'No especificado',
                    departamento=origin if origin else 'No especificado',
                    hectareas=1.0,  # Valor por defecto
                    activa=True
                )
                
                # Verificar que se guard correctamente refrescando desde la BD
                finca.refresh_from_db()
                
                # Verificar nuevamente que existe en la BD
                try:
                    finca_verificada = Finca.objects.get(id=finca.id)
                    logger.info(f"Finca '{farm_name}' creada para usuario {request.user.username} - ID: {finca_verificada.id}")
                    logger.debug(f"Finca guardada: tabla={Finca._meta.db_table}, agricultor_id={finca_verificada.agricultor_id}")
                    return finca_verificada
                except Finca.DoesNotExist:
                    logger.error(f"Finca creada pero no encontrada en BD despus de refresh - ID: {finca.id}")
                    return None
            
        except Exception as e:
            logger.error(f"Error obteniendo/creando finca: {e}", exc_info=True)
            return None
    
    def _get_or_create_lote(self, request, finca, name, genetics, collection_date, notes):
        """Obtener o crear lote."""
        try:
            # Buscar lote existente
            lote = Lote.objects.filter(
                finca=finca,
                identificador=name
            ).first()
            
            if lote:
                logger.debug(f"Lote existente encontrado: ID={lote.id}, identificador={lote.identificador}")
                return lote
            
            # Crear nuevo lote
            from datetime import datetime, date
            
            # Convertir fecha string a date
            fecha_recoleccion = None
            try:
                fecha_recoleccion = datetime.strptime(collection_date, '%Y-%m-%d').date()
            except:
                fecha_recoleccion = date.today()
            
            # Usar fecha de recolección como fecha de plantación (ya que es lo que tenemos)
            fecha_plantacion = fecha_recoleccion
            
            # Verificar que la finca existe antes de crear el lote
            if not finca or not finca.id:
                logger.error(f"Error: Finca no vlida al crear lote. Finca={finca}")
                return None
            
            # Verificar que la finca existe en la base de datos y recargarla para asegurar consistencia
            try:
                finca_verificada = Finca.objects.get(id=finca.id)
                logger.debug(f"Finca verificada: ID={finca_verificada.id}, nombre={finca_verificada.nombre}, tabla={Finca._meta.db_table}")
            except Finca.DoesNotExist:
                logger.error(f"Error: Finca con ID={finca.id} no existe en la base de datos. Tabla esperada: {Finca._meta.db_table}")
                return None
            
            # Verificar la tabla de referencia del modelo Lote
            lote_finca_model = Lote._meta.get_field('finca').remote_field.model
            lote_finca_table = lote_finca_model._meta.db_table
            finca_table = Finca._meta.db_table
            
            if lote_finca_table != finca_table:
                logger.error(
                    f"Error: Desajuste de tablas - Lote referencia '{lote_finca_table}' "
                    f"pero Finca est en '{finca_table}'"
                )
                return None
            
            logger.debug(f"Creando lote con finca_id={finca_verificada.id}, nombre={name}")
            logger.debug(f"Lote tabla: {Lote._meta.db_table}, Finca referencia: {lote_finca_table}")
            
            from django.db import transaction
            
            # Verificar una vez ms que la finca existe directamente en la BD usando SQL raw
            from django.db import connection as db_conn
            with db_conn.cursor() as cursor:
                cursor.execute("SELECT id, nombre FROM api_finca WHERE id = %s", [finca_verificada.id])
                finca_row = cursor.fetchone()
                
                if not finca_row:
                    logger.error(f"Error crtico: Finca ID={finca_verificada.id} no existe en tabla api_finca")
                    return None
                
                finca_id_bd, finca_nombre_bd = finca_row
                logger.debug(f"Verificacin SQL: Finca ID={finca_id_bd} existe en api_finca: {finca_nombre_bd}")
            
            try:
                with transaction.atomic():
                    # Usar SQL directo para insertar si Django sigue teniendo problemas
                    # Primero intentar con Django ORM
                    try:
                        lote = Lote.objects.create(
                            finca_id=finca_id_bd,  # Usar ID directamente desde BD
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
                        # Si falla con ORM, verificar si es problema de foreign key
                        error_msg = str(orm_error)
                        if 'foreign key' in error_msg.lower() or 'viola la llave fornea' in error_msg.lower():
                            logger.warning(f"Error con ORM: {error_msg}. Intentando con SQL directo...")
                            
                            # Insertar directamente con SQL
                            from datetime import datetime
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
                                
                                # Recargar el objeto desde la BD
                                lote = Lote.objects.get(id=lote_id)
                                logger.info(f"Lote '{name}' (ID={lote.id}) creado con SQL directo para finca {finca_nombre_bd} (ID={finca_id_bd})")
                                return lote
                        else:
                            raise
            except Exception as db_error:
                # Capturar especficamente errores de foreign key
                error_msg = str(db_error)
                if 'foreign key' in error_msg.lower() or 'viola la llave fornea' in error_msg.lower():
                    logger.error(
                        f"Error de foreign key al crear lote: {error_msg}. "
                        f"Finca ID={finca_id_bd} existe en tabla api_finca. "
                        f"Verificando esquema de BD..."
                    )
                    # Verificar el esquema en la BD directamente
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
    
    def _process_images_batch(self, request, images, lote):
        """Procesar múltiples imágenes con ML."""
        results = []
        predictor = None
        
        try:
            # Obtener predictor
            from ml.prediction.predict import get_predictor, load_artifacts
            
            predictor = get_predictor()
            
            if not predictor.models_loaded:
                logger.info("Modelos no cargados. Intentando carga automática...")
                success = load_artifacts()
                
                if success:
                    predictor = get_predictor()
                else:
                    logger.error("No se pudieron cargar los modelos ML")
                    return results
        
        except Exception as e:
            logger.error(f"Error obteniendo predictor: {e}", exc_info=True)
            return results
        
        for idx, image_file in enumerate(images):
            try:
                # Guardar imagen
                cacao_image = CacaoImage(
                    user=request.user,
                    image=image_file,
                    file_name=image_file.name,
                    file_size=image_file.size,
                    file_type=image_file.content_type,
                    processed=False,
                    lote=lote,
                    variedad=lote.variedad,
                    fecha_cosecha=lote.fecha_cosecha
                )
                cacao_image.save()
                
                # Procesar con ML
                prediction_result = None
                if predictor and predictor.models_loaded:
                    try:
                        # Leer imagen desde el archivo guardado en disco
                        from PIL import Image
                        # Opcin 1: Intentar leer desde el archivo en memoria primero
                        try:
                            image_file.seek(0)  # Reset file pointer si es posible
                            image_bytes = image_file.read()
                            if image_bytes:
                                pil_image = Image.open(io.BytesIO(image_bytes))
                            else:
                                # Si est vaco, leer desde disco
                                pil_image = Image.open(cacao_image.image.path)
                        except (AttributeError, ValueError, IOError):
                            # Si falla, leer desde el archivo guardado en disco
                            pil_image = Image.open(cacao_image.image.path)
                        
                        prediction_start = time.time()
                        result = predictor.predict(pil_image)
                        prediction_time_ms = int((time.time() - prediction_start) * 1000)
                        
                        # Guardar predicción
                        cacao_prediction = CacaoPrediction(
                            image=cacao_image,
                            alto_mm=result['alto_mm'],
                            ancho_mm=result['ancho_mm'],
                            grosor_mm=result['grosor_mm'],
                            peso_g=result['peso_g'],
                            confidence_alto=result['confidences']['alto'],
                            confidence_ancho=result['confidences']['ancho'],
                            confidence_grosor=result['confidences']['grosor'],
                            confidence_peso=result['confidences']['peso'],
                            processing_time_ms=prediction_time_ms,
                            crop_url=result.get('crop_url', ''),
                            model_version=result.get('debug', {}).get('models_version', 'v1.0'),
                            device_used=result.get('debug', {}).get('device', 'cpu').split(':')[0] if ':' in str(result.get('debug', {}).get('device', 'cpu')) else 'cpu'
                        )
                        cacao_prediction.save()
                        
                        cacao_image.processed = True
                        cacao_image.save()
                        
                        prediction_result = {
                            'success': True,
                            'image_id': cacao_image.id,
                            'prediction': result
                        }
                        
                    except Exception as pred_error:
                        logger.error(f"Error en predicción de imagen {idx + 1}: {pred_error}", exc_info=True)
                        prediction_result = {
                            'success': False,
                            'image_id': cacao_image.id,
                            'error': str(pred_error)
                        }
                else:
                    prediction_result = {
                        'success': False,
                        'image_id': cacao_image.id,
                        'error': 'Modelos ML no disponibles'
                    }
                
                results.append(prediction_result)
                
            except Exception as e:
                logger.error(f"Error procesando imagen {idx + 1}: {e}")
                results.append({
                    'success': False,
                    'error': str(e)
                })
        
        return results
    
    def _calculate_stats(self, results):
        """Calcular estadísticas del batch."""
        total_images = len(results)
        processed_images = sum(1 for r in results if r.get('success', False))
        failed_images = total_images - processed_images
        
        successful_results = [r for r in results if r.get('success', False)]
        
        # Calcular promedios
        avg_confidence = 0
        avg_dimensions = {
            'alto': 0,
            'ancho': 0,
            'grosor': 0
        }
        total_weight = 0
        
        if successful_results:
            confidences = []
            altos = []
            anchos = []
            grosor = []
            pesos = []
            
            for r in successful_results:
                pred = r.get('prediction', {})
                conf = pred.get('confidences', {})
                
                # Confianza promedio
                avg_conf = sum([
                    conf.get('alto', 0),
                    conf.get('ancho', 0),
                    conf.get('grosor', 0),
                    conf.get('peso', 0)
                ]) / 4
                confidences.append(avg_conf)
                
                altos.append(pred.get('alto_mm', 0))
                anchos.append(pred.get('ancho_mm', 0))
                grosor.append(pred.get('grosor_mm', 0))
                pesos.append(pred.get('peso_g', 0))
            
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            avg_dimensions = {
                'alto': sum(altos) / len(altos) if altos else 0,
                'ancho': sum(anchos) / len(anchos) if anchos else 0,
                'grosor': sum(grosor) / len(grosor) if grosor else 0
            }
            total_weight = sum(pesos)
        
        return {
            'total_images': total_images,
            'processed_images': processed_images,
            'failed_images': failed_images,
            'average_confidence': round(avg_confidence, 3),
            'average_dimensions': avg_dimensions,
            'total_weight': round(total_weight, 2)
        }



