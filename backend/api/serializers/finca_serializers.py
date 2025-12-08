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
    """
    Serializer for fincas with complete validations.
    
    NOTA DE OPTIMIZACIÓN:
    Para evitar consultas N+1, las vistas deben usar select_related al obtener Finca:
    Finca.objects.select_related('agricultor').prefetch_related('lotes')
    """
    agricultor_name = serializers.CharField(source='agricultor.get_full_name', read_only=True)
    agricultor_email = serializers.CharField(source='agricultor.email', read_only=True)
    ubicacion_completa = serializers.ReadOnlyField()
    estadisticas = serializers.SerializerMethodField()
    # Alias fields for compatibility with tests
    area_total = serializers.DecimalField(source='hectareas', max_digits=10, decimal_places=2, read_only=True)
    propietario = serializers.PrimaryKeyRelatedField(source='agricultor', read_only=True)
    
    class Meta:
        model = Finca
        fields = (
            'id', 'nombre', 'ubicacion', 'municipio', 'departamento', 
            'hectareas', 'area_total', 'agricultor', 'propietario', 'agricultor_name', 'agricultor_email',
            'descripcion', 'coordenadas_lat', 'coordenadas_lng', 
            'fecha_registro', 'activa', 'ubicacion_completa', 'estadisticas',
            'altitud', 'tipo_suelo', 'clima', 'estado', 'precipitacion_anual', 'temperatura_promedio',
            'created_at', 'updated_at'
        )
        read_only_fields = (
            'id', 'fecha_registro', 'created_at', 'updated_at', 
            'ubicacion_completa', 'estadisticas', 'agricultor', 'area_total', 'propietario'
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
        # Priority: context.agricultor > instance.agricultor > request.user
        agricultor = self.context.get('agricultor')
        if not agricultor and self.instance and hasattr(self.instance, 'agricultor'):
            agricultor = self.instance.agricultor
        if not agricultor and self.context.get('request'):
            agricultor = self.context.get('request').user
        
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
        if value is None:
            raise serializers.ValidationError("Las hectáreas son requeridas.")
        if value < 0:
            raise serializers.ValidationError("Las hectáreas deben ser mayores o iguales a 0.")
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
    
    def _validate_field(self, attrs, field_name, error_message, errors):
        """Validate a single required field."""
        field_value = attrs.get(field_name, '')
        if not field_value or (isinstance(field_value, str) and not field_value.strip()):
            errors[field_name] = [error_message]
    
    def _validate_required_fields(self, attrs, errors, is_partial=False):
        """Validate required fields."""
        if is_partial:
            if 'municipio' in attrs:
                self._validate_field(attrs, 'municipio', "El municipio es requerido.", errors)
            if 'departamento' in attrs:
                self._validate_field(attrs, 'departamento', "El departamento es requerido.", errors)
        else:
            self._validate_field(attrs, 'municipio', "El municipio es requerido.", errors)
            self._validate_field(attrs, 'departamento', "El departamento es requerido.", errors)

    def _handle_coordinate_validation_error(self, e, errors):
        """Handle coordinate validation errors."""
        error_str = str(e)
        if 'coordenadas_lat' in error_str or 'coordenadas_lng' in error_str:
            errors.setdefault('non_field_errors', []).append(error_str)
        else:
            if 'coordenadas_lat' not in errors:
                errors['coordenadas_lat'] = []
            if 'coordenadas_lng' not in errors:
                errors['coordenadas_lng'] = []
            errors.setdefault('non_field_errors', []).append(error_str)

    def validate(self, attrs):
        """General validations."""
        from core.utils import validate_coordinates
        errors = {}
        
        # Check if this is a partial update
        is_partial = self.partial
        
        self._validate_required_fields(attrs, errors, is_partial=is_partial)
        
        try:
            validate_coordinates(attrs)
        except Exception as e:
            self._handle_coordinate_validation_error(e, errors)
        
        if errors:
            raise serializers.ValidationError(errors)
        
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
    # Alias field for compatibility with tests (accept both input and output)
    area = serializers.DecimalField(source='area_hectareas', max_digits=8, decimal_places=2, required=False, allow_null=True)
    # Make nombre optional in input, will be generated from identificador if not provided
    nombre = serializers.CharField(max_length=200, required=False, allow_blank=True)
    
    class Meta:
        model = Lote
        fields = (
            'id', 'finca', 'finca_nombre', 'finca_ubicacion', 'agricultor_nombre',
            'identificador', 'nombre', 'variedad', 'fecha_plantacion', 'fecha_cosecha',
            'area_hectareas', 'area', 'estado', 'descripcion', 'coordenadas_lat', 
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
        if value is None:
            raise serializers.ValidationError("El área es requerida.")
        if value < 0:
            raise serializers.ValidationError("El área debe ser mayor o igual a 0.")
        if value > 1000:
            raise serializers.ValidationError("El área no puede ser mayor a 1,000 hectáreas.")
        return value
    
    def validate_area(self, value):
        """Validate area alias (maps to area_hectareas)."""
        if value is None:
            return None
        if value < 0:
            raise serializers.ValidationError("El área debe ser mayor o igual a 0.")
        if value > 1000:
            raise serializers.ValidationError("El área no puede ser mayor a 1,000 hectáreas.")
        # Normalize to float to ensure consistent type
        return float(value)
    
    def _parse_fecha_plantacion(self, fecha_plantacion):
        """Parse fecha_plantacion from string to date if needed."""
        if not fecha_plantacion:
            return None
        
        if isinstance(fecha_plantacion, str):
            from datetime import datetime
            try:
                return datetime.strptime(fecha_plantacion, '%Y-%m-%d').date()
            except ValueError:
                try:
                    return datetime.fromisoformat(fecha_plantacion).date()
                except ValueError:
                    return None
        return fecha_plantacion

    def _validate_fecha_cosecha_basic(self, value):
        """Validate basic fecha_cosecha constraints."""
        from datetime import date
        from django.utils import timezone
        
        if value.year < 1900:
            raise serializers.ValidationError("La fecha de cosecha debe ser posterior a 1900.")
        
        today = timezone.now().date()
        if value > today:
            raise serializers.ValidationError("La fecha de cosecha no puede ser futura.")

    def validate_fecha_cosecha(self, value):
        """Validate harvest date."""
        if value is None:
            return None
        
        self._validate_fecha_cosecha_basic(value)
        
        fecha_plantacion = self._parse_fecha_plantacion(self.initial_data.get('fecha_plantacion'))
        if fecha_plantacion and value < fecha_plantacion:
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
    
    def _handle_coordinate_validation_error(self, e, errors):
        """Handle coordinate validation errors."""
        error_str = str(e)
        if 'coordenadas_lat' in error_str or 'coordenadas_lng' in error_str:
            errors.setdefault('non_field_errors', []).append(error_str)
        else:
            if 'coordenadas_lat' not in errors:
                errors['coordenadas_lat'] = []
            if 'coordenadas_lng' not in errors:
                errors['coordenadas_lng'] = []
            errors.setdefault('non_field_errors', []).append(error_str)
    
    def _handle_area_alias(self, attrs):
        """Handle area alias mapping to area_hectareas."""
        if 'area' in attrs and 'area_hectareas' not in attrs:
            attrs['area_hectareas'] = attrs.pop('area')
        elif 'area' in attrs and 'area_hectareas' in attrs:
            attrs.pop('area')
    
    def validate(self, attrs):
        """General validations and handle area alias mapping."""
        from core.utils import validate_coordinates
        
        self._handle_area_alias(attrs)
        
        errors = {}
        
        variedad = attrs.get('variedad', '')
        if not variedad or (isinstance(variedad, str) and not variedad.strip()):
            errors['variedad'] = ["La variedad es requerida."]
        
        # Generate nombre from identificador if not provided
        if 'nombre' not in attrs or not attrs.get('nombre'):
            identificador = attrs.get('identificador', '')
            if identificador:
                attrs['nombre'] = identificador.strip()
            else:
                errors['nombre'] = ["El nombre del lote es requerido."]
        
        try:
            validate_coordinates(attrs)
        except Exception as e:
            self._handle_coordinate_validation_error(e, errors)
        
        if errors:
            raise serializers.ValidationError(errors)
        
        return attrs


class LoteListSerializer(serializers.ModelSerializer):
    """Optimized serializer for lote listings."""
    finca_nombre = serializers.CharField(source='finca.nombre', read_only=True)
    agricultor_nombre = serializers.CharField(source='finca.agricultor.get_full_name', read_only=True)
    ubicacion_completa = serializers.SerializerMethodField()
    total_analisis = serializers.ReadOnlyField()
    analisis_procesados = serializers.ReadOnlyField()
    edad_meses = serializers.ReadOnlyField()
    
    class Meta:
        model = Lote
        fields = (
            'id', 'identificador', 'variedad', 'finca_nombre', 'agricultor_nombre',
            'area_hectareas', 'estado', 'total_analisis', 'analisis_procesados',
            'edad_meses', 'activo', 'fecha_plantacion', 'fecha_cosecha', 'ubicacion_completa'
        )
    
    def get_ubicacion_completa(self, obj):
        """Get complete location."""
        return obj.ubicacion_completa if hasattr(obj, 'ubicacion_completa') else f"{obj.finca.ubicacion}, {obj.finca.municipio}, {obj.finca.departamento}"


class LoteDetailSerializer(LoteSerializer):
    """Detailed serializer for lotes with related data."""
    cacao_images = serializers.SerializerMethodField()
    
    class Meta(LoteSerializer.Meta):
        fields = LoteSerializer.Meta.fields + ('cacao_images',)
    
    def get_cacao_images(self, obj):
        """Get cacao images from lote."""
        try:
            from .image_serializers import CacaoImageSerializer
            if hasattr(obj, 'cacao_images'):
                images = obj.cacao_images.all()[:10]
                return CacaoImageSerializer(images, many=True).data
            return []
        except Exception:
            # Return empty list if there's any error accessing images
            return []


class LoteStatsSerializer(serializers.Serializer):
    """Serializer for lote statistics."""
    total_lotes = serializers.IntegerField()
    lotes_activos = serializers.IntegerField()
    lotes_por_estado = serializers.DictField()
    total_area_hectareas = serializers.DecimalField(max_digits=12, decimal_places=2)
    promedio_area_hectareas = serializers.DecimalField(max_digits=10, decimal_places=2)
    variedades_mas_comunes = serializers.ListField()
    calidad_promedio_general = serializers.FloatField()

