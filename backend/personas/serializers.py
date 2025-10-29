"""
Serializers para la app personas.
"""
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import TipoDocumento, Genero, Ubicacion, Persona


class TipoDocumentoSerializer(serializers.ModelSerializer):
    """Serializer para TipoDocumento."""
    class Meta:
        model = TipoDocumento
        fields = ['id', 'codigo', 'nombre']


class GeneroSerializer(serializers.ModelSerializer):
    """Serializer para Genero."""
    class Meta:
        model = Genero
        fields = ['id', 'codigo', 'nombre']


class UbicacionSerializer(serializers.ModelSerializer):
    """Serializer para Ubicacion."""
    class Meta:
        model = Ubicacion
        fields = ['id', 'municipio', 'departamento']


class PersonaRegistroSerializer(serializers.Serializer):
    """Serializer para registro de usuario y persona en una sola petición."""
    # Campos para crear el usuario
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, min_length=8, required=True)
    
    # Campos para crear la persona
    tipo_documento = serializers.CharField(required=True)
    numero_documento = serializers.CharField(required=True, max_length=20)
    primer_nombre = serializers.CharField(required=True, max_length=50)
    segundo_nombre = serializers.CharField(required=False, allow_blank=True, max_length=50)
    primer_apellido = serializers.CharField(required=True, max_length=50)
    segundo_apellido = serializers.CharField(required=False, allow_blank=True, max_length=50)
    telefono = serializers.CharField(required=True, max_length=15)
    direccion = serializers.CharField(required=False, allow_blank=True, max_length=255)
    genero = serializers.CharField(required=True)
    fecha_nacimiento = serializers.DateField(required=False, allow_null=True)
    municipio = serializers.CharField(required=False, allow_blank=True, max_length=100)
    departamento = serializers.CharField(required=False, allow_blank=True, max_length=100)
    
    def validate_email(self, value):
        """Validar que el email no exista."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Este email ya está registrado.")
        return value
    
    def validate_numero_documento(self, value):
        """Validar que el número de documento sea único."""
        if Persona.objects.filter(numero_documento=value).exists():
            raise serializers.ValidationError("Este número de documento ya está registrado.")
        return value
    
    def create(self, validated_data):
        """Crear el usuario y la persona en una sola transacción."""
        # Extraer datos del usuario
        email = validated_data.pop('email')
        password = validated_data.pop('password')
        
        # Extraer datos de la ubicación
        municipio = validated_data.pop('municipio', None)
        departamento = validated_data.pop('departamento', None)
        
        # Obtener o crear TipoDocumento
        tipo_documento_codigo = validated_data.pop('tipo_documento')
        tipo_documento = TipoDocumento.objects.filter(codigo=tipo_documento_codigo).first()
        if not tipo_documento:
            raise serializers.ValidationError(f"Tipo de documento '{tipo_documento_codigo}' no existe.")
        
        # Obtener o crear Genero
        genero_codigo = validated_data.pop('genero')
        genero = Genero.objects.filter(codigo=genero_codigo).first()
        if not genero:
            raise serializers.ValidationError(f"Género '{genero_codigo}' no existe.")
        
        # Obtener o crear Ubicacion
        ubicacion = None
        if municipio and departamento:
            ubicacion, created = Ubicacion.objects.get_or_create(
                municipio=municipio,
                departamento=departamento
            )
        
        # Crear el usuario
        # El username será el email
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            is_active=True
        )
        
        # Crear la persona asociada al usuario
        persona = Persona.objects.create(
            user=user,
            tipo_documento=tipo_documento,
            genero=genero,
            ubicacion=ubicacion,
            **validated_data
        )
        
        return persona
    
    def to_representation(self, instance):
        """Personalizar la representación de la respuesta."""
        return {
            'id': instance.id,
            'user': {
                'id': instance.user.id,
                'email': instance.user.email
            },
            'primer_nombre': instance.primer_nombre,
            'segundo_nombre': instance.segundo_nombre,
            'primer_apellido': instance.primer_apellido,
            'segundo_apellido': instance.segundo_apellido,
            'numero_documento': instance.numero_documento,
            'telefono': instance.telefono,
            'genero': instance.genero.codigo,
            'ubicacion': UbicacionSerializer(instance.ubicacion).data if instance.ubicacion else None,
            'tipo_documento': instance.tipo_documento.codigo,
        }


class PersonaSerializer(serializers.ModelSerializer):
    """Serializer estándar para Persona."""
    tipo_documento = TipoDocumentoSerializer(read_only=True)
    genero = GeneroSerializer(read_only=True)
    ubicacion = UbicacionSerializer(read_only=True)
    
    class Meta:
        model = Persona
        fields = '__all__'
        read_only_fields = ['user', 'fecha_creacion']

