from rest_framework import serializers
from .models import Tema, Parametro, Departamento, Municipio


class ParametroSerializer(serializers.ModelSerializer):
    """Serializer para ParÃ¡metro (sin tema anidado)"""
    
    class Meta:
        model = Parametro
        fields = ['id', 'codigo', 'nombre', 'descripcion', 'activo']
        read_only_fields = ['id']


class ParametroDetalleSerializer(serializers.ModelSerializer):
    """Serializer para ParÃ¡metro con informaciÃ³n del tema"""
    tema_nombre = serializers.CharField(source='tema.nombre', read_only=True)
    tema_codigo = serializers.CharField(source='tema.codigo', read_only=True)
    
    class Meta:
        model = Parametro
        fields = ['id', 'tema', 'tema_nombre', 'tema_codigo', 'codigo', 'nombre', 'descripcion', 'activo']
        read_only_fields = ['id']


class TemaSerializer(serializers.ModelSerializer):
    """Serializer para Tema sin parÃ¡metros"""
    
    class Meta:
        model = Tema
        fields = ['id', 'codigo', 'nombre', 'descripcion', 'activo', 'parametros_count']
        read_only_fields = ['id', 'parametros_count']


class TemaConParametrosSerializer(serializers.ModelSerializer):
    """Serializer para Tema con sus parÃ¡metros incluidos"""
    parametros = ParametroSerializer(many=True, read_only=True)
    parametros_activos = serializers.SerializerMethodField()
    
    class Meta:
        model = Tema
        fields = ['id', 'codigo', 'nombre', 'descripcion', 'activo', 'parametros', 'parametros_activos']
        read_only_fields = ['id']
    
    def get_parametros_activos(self, obj):
        """Devuelve solo los parÃ¡metros activos"""
        parametros = obj.parametros.filter(activo=True)
        return ParametroSerializer(parametros, many=True).data


class ParametroCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear un nuevo parÃ¡metro"""
    
    class Meta:
        model = Parametro
        fields = ['tema', 'codigo', 'nombre', 'descripcion', 'activo']
    
    def validate(self, data):
        """Valida que el cÃ³digo del parÃ¡metro sea Ãºnico dentro del tema"""
        tema = data.get('tema')
        codigo = data.get('codigo')
        
        if tema and codigo:
            existe = Parametro.objects.filter(tema=tema, codigo=codigo).exists()
            if existe and self.instance is None:
                raise serializers.ValidationError({
                    'codigo': f'Ya existe un parÃ¡metro con el cÃ³digo "{codigo}" para el tema "{tema.nombre}"'
                })
        
        return data


# Serializers para Departamentos y Municipios

class MunicipioSerializer(serializers.ModelSerializer):
    """Serializer para Municipio (sin departamento anidado)"""
    
    class Meta:
        model = Municipio
        fields = ['id', 'codigo', 'nombre']
        read_only_fields = ['id']


class MunicipioDetalleSerializer(serializers.ModelSerializer):
    """Serializer para Municipio con informaciÃ³n del departamento"""
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
        """Valida que el cÃ³digo del municipio sea Ãºnico dentro del departamento"""
        departamento = data.get('departamento')
        codigo = data.get('codigo')
        
        if departamento and codigo:
            existe = Municipio.objects.filter(departamento=departamento, codigo=codigo).exists()
            if existe and self.instance is None:
                raise serializers.ValidationError({
                    'codigo': f'Ya existe un municipio con el cÃ³digo "{codigo}" en el departamento "{departamento.nombre}"'
                })
        
        return data


