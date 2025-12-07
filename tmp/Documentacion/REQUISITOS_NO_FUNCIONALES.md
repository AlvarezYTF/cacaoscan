# Requisitos No Funcionales (RNF) - Sistema CacaoScan

## Caso de Uso: Registrar Usuario

### Requisitos No Funcionales

**Rendimiento:**
- El sistema debe completar el registro de un nuevo usuario en un tiempo máximo de 2 segundos bajo carga normal (hasta 50 usuarios concurrentes).
- La validación de datos del formulario de registro debe ejecutarse en menos de 500 milisegundos en el cliente.

**Seguridad:**
- Las contraseñas deben almacenarse utilizando algoritmos de hash unidireccionales (bcrypt, Argon2) con un factor de costo mínimo de 12.
- El sistema debe validar la fortaleza de la contraseña antes de aceptarla (mínimo 8 caracteres, al menos una mayúscula, una minúscula, un número y un carácter especial).
- Los datos sensibles transmitidos durante el registro deben usar protocolo HTTPS con cifrado TLS 1.2 o superior.
- El sistema debe implementar protección contra ataques de fuerza bruta limitando intentos de registro a 5 por dirección IP cada 15 minutos.

**Usabilidad:**
- El formulario de registro debe ser accesible y cumplir con WCAG 2.1 nivel AA.
- Los mensajes de error de validación deben mostrarse en menos de 1 segundo después de que el usuario complete un campo.
- El proceso de registro debe completarse en máximo 3 pasos sin requerir navegación adicional.

**Confiabilidad:**
- El sistema debe mantener una tasa de éxito de registro del 99.5% bajo condiciones normales de operación.
- En caso de fallo durante el registro, el sistema debe preservar los datos ingresados (excepto contraseña) para evitar pérdida de información del usuario.

**Disponibilidad:**
- El servicio de registro debe estar disponible el 99.9% del tiempo durante horario laboral (8:00 AM - 8:00 PM, zona horaria local).
- El sistema debe manejar picos de hasta 100 registros simultáneos sin degradación del servicio.

**Compatibilidad:**
- El formulario de registro debe funcionar correctamente en navegadores Chrome 90+, Firefox 88+, Safari 14+, y Edge 90+.
- El sistema debe ser compatible con dispositivos móviles (iOS 13+, Android 10+) manteniendo la misma funcionalidad.

**Mantenibilidad:**
- El código del módulo de registro debe tener una cobertura de pruebas unitarias mínima del 80%.
- Los logs de registro deben incluir timestamp, IP de origen, y resultado de la operación para facilitar auditoría y depuración.

**Portabilidad:**
- El sistema de registro debe poder desplegarse en entornos Linux, Windows Server y contenedores Docker sin modificaciones al código.

---

## Caso de Uso: Iniciar Sesión

### Requisitos No Funcionales

**Rendimiento:**
- El proceso de autenticación debe completarse en un tiempo máximo de 1.5 segundos bajo carga normal.
- La verificación de credenciales contra la base de datos debe ejecutarse en menos de 300 milisegundos.

**Seguridad:**
- El sistema debe implementar tokens JWT con tiempo de expiración de 24 horas para sesiones activas y 7 días para "recordar sesión".
- Después de 5 intentos fallidos de inicio de sesión, la cuenta debe bloquearse temporalmente por 30 minutos.
- El sistema debe registrar todos los intentos de inicio de sesión (exitosos y fallidos) con timestamp, IP y user agent.
- Las sesiones deben invalidarse automáticamente después de 30 minutos de inactividad.
- El sistema debe implementar protección CSRF en todos los endpoints de autenticación.

**Usabilidad:**
- El formulario de inicio de sesión debe mostrar mensajes de error claros y específicos sin revelar si el usuario o la contraseña son incorrectos (por seguridad).
- El sistema debe ofrecer recuperación de contraseña accesible desde la pantalla de inicio de sesión.

**Confiabilidad:**
- El sistema debe mantener una tasa de éxito de autenticación del 99.8% bajo condiciones normales.
- En caso de fallo del servicio de autenticación, el sistema debe mostrar un mensaje de error claro sin exponer detalles técnicos.

**Disponibilidad:**
- El servicio de autenticación debe estar disponible el 99.95% del tiempo (máximo 4.38 horas de inactividad por año).
- El sistema debe soportar hasta 200 autenticaciones simultáneas sin degradación.

**Compatibilidad:**
- El sistema de autenticación debe funcionar con estándares OAuth 2.0 y OpenID Connect para integración futura con proveedores externos.
- Debe ser compatible con autenticación de dos factores (2FA) usando TOTP (RFC 6238).

**Mantenibilidad:**
- Los logs de autenticación deben almacenarse por un período mínimo de 90 días para auditoría y análisis de seguridad.
- El código de autenticación debe seguir el patrón de diseño Strategy para permitir múltiples métodos de autenticación.

