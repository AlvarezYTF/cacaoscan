# Requisitos Funcionales Generalizados - Sistema CacaoScan

## Rendimiento

### RF-PERF-001: Gestión de Tiempos de Respuesta

**Descripción breve:**

El sistema debe implementar mecanismos para garantizar tiempos de respuesta rápidos en todas las operaciones según su criticidad.

**Prioridad:** Alta

**Criterios de aceptación:**

• El sistema debe completar operaciones CRUD simples en menos de 2 segundos bajo carga normal.

• El sistema debe ejecutar validaciones de formularios en menos de 500 milisegundos en el cliente.

• El sistema debe completar operaciones complejas (análisis, procesamiento, generación de reportes) en menos de 30 segundos.

• El sistema debe mostrar resultados de consultas simples en menos de 2 segundos.

• El sistema debe renderizar visualizaciones y gráficos en menos de 3 segundos.

---

### RF-PERF-002: Procesamiento en Paralelo y Lotes

**Descripción breve:**

El sistema debe soportar procesamiento paralelo y en lote para operaciones que involucran múltiples elementos.

**Prioridad:** Alta

**Criterios de aceptación:**

• El sistema debe procesar múltiples imágenes en paralelo, soportando hasta 5 imágenes simultáneas por servidor.

• El sistema debe permitir procesar análisis en lote de hasta 20 imágenes.

• El sistema debe soportar subida de múltiples archivos (hasta 10) en lote con progreso individual por archivo.

• El sistema debe soportar entrenamiento distribuido para datasets grandes (> 50,000 imágenes).

• El sistema debe manejar múltiples operaciones CRUD simultáneas sin degradación de rendimiento.

---

### RF-PERF-003: Gestión de Carga y Escalabilidad

**Descripción breve:**

El sistema debe manejar cargas de trabajo variables y picos de tráfico sin degradación del servicio.

**Prioridad:** Alta

**Criterios de aceptación:**

• El sistema debe soportar hasta 50 usuarios concurrentes para operaciones normales.

• El sistema debe manejar picos de hasta 100 registros simultáneos.

• El sistema debe soportar hasta 200 autenticaciones simultáneas.

• El sistema debe manejar hasta 50 subidas simultáneas de imágenes.

• El sistema debe soportar hasta 10 análisis simultáneos sin degradación de precisión.

• El sistema debe manejar hasta 5 generaciones simultáneas de reportes.

• El sistema debe soportar hasta 50 búsquedas simultáneas.

• El sistema debe manejar hasta 2 entrenamientos simultáneos de modelos.

---

### RF-PERF-004: Paginación y Carga Bajo Demanda

**Descripción breve:**

El sistema debe implementar paginación eficiente para grandes conjuntos de datos.

**Prioridad:** Media

**Criterios de aceptación:**

• El sistema debe mostrar 20 resultados por página en listados estándar.

• El sistema debe mostrar 25 registros por página en historiales.

• El sistema debe implementar carga bajo demanda para reducir tiempos de carga inicial.

• El sistema debe cargar hasta 500 registros en menos de 3 segundos con paginación.

• El sistema debe cargar hasta 100 resultados en menos de 2 segundos.

---

### RF-PERF-005: Optimización de Consultas y Búsquedas

**Descripción breve:**

El sistema debe implementar mecanismos de optimización para búsquedas y consultas complejas.

**Prioridad:** Media

**Criterios de aceptación:**

• El sistema debe implementar búsqueda full-text con índice invertido para búsquedas por texto libre.

• El sistema debe devolver resultados de búsqueda en menos de 2 segundos para consultas sobre hasta 10,000 registros.

• El sistema debe soportar múltiples criterios combinados en búsquedas sin degradación de rendimiento.

• El sistema debe implementar índices de base de datos apropiados para búsquedas eficientes.

---

### RF-PERF-006: Sistema de Caché

**Descripción breve:**

El sistema debe implementar caché para mejorar tiempos de respuesta en consultas frecuentes.

**Prioridad:** Media

**Criterios de aceptación:**

• El sistema debe cachear resultados frecuentemente consultados.

• El sistema debe cachear consultas frecuentes del historial.

• El sistema debe cachear datos de configuración estáticos.

---

## Seguridad

### RF-SEC-001: Gestión de Contraseñas y Autenticación

**Descripción breve:**

El sistema debe implementar mecanismos seguros para almacenamiento y validación de contraseñas.

**Prioridad:** Alta

**Criterios de aceptación:**

• El sistema debe almacenar contraseñas utilizando algoritmos de hash unidireccionales (bcrypt, Argon2) con un factor de costo mínimo de 12.

• El sistema debe validar la fortaleza de la contraseña antes de aceptarla (mínimo 8 caracteres, al menos una mayúscula, una minúscula, un número y un carácter especial).

• El sistema debe implementar tokens JWT con tiempo de expiración de 24 horas para sesiones activas y 7 días para "recordar sesión".

• El sistema debe invalidar sesiones automáticamente después de 30 minutos de inactividad.

• El sistema debe bloquear temporalmente cuentas después de 5 intentos fallidos de inicio de sesión por 30 minutos.

• El sistema debe requerir confirmación de la contraseña actual para cambios de contraseña.

---

### RF-SEC-002: Protección Contra Ataques

**Descripción breve:**

El sistema debe implementar protecciones contra diversos tipos de ataques y amenazas.

**Prioridad:** Alta

**Criterios de aceptación:**

• El sistema debe implementar protección contra ataques de fuerza bruta limitando intentos de registro a 5 por dirección IP cada 15 minutos.

• El sistema debe implementar protección CSRF en todos los endpoints de autenticación y operaciones críticas.

• El sistema debe validar todos los datos de entrada para prevenir inyección SQL y XSS.

• El sistema debe validar consultas de búsqueda para prevenir inyección de código (SQL injection, NoSQL injection).

• El sistema debe validar datos geográficos para prevenir inyección de datos maliciosos.

• El sistema debe validar el tipo MIME real del archivo (no solo la extensión) para prevenir ataques de carga de archivos maliciosos.

