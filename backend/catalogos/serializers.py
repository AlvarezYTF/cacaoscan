from rest_framework import serializers
from .models import Tema, Parametro, Departamento, Municipio, TemaParametro


class ParametroSerializer(serializers.ModelSerializer):
    """Serializer para Parámetro (sin tema anidado)"""
    
    class Meta:
        model = Parametro
        fields = ['id', 'codigo', 'nombre', 'descripcion', 'activo']
        read_only_fields = ['id']


class ParametroDetalleSerializer(serializers.ModelSerializer):
    """Serializer para Parámetro con información de los temas"""
    temas = serializers.SerializerMethodField()
    temas_ids = serializers.SerializerMethodField()
    
    class Meta:
        model = Parametro
        fields = ['id', 'temas', 'temas_ids', 'codigo', 'nombre', 'descripcion', 'activo']
        read_only_fields = ['id']
    
    def get_temas(self, obj):
        """Devuelve información de los temas asociados"""
        temas = obj.temas.all()
        return [{'id': t.id, 'codigo': t.codigo, 'nombre': t.nombre} for t in temas]
    
    def get_temas_ids(self, obj):
        """Devuelve los IDs de los temas asociados"""
        return list(obj.temas.values_list('id', flat=True))


class TemaSerializer(serializers.ModelSerializer):
    """Serializer para Tema sin parámetros"""
    
    class Meta:
        model = Tema
        fields = ['id', 'codigo', 'nombre', 'descripcion', 'activo', 'parametros_count']
        read_only_fields = ['id', 'parametros_count']


class TemaConParametrosSerializer(serializers.ModelSerializer):
    """Serializer para Tema con sus parámetros incluidos"""
    parametros = ParametroSerializer(many=True, read_only=True)
    parametros_activos = serializers.SerializerMethodField()
    
    class Meta:
        model = Tema
        fields = ['id', 'codigo', 'nombre', 'descripcion', 'activo', 'parametros', 'parametros_activos']
        read_only_fields = ['id']
    
    def get_parametros_activos(self, obj):
        """Devuelve solo los parámetros activos"""
        parametros = obj.parametros.filter(activo=True)
        return ParametroSerializer(parametros, many=True).data


class ParametroCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear un nuevo parámetro con temas"""
    temas = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tema.objects.all(),
        help_text="Lista de IDs de temas asociados al parámetro"
    )
    
    class Meta:
        model = Parametro
        fields = ['temas', 'codigo', 'nombre', 'descripcion', 'activo']
    
    def validate(self, data):
        """Valida que el código del parámetro sea único dentro de cada tema"""
        temas = data.get('temas', [])
        codigo = data.get('codigo')
        
        if temas and codigo:
            for tema in temas:
                # Check if a parametro with this codigo already exists in this tema
                existing = Parametro.objects.filter(
                    temas=tema,
                    codigo=codigo
                ).exclude(id=self.instance.id if self.instance else None)
                
                if existing.exists():
                    raise serializers.ValidationError({
                        'codigo': f'Ya existe un parámetro con el código "{codigo}" para el tema "{tema.nombre}"'
                    })
        
        return data
    
    def create(self, validated_data):
        """Crea el parámetro y asocia los temas"""
        temas = validated_data.pop('temas', [])
        parametro = Parametro.objects.create(**validated_data)
        parametro.temas.set(temas)
        return parametro
    
    def update(self, instance, validated_data):
        """Actualiza el parámetro y sus temas"""
        temas = validated_data.pop('temas', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if temas is not None:
            instance.temas.set(temas)
        
        return instance


# Serializers para Departamentos y Municipios

class MunicipioSerializer(serializers.ModelSerializer):
    """Serializer para Municipio (sin departamento anidado)"""
    
    class Meta:
        model = Municipio
        fields = ['id', 'codigo', 'nombre']
        read_only_fields = ['id']


class MunicipioDetalleSerializer(serializers.ModelSerializer):
    """Serializer para Municipio con información del departamento"""
    departamento_nombre = serializers.CharField(source='departamento.nombre', read_only=True)
    departamento_codigo = serializers.CharField(source='departamento.codigo', read_only=True)
    
    class Meta:
        model = Municipio
        fields = ['id', 'departamento', 'departamento_nombre', 'departamento_codigo', 'codigo', 'nombre']
        read_only_fields = ['id']


class DepartamentoSerializer(serializers.ModelSerializer):
    """Serializer para Departamento sin municipios"""
    
    class Meta:
        model = Departamento
        fields = ['id', 'codigo', 'nombre', 'municipios_count']
        read_only_fields = ['id', 'municipios_count']


class DepartamentoConMunicipiosSerializer(serializers.ModelSerializer):
    """Serializer para Departamento con sus municipios incluidos"""
    municipios = MunicipioSerializer(many=True, read_only=True)
    
    class Meta:
        model = Departamento
        fields = ['id', 'codigo', 'nombre', 'municipios']
        read_only_fields = ['id']


class MunicipioCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear un nuevo municipio"""
    
    class Meta:
        model = Municipio
        fields = ['departamento', 'codigo', 'nombre']
    
    def validate(self, data):
        """Valida que el código del municipio sea único dentro del departamento"""
        departamento = data.get('departamento')
        codigo = data.get('codigo')
        
        if departamento and codigo:
            existe = Municipio.objects.filter(departamento=departamento, codigo=codigo).exists()
            if existe and self.instance is None:
                raise serializers.ValidationError({
                    'codigo': f'Ya existe un municipio con el código "{codigo}" en el departamento "{departamento.nombre}"'
                })
        
        return data