**Portabilidad:**
- El módulo de autenticación debe ser independiente del framework web utilizado, permitiendo migración futura sin afectar la lógica de negocio.

---

## Caso de Uso: Subir Imagen

### Requisitos No Funcionales

**Rendimiento:**
- El sistema debe aceptar archivos de imagen de hasta 50 MB y procesar la subida en menos de 10 segundos para conexiones de 10 Mbps.
- La validación de formato y tamaño de imagen debe ejecutarse en menos de 2 segundos.
- El sistema debe soportar subida de múltiples imágenes (hasta 10) en lote con progreso individual por archivo.

**Seguridad:**
- El sistema debe validar el tipo MIME real del archivo (no solo la extensión) para prevenir ataques de carga de archivos maliciosos.
- Solo se permiten formatos de imagen: JPEG, PNG, WebP, con validación de firma de archivo (magic bytes).
- El sistema debe escanear imágenes subidas con un antivirus/antimalware antes de almacenarlas.
- Las imágenes deben almacenarse con nombres únicos generados criptográficamente para prevenir enumeración de archivos.
- El acceso a las imágenes debe estar restringido mediante autenticación y autorización basada en roles.

**Usabilidad:**
- El sistema debe mostrar una barra de progreso visual durante la subida con porcentaje y tiempo estimado restante.
- El sistema debe permitir cancelar la subida en curso.
- Los mensajes de error deben ser claros e indicar el motivo específico del fallo (tamaño excedido, formato no soportado, etc.).

**Confiabilidad:**
- El sistema debe mantener una tasa de éxito de subida del 99% incluso con conexiones inestables mediante reintentos automáticos.
- En caso de fallo durante la subida, el sistema debe limpiar archivos parcialmente subidos para evitar consumo innecesario de almacenamiento.

**Disponibilidad:**
- El servicio de subida de imágenes debe estar disponible el 99.5% del tiempo.
- El sistema debe manejar hasta 50 subidas simultáneas sin degradación del rendimiento.

**Compatibilidad:**
- El sistema debe aceptar imágenes con resoluciones desde 320x240 hasta 8192x8192 píxeles.
- Debe ser compatible con perfiles de color sRGB, Adobe RGB y espacios de color estándar.
- El sistema debe normalizar automáticamente las imágenes a un formato estándar para procesamiento posterior.

**Mantenibilidad:**
- El sistema debe registrar todas las subidas con metadata: usuario, timestamp, tamaño, formato, y hash del archivo.
- El código de gestión de subida debe estar separado en módulos independientes (validación, almacenamiento, procesamiento).

**Portabilidad:**
- El sistema de almacenamiento debe ser compatible con sistemas de archivos locales, S3-compatible, y Azure Blob Storage mediante abstracción de capa de almacenamiento.

---

## Caso de Uso: Procesar Imagen

### Requisitos No Funcionales

**Rendimiento:**
- El procesamiento de una imagen de 1920x1080 píxeles debe completarse en un tiempo máximo de 15 segundos.
- El sistema debe procesar imágenes en paralelo, soportando hasta 5 imágenes simultáneas por servidor de procesamiento.
- La optimización y redimensionamiento de imágenes debe ejecutarse en menos de 5 segundos para imágenes de hasta 10 MB.

**Seguridad:**
- El procesamiento de imágenes debe ejecutarse en un entorno aislado (sandbox) para prevenir ejecución de código malicioso.
- El sistema debe validar la integridad de la imagen antes y después del procesamiento mediante checksums.
- Los procesos de transformación de imagen no deben tener acceso a información sensible del sistema.

**Usabilidad:**
- El sistema debe proporcionar notificaciones en tiempo real sobre el estado del procesamiento (pendiente, en proceso, completado, error).
- Los usuarios deben poder ver una vista previa de la imagen procesada antes de confirmar.

**Confiabilidad:**
- El sistema debe mantener una tasa de éxito de procesamiento del 98% para imágenes válidas.
- En caso de fallo durante el procesamiento, el sistema debe registrar el error con detalles técnicos y notificar al usuario.
- El sistema debe implementar reintentos automáticos (máximo 3 intentos) para fallos transitorios.

**Disponibilidad:**
- El servicio de procesamiento debe estar disponible el 99% del tiempo.
- El sistema debe manejar colas de procesamiento con priorización para evitar bloqueos.

**Compatibilidad:**
- El sistema debe procesar imágenes en formatos JPEG, PNG y WebP manteniendo la calidad visual original.
- Debe ser compatible con diferentes profundidades de color (8-bit, 16-bit) y espacios de color (sRGB, Adobe RGB).

**Mantenibilidad:**
- El sistema debe registrar métricas de procesamiento: tiempo de ejecución, tamaño de entrada/salida, y recursos utilizados.
- El código de procesamiento debe estar modularizado permitiendo agregar nuevos algoritmos sin modificar código existente.

**Portabilidad:**
- El procesamiento de imágenes debe poder ejecutarse en servidores Linux y Windows, y en contenedores Docker.
- Debe ser compatible con librerías de procesamiento de imágenes estándar (Pillow, OpenCV) para facilitar mantenimiento.