• El sistema debe escanear imágenes subidas con un antivirus/antimalware antes de almacenarlas.

• El sistema debe ejecutar procesamiento de imágenes en un entorno aislado (sandbox) para prevenir ejecución de código malicioso.

---

### RF-SEC-003: Cifrado y Protección de Datos

**Descripción breve:**

El sistema debe cifrar datos sensibles tanto en tránsito como en reposo.

**Prioridad:** Alta

**Criterios de aceptación:**

• El sistema debe usar protocolo HTTPS con cifrado TLS 1.2 o superior para transmisión de datos sensibles.

• El sistema debe cifrar datos sensibles en reposo con AES-256.

• Los datasets de entrenamiento deben estar cifrados en reposo y en tránsito.

• Los reportes generados deben almacenarse de forma cifrada.

• Los datos sensibles de usuarios deben almacenarse cifrados en reposo.

---

### RF-SEC-004: Validación de Archivos

**Descripción breve:**

El sistema debe validar archivos subidos para garantizar seguridad e integridad.

**Prioridad:** Alta

**Criterios de aceptación:**

• El sistema debe validar el tipo MIME real del archivo usando magic bytes (no solo la extensión).

• Solo se permiten formatos de imagen: JPEG, PNG, WebP, con validación de firma de archivo.

• El sistema debe validar la integridad de la imagen antes y después del procesamiento mediante checksums.

• El sistema debe validar la integridad del dataset antes de iniciar entrenamiento.

• El sistema debe validar documentos de identidad (formato, checksum) si se requieren.

---

### RF-SEC-005: Control de Acceso y Autorización

**Descripción breve:**

El sistema debe implementar control de acceso basado en roles y permisos.

**Prioridad:** Alta

**Criterios de aceptación:**

• El sistema debe validar permisos de usuario antes de permitir operaciones (crear, editar, eliminar).

• El sistema debe restringir el acceso a recursos mediante autorización basada en roles (solo el propietario o usuarios con permisos específicos).

• Solo usuarios con rol de administrador o superadministrador pueden asignar roles.

• El sistema debe validar que el rol asignado existe y es válido.

• El sistema debe prevenir asignación de roles que otorguen más permisos que el usuario que asigna.

• El usuario solo puede editar su propio perfil (excepto administradores que pueden editar cualquier perfil).

• El acceso al entrenamiento de modelos debe estar restringido a usuarios con rol de administrador o científico de datos.

• El acceso a resultados debe estar restringido según permisos del usuario.

• El acceso al historial debe estar restringido según permisos del usuario (solo sus propios datos o datos autorizados).

---

### RF-SEC-006: Gestión de Sesiones y Tokens

**Descripción breve:**

El sistema debe gestionar sesiones de usuario de forma segura.

**Prioridad:** Alta

**Criterios de aceptación:**

• El sistema debe implementar tokens JWT con tiempo de expiración configurable.

• El sistema debe invalidar sesiones automáticamente después de períodos de inactividad.

• El sistema debe registrar todos los intentos de inicio de sesión (exitosos y fallidos) con timestamp, IP y user agent.

• El sistema debe soportar estándares OAuth 2.0 y OpenID Connect para integración futura.

• El sistema debe ser compatible con autenticación de dos factores (2FA) usando TOTP (RFC 6238).

---

### RF-SEC-007: Nombres Seguros de Archivos

**Descripción breve:**

El sistema debe generar nombres únicos y seguros para archivos almacenados.

**Prioridad:** Media

**Criterios de aceptación:**

• Las imágenes deben almacenarse con nombres únicos generados criptográficamente para prevenir enumeración de archivos.

---

### RF-SEC-008: Verificación de Integridad de Modelos

**Descripción breve:**

El sistema debe verificar la integridad de modelos de ML para prevenir modificaciones no autorizadas.

**Prioridad:** Media

**Criterios de aceptación:**

• El sistema debe validar que el modelo de ML utilizado no haya sido modificado mediante verificación de firma digital.

• Los modelos entrenados deben firmarse digitalmente para prevenir modificaciones no autorizadas.

---

### RF-SEC-009: Protección de Datos Personales

**Descripción breve:**

El sistema debe cumplir con normativas de protección de datos personales.

**Prioridad:** Alta

**Criterios de aceptación:**

• Los datos personales deben cumplir con normativas de protección de datos (GDPR/LOPD).

• Los datos de entrenamiento y resultados de análisis deben cumplir con normativas de protección de datos.

• El sistema debe validar que el nuevo email no esté en uso por otro usuario.

---

### RF-SEC-010: Verificación de Email

**Descripción breve:**

El sistema debe implementar verificación de email para cambios críticos.

**Prioridad:** Alta

**Criterios de aceptación:**

• Los cambios en email deben requerir verificación mediante enlace enviado al nuevo email.

---

### RF-SEC-011: Restricción de Acceso a Procesos

**Descripción breve:**

El sistema debe restringir el acceso de procesos de transformación a información sensible.

**Prioridad:** Media

**Criterios de aceptación:**

• Los procesos de transformación de imagen no deben tener acceso a información sensible del sistema.

---

## Usabilidad

### RF-USAB-001: Accesibilidad

**Descripción breve:**

El sistema debe ser accesible cumpliendo con estándares de accesibilidad web.

**Prioridad:** Alta

**Criterios de aceptación:**

• El sistema debe cumplir con WCAG 2.1 nivel AA en todos los formularios e interfaces.

---

### RF-USAB-002: Mensajes de Error y Validación

**Descripción breve:**

El sistema debe proporcionar mensajes de error claros y específicos para el usuario.

**Prioridad:** Alta

**Criterios de aceptación:**

• Los mensajes de error de validación deben mostrarse en menos de 1 segundo después de que el usuario complete un campo.

• Los mensajes de error deben ser claros e indicar el motivo específico del fallo.

• Los mensajes de error deben indicar específicamente qué campo tiene problemas y cómo corregirlo.

• El sistema debe mostrar mensajes de error claros y específicos sin revelar información sensible del sistema.

