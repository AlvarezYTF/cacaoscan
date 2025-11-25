"""
Finca serializers for CacaoScan API.
"""
from rest_framework import serializers
from ..utils.model_imports import get_models_safely

# Import models safely
models = get_models_safely({
    'Finca': 'fincas_app.models.Finca',
    'Lote': 'fincas_app.models.Lote',
    'CacaoImage': 'images_app.models.CacaoImage'
})
Finca = models['Finca']
Lote = models['Lote']
CacaoImage = models['CacaoImage']


class FincaSerializer(serializers.ModelSerializer):
    """Serializer for fincas with complete validations."""
    agricultor_name = serializers.CharField(source='agricultor.get_full_name', read_only=True)
    agricultor_email = serializers.CharField(source='agricultor.email', read_only=True)
    ubicacion_completa = serializers.ReadOnlyField()
    estadisticas = serializers.SerializerMethodField()
    
    class Meta:
        model = Finca
        fields = (
            'id', 'nombre', 'ubicacion', 'municipio', 'departamento', 
            'hectareas', 'agricultor', 'agricultor_name', 'agricultor_email',
            'descripcion', 'coordenadas_lat', 'coordenadas_lng', 
            'fecha_registro', 'activa', 'ubicacion_completa', 'estadisticas',
            'created_at', 'updated_at'
        )
        read_only_fields = (
            'id', 'fecha_registro', 'created_at', 'updated_at', 
            'ubicacion_completa', 'estadisticas', 'agricultor'
        )
    
    def get_estadisticas(self, obj):
        """Get finca statistics."""
        try:
            return obj.get_estadisticas()
        except Exception:
            # Return empty statistics if there's an error
            return {
                'total_lotes': 0,
                'lotes_activos': 0,
                'total_analisis': 0,
                'calidad_promedio': 0.0,
                'hectareas': float(obj.hectareas) if obj.hectareas else 0.0,
                'fecha_registro': obj.fecha_registro.strftime('%d/%m/%Y') if obj.fecha_registro else '',
                'activa': obj.activa if hasattr(obj, 'activa') else True
            }
    
    def validate_nombre(self, value):
        """Validate finca name."""
        if not value or len(value.strip()) < 3:
            raise serializers.ValidationError("El nombre de la finca debe tener al menos 3 caracteres.")
        
        # Check uniqueness per agricultor
        agricultor = self.context.get('request').user if self.context.get('request') else None
        if agricultor and self.instance:
            # Update: exclude current instance
            if Finca.objects.filter(
                agricultor=agricultor, 
                nombre__iexact=value.strip()
            ).exclude(id=self.instance.id).exists():
                raise serializers.ValidationError("Ya tienes una finca con este nombre.")
        elif agricultor:
            # Creation: check uniqueness
            if Finca.objects.filter(
                agricultor=agricultor, 
                nombre__iexact=value.strip()
            ).exists():
                raise serializers.ValidationError("Ya tienes una finca con este nombre.")
        
        return value.strip()
    
    def validate_hectareas(self, value):
        """Validate hectares."""
        if value <= 0:
            raise serializers.ValidationError("Las hectáreas deben ser mayores a 0.")
        if value > 10000:
            raise serializers.ValidationError("Las hectáreas no pueden ser mayores a 10,000.")
        return value
    
    def validate_coordenadas_lat(self, value):
        """Validate GPS latitude."""
        from core.utils import validate_latitude
        return validate_latitude(value)
    
    def validate_coordenadas_lng(self, value):
        """Validate GPS longitude."""
        from core.utils import validate_longitude
        return validate_longitude(value)
    
    def validate(self, attrs):
        """General validations."""
        from core.utils import validate_coordinates
        if not attrs.get('municipio', '').strip():
            raise serializers.ValidationError("El municipio es requerido.")
        if not attrs.get('departamento', '').strip():
            raise serializers.ValidationError("El departamento es requerido.")
        validate_coordinates(attrs)
        return attrs


class FincaListSerializer(serializers.ModelSerializer):
    """Optimized serializer for finca listings (without heavy statistics)."""
    ubicacion_completa = serializers.SerializerMethodField()
    
    class Meta:
        model = Finca
        fields = (
            'id', 'nombre', 'municipio', 'departamento', 'ubicacion', 
            'ubicacion_completa', 'hectareas', 'activa', 'fecha_registro', 'agricultor_id',
            'coordenadas_lat', 'coordenadas_lng'
        )
    
    def get_ubicacion_completa(self, obj):
        """Get complete location."""
        return f"{obj.municipio}, {obj.departamento}"


class FincaDetailSerializer(FincaSerializer):
    """Detailed serializer for fincas with related data."""
    lotes = serializers.SerializerMethodField()
    
    class Meta(FincaSerializer.Meta):
        fields = FincaSerializer.Meta.fields + ('lotes',)
    
    def get_lotes(self, obj):
        """Get finca lots."""
        # Deferred import to avoid circular imports
        try:
            from fincas_app.models import Lote
            lotes = obj.lotes.all()[:10]  # Limit to 10 lotes to avoid overload
            
            # Serialize manually to avoid circular dependencies
            lotes_data = []
            for lote in lotes:
                lotes_data.append({
                    'id': lote.id,
                    'identificador': lote.identificador,
                    'variedad': lote.variedad,
                    'estado': lote.estado,
                    'activo': lote.activo,
                    'fecha_plantacion': lote.fecha_plantacion.isoformat() if lote.fecha_plantacion else None,
                    'area_hectareas': float(lote.area_hectareas) if lote.area_hectareas else None,
                })
            return lotes_data
        except Exception as e:
            # If there's any error, return empty list instead of failing
            import logging
            logger = logging.getLogger("cacaoscan.api")
            logger.warning(f"Error serializing lotes de finca {obj.id}: {e}")
            return []