---

## Caso de Uso: Analizar Imagen

### Requisitos No Funcionales

**Rendimiento:**
- El análisis de una imagen de cacao (clasificación de calidad) debe completarse en un tiempo máximo de 30 segundos para imágenes de hasta 5 MB.
- El sistema debe procesar análisis en lote de hasta 20 imágenes con tiempo total no superior a 10 minutos.
- La inferencia del modelo de machine learning debe ejecutarse en menos de 10 segundos por imagen.

**Seguridad:**
- Los resultados del análisis deben estar asociados únicamente al usuario autorizado que subió la imagen.
- El sistema debe validar que el modelo de ML utilizado no haya sido modificado mediante verificación de firma digital.
- Los datos de entrenamiento y resultados de análisis deben cumplir con normativas de protección de datos (GDPR/LOPD).

**Usabilidad:**
- El sistema debe mostrar resultados de análisis en un formato visual claro con porcentajes de confianza y categorías identificadas.
- Los resultados deben estar disponibles en menos de 2 segundos después de completar el análisis.
- El sistema debe permitir exportar resultados en formatos PDF, CSV y JSON.

**Confiabilidad:**
- El sistema debe mantener una precisión mínima del 85% en la clasificación de calidad de granos de cacao.
- En caso de baja confianza del modelo (< 60%), el sistema debe alertar al usuario y sugerir revisión manual.
- El sistema debe registrar todos los análisis con timestamp, usuario, imagen y resultados para trazabilidad.

**Disponibilidad:**
- El servicio de análisis debe estar disponible el 99% del tiempo durante horario laboral.
- El sistema debe manejar hasta 10 análisis simultáneos sin degradación de precisión.

**Compatibilidad:**
- El sistema debe ser compatible con modelos de ML en formatos estándar (ONNX, TensorFlow SavedModel, PyTorch).
- Debe soportar actualización de modelos sin interrumpir el servicio mediante versionado de modelos.

**Mantenibilidad:**
- El sistema debe registrar métricas de rendimiento del modelo: precisión, recall, F1-score por lote de análisis.
- El código de análisis debe estar separado en capas: preprocesamiento, inferencia, postprocesamiento.

**Portabilidad:**
- El sistema de análisis debe poder ejecutarse en CPU y GPU (CUDA, OpenCL) para optimización de rendimiento.
- Debe ser compatible con servicios de ML en la nube (AWS SageMaker, Azure ML) para escalabilidad.

---

## Caso de Uso: Ver Resultados

### Requisitos No Funcionales

**Rendimiento:**
- La carga de resultados de análisis debe completarse en menos de 2 segundos para hasta 100 resultados.
- La visualización de gráficos y estadísticas debe renderizarse en menos de 3 segundos.
- El sistema debe implementar paginación eficiente mostrando 20 resultados por página.

**Seguridad:**
- El acceso a resultados debe estar restringido mediante autorización basada en roles (solo el propietario o usuarios con permisos específicos).
- Los resultados deben transmitirse mediante HTTPS para prevenir interceptación de datos.
- El sistema debe registrar todos los accesos a resultados con timestamp y usuario para auditoría.

**Usabilidad:**
- La interfaz de resultados debe ser responsive y funcionar correctamente en dispositivos móviles, tablets y desktop.
- El sistema debe permitir filtrar y ordenar resultados por fecha, calidad, finca, lote, etc.
- Los resultados deben mostrarse con visualizaciones claras (gráficos, tablas, imágenes anotadas).

**Confiabilidad:**
- El sistema debe mantener una tasa de éxito de carga de resultados del 99.5%.
- En caso de error al cargar resultados, el sistema debe mostrar un mensaje claro y permitir reintento.

**Disponibilidad:**
- El servicio de visualización de resultados debe estar disponible el 99.9% del tiempo.
- El sistema debe cachear resultados frecuentemente consultados para mejorar tiempos de respuesta.

**Compatibilidad:**
- Los resultados deben ser accesibles desde navegadores modernos (Chrome 90+, Firefox 88+, Safari 14+, Edge 90+).
- El sistema debe soportar exportación de resultados en múltiples formatos (PDF, Excel, CSV, JSON).

**Mantenibilidad:**
- El sistema debe registrar métricas de uso: consultas más frecuentes, tiempos de carga, errores comunes.
- El código de visualización debe estar separado en componentes reutilizables.

**Portabilidad:**
- La capa de presentación de resultados debe ser independiente del backend, permitiendo múltiples clientes (web, móvil, API).

---

## Caso de Uso: Descargar Reporte

### Requisitos No Funcionales

**Rendimiento:**
- La generación de un reporte PDF estándar (hasta 50 páginas) debe completarse en menos de 30 segundos.
- La descarga de un reporte de 10 MB debe completarse en menos de 1 minuto con conexión de 10 Mbps.
- El sistema debe permitir generar reportes en segundo plano y notificar al usuario cuando estén listos.

