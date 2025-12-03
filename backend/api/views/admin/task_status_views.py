"""
Vistas para consultar el estado de tareas Celery.
"""
import logging
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from celery.result import AsyncResult

from ...serializers import ErrorResponseSerializer

logger = logging.getLogger("cacaoscan.api.admin.tasks")


class TaskStatusView(APIView):
    """
    Endpoint para consultar el estado de una tarea Celery.
    """
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Consulta el estado de una tarea Celery por su task_id",
        operation_summary="Estado de tarea",
        responses={
            200: openapi.Response(
                description="Estado de la tarea",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'task_id': openapi.Schema(type=openapi.TYPE_STRING),
                        'status': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            enum=['PENDING', 'PROGRESS', 'SUCCESS', 'FAILURE'],
                            description="Estado de la tarea"
                        ),
                        'result': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            description="Resultado de la tarea (si está completada)"
                        ),
                        'error': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="Mensaje de error (si falló)"
                        ),
                        'progress': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            description="Información de progreso (si está en progreso)"
                        )
                    }
                )
            ),
            404: ErrorResponseSerializer,
            500: ErrorResponseSerializer,
        },
        tags=['Tareas']
    )
    def get(self, request, task_id):
        """
        Consulta el estado de una tarea Celery.
        
        Args:
            task_id: ID de la tarea Celery
        
        Returns:
            Estado y resultado de la tarea
        """
        try:
            task_result = AsyncResult(task_id)
            
            response_data = {
                'task_id': task_id,
                'status': task_result.state
            }
            
            if task_result.state == 'PENDING':
                response_data['message'] = 'Tarea pendiente de ejecución'
            elif task_result.state == 'PROGRESS':
                response_data['progress'] = task_result.info
            elif task_result.state == 'SUCCESS':
                response_data['result'] = task_result.result
                response_data['message'] = 'Tarea completada exitosamente'
            elif task_result.state == 'FAILURE':
                response_data['error'] = str(task_result.info)
                response_data['message'] = 'Tarea falló'
            else:
                response_data['message'] = f'Estado desconocido: {task_result.state}'
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error consultando estado de tarea {task_id}: {e}")
            return Response({
                'error': f'Error consultando estado de tarea: {str(e)}',
                'details': f'Error consultando estado de tarea: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