• Los mensajes de error deben ser específicos y accionables.

---

### RF-USAB-003: Procesos Simplificados

**Descripción breve:**

El sistema debe simplificar procesos para reducir pasos y navegación innecesaria.

**Prioridad:** Alta

**Criterios de aceptación:**

• El proceso de registro debe completarse en máximo 3 pasos sin requerir navegación adicional.

---

### RF-USAB-004: Indicadores de Progreso

**Descripción breve:**

El sistema debe mostrar indicadores visuales de progreso para operaciones largas.

**Prioridad:** Alta

**Criterios de aceptación:**

• El sistema debe mostrar una barra de progreso visual durante la subida de archivos con porcentaje y tiempo estimado restante.

• El sistema debe mostrar progreso de generación del reporte con tiempo estimado.

• El sistema debe mostrar progreso del entrenamiento en tiempo real con métricas (loss, accuracy, epoch).

• El sistema debe proporcionar notificaciones en tiempo real sobre el estado del procesamiento (pendiente, en proceso, completado, error).

---

### RF-USAB-005: Cancelación de Operaciones

**Descripción breve:**

El sistema debe permitir cancelar operaciones en curso cuando sea posible.

**Prioridad:** Media

**Criterios de aceptación:**

• El sistema debe permitir cancelar la subida en curso.

---

### RF-USAB-006: Validación en Tiempo Real

**Descripción breve:**

El sistema debe validar datos mientras el usuario los ingresa.

**Prioridad:** Alta

**Criterios de aceptación:**

• El formulario debe incluir validación en tiempo real con mensajes claros de error.

• El sistema debe validar en tiempo real que el nombre del lote no esté duplicado en la finca seleccionada.

• El sistema debe validar en tiempo real disponibilidad de email y username.

---

### RF-USAB-007: Visualización de Resultados

**Descripción breve:**

El sistema debe presentar resultados de forma clara y visualmente comprensible.

**Prioridad:** Alta

**Criterios de aceptación:**

• El sistema debe mostrar resultados de análisis en un formato visual claro con porcentajes de confianza y categorías identificadas.

• Los resultados deben mostrarse con visualizaciones claras (gráficos, tablas, imágenes anotadas).

• Los usuarios deben poder ver una vista previa de la imagen procesada antes de confirmar.

• El sistema debe mostrar visualizaciones de métricas de entrenamiento (gráficos de loss, accuracy, confusion matrix).

• El sistema debe ofrecer visualizaciones temporales (gráficos de tendencias) del historial.

---

### RF-USAB-008: Interfaz Responsive

**Descripción breve:**

El sistema debe funcionar correctamente en diferentes dispositivos y tamaños de pantalla.

**Prioridad:** Alta

**Criterios de aceptación:**

• La interfaz de resultados debe ser responsive y funcionar correctamente en dispositivos móviles, tablets y desktop.

• La interfaz debe ser responsive y funcional en dispositivos móviles.

---

### RF-USAB-009: Filtrado y Ordenamiento

**Descripción breve:**

El sistema debe permitir filtrar y ordenar datos de forma flexible.

**Prioridad:** Alta

**Criterios de aceptación:**

• El sistema debe permitir filtrar y ordenar resultados por fecha, calidad, finca, lote, etc.

• El historial debe mostrarse en formato de tabla ordenable y filtrable por múltiples criterios (fecha, finca, lote, calidad).

---

### RF-USAB-010: Autocompletado y Sugerencias

**Descripción breve:**

El sistema debe ofrecer autocompletado y sugerencias en búsquedas.

**Prioridad:** Media

**Criterios de aceptación:**

• El sistema debe ofrecer búsqueda con autocompletado y sugerencias mientras el usuario escribe.

• Los resultados deben mostrarse con resaltado de términos buscados.

---

### RF-USAB-011: Guardado Automático de Borradores

**Descripción breve:**

El sistema debe guardar automáticamente borradores para prevenir pérdida de datos.

**Prioridad:** Alta

**Criterios de aceptación:**

• El formulario debe guardar automáticamente borradores cada 30 segundos para prevenir pérdida de datos.

• Los cambios deben guardarse automáticamente como borrador cada 30 segundos.

---

### RF-USAB-012: Indicadores de Cambios

**Descripción breve:**

El sistema debe mostrar claramente qué campos han sido modificados.

**Prioridad:** Media

**Criterios de aceptación:**

• El formulario de edición debe mostrar claramente qué campos han sido modificados.

---

### RF-USAB-013: Deshacer Cambios

**Descripción breve:**

El sistema debe permitir deshacer cambios antes de guardar.

**Prioridad:** Media

**Criterios de aceptación:**

• El sistema debe permitir deshacer cambios antes de guardar.

---

### RF-USAB-014: Información Contextual

**Descripción breve:**

El sistema debe proporcionar información contextual relevante durante las operaciones.

**Prioridad:** Media

**Criterios de aceptación:**

• El formulario debe mostrar información contextual de la finca asociada.

• El sistema debe mostrar claramente los permisos asociados a cada rol antes de asignar.

• El sistema debe mostrar el historial de cambios de rol del usuario.

• El sistema debe mostrar claramente qué datos serán afectados por la eliminación (análisis, imágenes, reportes).

---

### RF-USAB-015: Exportación de Datos

**Descripción breve:**

El sistema debe permitir exportar datos en múltiples formatos.

**Prioridad:** Alta

**Criterios de aceptación:**

• El sistema debe permitir exportar resultados en formatos PDF, CSV y JSON.

• El sistema debe soportar exportación de resultados en múltiples formatos (PDF, Excel, CSV, JSON).

• El historial debe ser exportable en formatos CSV, Excel y JSON.

• El sistema debe soportar exportación adicional en formatos Excel (.xlsx) y CSV para reportes.

---

### RF-USAB-016: Configuración de Hiperparámetros

**Descripción breve:**

El sistema debe proporcionar interfaz para configurar parámetros de entrenamiento.

**Prioridad:** Baja

**Criterios de aceptación:**

• El sistema debe proporcionar una interfaz clara para configurar hiperparámetros de entrenamiento.