**Seguridad:**
- Los reportes deben incluir marca de agua con información del usuario y timestamp para trazabilidad.
- El acceso a reportes debe estar restringido mediante autenticación y autorización.
- Los reportes generados deben almacenarse de forma cifrada y eliminarse automáticamente después de 30 días.

**Usabilidad:**
- El sistema debe ofrecer plantillas de reporte predefinidas y personalizables.
- Los usuarios deben poder seleccionar el rango de fechas, fincas, lotes y métricas a incluir en el reporte.
- El sistema debe mostrar un progreso de generación del reporte con tiempo estimado.

**Confiabilidad:**
- El sistema debe mantener una tasa de éxito de generación de reportes del 98%.
- En caso de fallo durante la generación, el sistema debe notificar al usuario y permitir reintento sin pérdida de configuración.

**Disponibilidad:**
- El servicio de generación de reportes debe estar disponible el 99% del tiempo.
- El sistema debe manejar hasta 5 generaciones simultáneas de reportes sin degradación.

**Compatibilidad:**
- Los reportes deben generarse en formato PDF/A para garantizar compatibilidad a largo plazo.
- El sistema debe soportar exportación adicional en formatos Excel (.xlsx) y CSV.

**Mantenibilidad:**
- El sistema debe registrar todas las generaciones de reportes: usuario, tipo, tamaño, tiempo de generación.
- El código de generación de reportes debe estar modularizado permitiendo agregar nuevas plantillas fácilmente.

**Portabilidad:**
- El sistema de generación de reportes debe ser compatible con librerías estándar (ReportLab, WeasyPrint) para facilitar mantenimiento.

---

## Caso de Uso: Crear Finca

### Requisitos No Funcionales

**Rendimiento:**
- La creación de una finca debe completarse en menos de 2 segundos incluyendo validaciones.
- La validación de coordenadas geográficas y polígonos debe ejecutarse en menos de 500 milisegundos.

**Seguridad:**
- El sistema debe validar que el usuario tenga permisos para crear fincas (rol de administrador o agricultor con permisos).
- Los datos geográficos deben validarse para prevenir inyección de datos maliciosos.
- El sistema debe registrar la creación de fincas con usuario, timestamp y datos de auditoría.

**Usabilidad:**
- El formulario de creación debe incluir validación en tiempo real con mensajes claros de error.
- El sistema debe permitir seleccionar ubicación mediante mapa interactivo (integración con mapas).
- El formulario debe guardar automáticamente borradores cada 30 segundos para prevenir pérdida de datos.

**Confiabilidad:**
- El sistema debe mantener una tasa de éxito de creación del 99.5%.
- En caso de datos duplicados (mismo nombre y ubicación), el sistema debe alertar al usuario antes de crear.

**Disponibilidad:**
- El servicio de gestión de fincas debe estar disponible el 99.5% del tiempo.
- El sistema debe manejar hasta 20 creaciones simultáneas de fincas sin degradación.

**Compatibilidad:**
- El sistema debe aceptar coordenadas en formatos estándar (WGS84, UTM) y convertirlas automáticamente.
- Debe ser compatible con importación de datos de fincas desde archivos KML, GeoJSON y CSV.

**Mantenibilidad:**
- El sistema debe registrar todas las operaciones CRUD de fincas con logs estructurados.
- El código de gestión de fincas debe seguir el patrón Repository para facilitar testing y mantenimiento.

**Portabilidad:**
- El sistema debe ser compatible con bases de datos geoespaciales (PostGIS, MongoDB con índices geoespaciales).

---

## Caso de Uso: Editar Finca

### Requisitos No Funcionales

**Rendimiento:**
- La carga de datos de una finca para edición debe completarse en menos de 1 segundo.
- El guardado de cambios debe ejecutarse en menos de 2 segundos incluyendo validaciones.

**Seguridad:**
- El sistema debe validar que el usuario tenga permisos de edición sobre la finca específica.
- Los cambios críticos (coordenadas, nombre, propietario) deben requerir confirmación explícita del usuario.
- El sistema debe mantener un historial de cambios (auditoría) con usuario, timestamp y valores anteriores/nuevos.

**Usabilidad:**
- El formulario de edición debe mostrar claramente qué campos han sido modificados.
- El sistema debe permitir deshacer cambios antes de guardar.
- Los mensajes de error deben indicar específicamente qué campo tiene problemas y cómo corregirlo.

**Confiabilidad:**
- El sistema debe mantener una tasa de éxito de edición del 99.5%.
- En caso de conflicto de edición simultánea, el sistema debe implementar control de concurrencia (optimistic locking).

**Disponibilidad:**
- El servicio de edición debe estar disponible el 99.5% del tiempo.
- El sistema debe manejar hasta 15 ediciones simultáneas de diferentes fincas sin degradación.

**Compatibilidad:**
- El sistema debe mantener compatibilidad con versiones anteriores de datos de fincas durante actualizaciones de esquema.

