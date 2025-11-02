"""
Serializers para la app personas.

INTEGRACIÃ“N CON MÃ“DULOS:
- Usa Parametro (catÃ¡logos) para tipo_documento y genero
- Usa Departamento y Municipio (ubicaciones) para ubicaciÃ³n
"""
from rest_framework import serializers
from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone
from datetime import date
import re
from catalogos.models import Parametro, Departamento, Municipio
from .models import Persona


class PersonaSerializer(serializers.ModelSerializer):
    """Serializer estÃ¡ndar para Persona con informaciÃ³n completa de catÃ¡logos."""
    # Campos anidados de catÃ¡logos
    tipo_documento_info = serializers.SerializerMethodField()
    genero_info = serializers.SerializerMethodField()
    departamento_info = serializers.SerializerMethodField()
    municipio_info = serializers.SerializerMethodField()
    email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = Persona
        fields = [
            'id', 'user', 'email', 'tipo_documento', 'tipo_documento_info', 
            'numero_documento', 'primer_nombre', 'segundo_nombre',
            'primer_apellido', 'segundo_apellido', 'telefono', 'direccion',
            'genero', 'genero_info', 'fecha_nacimiento',
            'departamento', 'departamento_info', 'municipio', 'municipio_info',
            'fecha_creacion'
        ]
        read_only_fields = ['user', 'fecha_creacion', 'email']
    
    def get_tipo_documento_info(self, obj):
        """Devuelve informaciÃ³n del tipo de documento."""
        if obj.tipo_documento:
            return {
                'id': obj.tipo_documento.id,
                'codigo': obj.tipo_documento.codigo,
                'nombre': obj.tipo_documento.nombre
            }
        return None
    
    def get_genero_info(self, obj):
        """Devuelve informaciÃ³n del gÃ©nero."""
        if obj.genero:
            return {
                'id': obj.genero.id,
                'codigo': obj.genero.codigo,
                'nombre': obj.genero.nombre
            }
        return None
    
    def get_departamento_info(self, obj):
        """Devuelve informaciÃ³n del departamento."""
        if obj.departamento:
            return {
                'id': obj.departamento.id,
                'codigo': obj.departamento.codigo,
                'nombre': obj.departamento.nombre
            }
        return None
    
    def get_municipio_info(self, obj):
        """Devuelve informaciÃ³n del municipio."""
        if obj.municipio:
            return {
                'id': obj.municipio.id,
                'codigo': obj.municipio.codigo,
                'nombre': obj.municipio.nombre
            }
        return None


