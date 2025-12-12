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
    Finca.objects.select_related('agricultor', 'municipio', 'municipio__departamento').prefetch_related('lotes')
    """
    agricultor_name = serializers.CharField(source='agricultor.get_full_name', read_only=True)
    agricultor_email = serializers.CharField(source='agricultor.email', read_only=True)
    ubicacion_completa = serializers.ReadOnlyField()
    estadisticas = serializers.SerializerMethodField()
    # Departamento is now read-only, obtained from municipio.departamento
    departamento = serializers.SerializerMethodField()
    municipio_nombre = serializers.SerializerMethodField()
    departamento_nombre = serializers.SerializerMethodField()
    # Alias fields for compatibility with tests
    area_total = serializers.DecimalField(source='hectareas', max_digits=10, decimal_places=2, read_only=True)
    propietario = serializers.PrimaryKeyRelatedField(source='agricultor', read_only=True)
    
    class Meta:
        model = Finca
        fields = (
            'id', 'nombre', 'ubicacion', 'municipio', 'departamento', 
            'municipio_nombre', 'departamento_nombre',
            'hectareas', 'area_total', 'agricultor', 'propietario', 'agricultor_name', 'agricultor_email',
            'descripcion', 'coordenadas_lat', 'coordenadas_lng', 
            'fecha_registro', 'activa', 'ubicacion_completa', 'estadisticas',
            'altitud', 'tipo_suelo', 'clima', 'estado', 'precipitacion_anual', 'temperatura_promedio',
            'created_at', 'updated_at'
        )
        read_only_fields = (
            'id', 'fecha_registro', 'created_at', 'updated_at', 
            'ubicacion_completa', 'estadisticas', 'agricultor', 'area_total', 'propietario', 'departamento',
            'municipio_nombre', 'departamento_nombre'
        )
    
    def get_departamento(self, obj):
        """Get departamento from municipio.departamento (normalized relationship)."""
        if obj.municipio and hasattr(obj.municipio, 'departamento'):
            return obj.municipio.departamento.id
        return None
    
    def get_municipio_nombre(self, obj):
        """Get municipio name for frontend convenience."""
        if obj.municipio:
            return obj.municipio.nombre
        return None
    
    def get_departamento_nombre(self, obj):
        """Get departamento name for frontend convenience."""
        if obj.municipio and hasattr(obj.municipio, 'departamento'):
            return obj.municipio.departamento.nombre
        return None
    
    def get_estadisticas(self, obj):
        """Get finca statistics."""
        try:
            stats = obj.get_estadisticas()
            # Ensure total_lotes is included
            if 'total_lotes' not in stats:
                # Fallback: count lotes directly
                stats['total_lotes'] = obj.lotes.count() if hasattr(obj, 'lotes') else 0
            return stats
        except Exception as e:
            # Log the error for debugging
            import logging
            logger = logging.getLogger("cacaoscan.api")
            logger.error(f"Error obteniendo estadísticas de finca {obj.id}: {e}", exc_info=True)
            # Return empty statistics if there's an error, but try to get total_lotes directly
            total_lotes = 0
            try:
                if hasattr(obj, 'lotes'):
                    total_lotes = obj.lotes.count()
            except Exception:
                pass
            return {
                'total_lotes': total_lotes,
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
        
        # Check uniqueness per agricultor (only for active fincas)
        # Priority: context.agricultor > instance.agricultor > request.user
        agricultor = self.context.get('agricultor')
        if not agricultor and self.instance and hasattr(self.instance, 'agricultor'):
            agricultor = self.instance.agricultor
        if not agricultor and self.context.get('request'):
            agricultor = self.context.get('request').user
        
        if agricultor and self.instance:
            # Update: exclude current instance and only check active fincas
            if Finca.objects.filter(
                agricultor=agricultor, 
                nombre__iexact=value.strip(),
                activa=True
            ).exclude(id=self.instance.id).exists():
                raise serializers.ValidationError("Ya tienes una finca con este nombre.")
        elif agricultor:
            # Creation: check uniqueness only for active fincas
            if Finca.objects.filter(
                agricultor=agricultor, 
                nombre__iexact=value.strip(),
                activa=True
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
        # Departamento is now obtained from municipio, so we only validate municipio
        if is_partial:
            if 'municipio' in attrs:
                self._validate_field(attrs, 'municipio', "El municipio es requerido.", errors)
        else:
            self._validate_field(attrs, 'municipio', "El municipio es requerido.", errors)

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
    """Optimized serializer for finca listings with basic statistics."""
    ubicacion_completa = serializers.SerializerMethodField()
    departamento = serializers.SerializerMethodField()
    total_lotes = serializers.SerializerMethodField()
    total_analisis = serializers.SerializerMethodField()
    
    class Meta:
        model = Finca
        fields = (
            'id', 'nombre', 'municipio', 'departamento', 'ubicacion', 
            'ubicacion_completa', 'hectareas', 'activa', 'fecha_registro', 'agricultor_id',
            'coordenadas_lat', 'coordenadas_lng', 'total_lotes', 'total_analisis'
        )
    
    def get_departamento(self, obj):
        """Get departamento from municipio.departamento (normalized relationship)."""
        if obj.municipio and hasattr(obj.municipio, 'departamento'):
            return obj.municipio.departamento.id
        return None
    
    def get_ubicacion_completa(self, obj):
        """Get complete location."""
        if obj.municipio and hasattr(obj.municipio, 'departamento'):
            return f"{obj.municipio.nombre}, {obj.municipio.departamento.nombre}"
        elif obj.municipio:
            return obj.municipio.nombre
        return obj.ubicacion
    
    def get_total_lotes(self, obj):
        """Get total number of lotes for this finca."""
        try:
            if hasattr(obj, 'lotes'):
                return obj.lotes.count()
            return 0
        except Exception:
            return 0
    
    def get_total_analisis(self, obj):
        """Get total number of analyses for this finca."""
        try:
            if hasattr(obj, 'total_analisis'):
                return obj.total_analisis
            # Fallback: count from lotes
            if hasattr(obj, 'lotes'):
                from django.db.models import Count
                return obj.lotes.aggregate(
                    total=Count('cacao_images__prediction', distinct=True)
                )['total'] or 0
            return 0
        except Exception:
            return 0


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
                    'nombre': lote.nombre,
                    'variedad': lote.variedad.nombre if lote.variedad else None,
                    'estado': lote.estado.nombre if lote.estado else None,
                    'activo': lote.activo,
                    'peso_kg': float(lote.peso_kg) if lote.peso_kg else None,
                    'fecha_recepcion': lote.fecha_recepcion.isoformat() if lote.fecha_recepcion else None,
                    'fecha_plantacion': lote.fecha_plantacion.isoformat() if lote.fecha_plantacion else None,
                    'fecha_cosecha': lote.fecha_cosecha.isoformat() if lote.fecha_cosecha else None,
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
    # Make nombre optional in input, will be generated from identificador if not provided
    nombre = serializers.CharField(max_length=200, required=False, allow_blank=True)
    
    class Meta:
        model = Lote
        fields = (
            'id', 'finca', 'finca_nombre', 'finca_ubicacion', 'agricultor_nombre',
            'identificador', 'nombre', 'variedad', 'peso_kg', 'fecha_recepcion',
            'fecha_procesamiento', 'fecha_plantacion', 'fecha_cosecha',
            'estado', 'descripcion', 'activo', 'ubicacion_completa',
            'estadisticas', 'edad_meses', 'created_at', 'updated_at'
        )
        read_only_fields = (
            'id', 'created_at', 'updated_at', 
            'ubicacion_completa', 'estadisticas', 'edad_meses'
        )
    
    def get_estadisticas(self, obj):
        """Get lote statistics."""
        try:
            return obj.get_estadisticas()
        except Exception as e:
            # Log the error for debugging
            import logging
            logger = logging.getLogger("cacaoscan.api")
            logger.error(f"Error obteniendo estadísticas de lote {obj.id}: {e}", exc_info=True)
            # Return empty statistics if there's an error
            return {
                'total_analisis': 0,
                'analisis_procesados': 0,
                'calidad_promedio': 0.0,
                'peso_kg': float(obj.peso_kg) if obj.peso_kg else 0.0,
                'edad_meses': 0,
                'estado': None,
                'activo': obj.activo if hasattr(obj, 'activo') else True,
                'fecha_plantacion': None,
                'fecha_cosecha': None,
                'fecha_recepcion': None,
                'fecha_procesamiento': None,
            }
    
    def validate_identificador(self, value):
        """Validate lote identifier."""
        # Identificador is optional, but if provided must be valid
        if value and value.strip():
            if len(value.strip()) < 2:
                raise serializers.ValidationError("El identificador debe tener al menos 2 caracteres.")
            
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
        return value or ''
    
    def validate_peso_kg(self, value):
        """Validate weight in kilograms."""
        if value is None:
            raise serializers.ValidationError("El peso en kilogramos es requerido.")
        if value <= 0:
            raise serializers.ValidationError("El peso debe ser mayor a 0.")
        if value > 100000:
            raise serializers.ValidationError("El peso no puede exceder 100,000 kg.")
        return value
    
    def validate_fecha_recepcion(self, value):
        """Validate reception date."""
        if value is None:
            raise serializers.ValidationError("La fecha de recepción es requerida.")
        from django.utils import timezone
        today = timezone.now().date()
        if value > today:
            raise serializers.ValidationError("La fecha de recepción no puede ser futura.")
        return value
    
    def validate_fecha_procesamiento(self, value):
        """Validate processing date."""
        if value is None:
            return None
        from django.utils import timezone
        today = timezone.now().date()
        if value > today:
            raise serializers.ValidationError("La fecha de procesamiento no puede ser futura.")
        # Check that it's >= fecha_recepcion (handled in model constraint, but validate here too)
        fecha_recepcion = self.initial_data.get('fecha_recepcion')
        if fecha_recepcion:
            from datetime import datetime
            try:
                if isinstance(fecha_recepcion, str):
                    fecha_recepcion = datetime.strptime(fecha_recepcion, '%Y-%m-%d').date()
                if value < fecha_recepcion:
                    raise serializers.ValidationError("La fecha de procesamiento no puede ser anterior a la fecha de recepción.")
            except (ValueError, TypeError):
                pass
        return value
    
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
    
    def validate_estado(self, value):
        """Validate estado is a valid Parametro with TEMA_ESTADO_LOTE."""
        if value is None:
            raise serializers.ValidationError("El estado es requerido.")
        
        from catalogos.models import Parametro
        from django.db.models import Q
        
        try:
            # If value is already a Parametro instance, validate it
            if hasattr(value, 'tema'):
                if value.tema.codigo != 'TEMA_ESTADO_LOTE':
                    raise serializers.ValidationError("El estado debe ser un parámetro de tipo TEMA_ESTADO_LOTE.")
                if not value.activo:
                    raise serializers.ValidationError("El estado seleccionado no está activo.")
                return value
            
            # If value is an ID (int), get the Parametro
            if isinstance(value, int):
                estado_param = Parametro.objects.get(
                    id=value,
                    tema__codigo='TEMA_ESTADO_LOTE',
                    activo=True
                )
                return estado_param
            
            # If value is a string, try to find by codigo or nombre
            if isinstance(value, str):
                estado_param = Parametro.objects.filter(
                    tema__codigo='TEMA_ESTADO_LOTE',
                    activo=True
                ).filter(
                    Q(codigo__iexact=value) | Q(nombre__iexact=value)
                ).first()
                
                if not estado_param:
                    raise serializers.ValidationError(f"Estado '{value}' no encontrado o no está activo.")
                return estado_param
            
            raise serializers.ValidationError("Formato de estado inválido.")
            
        except Parametro.DoesNotExist:
            raise serializers.ValidationError("El estado seleccionado no existe o no está activo.")
        except Exception as e:
            if isinstance(e, serializers.ValidationError):
                raise
            raise serializers.ValidationError(f"Error validando estado: {str(e)}")
    
    def validate(self, attrs):
        """General validations."""
        errors = {}
        
        # Validate variedad (required)
        variedad = attrs.get('variedad')
        if not variedad:
            errors['variedad'] = ["La variedad es requerida."]
        
        # Validate estado (required)
        estado = attrs.get('estado')
        if not estado:
            errors['estado'] = ["El estado es requerido."]
        
        # Ensure nombre is always set (required field in model)
        nombre = attrs.get('nombre', '').strip() if attrs.get('nombre') else ''
        if not nombre:
            identificador = attrs.get('identificador', '')
            if identificador:
                # Handle both string and None cases
                identificador_str = str(identificador).strip() if identificador else ''
                if identificador_str:
                    attrs['nombre'] = identificador_str
                else:
                    attrs['nombre'] = 'Bulto de cacao'
            else:
                attrs['nombre'] = 'Bulto de cacao'
        else:
            attrs['nombre'] = nombre
        
        # Ensure identificador is a string (can be empty)
        if 'identificador' in attrs:
            identificador = attrs.get('identificador')
            if identificador is None:
                attrs['identificador'] = ''
            else:
                attrs['identificador'] = str(identificador).strip()
        
        if errors:
            raise serializers.ValidationError(errors)
        
        return attrs


class LoteListSerializer(serializers.ModelSerializer):
    """Optimized serializer for lote listings."""
    finca_nombre = serializers.CharField(source='finca.nombre', read_only=True)
    agricultor_nombre = serializers.SerializerMethodField()
    ubicacion_completa = serializers.SerializerMethodField()
    total_analisis = serializers.SerializerMethodField()
    analisis_procesados = serializers.SerializerMethodField()
    edad_meses = serializers.SerializerMethodField()
    variedad_nombre = serializers.SerializerMethodField()
    
    class Meta:
        model = Lote
        fields = (
            'id', 'identificador', 'nombre', 'variedad', 'variedad_nombre', 'finca_nombre', 'agricultor_nombre',
            'peso_kg', 'fecha_recepcion', 'fecha_procesamiento', 'estado', 
            'total_analisis', 'analisis_procesados', 'edad_meses', 'activo', 
            'fecha_plantacion', 'fecha_cosecha', 'ubicacion_completa'
        )
    
    def get_agricultor_nombre(self, obj):
        """Get agricultor name safely."""
        try:
            if obj.finca and obj.finca.agricultor:
                return obj.finca.agricultor.get_full_name() or obj.finca.agricultor.username
            return ""
        except Exception:
            return ""
    
    def get_total_analisis(self, obj):
        """Get total analyses safely."""
        try:
            return obj.total_analisis if hasattr(obj, 'total_analisis') else 0
        except Exception:
            return 0
    
    def get_analisis_procesados(self, obj):
        """Get processed analyses safely."""
        try:
            return obj.analisis_procesados if hasattr(obj, 'analisis_procesados') else 0
        except Exception:
            return 0
    
    def get_edad_meses(self, obj):
        """Get age in months safely."""
        try:
            return obj.edad_meses if hasattr(obj, 'edad_meses') else 0
        except Exception:
            return 0
    
    def get_variedad_nombre(self, obj):
        """Get variedad name safely."""
        try:
            if obj.variedad:
                return obj.variedad.nombre if hasattr(obj.variedad, 'nombre') else str(obj.variedad)
            return None
        except Exception:
            return None
    
    def get_ubicacion_completa(self, obj):
        """Get complete location."""
        try:
            if hasattr(obj, 'ubicacion_completa') and obj.ubicacion_completa:
                return obj.ubicacion_completa
            # Use normalized relationship: municipio.departamento
            if obj.finca and obj.finca.municipio and hasattr(obj.finca.municipio, 'departamento'):
                return f"{obj.finca.ubicacion}, {obj.finca.municipio.nombre}, {obj.finca.municipio.departamento.nombre}"
            elif obj.finca:
                return obj.finca.ubicacion
            return ""
        except Exception:
            return ""


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