**Mantenibilidad:**
- El sistema debe registrar todos los cambios con logs estructurados incluyendo valores anteriores y nuevos.
- El código de edición debe reutilizar la lógica de validación de creación para mantener consistencia.

**Portabilidad:**
- Las operaciones de edición deben ser transaccionales garantizando integridad de datos en cualquier base de datos compatible.

---

## Caso de Uso: Crear Lote

### Requisitos No Funcionales

**Rendimiento:**
- La creación de un lote debe completarse en menos de 2 segundos incluyendo validaciones y asociación con finca.
- La validación de que el lote pertenece a una finca existente debe ejecutarse en menos de 300 milisegundos.

**Seguridad:**
- El sistema debe validar que el usuario tenga permisos para crear lotes en la finca especificada.
- El sistema debe prevenir la creación de lotes duplicados (mismo nombre en la misma finca).
- Los datos del lote deben validarse para prevenir inyección SQL y XSS.

**Usabilidad:**
- El formulario debe permitir seleccionar la finca desde un listado filtrado y ordenado.
- El sistema debe validar en tiempo real que el nombre del lote no esté duplicado en la finca seleccionada.
- El formulario debe incluir campos obligatorios claramente marcados.

**Confiabilidad:**
- El sistema debe mantener una tasa de éxito de creación del 99.5%.
- En caso de error, el sistema debe preservar los datos ingresados (excepto datos sensibles) para evitar pérdida de información.

**Disponibilidad:**
- El servicio de gestión de lotes debe estar disponible el 99.5% del tiempo.
- El sistema debe manejar hasta 25 creaciones simultáneas de lotes sin degradación.

**Compatibilidad:**
- El sistema debe soportar importación masiva de lotes desde archivos CSV y Excel con validación de datos.

**Mantenibilidad:**
- El sistema debe registrar todas las creaciones de lotes con logs estructurados.
- El código debe seguir el principio DRY reutilizando validaciones comunes con fincas.

**Portabilidad:**
- El sistema de gestión de lotes debe ser independiente del ORM utilizado, permitiendo migración futura.

---

## Caso de Uso: Editar Lote

### Requisitos No Funcionales

**Rendimiento:**
- La carga de datos de un lote para edición debe completarse en menos de 1 segundo.
- El guardado de cambios debe ejecutarse en menos de 2 segundos.

**Seguridad:**
- El sistema debe validar permisos de edición sobre el lote específico y su finca asociada.
- Los cambios en la asociación finca-lote deben validarse para mantener integridad referencial.
- El sistema debe mantener historial de cambios con auditoría completa.

**Usabilidad:**
- El formulario debe mostrar información contextual de la finca asociada.
- El sistema debe alertar si los cambios afectan análisis o datos históricos asociados al lote.
- Los campos deshabilitados deben indicar claramente el motivo (por ejemplo, lote con análisis históricos).

**Confiabilidad:**
- El sistema debe mantener una tasa de éxito de edición del 99.5%.
- En caso de edición simultánea, el sistema debe implementar control de concurrencia.

**Disponibilidad:**
- El servicio de edición debe estar disponible el 99.5% del tiempo.
- El sistema debe manejar hasta 20 ediciones simultáneas de diferentes lotes.

**Compatibilidad:**
- El sistema debe mantener compatibilidad con versiones anteriores de datos durante actualizaciones.

**Mantenibilidad:**
- El sistema debe registrar todos los cambios con logs estructurados.
- El código debe reutilizar validaciones de creación para mantener consistencia.

**Portabilidad:**
- Las operaciones deben ser transaccionales garantizando integridad de datos.

---

## Caso de Uso: Eliminar Lote

### Requisitos No Funcionales

**Rendimiento:**
- La eliminación de un lote (incluyendo validaciones de dependencias) debe completarse en menos de 3 segundos.
- La verificación de dependencias (análisis asociados, imágenes, etc.) debe ejecutarse en menos de 1 segundo.

**Seguridad:**
- El sistema debe validar permisos de eliminación (solo administradores o propietarios autorizados).
- La eliminación debe requerir confirmación explícita del usuario con advertencia sobre datos asociados.
- El sistema debe implementar eliminación lógica (soft delete) en lugar de eliminación física para mantener integridad histórica.
- El sistema debe registrar todas las eliminaciones con usuario, timestamp y datos eliminados para auditoría.

**Usabilidad:**
- El sistema debe mostrar claramente qué datos serán afectados por la eliminación (análisis, imágenes, reportes).
- El sistema debe ofrecer opción de archivar en lugar de eliminar para preservar datos históricos.
- Los mensajes de confirmación deben ser claros y específicos sobre las consecuencias.

**Confiabilidad:**
- El sistema debe prevenir eliminación de lotes con análisis históricos críticos a menos que el usuario tenga permisos especiales.
- En caso de error durante eliminación, el sistema debe revertir cambios parciales mediante transacciones.