class PersonaRegistroSerializer(serializers.Serializer):
    """
    Serializer para registro de usuario y persona en una sola peticiÃ³n.
    
    INTEGRACIÃ“N CON CATÃLOGOS:
    - tipo_documento: CÃ³digo del parÃ¡metro del tema TIPO_DOC (ej: 'CC', 'CE')
    - genero: CÃ³digo del parÃ¡metro del tema SEXO (ej: 'M', 'F')
    - departamento: ID del departamento
    - municipio: ID del municipio
    """
    # Campos para crear el usuario
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, min_length=8, required=True)
    
    # Campos para crear la persona
    tipo_documento = serializers.CharField(required=True, help_text="CÃ³digo del parÃ¡metro TIPO_DOC (ej: CC, CE)")
    numero_documento = serializers.CharField(required=True, max_length=20)
    primer_nombre = serializers.CharField(required=True, max_length=50)
    segundo_nombre = serializers.CharField(required=False, allow_blank=True, max_length=50)
    primer_apellido = serializers.CharField(required=True, max_length=50)
    segundo_apellido = serializers.CharField(required=False, allow_blank=True, max_length=50)
    telefono = serializers.CharField(required=True, max_length=15)
    direccion = serializers.CharField(required=False, allow_blank=True, max_length=255)
    genero = serializers.CharField(required=True, help_text="CÃ³digo del parÃ¡metro SEXO (ej: M, F, O)")
    fecha_nacimiento = serializers.DateField(required=False, allow_null=True)
    
    # UbicaciÃ³n (IDs de departamento y municipio)
    departamento = serializers.IntegerField(required=False, allow_null=True)
    municipio = serializers.IntegerField(required=False, allow_null=True)
    
    def validate_email(self, value):
        """Validar que el email no exista y tenga formato vÃ¡lido."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Este correo ya estÃ¡ registrado.")
        
        # ValidaciÃ³n adicional de formato de email
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, value):
            raise serializers.ValidationError("El formato del correo electrÃ³nico no es vÃ¡lido.")
        
        return value
    
    def validate_numero_documento(self, value):
        """
        Validar que el nÃºmero de documento sea Ãºnico y vÃ¡lido.
        - Solo nÃºmeros
        - Longitud entre 6 y 11 dÃ­gitos
        """
        # Eliminar espacios
        value = value.strip()
        
        # Validar que solo contenga nÃºmeros
        if not value.isdigit():
            raise serializers.ValidationError("El nÃºmero de documento solo puede contener nÃºmeros.")
        
        # Validar longitud
        if len(value) < 6 or len(value) > 11:
            raise serializers.ValidationError("El nÃºmero de documento debe tener entre 6 y 11 dÃ­gitos.")
        
        # Validar unicidad
        if Persona.objects.filter(numero_documento=value).exists():
            raise serializers.ValidationError("Este nÃºmero de documento ya estÃ¡ registrado.")
        
        return value
    
    def validate_password(self, value):
        """
        Validar que la contraseÃ±a cumpla con los requisitos de seguridad:
        - MÃ­nimo 8 caracteres
        - Al menos una letra mayÃºscula
        - Al menos una letra minÃºscula
        - Al menos un nÃºmero
        """
        if len(value) < 8:
            raise serializers.ValidationError("La contraseÃ±a debe tener al menos 8 caracteres.")
        
        if not re.search(r"[A-Z]", value):
            raise serializers.ValidationError("La contraseÃ±a debe contener al menos una letra mayÃºscula.")
        
        if not re.search(r"[a-z]", value):
            raise serializers.ValidationError("La contraseÃ±a debe contener al menos una letra minÃºscula.")
        
        if not re.search(r"[0-9]", value):
            raise serializers.ValidationError("La contraseÃ±a debe contener al menos un nÃºmero.")
        
        return value
    
    def validate_telefono(self, value):
        """
        Validar que el telÃ©fono sea vÃ¡lido:
        - Solo nÃºmeros (se permiten espacios y guiones que serÃ¡n eliminados)
        - Longitud entre 7 y 15 dÃ­gitos
        - Ãšnico (no registrado previamente)
        """
        # Eliminar espacios, guiones y parÃ©ntesis
        cleaned_value = re.sub(r'[\s\-\(\)]', '', value)
        
        # Validar que solo contenga nÃºmeros (puede tener + al inicio)
        if cleaned_value.startswith('+'):
            cleaned_value = cleaned_value[1:]
        
        if not cleaned_value.isdigit():
            raise serializers.ValidationError("El telÃ©fono solo puede contener nÃºmeros.")
        
        # Validar longitud
        if len(cleaned_value) < 7 or len(cleaned_value) > 15:
            raise serializers.ValidationError("El telÃ©fono debe tener entre 7 y 15 dÃ­gitos.")
        
        # Validar unicidad - buscar si ya existe este telÃ©fono
        if Persona.objects.filter(telefono=value).exists():
            raise serializers.ValidationError("Este nÃºmero de telÃ©fono ya estÃ¡ registrado.")
        
        return value
    
    def validate_fecha_nacimiento(self, value):
        """
        Validar que la fecha de nacimiento sea vÃ¡lida:
        - No puede ser futura
        - El usuario debe tener al menos 14 aÃ±os
        """
        if not value:
            return value
        
        hoy = timezone.now().date()
        
        # Validar que no sea futura
        if value > hoy:
            raise serializers.ValidationError("La fecha de nacimiento no puede ser futura.")
        
        # Calcular edad
        edad = hoy.year - value.year - ((hoy.month, hoy.day) < (value.month, value.day))
        
        # Validar edad mÃ­nima de 14 aÃ±os
        if edad < 14:
            raise serializers.ValidationError("El usuario debe tener al menos 14 aÃ±os.")
        
        # Validar edad mÃ¡xima razonable (opcional, ej: 120 aÃ±os)
        if edad > 120:
            raise serializers.ValidationError("La fecha de nacimiento no es vÃ¡lida.")
        
        return value
    
    def validate_primer_nombre(self, value):
        """Validar que el primer nombre solo contenga letras y espacios."""
        value = value.strip()
        if not value:
            raise serializers.ValidationError("El primer nombre es obligatorio.")
        
        if not re.match(r'^[a-zA-ZÃ¡Ã©Ã­Ã³ÃºÃÃ‰ÃÃ“ÃšÃ±Ã‘Ã¼Ãœ\s]+$', value):
            raise serializers.ValidationError("El primer nombre solo puede contener letras.")
        
        return value
    
    def validate_primer_apellido(self, value):
        """Validar que el primer apellido solo contenga letras y espacios."""
        value = value.strip()
        if not value:
            raise serializers.ValidationError("El primer apellido es obligatorio.")
        
        if not re.match(r'^[a-zA-ZÃ¡Ã©Ã­Ã³ÃºÃÃ‰ÃÃ“ÃšÃ±Ã‘Ã¼Ãœ\s]+$', value):
            raise serializers.ValidationError("El primer apellido solo puede contener letras.")
        
        return value
    
    def validate(self, data):
        """Validar referencias a catÃ¡logos y ubicaciones."""
        # Validar tipo_documento (debe ser un Parametro con tema TIPO_DOC)
        tipo_doc_codigo = data.get('tipo_documento')
        tipo_doc = Parametro.objects.filter(
            codigo=tipo_doc_codigo,
            tema__codigo='TIPO_DOC',
            activo=True
        ).first()
        
        if not tipo_doc:
            raise serializers.ValidationError({
                'tipo_documento': f"Tipo de documento '{tipo_doc_codigo}' no existe o no estÃ¡ activo."
            })
        data['tipo_documento_obj'] = tipo_doc
        
        # Validar genero (debe ser un Parametro con tema SEXO)
        genero_codigo = data.get('genero')
        genero = Parametro.objects.filter(
            codigo=genero_codigo,
            tema__codigo='SEXO',
            activo=True
        ).first()
        
        if not genero:
            raise serializers.ValidationError({
                'genero': f"GÃ©nero '{genero_codigo}' no existe o no estÃ¡ activo."
            })
        data['genero_obj'] = genero
        
        # Validar municipio (debe existir y pertenecer al departamento) - OPCIONAL
        municipio_id = data.get('municipio')
        departamento_id = data.get('departamento')
        
        if municipio_id:
            municipio = Municipio.objects.filter(id=municipio_id).first()
            if not municipio:
                raise serializers.ValidationError({
                    'municipio': f"Municipio con ID '{municipio_id}' no existe."
                })
            
            # Si se especifica departamento, validar que coincida
            if departamento_id and municipio.departamento.id != departamento_id:
                raise serializers.ValidationError({
                    'municipio': f"El municipio no pertenece al departamento especificado."
                })
            data['municipio_obj'] = municipio
        else:
            data['municipio_obj'] = None
        
        if departamento_id:
            departamento = Departamento.objects.filter(id=departamento_id).first()
            if not departamento:
                raise serializers.ValidationError({
                    'departamento': f"Departamento con ID '{departamento_id}' no existe."
                })
            data['departamento_obj'] = departamento
        else:
            data['departamento_obj'] = None
        
        return data
    
    @transaction.atomic
    def create(self, validated_data):
        """Crear el usuario y la persona en una sola transacciÃ³n."""
        # Extraer datos del usuario
        email = validated_data.pop('email')
        password = validated_data.pop('password')
        
        # Extraer objetos de catÃ¡logos ya validados
        tipo_documento = validated_data.pop('tipo_documento_obj')
        genero = validated_data.pop('genero_obj')
        departamento = validated_data.pop('departamento_obj', None)
        municipio = validated_data.pop('municipio_obj', None)
        
        # Verificar si se debe omitir la verificaciÃ³n de email (para admins)
        skip_email_verification = self.context.get('skip_email_verification', False)
        
        # Crear el usuario (username serÃ¡ el email)
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=validated_data.get('primer_nombre', ''),
            last_name=validated_data.get('primer_apellido', ''),
            is_active=True if skip_email_verification else False  # Activo si es admin
        )
        
        # Crear token de verificaciÃ³n de email
        from api.models import EmailVerificationToken
        verification_token = EmailVerificationToken.create_for_user(user)
        
        # Si es creaciÃ³n por admin, marcar como verificado
        if skip_email_verification:
            verification_token.is_verified = True
            verification_token.verified_at = timezone.now()
            verification_token.save()
        
        # Enviar email de verificaciÃ³n solo si no se omite
        if not skip_email_verification:
            try:
                from django.conf import settings
                from api.email_service import send_custom_email
                
                verification_url = f"{settings.FRONTEND_URL}/verify-email/{verification_token.token}"
                
                html_content = f"""
                <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                        <h2 style="color: #4CAF50;">Â¡Bienvenido a CacaoScan, {user.get_full_name() or user.username}!</h2>
                        <p>Gracias por registrarte en nuestra plataforma. Para completar tu registro, por favor verifica tu direcciÃ³n de correo electrÃ³nico haciendo clic en el siguiente enlace:</p>
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="{verification_url}" style="background-color: #4CAF50; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold;">Verificar mi correo</a>
                        </div>
                        <p>O copia y pega este enlace en tu navegador:</p>
                        <p style="word-break: break-all; color: #666;">{verification_url}</p>
                        <p style="margin-top: 30px; font-size: 12px; color: #999;">Este enlace expirarÃ¡ en 24 horas.</p>
                        <p style="font-size: 12px; color: #999;">Si no creaste esta cuenta, puedes ignorar este correo.</p>
                    </div>
                </body>
                </html>
                """
                
                text_content = f"""
