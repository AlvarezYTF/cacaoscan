"""
Mixin for finca views to reduce code duplication in serializer operations.
"""
from rest_framework.response import Response
from rest_framework import status
from api.serializers import FincaSerializer, FincaDetailSerializer
from api.utils.model_imports import get_model_safely

Finca = get_model_safely('fincas_app.models.Finca')


class FincaSerializerMixin:
    """
    Mixin that provides common serializer patterns for finca views.
    """
    
    def get_finca_with_error_handling(self, finca_id: int):
        """
        Get finca by ID with error handling.
        
        Args:
            finca_id: Finca ID
            
        Returns:
            tuple: (finca, error_response) where error_response is None if successful
        """
        try:
            queryset = self.get_queryset()
            finca = queryset.get(id=finca_id)
            return finca, None
        except Finca.DoesNotExist:
            return None, self.handle_finca_not_found(finca_id)
        except Exception as e:
            return None, self.handle_finca_error(e, "obteniendo finca", finca_id)
    
    def serialize_finca_response(self, finca, status_code=status.HTTP_200_OK, serializer_class=FincaSerializer, include_success=False):
        """
        Serialize finca and return response.
        
        Args:
            finca: Finca instance
            status_code: HTTP status code
            serializer_class: Serializer class to use
            include_success: Whether to include success flag in response
            
        Returns:
            Response with serialized finca data
        """
        serializer = serializer_class(finca, context={'request': self.request})
        if include_success:
            return Response({
                'success': True,
                'finca': serializer.data
            }, status=status_code)
        return Response(serializer.data, status=status_code)
    
    def create_finca_response(self, finca, serializer_class=FincaSerializer):
        """
        Create response for newly created finca.
        
        Args:
            finca: Finca instance
            serializer_class: Serializer class to use
            
        Returns:
            Response with serialized finca data and success flag
        """
        serializer = serializer_class(finca, context={'request': self.request})
        return Response({
            'success': True,
            'finca': serializer.data
        }, status=status.HTTP_201_CREATED)
    
    def update_finca_response(self, finca, serializer_class=FincaSerializer):
        """
        Create response for updated finca.
        
        Args:
            finca: Finca instance
            serializer_class: Serializer class to use
            
        Returns:
            Response with serialized finca data and success flag
        """
        serializer = serializer_class(finca, context={'request': self.request})
        return Response({
            'success': True,
            'finca': serializer.data
        }, status=status.HTTP_200_OK)

