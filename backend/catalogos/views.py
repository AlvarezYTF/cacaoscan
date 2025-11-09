from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404

from .models import Tema, Parametro, Departamento, Municipio
from .serializers import (
    TemaSerializer,
    TemaConParametrosSerializer,
    ParametroSerializer,
    ParametroDetalleSerializer,
    ParametroCreateSerializer,
    DepartamentoSerializer,
    DepartamentoConMunicipiosSerializer,
    MunicipioSerializer,
    MunicipioDetalleSerializer,
    MunicipioCreateSerializer
)


class TemaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar los Temas del sistema.
    
    list: Obtiene todos los temas activos
    retrieve: Obtiene un tema específico
    parametros: Obtiene los parámetros de un tema específico (custom action)
    """
    queryset = Tema.objects.all()
    serializer_class = TemaSerializer
    permission_classes = [AllowAny]
    lookup_field = 'id'

    def get_serializer_class(self):
        """Devuelve diferentes serializers según la acción"""
        if self.action == 'retrieve' or self.action == 'parametros':
            return TemaConParametrosSerializer
        return TemaSerializer

    @action(detail=True, methods=['get'], url_path='parametros')
    def parametros(self, request, id=None):
        """
        Obtiene todos los parámetros de un tema específico.
        Endpoint: GET /api/temas/{id}/parametros/
        """
        tema = self.get_object()
        parametros = tema.parametros.all()
        
        # Filtrar por activos si se solicita
        solo_activos = request.query_params.get('activos', 'false').lower() == 'true'
        if solo_activos:
            parametros = parametros.filter(activo=True)
        
        serializer = ParametroSerializer(parametros, many=True)
        return Response(serializer.data)


class ParametroViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar los Parámetros del sistema.
    
    list: Obtiene todos los parámetros
    retrieve: Obtiene un parámetro específico
    by_tema: Obtiene parámetros filtrados por tema (custom action)
    """
    queryset = Parametro.objects.all().select_related('tema')
    serializer_class = ParametroSerializer
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        """Devuelve diferentes serializers según la acción"""
        if self.action == 'create':
            return ParametroCreateSerializer
        elif self.action == 'retrieve':
            return ParametroDetalleSerializer
        return ParametroSerializer

    def get_queryset(self):
        """Permite filtrar por tema (id o código) y por activos."""
        queryset = super().get_queryset()

        tema_param = (self.request.query_params.get('tema') or '').strip()
        if tema_param:
            # Si es numérico -> asumir ID; si no, filtrar por código
            if tema_param.isdigit():
                queryset = queryset.filter(tema_id=int(tema_param))
            else:
                queryset = queryset.filter(tema__codigo=tema_param)

        solo_activos = self.request.query_params.get('activos', 'false').lower() == 'true'
        if solo_activos:
            queryset = queryset.filter(activo=True)

        return queryset

    @action(detail=False, methods=['get'], url_path='tema/(?P<codigo_tema>[^/.]+)')
    def by_tema(self, request, codigo_tema=None):
        """
        Obtiene los parámetros de un tema por su código.
        Endpoint: GET /api/parametros/tema/{codigo_tema}/
        """
        try:
            tema = get_object_or_404(Tema, codigo=codigo_tema)
            parametros = Parametro.objects.filter(tema=tema)
            
            # Filtrar por activos si se solicita
            solo_activos = request.query_params.get('activos', 'false').lower() == 'true'
            if solo_activos:
                parametros = parametros.filter(activo=True)
            
            serializer = ParametroSerializer(parametros, many=True)
            return Response({
                'tema': {
                    'codigo': tema.codigo,
                    'nombre': tema.nombre
                },
                'parametros': serializer.data
            })
        except Tema.DoesNotExist:
            return Response(
                    {'error': f'Tema con código "{codigo_tema}" no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )


# ViewSets para Departamentos y Municipios

class DepartamentoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar los Departamentos de Colombia.
    
    list: Obtiene todos los departamentos
    retrieve: Obtiene un departamento específico con sus municipios
    municipios: Obtiene los municipios de un departamento específico (custom action)
    """
    queryset = Departamento.objects.all()
    serializer_class = DepartamentoSerializer
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        """Devuelve diferentes serializers según la acción"""
        if self.action == 'retrieve' or self.action == 'municipios':
            return DepartamentoConMunicipiosSerializer
        return DepartamentoSerializer

    @action(detail=True, methods=['get'], url_path='municipios')
    def municipios(self, request, pk=None):
        """
        Obtiene todos los municipios de un departamento específico.
        Endpoint: GET /api/departamentos/{id}/municipios/
        """
        departamento = self.get_object()
        municipios = departamento.municipios.all()
        
        serializer = MunicipioSerializer(municipios, many=True)
        return Response(serializer.data)


class MunicipioViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar los Municipios de Colombia.
    
    list: Obtiene todos los municipios (filtrable por departamento)
    retrieve: Obtiene un municipio específico
    by_departamento: Obtiene municipios filtrados por departamento (custom action)
    """
    queryset = Municipio.objects.all().select_related('departamento')
    serializer_class = MunicipioSerializer
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        """Devuelve diferentes serializers según la acción"""
        if self.action == 'create':
            return MunicipioCreateSerializer
        elif self.action == 'retrieve':
            return MunicipioDetalleSerializer
        return MunicipioSerializer

    def get_queryset(self):
        """Permite filtrar por departamento"""
        queryset = super().get_queryset()
        
        # Filtrar por departamento si se proporciona
        departamento_id = self.request.query_params.get('departamento')
        if departamento_id:
            queryset = queryset.filter(departamento_id=departamento_id)
        
        # Filtrar por nombre si se proporciona
        nombre = self.request.query_params.get('nombre')
        if nombre:
            queryset = queryset.filter(nombre__icontains=nombre)
        
        return queryset

    @action(detail=False, methods=['get'], url_path='departamento/(?P<codigo_departamento>[^/.]+)')
    def by_departamento(self, request, codigo_departamento=None):
        """
        Obtiene los municipios de un departamento por su código.
        Endpoint: GET /api/municipios/departamento/{codigo_departamento}/
        """
        try:
            departamento = get_object_or_404(Departamento, codigo=codigo_departamento)
            municipios = Municipio.objects.filter(departamento=departamento)
            
            serializer = MunicipioSerializer(municipios, many=True)
            return Response({
                'departamento': {
                    'codigo': departamento.codigo,
                    'nombre': departamento.nombre
                },
                'municipios': serializer.data
            })
        except Departamento.DoesNotExist:
            return Response(
                {'error': f'Departamento con código "{codigo_departamento}" no encontrado'},
                status=status.HTTP_404_NOT_FOUND
            )