**Disponibilidad:**
- El servicio de eliminación debe estar disponible el 99.5% del tiempo.
- El sistema debe manejar hasta 10 eliminaciones simultáneas sin degradación.

**Compatibilidad:**
- El sistema debe mantener referencias históricas incluso después de eliminación lógica para reportes y auditoría.

**Mantenibilidad:**
- El sistema debe registrar todas las eliminaciones con logs detallados incluyendo datos eliminados y dependencias.
- El código debe implementar el patrón Strategy para diferentes políticas de eliminación (física, lógica, archivado).

**Portabilidad:**
- Las operaciones de eliminación deben ser transaccionales garantizando consistencia en cualquier base de datos.

---

## Caso de Uso: Ver Historial

### Requisitos No Funcionales

**Rendimiento:**
- La carga del historial de análisis debe completarse en menos de 3 segundos para hasta 500 registros.
- El sistema debe implementar paginación eficiente mostrando 25 registros por página con carga bajo demanda.
- La búsqueda y filtrado del historial debe ejecutarse en menos de 2 segundos.

**Seguridad:**
- El acceso al historial debe estar restringido según permisos del usuario (solo sus propios datos o datos autorizados).
- Los datos históricos deben transmitirse mediante HTTPS.
- El sistema debe registrar todos los accesos al historial para auditoría.

**Usabilidad:**
- El historial debe mostrarse en formato de tabla ordenable y filtrable por múltiples criterios (fecha, finca, lote, calidad).
- El sistema debe ofrecer visualizaciones temporales (gráficos de tendencias) del historial.
- La interfaz debe ser responsive y funcional en dispositivos móviles.

**Confiabilidad:**
- El sistema debe mantener una tasa de éxito de carga del historial del 99.5%.
- El historial debe preservarse indefinidamente (o según política de retención configurada) sin pérdida de datos.

**Disponibilidad:**
- El servicio de historial debe estar disponible el 99.5% del tiempo.
- El sistema debe cachear consultas frecuentes del historial para mejorar rendimiento.

**Compatibilidad:**
- El historial debe ser exportable en formatos CSV, Excel y JSON.
- El sistema debe soportar integración con sistemas de BI externos mediante APIs.

**Mantenibilidad:**
- El sistema debe registrar métricas de uso del historial: consultas más frecuentes, filtros utilizados, tiempos de carga.
- El código debe estar optimizado para consultas eficientes sobre grandes volúmenes de datos históricos.

**Portabilidad:**
- El sistema de historial debe ser compatible con bases de datos relacionales y NoSQL para escalabilidad.

---

## Caso de Uso: Buscar Análisis

### Requisitos No Funcionales

**Rendimiento:**
- La búsqueda de análisis debe devolver resultados en menos de 2 segundos para consultas sobre hasta 10,000 registros.
- El sistema debe implementar búsqueda full-text con índice invertido para búsquedas por texto libre.
- La búsqueda debe soportar múltiples criterios combinados (fecha, finca, lote, calidad, usuario) sin degradación de rendimiento.

**Seguridad:**
- Los resultados de búsqueda deben filtrarse según permisos del usuario (solo análisis autorizados).
- Las consultas de búsqueda deben validarse para prevenir inyección de código (SQL injection, NoSQL injection).
- El sistema debe registrar todas las búsquedas con usuario, criterios y timestamp para auditoría.

**Usabilidad:**
- El sistema debe ofrecer búsqueda con autocompletado y sugerencias mientras el usuario escribe.
- Los resultados deben mostrarse con resaltado de términos buscados.
- El sistema debe permitir guardar búsquedas frecuentes como favoritos.

**Confiabilidad:**
- El sistema debe mantener una tasa de éxito de búsqueda del 99.5%.
- Los resultados deben ser consistentes y reproducibles para las mismas consultas.

**Disponibilidad:**
- El servicio de búsqueda debe estar disponible el 99.5% del tiempo.
- El sistema debe manejar hasta 50 búsquedas simultáneas sin degradación.

**Compatibilidad:**
- El sistema debe soportar operadores de búsqueda estándar (AND, OR, NOT, comodines).
- Debe ser compatible con búsqueda por rangos de fechas, rangos numéricos y búsqueda fuzzy.

**Mantenibilidad:**
- El sistema debe registrar métricas de búsqueda: términos más buscados, tiempos de respuesta, resultados vacíos.
- El código debe estar optimizado con índices de base de datos apropiados para búsquedas eficientes.

**Portabilidad:**
- El sistema de búsqueda debe ser compatible con motores de búsqueda externos (Elasticsearch, Solr) para escalabilidad.

---

## Caso de Uso: Entrenar Modelo

### Requisitos No Funcionales

**Rendimiento:**
- El entrenamiento de un modelo con dataset de 10,000 imágenes debe completarse en menos de 4 horas en hardware estándar (CPU multi-core o GPU).
- El sistema debe mostrar progreso del entrenamiento en tiempo real con métricas (loss, accuracy, epoch).
- El sistema debe soportar entrenamiento distribuido para datasets grandes (> 50,000 imágenes).

