"""
Vistas para la app personas.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from .serializers import (
    PersonaRegistroSerializer, 
    PersonaSerializer,
    TipoDocumentoSerializer,
    GeneroSerializer,
    UbicacionSerializer
)
from .models import Persona, TipoDocumento, Genero, Ubicacion


class PersonaRegistroView(APIView):
    """Vista para registrar usuario y persona en una sola petición."""
    permission_classes = [AllowAny]  # Permitir registro sin autenticación
    
    def post(self, request):
        """Crear usuario y persona."""
        serializer = PersonaRegistroSerializer(data=request.data)
        
        if serializer.is_valid():
            persona = serializer.save()
            
            # Retornar la persona creada con su estructura personalizada
            return Response(
                serializer.to_representation(persona),
                status=status.HTTP_201_CREATED
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PersonaListaView(APIView):
    """Vista para listar todas las personas."""
    
    def get(self, request):
        """Listar todas las personas."""
        personas = Persona.objects.all()
        serializer = PersonaSerializer(personas, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PersonaDetalleView(APIView):
    """Vista para obtener, actualizar o eliminar una persona específica."""
    
    def get(self, request, persona_id):
        """Obtener una persona específica."""
        try:
            persona = Persona.objects.get(id=persona_id)
            serializer = PersonaSerializer(persona)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Persona.DoesNotExist:
            return Response(
                {'error': 'Persona no encontrada'},
                status=status.HTTP_404_NOT_FOUND
            )


class TipoDocumentoListaView(APIView):
    """Vista para listar tipos de documento."""
    
    def get(self, request):
        """Listar todos los tipos de documento."""
        tipos = TipoDocumento.objects.all()
        serializer = TipoDocumentoSerializer(tipos, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class GeneroListaView(APIView):
    """Vista para listar géneros."""
    
    def get(self, request):
        """Listar todos los géneros."""
        generos = Genero.objects.all()
        serializer = GeneroSerializer(generos, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UbicacionListaView(APIView):
    """Vista para listar ubicaciones."""
    
    def get(self, request):
        """Listar todas las ubicaciones."""
        ubicaciones = Ubicacion.objects.all()
        serializer = UbicacionSerializer(ubicaciones, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