class FincaStatsSerializer(serializers.Serializer):
    """Serializer for finca statistics."""
    total_fincas = serializers.IntegerField()
    fincas_activas = serializers.IntegerField()
    total_hectareas = serializers.DecimalField(max_digits=12, decimal_places=2)
    promedio_hectareas = serializers.DecimalField(max_digits=10, decimal_places=2)
    fincas_por_departamento = serializers.ListField()
    fincas_por_municipio = serializers.ListField()
    calidad_promedio_general = serializers.FloatField()


class LoteSerializer(serializers.ModelSerializer):
    """Serializer for lotes with complete validations."""
    finca_nombre = serializers.CharField(source='finca.nombre', read_only=True)
    finca_ubicacion = serializers.CharField(source='finca.ubicacion_completa', read_only=True)
    agricultor_nombre = serializers.CharField(source='finca.agricultor.get_full_name', read_only=True)
    ubicacion_completa = serializers.ReadOnlyField()
    estadisticas = serializers.SerializerMethodField()
    edad_meses = serializers.ReadOnlyField()
    
    class Meta:
        model = Lote
        fields = (
            'id', 'finca', 'finca_nombre', 'finca_ubicacion', 'agricultor_nombre',
            'identificador', 'variedad', 'fecha_plantacion', 'fecha_cosecha',
            'area_hectareas', 'estado', 'descripcion', 'coordenadas_lat', 
            'coordenadas_lng', 'fecha_registro', 'activo', 'ubicacion_completa',
            'estadisticas', 'edad_meses', 'created_at', 'updated_at'
        )
        read_only_fields = (
            'id', 'fecha_registro', 'created_at', 'updated_at', 
            'ubicacion_completa', 'estadisticas', 'edad_meses'
        )
    
    def get_estadisticas(self, obj):
        """Get lote statistics."""
        return obj.get_estadisticas()
    
    def validate_identificador(self, value):
        """Validate lote identifier."""
        if not value or len(value.strip()) < 2:
            raise serializers.ValidationError("El identificador del lote debe tener al menos 2 caracteres.")
        
        # Check uniqueness per finca
        finca = self.context.get('finca')
        if finca and self.instance:
            # Update: exclude current instance
            if Lote.objects.filter(
                finca=finca, 
                identificador__iexact=value.strip()
            ).exclude(id=self.instance.id).exists():
                raise serializers.ValidationError("Ya existe un lote con este identificador en la finca.")
        elif finca:
            # Creation: check uniqueness
            if Lote.objects.filter(
                finca=finca, 
                identificador__iexact=value.strip()
            ).exists():
                raise serializers.ValidationError("Ya existe un lote con este identificador en la finca.")
        
        return value.strip()
    
    def validate_area_hectareas(self, value):
        """Validate area in hectares."""
        if value <= 0:
            raise serializers.ValidationError("El área debe ser mayor a 0.")
        if value > 1000:
            raise serializers.ValidationError("El área no puede ser mayor a 1,000 hectáreas.")
        return value
    
    def validate_fecha_cosecha(self, value):
        """Validate harvest date."""
        fecha_plantacion = self.initial_data.get('fecha_plantacion')
        if value and fecha_plantacion and value < fecha_plantacion:
            raise serializers.ValidationError("La fecha de cosecha no puede ser anterior a la fecha de plantación.")
        return value
    
    def validate_coordenadas_lat(self, value):
        """Validate GPS latitude."""
        from core.utils import validate_latitude
        return validate_latitude(value)
    
    def validate_coordenadas_lng(self, value):
        """Validate GPS longitude."""
        from core.utils import validate_longitude
        return validate_longitude(value)
    
    def validate(self, attrs):
        """General validations."""
        from core.utils import validate_coordinates
        if not attrs.get('variedad', '').strip():
            raise serializers.ValidationError("La variedad es requerida.")
        validate_coordinates(attrs)
        return attrs


class LoteListSerializer(serializers.ModelSerializer):
    """Optimized serializer for lote listings."""
    finca_nombre = serializers.CharField(source='finca.nombre', read_only=True)
    agricultor_nombre = serializers.CharField(source='finca.agricultor.get_full_name', read_only=True)
    ubicacion_completa = serializers.ReadOnlyField()
    total_analisis = serializers.ReadOnlyField()
    analisis_procesados = serializers.ReadOnlyField()
    edad_meses = serializers.ReadOnlyField()
    
    class Meta:
        model = Lote
        fields = (
            'id', 'identificador', 'variedad', 'finca_nombre', 'agricultor_nombre',
            'area_hectareas', 'estado', 'total_analisis', 'analisis_procesados',
            'edad_meses', 'activo', 'fecha_plantacion', 'fecha_cosecha'
        )


class LoteDetailSerializer(LoteSerializer):
    """Detailed serializer for lotes with related data."""
    cacao_images = serializers.SerializerMethodField()
    
    class Meta(LoteSerializer.Meta):
        fields = LoteSerializer.Meta.fields + ('cacao_images',)
    
    def get_cacao_images(self, obj):
        """Get cacao images from lote."""
        from .image_serializers import CacaoImageSerializer
        return CacaoImageSerializer(obj.cacao_images.all()[:10], many=True).data


class LoteStatsSerializer(serializers.Serializer):
    """Serializer for lote statistics."""
    total_lotes = serializers.IntegerField()
    lotes_activos = serializers.IntegerField()
    lotes_por_estado = serializers.DictField()
    total_area_hectareas = serializers.DecimalField(max_digits=12, decimal_places=2)
    promedio_area_hectareas = serializers.DecimalField(max_digits=10, decimal_places=2)
    variedades_mas_comunes = serializers.ListField()
    calidad_promedio_general = serializers.FloatField()