**Seguridad:**
- El acceso al entrenamiento de modelos debe estar restringido a usuarios con rol de administrador o científico de datos.
- Los datasets de entrenamiento deben estar cifrados en reposo y en tránsito.
- El sistema debe validar la integridad del dataset antes de iniciar entrenamiento.
- Los modelos entrenados deben firmarse digitalmente para prevenir modificaciones no autorizadas.

**Usabilidad:**
- El sistema debe proporcionar una interfaz clara para configurar hiperparámetros de entrenamiento.
- El sistema debe mostrar visualizaciones de métricas de entrenamiento (gráficos de loss, accuracy, confusion matrix).
- El sistema debe permitir pausar y reanudar entrenamientos largos.

**Confiabilidad:**
- El sistema debe mantener checkpoints automáticos durante el entrenamiento para permitir recuperación ante fallos.
- El sistema debe validar la calidad del modelo antes de desplegarlo (métricas mínimas: accuracy > 85%, F1-score > 0.80).
- En caso de fallo durante entrenamiento, el sistema debe permitir reanudar desde el último checkpoint.

**Disponibilidad:**
- El servicio de entrenamiento debe estar disponible el 95% del tiempo (permite mantenimiento programado).
- El sistema debe manejar hasta 2 entrenamientos simultáneos sin degradación de rendimiento.

**Compatibilidad:**
- El sistema debe soportar frameworks de ML estándar (TensorFlow, PyTorch, Scikit-learn).
- Los modelos entrenados deben exportarse en formatos estándar (ONNX, TensorFlow SavedModel, H5) para portabilidad.

**Mantenibilidad:**
- El sistema debe registrar todas las ejecuciones de entrenamiento: dataset, hiperparámetros, métricas finales, tiempo de ejecución.
- El código debe estar modularizado permitiendo agregar nuevos algoritmos de entrenamiento sin modificar código existente.

**Portabilidad:**
- El sistema debe poder ejecutarse en servidores con GPU (CUDA, OpenCL) y en la nube (AWS SageMaker, Google Colab, Azure ML).

---

## Caso de Uso: Crear Agricultor

### Requisitos No Funcionales

**Rendimiento:**
- La creación de un agricultor debe completarse en menos de 2 segundos incluyendo validaciones.
- La validación de datos personales y documentos debe ejecutarse en menos de 500 milisegundos.

**Seguridad:**
- El sistema debe validar que el usuario tenga permisos para crear agricultores (rol de administrador).
- Los datos personales deben cumplir con normativas de protección de datos (GDPR/LOPD).
- El sistema debe validar documentos de identidad (formato, checksum) si se requieren.
- Los datos sensibles deben almacenarse cifrados en reposo.

**Usabilidad:**
- El formulario debe incluir validación en tiempo real con mensajes claros.
- El sistema debe permitir buscar agricultores existentes antes de crear para evitar duplicados.
- El formulario debe guardar borradores automáticamente.

**Confiabilidad:**
- El sistema debe mantener una tasa de éxito de creación del 99.5%.
- El sistema debe prevenir creación de duplicados mediante validación de documentos únicos.

**Disponibilidad:**
- El servicio de gestión de agricultores debe estar disponible el 99.5% del tiempo.
- El sistema debe manejar hasta 15 creaciones simultáneas sin degradación.

**Compatibilidad:**
- El sistema debe aceptar diferentes formatos de documentos de identidad según país/región.
- Debe ser compatible con importación masiva desde archivos CSV y Excel.

**Mantenibilidad:**
- El sistema debe registrar todas las creaciones con logs estructurados.
- El código debe seguir el patrón Repository para facilitar testing.

**Portabilidad:**
- El sistema debe ser compatible con diferentes bases de datos relacionales.

---

## Caso de Uso: Editar Agricultor

### Requisitos No Funcionales

**Rendimiento:**
- La carga de datos de un agricultor para edición debe completarse en menos de 1 segundo.
- El guardado de cambios debe ejecutarse en menos de 2 segundos.

**Seguridad:**
- El sistema debe validar permisos de edición (solo administradores o usuarios autorizados).
- Los cambios en datos sensibles deben requerir confirmación y registro de auditoría.
- El sistema debe mantener historial completo de cambios con usuario, timestamp y valores anteriores/nuevos.

**Usabilidad:**
- El formulario debe mostrar claramente qué campos han sido modificados.
- El sistema debe permitir deshacer cambios antes de guardar.
- Los mensajes de error deben ser específicos y accionables.

**Confiabilidad:**
- El sistema debe mantener una tasa de éxito de edición del 99.5%.
- En caso de edición simultánea, el sistema debe implementar control de concurrencia.

**Disponibilidad:**
- El servicio de edición debe estar disponible el 99.5% del tiempo.
- El sistema debe manejar hasta 12 ediciones simultáneas sin degradación.