---

### RF-USAB-017: Plantillas Personalizables

**Descripción breve:**

El sistema debe ofrecer plantillas predefinidas y personalizables.

**Prioridad:** Media

**Criterios de aceptación:**

• El sistema debe ofrecer plantillas de reporte predefinidas y personalizables.

• Los usuarios deben poder seleccionar el rango de fechas, fincas, lotes y métricas a incluir en el reporte.

---

### RF-USAB-018: Búsquedas Guardadas

**Descripción breve:**

El sistema debe permitir guardar búsquedas frecuentes.

**Prioridad:** Baja

**Criterios de aceptación:**

• El sistema debe permitir guardar búsquedas frecuentes como favoritos.

---

### RF-USAB-019: Recuperación de Contraseña

**Descripción breve:**

El sistema debe ofrecer funcionalidad de recuperación de contraseña accesible.

**Prioridad:** Alta

**Criterios de aceptación:**

• El sistema debe ofrecer recuperación de contraseña accesible desde la pantalla de inicio de sesión.

---

### RF-USAB-020: Búsqueda de Duplicados

**Descripción breve:**

El sistema debe permitir buscar entidades existentes antes de crear para evitar duplicados.

**Prioridad:** Media

**Criterios de aceptación:**

• El sistema debe permitir buscar agricultores existentes antes de crear para evitar duplicados.

---

### RF-USAB-021: Campos Obligatorios Marcados

**Descripción breve:**

El sistema debe indicar claramente qué campos son obligatorios.

**Prioridad:** Media

**Criterios de aceptación:**

• El formulario debe incluir campos obligatorios claramente marcados.

---

### RF-USAB-022: Selección Interactiva de Ubicación

**Descripción breve:**

El sistema debe permitir seleccionar ubicación mediante mapas interactivos.

**Prioridad:** Media

**Criterios de aceptación:**

• El sistema debe permitir seleccionar ubicación mediante mapa interactivo (integración con mapas).

---

### RF-USAB-023: Gestión de Avatar

**Descripción breve:**

El sistema debe permitir gestionar avatar del usuario.

**Prioridad:** Baja

**Criterios de aceptación:**

• El formulario debe mostrar avatar del usuario con opción de actualización.

---

### RF-USAB-024: Selección Intuitiva de Roles

**Descripción breve:**

El sistema debe proporcionar interfaz intuitiva para selección de roles.

**Prioridad:** Media

**Criterios de aceptación:**

• La interfaz debe ser intuitiva con selección de rol desde dropdown o lista.

---

### RF-USAB-025: Selección de Finca desde Listado

**Descripción breve:**

El sistema debe permitir seleccionar finca desde un listado filtrado y ordenado.

**Prioridad:** Media

**Criterios de aceptación:**

• El formulario debe permitir seleccionar la finca desde un listado filtrado y ordenado.

---

### RF-USAB-026: Pausar y Reanudar Operaciones

**Descripción breve:**

El sistema debe permitir pausar y reanudar operaciones largas.

**Prioridad:** Baja

**Criterios de aceptación:**

• El sistema debe permitir pausar y reanudar entrenamientos largos.

---

## Confiabilidad

### RF-CONF-001: Tasas de Éxito

**Descripción breve:**

El sistema debe mantener tasas de éxito mínimas para diferentes operaciones.

**Prioridad:** Alta

**Criterios de aceptación:**

• El sistema debe mantener una tasa de éxito de registro del 99.5% bajo condiciones normales de operación.

• El sistema debe mantener una tasa de éxito de autenticación del 99.8% bajo condiciones normales.

• El sistema debe mantener una tasa de éxito de subida del 99% incluso con conexiones inestables.

• El sistema debe mantener una tasa de éxito de procesamiento del 98% para imágenes válidas.

• El sistema debe mantener una tasa de éxito de carga de resultados del 99.5%.

• El sistema debe mantener una tasa de éxito de generación de reportes del 98%.

• El sistema debe mantener una tasa de éxito de creación del 99.5% para operaciones CRUD.

• El sistema debe mantener una tasa de éxito de edición del 99.5%.

• El sistema debe mantener una tasa de éxito de carga del historial del 99.5%.

• El sistema debe mantener una tasa de éxito de búsqueda del 99.5%.

• El sistema debe mantener una tasa de éxito de asignación de roles del 99.8%.

• El sistema debe mantener una tasa de éxito de edición de perfil del 99.5%.

---

### RF-CONF-002: Preservación de Datos en Fallos

**Descripción breve:**

El sistema debe preservar datos ingresados por el usuario en caso de fallos.

**Prioridad:** Alta

**Criterios de aceptación:**

• En caso de fallo durante el registro, el sistema debe preservar los datos ingresados (excepto contraseña) para evitar pérdida de información del usuario.

• En caso de error, el sistema debe preservar los datos ingresados (excepto datos sensibles) para evitar pérdida de información.

• En caso de error, el sistema debe preservar los datos ingresados en edición de perfil.

---

### RF-CONF-003: Reintentos Automáticos

**Descripción breve:**

El sistema debe implementar mecanismos de reintento para operaciones que fallan por causas transitorias.

**Prioridad:** Alta

**Criterios de aceptación:**

• El sistema debe implementar reintentos automáticos para conexiones inestables durante subida de archivos.

• El sistema debe implementar reintentos automáticos (máximo 3 intentos) para fallos transitorios en procesamiento.

• En caso de error al cargar resultados, el sistema debe mostrar un mensaje claro y permitir reintento.

• En caso de fallo durante la generación, el sistema debe notificar al usuario y permitir reintento sin pérdida de configuración.

---

### RF-CONF-004: Limpieza de Archivos Parciales

**Descripción breve:**

El sistema debe limpiar archivos parcialmente procesados en caso de fallos.

**Prioridad:** Media

**Criterios de aceptación:**

• En caso de fallo durante la subida, el sistema debe limpiar archivos parcialmente subidos para evitar consumo innecesario de almacenamiento.

---

### RF-CONF-005: Precisión de Modelos ML

