"""
Helper functions for Swagger/OpenAPI decorators to reduce duplication.
"""
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


def create_incremental_success_response_schema():
    """
    Creates a standard success response schema for incremental training endpoints.
    
    Returns:
        openapi.Schema: Success response schema
    """
    return openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
            'data': openapi.Schema(type=openapi.TYPE_OBJECT),
            'message': openapi.Schema(type=openapi.TYPE_STRING)
        }
    )


def create_incremental_swagger_decorator(
    operation_description: str,
    operation_summary: str,
    request_body: openapi.Schema = None,
    manual_parameters: list = None,
    responses: dict = None
):
    """
    Creates a standardized @swagger_auto_schema decorator for incremental training endpoints.
    
    Args:
        operation_description: Description of the operation
        operation_summary: Summary of the operation
        request_body: Optional request body schema
        manual_parameters: Optional list of manual parameters
        responses: Optional custom responses dict (will merge with defaults)
        
    Returns:
        Decorator function
    """
    default_responses = {
        200: openapi.Response(
            description="Operación completada exitosamente",
            schema=create_incremental_success_response_schema()
        ),
        400: openapi.Response(description="Datos inválidos"),
        401: openapi.Response(description="No autorizado"),
    }
    
    if responses:
        default_responses.update(responses)
    
    return swagger_auto_schema(
        operation_description=operation_description,
        operation_summary=operation_summary,
        request_body=request_body,
        manual_parameters=manual_parameters,
        responses=default_responses,
        tags=['Entrenamiento Incremental']
    )

