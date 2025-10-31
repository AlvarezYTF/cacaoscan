"""
Vistas para documentos legales de CacaoScan.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny


class TermsView(APIView):
    """
    Vista para obtener los términos y condiciones de CacaoScan.
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        return Response({
            "title": "Términos y Condiciones - CacaoScan",
            "content": """
CacaoScan es una plataforma desarrollada por aprendices del SENA como parte del programa de formación técnica en análisis de sistemas.

1. ACEPTACIÓN DE LOS TÉRMINOS

Al acceder y utilizar CacaoScan, usted acepta estar sujeto a estos términos y condiciones de uso. Si no está de acuerdo con alguna parte de estos términos, no debe utilizar nuestra plataforma.

2. DESCRIPCIÓN DEL SERVICIO

CacaoScan proporciona herramientas para el análisis de granos de cacao mediante técnicas de machine learning, permitiendo a los usuarios:
- Subir imágenes de granos de cacao
- Realizar análisis de dimensiones y peso
- Generar reportes y estadísticas
- Gestionar fincas y lotes de cultivo

3. REGISTRO Y CUENTA DE USUARIO

3.1. Para utilizar ciertas funciones de CacaoScan, debe registrarse y crear una cuenta.
3.2. Usted es responsable de mantener la confidencialidad de su cuenta y contraseña.
3.3. Debe proporcionar información precisa y completa durante el registro.
3.4. CacaoScan se reserva el derecho de rechazar o cancelar cuentas que violen estos términos.

4. USO ACEPTABLE

4.1. Usted se compromete a utilizar CacaoScan únicamente para fines legales y apropiados.
4.2. No debe:
    - Intentar acceder a áreas no autorizadas de la plataforma
    - Interferir con el funcionamiento del servicio
    - Cargar contenido malicioso o que viole derechos de terceros
    - Utilizar la plataforma para actividades comerciales no autorizadas

5. PROPIEDAD INTELECTUAL

5.1. Todos los contenidos de CacaoScan, incluyendo diseño, textos, gráficos y software, son propiedad de los desarrolladores o sus licenciantes.
5.2. El contenido generado por los usuarios mediante la plataforma pertenece al usuario, pero CacaoScan puede utilizarlo para mejorar el servicio.

6. PRIVACIDAD

El uso de sus datos personales se rige por nuestra Política de Privacidad, que forma parte integral de estos términos.

7. DISPONIBILIDAD DEL SERVICIO

7.1. CacaoScan se proporciona "tal cual" sin garantías de ningún tipo.
7.2. No garantizamos que el servicio esté disponible de forma ininterrumpida o libre de errores.
7.3. Nos reservamos el derecho de suspender o modificar el servicio en cualquier momento.

8. LIMITACIÓN DE RESPONSABILIDAD

8.1. CacaoScan no será responsable por daños directos, indirectos, incidentales o consecuentes resultantes del uso de la plataforma.
8.2. Los resultados de los análisis son estimaciones y no deben ser considerados como mediciones oficiales sin validación adicional.

9. MODIFICACIONES DE LOS TÉRMINOS

Nos reservamos el derecho de modificar estos términos en cualquier momento. Los cambios entrarán en vigor al publicarlos en la plataforma.

10. TERMINACIÓN

CacaoScan puede suspender o terminar su acceso al servicio en cualquier momento, con o sin causa, con o sin previo aviso.

11. LEY APLICABLE

Estos términos se rigen por las leyes de la República de Colombia.

12. CONTACTO

Para consultas sobre estos términos, puede contactarnos a través de los canales oficiales del SENA.

Fecha de última actualización: Octubre 2025
"""
        })


class PrivacyView(APIView):
    """
    Vista para obtener la política de privacidad de CacaoScan.
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        return Response({
            "title": "Política de Privacidad - CacaoScan",
            "content": """
CacaoScan cumple con la Ley 1581 de 2012 sobre protección de datos personales y el Decreto 1377 de 2013.

1. INFORMACIÓN QUE RECOPILAMOS

1.1. Información de Registro:
    - Nombre completo
    - Correo electrónico
    - Número de teléfono (opcional)
    - Información de perfil profesional

1.2. Información de Uso:
    - Imágenes de granos de cacao que usted sube
    - Resultados de análisis realizados
    - Información de fincas y lotes registrados
    - Historial de actividad en la plataforma

1.3. Información Técnica:
    - Dirección IP
    - Tipo de navegador
    - Sistema operativo
    - Fecha y hora de acceso

2. CÓMO UTILIZAMOS SU INFORMACIÓN

2.1. Para proporcionar y mejorar nuestros servicios.
2.2. Para personalizar su experiencia en la plataforma.
2.3. Para comunicarnos con usted sobre su cuenta y nuestros servicios.
2.4. Para cumplir con obligaciones legales y regulatorias.
2.5. Para entrenar y mejorar nuestros modelos de machine learning (con imágenes anonimizadas).

3. COMPARTIR INFORMACIÓN

3.1. No vendemos ni alquilamos su información personal a terceros.
3.2. Podemos compartir información:
    - Con proveedores de servicios que nos ayudan a operar la plataforma
    - Cuando sea requerido por ley o proceso legal
    - Para proteger los derechos y seguridad de CacaoScan y sus usuarios

4. SEGURIDAD DE LOS DATOS

4.1. Implementamos medidas de seguridad técnicas y organizacionales para proteger su información.
4.2. Utilizamos encriptación para datos sensibles.
4.3. Sin embargo, ningún método de transmisión por Internet es 100% seguro.

5. SUS DERECHOS

De acuerdo con la Ley 1581 de 2012, usted tiene derecho a:

5.1. Conocer, actualizar y rectificar sus datos personales.
5.2. Solicitar prueba de la autorización otorgada.
5.3. Revocar la autorización y/o solicitar la supresión del dato.
5.4. Acceder de forma gratuita a sus datos personales.
5.5. Presentar quejas ante la Superintendencia de Industria y Comercio.

6. RETENCIÓN DE DATOS

6.1. Conservamos su información mientras su cuenta esté activa o según sea necesario para proporcionar nuestros servicios.
6.2. Podemos retener cierta información incluso después del cierre de su cuenta para cumplir con obligaciones legales.

7. COOKIES Y TECNOLOGÍAS SIMILARES

7.1. Utilizamos cookies para mejorar su experiencia en la plataforma.
7.2. Puede configurar su navegador para rechazar cookies, aunque esto puede afectar algunas funcionalidades.

8. MENORES DE EDAD

CacaoScan no está dirigido a menores de 18 años. No recopilamos intencionalmente información de menores.

9. CAMBIOS A ESTA POLÍTICA

Podemos actualizar esta política de privacidad ocasionalmente. Le notificaremos de cambios significativos.

10. CONTACTO

Para ejercer sus derechos de protección de datos o hacer consultas sobre esta política, puede contactarnos a través de los canales oficiales del SENA.

Fecha de última actualización: Octubre 2025
"""
        })