**Descripción breve:**

El sistema debe mantener niveles mínimos de precisión en análisis y predicciones.

**Prioridad:** Alta

**Criterios de aceptación:**

• El sistema debe mantener una precisión mínima del 85% en la clasificación de calidad de granos de cacao.

• El sistema debe validar la calidad del modelo antes de desplegarlo (métricas mínimas: accuracy > 85%, F1-score > 0.80).

---

### RF-CONF-006: Alertas de Baja Confianza

**Descripción breve:**

El sistema debe alertar al usuario cuando la confianza del modelo es baja.

**Prioridad:** Media

**Criterios de aceptación:**

• En caso de baja confianza del modelo (< 60%), el sistema debe alertar al usuario y sugerir revisión manual.

---

### RF-CONF-007: Validación de Duplicados

**Descripción breve:**

El sistema debe prevenir creación de entidades duplicadas.

**Prioridad:** Alta

**Criterios de aceptación:**

• En caso de datos duplicados (mismo nombre y ubicación), el sistema debe alertar al usuario antes de crear.

• El sistema debe prevenir la creación de lotes duplicados (mismo nombre en la misma finca).

• El sistema debe prevenir creación de duplicados mediante validación de documentos únicos.

---

### RF-CONF-008: Control de Concurrencia

**Descripción breve:**

El sistema debe manejar ediciones simultáneas de la misma entidad.

**Prioridad:** Alta

**Criterios de aceptación:**

• En caso de conflicto de edición simultánea, el sistema debe implementar control de concurrencia (optimistic locking).

• En caso de edición simultánea, el sistema debe implementar control de concurrencia.

---

### RF-CONF-009: Prevención de Eliminaciones Críticas

**Descripción breve:**

El sistema debe prevenir eliminación de datos críticos con dependencias importantes.

**Prioridad:** Alta

**Criterios de aceptación:**

• El sistema debe prevenir eliminación de lotes con análisis históricos críticos a menos que el usuario tenga permisos especiales.

---

### RF-CONF-010: Transacciones y Reversión

**Descripción breve:**

El sistema debe usar transacciones para garantizar integridad y permitir reversión en caso de error.

**Prioridad:** Alta

**Criterios de aceptación:**

• En caso de error durante eliminación, el sistema debe revertir cambios parciales mediante transacciones.

• En caso de error, el sistema debe revertir el cambio mediante transacciones (para asignación de roles).

• Las operaciones deben ser transaccionales garantizando integridad de datos.

---

### RF-CONF-011: Consistencia de Resultados

**Descripción breve:**

El sistema debe garantizar que los resultados sean consistentes y reproducibles.

**Prioridad:** Media

**Criterios de aceptación:**

• Los resultados deben ser consistentes y reproducibles para las mismas consultas.

---

### RF-CONF-012: Checkpoints en Entrenamiento

**Descripción breve:**

El sistema debe mantener checkpoints durante entrenamiento para permitir recuperación.

**Prioridad:** Media

**Criterios de aceptación:**

• El sistema debe mantener checkpoints automáticos durante el entrenamiento para permitir recuperación ante fallos.

• En caso de fallo durante entrenamiento, el sistema debe permitir reanudar desde el último checkpoint.

---

### RF-CONF-013: Mensajes de Error Claros

**Descripción breve:**

El sistema debe mostrar mensajes de error claros sin exponer detalles técnicos.

**Prioridad:** Alta

**Criterios de aceptación:**

• En caso de fallo del servicio de autenticación, el sistema debe mostrar un mensaje de error claro sin exponer detalles técnicos.

---

### RF-CONF-014: Preservación de Historial

**Descripción breve:**

El sistema debe preservar datos históricos según políticas de retención.

**Prioridad:** Alta

**Criterios de aceptación:**

• El historial debe preservarse indefinidamente (o según política de retención configurada) sin pérdida de datos.

---

### RF-CONF-015: Alertas de Impacto en Datos Históricos

**Descripción breve:**

El sistema debe alertar cuando los cambios afecten datos históricos.

**Prioridad:** Media

**Criterios de aceptación:**

• El sistema debe alertar si los cambios afectan análisis o datos históricos asociados al lote.

---

### RF-CONF-016: Indicación de Campos Deshabilitados

**Descripción breve:**

El sistema debe indicar claramente por qué ciertos campos están deshabilitados.

**Prioridad:** Baja

**Criterios de aceptación:**

• Los campos deshabilitados deben indicar claramente el motivo (por ejemplo, lote con análisis históricos).

---

## Disponibilidad

### RF-DISP-001: Disponibilidad de Servicios

**Descripción breve:**

El sistema debe mantener alta disponibilidad según la criticidad de cada servicio.

**Prioridad:** Alta

**Criterios de aceptación:**

• El servicio de registro debe estar disponible el 99.9% del tiempo durante horario laboral (8:00 AM - 8:00 PM, zona horaria local).

• El servicio de autenticación debe estar disponible el 99.95% del tiempo (máximo 4.38 horas de inactividad por año).

• El servicio de subida de imágenes debe estar disponible el 99.5% del tiempo.

• El servicio de procesamiento debe estar disponible el 99% del tiempo.

• El servicio de análisis debe estar disponible el 99% del tiempo durante horario laboral.

• El servicio de visualización de resultados debe estar disponible el 99.9% del tiempo.

• El servicio de generación de reportes debe estar disponible el 99% del tiempo.

• Los servicios de gestión de fincas, lotes y agricultores deben estar disponibles el 99.5% del tiempo.

• El servicio de historial debe estar disponible el 99.5% del tiempo.

• El servicio de búsqueda debe estar disponible el 99.5% del tiempo.

• El servicio de entrenamiento debe estar disponible el 95% del tiempo (permite mantenimiento programado).

• El servicio de gestión de roles debe estar disponible el 99.9% del tiempo.

• El servicio de edición de perfil debe estar disponible el 99.9% del tiempo.

---

### RF-DISP-002: Gestión de Colas de Procesamiento

**Descripción breve:**

