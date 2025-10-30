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
                return Response({
                    'error': 'Error al obtener/crear la finca',
                    'status': 'error'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 3. Obtener o crear lote
            lote = self._get_or_create_lote(
                request, finca, name, genetics, collection_date, notes
            )
            if not lote:
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
            
            return Response({
                'lote_id': lote.id,
                'lote_name': lote.identificador,
                'total_images': stats['total_images'],
                'processed_images': stats['processed_images'],
                'failed_images': stats['failed_images'],
                'average_confidence': stats['average_confidence'],
                'average_dimensions': stats['average_dimensions'],
                'total_weight': stats['total_weight'],
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
                return finca
            
            # Crear nueva finca si no existe
            finca = Finca.objects.create(
                nombre=farm_name,
                agricultor=request.user if not request.user.is_superuser else None,
                municipio=origin_place if origin_place else 'No especificado',
                departamento=origin if origin else 'No especificado',
                hectareas=1.0,  # Valor por defecto
                activa=True
            )
            
            logger.info(f"Finca '{farm_name}' creada para usuario {request.user.username}")
            return finca
            
        except Exception as e:
            logger.error(f"Error obteniendo/creando finca: {e}")
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
            
            lote = Lote.objects.create(
                finca=finca,
                identificador=name,
                variedad=genetics,
                fecha_plantacion=fecha_plantacion,
                fecha_cosecha=fecha_recoleccion,
                area_hectareas=0.1,  # Valor por defecto pequeño
                estado='activo',
                descripcion=notes if notes else '',
                activo=True
            )
            
            logger.info(f"Lote '{name}' creado para finca {finca.nombre}")
            return lote
            
        except Exception as e:
            logger.error(f"Error obteniendo/creando lote: {e}")
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
                        # Convertir imagen a PIL
                        from PIL import Image
                        image_bytes = image_file.read()
                        image_file.seek(0)  # Reset file pointer
                        pil_image = Image.open(io.BytesIO(image_bytes))
                        
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
        avg_dimensions = {}
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