**Compatibilidad:**
- El sistema debe mantener compatibilidad con versiones anteriores durante actualizaciones.

**Mantenibilidad:**
- El sistema debe registrar todos los cambios con logs estructurados.
- El código debe reutilizar validaciones de creación.

**Portabilidad:**
- Las operaciones deben ser transaccionales garantizando integridad.

---

## Caso de Uso: Asignar Rol

### Requisitos No Funcionales

**Rendimiento:**
- La asignación de rol a un usuario debe completarse en menos de 1 segundo.
- La carga de lista de roles disponibles debe ejecutarse en menos de 500 milisegundos.

**Seguridad:**
- Solo usuarios con rol de administrador o superadministrador pueden asignar roles.
- El sistema debe validar que el rol asignado existe y es válido.
- Los cambios de rol deben registrarse en auditoría con usuario que realiza el cambio, usuario afectado, rol anterior y nuevo, timestamp.
- El sistema debe notificar al usuario cuando su rol cambia.
- El sistema debe prevenir asignación de roles que otorguen más permisos que el usuario que asigna.

**Usabilidad:**
- El sistema debe mostrar claramente los permisos asociados a cada rol antes de asignar.
- El sistema debe mostrar el historial de cambios de rol del usuario.
- La interfaz debe ser intuitiva con selección de rol desde dropdown o lista.

**Confiabilidad:**
- El sistema debe mantener una tasa de éxito de asignación del 99.8%.
- En caso de error, el sistema debe revertir el cambio mediante transacciones.

**Disponibilidad:**
- El servicio de gestión de roles debe estar disponible el 99.9% del tiempo.
- El sistema debe manejar hasta 30 asignaciones simultáneas sin degradación.

**Compatibilidad:**
- El sistema debe ser compatible con estándares de autorización (RBAC, ABAC).
- Debe soportar roles personalizados además de roles predefinidos.

**Mantenibilidad:**
- El sistema debe registrar todas las asignaciones con logs estructurados.
- El código debe seguir el patrón Strategy para diferentes sistemas de autorización.

**Portabilidad:**
- El sistema de roles debe ser independiente del framework de autenticación utilizado.

---

## Caso de Uso: Editar Perfil

### Requisitos No Funcionales

**Rendimiento:**
- La carga del perfil del usuario actual debe completarse en menos de 1 segundo.
- El guardado de cambios debe ejecutarse en menos de 2 segundos.

**Seguridad:**
- El usuario solo puede editar su propio perfil (excepto administradores que pueden editar cualquier perfil).
- Los cambios en email deben requerir verificación mediante enlace enviado al nuevo email.
- Los cambios en contraseña deben requerir confirmación de la contraseña actual.
- El sistema debe validar que el nuevo email no esté en uso por otro usuario.

**Usabilidad:**
- El formulario debe mostrar avatar del usuario con opción de actualización.
- El sistema debe validar en tiempo real disponibilidad de email y username.
- Los cambios deben guardarse automáticamente como borrador cada 30 segundos.

**Confiabilidad:**
- El sistema debe mantener una tasa de éxito de edición del 99.5%.
- En caso de error, el sistema debe preservar los datos ingresados.

**Disponibilidad:**
- El servicio de edición de perfil debe estar disponible el 99.9% del tiempo.
- El sistema debe manejar hasta 50 ediciones simultáneas sin degradación.

**Compatibilidad:**
- El sistema debe soportar actualización de avatar en formatos JPEG, PNG, WebP.
- Debe ser compatible con integración con servicios de autenticación externos (OAuth) para sincronización de perfil.

**Mantenibilidad:**
- El sistema debe registrar cambios críticos (email, contraseña) con logs de auditoría.
- El código debe reutilizar validaciones comunes con otros formularios de usuario.

**Portabilidad:**
- Las operaciones deben ser transaccionales garantizando integridad de datos.

---

## Resumen de Métricas Clave

### Rendimiento Global
- Tiempo de respuesta promedio: < 2 segundos para operaciones CRUD
- Tiempo de respuesta máximo: < 30 segundos para operaciones complejas (análisis, reportes)
- Throughput: Soporte para 50-200 operaciones simultáneas según caso de uso

### Seguridad Global
- Cifrado: TLS 1.2+ para tránsito, AES-256 para datos en reposo
- Autenticación: JWT con expiración configurable
- Autorización: RBAC con auditoría completa
- Protección: Rate limiting, CSRF, XSS, SQL injection prevention

### Disponibilidad Global
- SLA objetivo: 99.5% - 99.9% según criticidad del servicio
- Tiempo de recuperación (RTO): < 4 horas
- Punto de recuperación (RPO): < 1 hora

### Compatibilidad Global
- Navegadores: Chrome 90+, Firefox 88+, Safari 14+, Edge 90+
- Dispositivos: iOS 13+, Android 10+, Desktop (Windows 10+, macOS 10.15+, Linux)
- Formatos: JPEG, PNG, WebP para imágenes; PDF, Excel, CSV, JSON para exportación