El sistema debe manejar colas de procesamiento con priorización para evitar bloqueos.

**Prioridad:** Media

**Criterios de aceptación:**

• El sistema debe manejar colas de procesamiento con priorización para evitar bloqueos.

---

### RF-DISP-003: Generación en Segundo Plano

**Descripción breve:**

El sistema debe permitir generar reportes y realizar operaciones largas en segundo plano.

**Prioridad:** Media

**Criterios de aceptación:**

• El sistema debe permitir generar reportes en segundo plano y notificar al usuario cuando estén listos.

---

## Compatibilidad

### RF-COMP-001: Compatibilidad con Navegadores

**Descripción breve:**

El sistema debe funcionar correctamente en navegadores modernos.

**Prioridad:** Alta

**Criterios de aceptación:**

• El sistema debe funcionar correctamente en navegadores Chrome 90+, Firefox 88+, Safari 14+, y Edge 90+.

• Los resultados deben ser accesibles desde navegadores modernos (Chrome 90+, Firefox 88+, Safari 14+, Edge 90+).

---

### RF-COMP-002: Compatibilidad con Dispositivos Móviles

**Descripción breve:**

El sistema debe ser compatible con dispositivos móviles manteniendo la misma funcionalidad.

**Prioridad:** Alta

**Criterios de aceptación:**

• El sistema debe ser compatible con dispositivos móviles (iOS 13+, Android 10+) manteniendo la misma funcionalidad.

---

### RF-COMP-003: Compatibilidad con Formatos de Imagen

**Descripción breve:**

El sistema debe soportar formatos de imagen estándar y diferentes características.

**Prioridad:** Alta

**Criterios de aceptación:**

• El sistema debe aceptar imágenes con resoluciones desde 320x240 hasta 8192x8192 píxeles.

• El sistema debe ser compatible con perfiles de color sRGB, Adobe RGB y espacios de color estándar.

• El sistema debe procesar imágenes en formatos JPEG, PNG y WebP manteniendo la calidad visual original.

• Debe ser compatible con diferentes profundidades de color (8-bit, 16-bit) y espacios de color (sRGB, Adobe RGB).

• El sistema debe soportar actualización de avatar en formatos JPEG, PNG, WebP.

---

### RF-COMP-004: Normalización de Imágenes

**Descripción breve:**

El sistema debe normalizar imágenes a formatos estándar para procesamiento.

**Prioridad:** Media

**Criterios de aceptación:**

• El sistema debe normalizar automáticamente las imágenes a un formato estándar para procesamiento posterior.

---

### RF-COMP-005: Compatibilidad con Formatos de Exportación

**Descripción breve:**

El sistema debe soportar múltiples formatos de exportación.

**Prioridad:** Alta

**Criterios de aceptación:**

• Los reportes deben generarse en formato PDF/A para garantizar compatibilidad a largo plazo.

• El sistema debe soportar exportación adicional en formatos Excel (.xlsx) y CSV.

---

### RF-COMP-006: Compatibilidad con Sistemas de Almacenamiento

**Descripción breve:**

El sistema debe ser compatible con diferentes sistemas de almacenamiento mediante abstracción.

**Prioridad:** Media

**Criterios de aceptación:**

• El sistema de almacenamiento debe ser compatible con sistemas de archivos locales, S3-compatible, y Azure Blob Storage mediante abstracción de capa de almacenamiento.

---

### RF-COMP-007: Compatibilidad con Coordenadas Geográficas

**Descripción breve:**

El sistema debe aceptar y convertir diferentes formatos de coordenadas.

**Prioridad:** Media

**Criterios de aceptación:**

• El sistema debe aceptar coordenadas en formatos estándar (WGS84, UTM) y convertirlas automáticamente.

---

### RF-COMP-008: Importación de Datos

**Descripción breve:**

El sistema debe soportar importación de datos desde diferentes formatos.

**Prioridad:** Media

**Criterios de aceptación:**

• Debe ser compatible con importación de datos de fincas desde archivos KML, GeoJSON y CSV.

• El sistema debe soportar importación masiva de lotes desde archivos CSV y Excel con validación de datos.

• Debe ser compatible con importación masiva desde archivos CSV y Excel para agricultores.

---

### RF-COMP-009: Compatibilidad con Modelos ML

**Descripción breve:**

El sistema debe ser compatible con modelos ML en formatos estándar.

**Prioridad:** Alta

**Criterios de aceptación:**

• El sistema debe ser compatible con modelos de ML en formatos estándar (ONNX, TensorFlow SavedModel, PyTorch).

• Debe soportar actualización de modelos sin interrumpir el servicio mediante versionado de modelos.

• El sistema debe soportar frameworks de ML estándar (TensorFlow, PyTorch, Scikit-learn).

• Los modelos entrenados deben exportarse en formatos estándar (ONNX, TensorFlow SavedModel, H5) para portabilidad.

---

### RF-COMP-010: Compatibilidad con Versiones Anteriores

**Descripción breve:**

El sistema debe mantener compatibilidad con versiones anteriores durante actualizaciones.

**Prioridad:** Media

**Criterios de aceptación:**

• El sistema debe mantener compatibilidad con versiones anteriores de datos de fincas durante actualizaciones de esquema.

• El sistema debe mantener compatibilidad con versiones anteriores durante actualizaciones.

---

### RF-COMP-011: Compatibilidad con Estándares de Autorización

**Descripción breve:**

El sistema debe ser compatible con estándares de autorización.

**Prioridad:** Media

**Criterios de aceptación:**

• El sistema debe ser compatible con estándares de autorización (RBAC, ABAC).

• Debe soportar roles personalizados además de roles predefinidos.

---

### RF-COMP-012: Compatibilidad con Servicios Externos de Autenticación

**Descripción breve:**

El sistema debe ser compatible con servicios de autenticación externos.

**Prioridad:** Baja

**Criterios de aceptación:**

• Debe ser compatible con integración con servicios de autenticación externos (OAuth) para sincronización de perfil.

---

### RF-COMP-013: Compatibilidad con Documentos de Identidad

**Descripción breve:**