Bienvenido a CacaoScan, {user.get_full_name() or user.username}!

Gracias por registrarte en nuestra plataforma. Para completar tu registro, por favor verifica tu direcciÃ³n de correo electrÃ³nico visitando el siguiente enlace:

{verification_url}

Este enlace expirarÃ¡ en 24 horas.

Si no creaste esta cuenta, puedes ignorar este correo.
                """
                
                send_custom_email(
                    to_emails=[user.email],
                    subject="Verifica tu correo electrÃ³nico - CacaoScan",
                    html_content=html_content,
                    text_content=text_content
                )
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error enviando email de verificaciÃ³n: {e}")
        
        # Crear la persona asociada al usuario con catÃ¡logos y ubicaciones normalizadas
        persona = Persona.objects.create(
            user=user,
            tipo_documento=tipo_documento,
            numero_documento=validated_data.get('numero_documento'),
            primer_nombre=validated_data.get('primer_nombre'),
            segundo_nombre=validated_data.get('segundo_nombre', None),
            primer_apellido=validated_data.get('primer_apellido'),
            segundo_apellido=validated_data.get('segundo_apellido', None),
            telefono=validated_data.get('telefono'),
            direccion=validated_data.get('direccion', None),
            genero=genero,
            fecha_nacimiento=validated_data.get('fecha_nacimiento', None),
            departamento=departamento,
            municipio=municipio
        )
        
        return persona
    
    def to_representation(self, instance):
        """Personalizar la representaciÃ³n de la respuesta."""
        return {
            'id': instance.id,
            'email': instance.user.email,
            'verification_required': True,  # Siempre se requiere verificaciÃ³n ahora
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
            'tipo_documento': instance.tipo_documento.codigo if instance.tipo_documento else None,
            'genero': instance.genero.codigo if instance.genero else None,
            'departamento': instance.departamento.nombre if instance.departamento else None,
            'municipio': instance.municipio.nombre if instance.municipio else None,
        }


class PersonaActualizacionSerializer(serializers.Serializer):
    """
    Serializer para actualizar los datos de una persona.
    No permite modificar el email del usuario.
    """
    # Campos bÃ¡sicos
    tipo_documento = serializers.CharField(required=False, help_text="CÃ³digo del parÃ¡metro TIPO_DOC")
    numero_documento = serializers.CharField(required=False, max_length=20)
    primer_nombre = serializers.CharField(required=False, max_length=50)
    segundo_nombre = serializers.CharField(required=False, allow_blank=True, max_length=50)
    primer_apellido = serializers.CharField(required=False, max_length=50)
    segundo_apellido = serializers.CharField(required=False, allow_blank=True, max_length=50)
    telefono = serializers.CharField(required=False, max_length=15)
    direccion = serializers.CharField(required=False, allow_blank=True, max_length=255)
    genero = serializers.CharField(required=False, help_text="CÃ³digo del parÃ¡metro SEXO")
    fecha_nacimiento = serializers.DateField(required=False, allow_null=True)
    
    # UbicaciÃ³n
    departamento = serializers.IntegerField(required=False, allow_null=True)
    municipio = serializers.IntegerField(required=False, allow_null=True)
    
    def validate_numero_documento(self, value):
        """Validar documento sin duplicar (excepto el propio usuario)."""
        value = value.strip()
        
        if not value.isdigit():
            raise serializers.ValidationError("El nÃºmero de documento solo puede contener nÃºmeros.")
        
        if len(value) < 6 or len(value) > 11:
            raise serializers.ValidationError("El nÃºmero de documento debe tener entre 6 y 11 dÃ­gitos.")
        
        # Validar unicidad excluyendo el usuario actual
        persona_actual = self.context.get('persona')
        if persona_actual:
            if Persona.objects.filter(numero_documento=value).exclude(id=persona_actual.id).exists():
                raise serializers.ValidationError("Este nÃºmero de documento ya estÃ¡ registrado.")
        
        return value
    
    def validate_telefono(self, value):
        """Validar telÃ©fono sin duplicar (excepto el propio usuario)."""
        cleaned_value = re.sub(r'[\s\-\(\)]', '', value)
        
        if cleaned_value.startswith('+'):
            cleaned_value = cleaned_value[1:]
        
        if not cleaned_value.isdigit():
            raise serializers.ValidationError("El telÃ©fono solo puede contener nÃºmeros.")
        
        if len(cleaned_value) < 7 or len(cleaned_value) > 15:
            raise serializers.ValidationError("El telÃ©fono debe tener entre 7 y 15 dÃ­gitos.")
        
        # Validar unicidad excluyendo el usuario actual
        persona_actual = self.context.get('persona')
        if persona_actual:
            if Persona.objects.filter(telefono=value).exclude(id=persona_actual.id).exists():
                raise serializers.ValidationError("Este nÃºmero de telÃ©fono ya estÃ¡ registrado.")
        
        return value
    
    def validate_fecha_nacimiento(self, value):
        """Validar fecha de nacimiento."""
        if not value:
            return value
        
        hoy = timezone.now().date()
        
        if value > hoy:
            raise serializers.ValidationError("La fecha de nacimiento no puede ser futura.")
        
        edad = hoy.year - value.year - ((hoy.month, hoy.day) < (value.month, value.day))
        
        if edad < 14:
            raise serializers.ValidationError("El usuario debe tener al menos 14 aÃ±os.")
        
        if edad > 120:
            raise serializers.ValidationError("La fecha de nacimiento no es vÃ¡lida.")
        
        return value
    
    def validate_primer_nombre(self, value):
        """Validar primer nombre."""
        value = value.strip()
        if not value:
            raise serializers.ValidationError("El primer nombre es obligatorio.")
        
        if not re.match(r'^[a-zA-ZÃ¡Ã©Ã­Ã³ÃºÃÃ‰ÃÃ“ÃšÃ±Ã‘Ã¼Ãœ\s]+$', value):
            raise serializers.ValidationError("El primer nombre solo puede contener letras.")
        
        return value
    
    def validate_primer_apellido(self, value):
        """Validar primer apellido."""
        value = value.strip()
        if not value:
            raise serializers.ValidationError("El primer apellido es obligatorio.")
        
        if not re.match(r'^[a-zA-ZÃ¡Ã©Ã­Ã³ÃºÃÃ‰ÃÃ“ÃšÃ±Ã‘Ã¼Ãœ\s]+$', value):
            raise serializers.ValidationError("El primer apellido solo puede contener letras.")
        
        return value
    
    def validate(self, data):
        """Validar catÃ¡logos y ubicaciones."""
        # Validar tipo_documento si se proporciona
        if 'tipo_documento' in data:
            tipo_doc_codigo = data['tipo_documento']
            tipo_doc = Parametro.objects.filter(
                codigo=tipo_doc_codigo,
                tema__codigo='TIPO_DOC',
                activo=True
            ).first()
            
            if not tipo_doc:
                raise serializers.ValidationError({
                    'tipo_documento': f"Tipo de documento '{tipo_doc_codigo}' no existe o no estÃ¡ activo."
                })
            data['tipo_documento_obj'] = tipo_doc
        
        # Validar genero si se proporciona
        if 'genero' in data:
            genero_codigo = data['genero']
            genero = Parametro.objects.filter(
                codigo=genero_codigo,
                tema__codigo='SEXO',
                activo=True
            ).first()
            
            if not genero:
                raise serializers.ValidationError({
                    'genero': f"GÃ©nero '{genero_codigo}' no existe o no estÃ¡ activo."
                })
            data['genero_obj'] = genero
        
        # Validar ubicaciones
        if 'municipio' in data and data['municipio']:
            municipio = Municipio.objects.filter(id=data['municipio']).first()
            if not municipio:
                raise serializers.ValidationError({
                    'municipio': f"Municipio con ID '{data['municipio']}' no existe."
                })
            data['municipio_obj'] = municipio
        else:
            data['municipio_obj'] = None
        
        if 'departamento' in data and data['departamento']:
            departamento = Departamento.objects.filter(id=data['departamento']).first()
            if not departamento:
                raise serializers.ValidationError({
                    'departamento': f"Departamento con ID '{data['departamento']}' no existe."
                })
            data['departamento_obj'] = departamento
        else:
            data['departamento_obj'] = None
        
        return data
    
    def update(self, instance, validated_data):
        """Actualizar la persona con los datos validados."""
        # Actualizar campos de catÃ¡logos si se proporcionan
        if 'tipo_documento_obj' in validated_data:
            instance.tipo_documento = validated_data['tipo_documento_obj']
        
        if 'genero_obj' in validated_data:
            instance.genero = validated_data['genero_obj']
        
        if 'departamento_obj' in validated_data:
            instance.departamento = validated_data['departamento_obj']
        
        if 'municipio_obj' in validated_data:
            instance.municipio = validated_data['municipio_obj']
        
        # Actualizar campos simples
        simple_fields = [
            'numero_documento', 'primer_nombre', 'segundo_nombre',
            'primer_apellido', 'segundo_apellido', 'telefono',
            'direccion', 'fecha_nacimiento'
        ]
        
        for field in simple_fields:
            if field in validated_data:
                setattr(instance, field, validated_data[field])
        
        instance.save()
        return instance