El sistema debe aceptar diferentes formatos de documentos según región.

**Prioridad:** Baja

**Criterios de aceptación:**

• El sistema debe aceptar diferentes formatos de documentos de identidad según país/región.

---

### RF-COMP-014: Compatibilidad con Operadores de Búsqueda

**Descripción breve:**

El sistema debe soportar operadores de búsqueda estándar y avanzados.

**Prioridad:** Media

**Criterios de aceptación:**

• El sistema debe soportar operadores de búsqueda estándar (AND, OR, NOT, comodines).

• Debe ser compatible con búsqueda por rangos de fechas, rangos numéricos y búsqueda fuzzy.

---

### RF-COMP-015: Compatibilidad con Sistemas BI Externos

**Descripción breve:**

El sistema debe soportar integración con sistemas de BI mediante APIs.

**Prioridad:** Baja

**Criterios de aceptación:**

• El sistema debe soportar integración con sistemas de BI externos mediante APIs.

---

### RF-COMP-016: Compatibilidad con Motores de Búsqueda Externos

**Descripción breve:**

El sistema debe ser compatible con motores de búsqueda externos para escalabilidad.

**Prioridad:** Baja

**Criterios de aceptación:**

• El sistema de búsqueda debe ser compatible con motores de búsqueda externos (Elasticsearch, Solr) para escalabilidad.

---

## Mantenibilidad

### RF-MANT-001: Registro de Logs Estructurados

**Descripción breve:**

El sistema debe registrar todas las operaciones con logs estructurados para auditoría y depuración.

**Prioridad:** Alta

**Criterios de aceptación:**

• Los logs de registro deben incluir timestamp, IP de origen, y resultado de la operación para facilitar auditoría y depuración.

• El sistema debe registrar todos los intentos de inicio de sesión (exitosos y fallidos) con timestamp, IP y user agent.

• Los logs de autenticación deben almacenarse por un período mínimo de 90 días para auditoría y análisis de seguridad.

• El sistema debe registrar todas las subidas con metadata: usuario, timestamp, tamaño, formato, y hash del archivo.

• El sistema debe registrar métricas de procesamiento: tiempo de ejecución, tamaño de entrada/salida, y recursos utilizados.

• El sistema debe registrar todos los análisis con timestamp, usuario, imagen y resultados para trazabilidad.

• El sistema debe registrar todos los accesos a resultados con timestamp y usuario para auditoría.

• El sistema debe registrar todas las generaciones de reportes: usuario, tipo, tamaño, tiempo de generación.

• El sistema debe registrar todas las operaciones CRUD de fincas con logs estructurados.

• El sistema debe registrar todos los cambios con logs estructurados incluyendo valores anteriores y nuevos.

• El sistema debe registrar todas las creaciones de lotes con logs estructurados.

• El sistema debe registrar todas las eliminaciones con logs detallados incluyendo datos eliminados y dependencias.

• El sistema debe registrar todos los accesos al historial para auditoría.

• El sistema debe registrar todas las búsquedas con usuario, criterios y timestamp para auditoría.

• El sistema debe registrar todas las ejecuciones de entrenamiento: dataset, hiperparámetros, métricas finales, tiempo de ejecución.

• El sistema debe registrar todas las creaciones con logs estructurados (agricultores).

• Los cambios de rol deben registrarse en auditoría con usuario que realiza el cambio, usuario afectado, rol anterior y nuevo, timestamp.

• El sistema debe registrar cambios críticos (email, contraseña) con logs de auditoría.

• El sistema debe registrar todas las asignaciones con logs estructurados.

---

### RF-MANT-002: Registro de Métricas de Uso

**Descripción breve:**

El sistema debe registrar métricas de uso para análisis y optimización.

**Prioridad:** Media

**Criterios de aceptación:**

• El sistema debe registrar métricas de uso: consultas más frecuentes, tiempos de carga, errores comunes.

• El sistema debe registrar métricas de uso del historial: consultas más frecuentes, filtros utilizados, tiempos de carga.

• El sistema debe registrar métricas de búsqueda: términos más buscados, tiempos de respuesta, resultados vacíos.

• El sistema debe registrar métricas de rendimiento del modelo: precisión, recall, F1-score por lote de análisis.

---

### RF-MANT-003: Cobertura de Pruebas

**Descripción breve:**

El sistema debe mantener cobertura mínima de pruebas unitarias.

**Prioridad:** Alta

**Criterios de aceptación:**

• El código del módulo de registro debe tener una cobertura de pruebas unitarias mínima del 80%.

---

### RF-MANT-004: Modularización del Código

**Descripción breve:**

El sistema debe estar organizado en módulos independientes para facilitar mantenimiento.

**Prioridad:** Alta

**Criterios de aceptación:**

• El código de gestión de subida debe estar separado en módulos independientes (validación, almacenamiento, procesamiento).

• El código de procesamiento debe estar modularizado permitiendo agregar nuevos algoritmos sin modificar código existente.

• El código de análisis debe estar separado en capas: preprocesamiento, inferencia, postprocesamiento.

• El código de generación de reportes debe estar modularizado permitiendo agregar nuevas plantillas fácilmente.

• El código de visualización debe estar separado en componentes reutilizables.

• El código debe estar optimizado para consultas eficientes sobre grandes volúmenes de datos históricos.

• El código debe estar optimizado con índices de base de datos apropiados para búsquedas eficientes.

• El código debe estar modularizado permitiendo agregar nuevos algoritmos de entrenamiento sin modificar código existente.

---

### RF-MANT-005: Patrones de Diseño

**Descripción breve:**

El sistema debe seguir patrones de diseño apropiados para facilitar extensibilidad y mantenimiento.

**Prioridad:** Media

**Criterios de aceptación:**

• El código de autenticación debe seguir el patrón de diseño Strategy para permitir múltiples métodos de autenticación.

• El código de gestión de fincas debe seguir el patrón Repository para facilitar testing y mantenimiento.

• El código debe seguir el patrón Repository para facilitar testing (agricultores).

• El código debe seguir el principio DRY reutilizando validaciones comunes con fincas.

• El código debe reutilizar la lógica de validación de creación para mantener consistencia en ediciones.

• El código debe implementar el patrón Strategy para diferentes políticas de eliminación (física, lógica, archivado).

• El código debe seguir el patrón Strategy para diferentes sistemas de autorización.

• El código debe reutilizar validaciones comunes con otros formularios de usuario.

---

### RF-MANT-006: Separación de Capas

**Descripción breve:**

El sistema debe separar claramente las capas de presentación, lógica de negocio y acceso a datos.

**Prioridad:** Alta

**Criterios de aceptación:**

• La capa de presentación de resultados debe ser independiente del backend, permitiendo múltiples clientes (web, móvil, API).

---

### RF-MANT-007: Notificación de Cambios de Rol

**Descripción breve:**

El sistema debe notificar a los usuarios cuando su rol cambia.

**Prioridad:** Media

**Criterios de aceptación:**

• El sistema debe notificar al usuario cuando su rol cambia.

---

## Portabilidad

### RF-PORT-001: Portabilidad entre Sistemas Operativos

**Descripción breve:**

El sistema debe poder desplegarse en diferentes sistemas operativos sin modificaciones.

**Prioridad:** Media

**Criterios de aceptación:**

• El sistema de registro debe poder desplegarse en entornos Linux, Windows Server y contenedores Docker sin modificaciones al código.

• El procesamiento de imágenes debe poder ejecutarse en servidores Linux y Windows, y en contenedores Docker.

---

### RF-PORT-002: Independencia del Framework Web

**Descripción breve:**

El sistema debe mantener módulos independientes del framework web utilizado.

**Prioridad:** Media

**Criterios de aceptación:**

• El módulo de autenticación debe ser independiente del framework web utilizado, permitiendo migración futura sin afectar la lógica de negocio.

---

### RF-PORT-003: Compatibilidad con Bases de Datos

**Descripción breve:**

El sistema debe ser compatible con diferentes bases de datos relacionales.

**Prioridad:** Media

**Criterios de aceptación:**

• El sistema debe ser compatible con diferentes bases de datos relacionales (agricultores).

• El sistema de historial debe ser compatible con bases de datos relacionales y NoSQL para escalabilidad.

---

### RF-PORT-004: Compatibilidad con Bases de Datos Geoespaciales

**Descripción breve:**

El sistema debe ser compatible con bases de datos geoespaciales.

**Prioridad:** Baja

**Criterios de aceptación:**

• El sistema debe ser compatible con bases de datos geoespaciales (PostGIS, MongoDB con índices geoespaciales).

---

### RF-PORT-005: Independencia del ORM

**Descripción breve:**

El sistema debe ser independiente del ORM utilizado para permitir migración futura.

**Prioridad:** Baja

**Criterios de aceptación:**

• El sistema de gestión de lotes debe ser independiente del ORM utilizado, permitiendo migración futura.

---

### RF-PORT-006: Compatibilidad con Librerías Estándar

**Descripción breve:**

El sistema debe usar librerías estándar para facilitar mantenimiento y portabilidad.

**Prioridad:** Media

**Criterios de aceptación:**

• Debe ser compatible con librerías de procesamiento de imágenes estándar (Pillow, OpenCV) para facilitar mantenimiento.

• El sistema de generación de reportes debe ser compatible con librerías estándar (ReportLab, WeasyPrint) para facilitar mantenimiento.

---

### RF-PORT-007: Ejecución en CPU y GPU

**Descripción breve:**

El sistema debe poder ejecutarse en diferentes plataformas de hardware.

**Prioridad:** Media

**Criterios de aceptación:**

• El sistema de análisis debe poder ejecutarse en CPU y GPU (CUDA, OpenCL) para optimización de rendimiento.

• El sistema debe poder ejecutarse en servidores con GPU (CUDA, OpenCL) y en la nube (AWS SageMaker, Google Colab, Azure ML).

---

### RF-PORT-008: Compatibilidad con Servicios en la Nube

**Descripción breve:**

El sistema debe ser compatible con servicios de ML en la nube para escalabilidad.

**Prioridad:** Baja

**Criterios de aceptación:**

• Debe ser compatible con servicios de ML en la nube (AWS SageMaker, Azure ML) para escalabilidad.

---

### RF-PORT-009: Independencia del Framework de Autenticación

**Descripción breve:**

El sistema de roles debe ser independiente del framework de autenticación utilizado.

**Prioridad:** Baja

**Criterios de aceptación:**

• El sistema de roles debe ser independiente del framework de autenticación utilizado.

---

### RF-PORT-010: Transacciones Portables

**Descripción breve:**

Las operaciones deben ser transaccionales garantizando integridad en cualquier base de datos compatible.

**Prioridad:** Alta

**Criterios de aceptación:**

• Las operaciones de edición deben ser transaccionales garantizando integridad de datos en cualquier base de datos compatible.

• Las operaciones deben ser transaccionales garantizando integridad de datos (lotes).

• Las operaciones de eliminación deben ser transaccionales garantizando consistencia en cualquier base de datos.

• Las operaciones deben ser transaccionales garantizando integridad (agricultores, perfil).

---

### RF-PORT-011: Mantenimiento de Referencias Históricas

**Descripción breve:**

El sistema debe mantener referencias históricas incluso después de eliminaciones lógicas.

**Prioridad:** Media

**Criterios de aceptación:**

• El sistema debe mantener referencias históricas incluso después de eliminación lógica para reportes y auditoría.

---

## Resumen de Requisitos Funcionales por Categoría

- **Rendimiento:** 6 requisitos funcionales
- **Seguridad:** 11 requisitos funcionales
- **Usabilidad:** 26 requisitos funcionales
- **Confiabilidad:** 16 requisitos funcionales
- **Disponibilidad:** 3 requisitos funcionales
- **Compatibilidad:** 16 requisitos funcionales
- **Mantenibilidad:** 7 requisitos funcionales
- **Portabilidad:** 11 requisitos funcionales

**Total:** 96 requisitos funcionales generalizados
