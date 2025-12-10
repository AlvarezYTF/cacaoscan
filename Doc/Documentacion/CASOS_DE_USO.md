# Casos de Uso Principales - CacaoScan

## Sistema: CacaoScan - Plataforma de Análisis Digital de Granos de Cacao

---

## UC-01: Registrar Usuario

**Caso de Uso:** Registrar Usuario  
**ID:** UC-01  
**De qué trata:** Permite a un usuario nuevo crear una cuenta en el sistema proporcionando sus datos personales y credenciales de acceso.  
**Actor(es):** Usuario no registrado  
**Tipo de actor:** Primario  
**Descripción breve:** El usuario proporciona información personal (nombre, apellido, email) y credenciales (contraseña) para crear una cuenta nueva en el sistema.  
**Disparador:** El usuario accede a la página de registro y completa el formulario.

**Precondiciones:**  
- El usuario no tiene una cuenta activa en el sistema
- El sistema está disponible y operativo
- El email proporcionado no está registrado previamente

**Postcondiciones:**  
- Se crea un nuevo usuario en el sistema con estado inactivo
- Se genera un token de verificación de email
- Se envía un email de verificación al usuario
- Se crea un registro de auditoría del evento de registro

**Flujo Principal:**  
1. El usuario accede a la página de registro
2. El usuario completa el formulario con: nombre, apellido, email, contraseña y confirmación de contraseña
3. El sistema valida que todos los campos requeridos estén completos
4. El sistema valida que el email no esté registrado previamente
5. El sistema valida la fortaleza de la contraseña (mínimo 8 caracteres, mayúsculas, números)
6. El sistema valida que las contraseñas coincidan
7. El sistema crea el usuario con estado inactivo
8. El sistema genera un token de verificación de email
9. El sistema envía un email con el enlace de verificación
10. El sistema muestra un mensaje indicando que debe verificar su email
11. El sistema registra el evento en el log de auditoría

**Flujos Alternativos:**  
A1. El usuario ya tiene una cuenta: El sistema muestra un mensaje indicando que el email ya está registrado y sugiere iniciar sesión.  
A2. Verificación automática (modo desarrollo): Si el sistema está en modo desarrollo, el usuario puede activarse automáticamente sin verificación de email.

**Flujos de Excepción:**  
E1. Error de validación: Si algún campo no cumple con las validaciones, el sistema muestra mensajes de error específicos y el usuario puede corregir los datos.  
E2. Error al enviar email: Si falla el envío del email de verificación, el sistema registra el error pero permite que el usuario solicite reenvío del email.  
E3. Error de conexión a base de datos: El sistema muestra un mensaje de error y solicita al usuario intentar más tarde.

**Reglas de Negocio:**  
- El email debe ser único en el sistema
- La contraseña debe tener mínimo 8 caracteres, incluir mayúsculas, minúsculas y números
- El usuario permanece inactivo hasta verificar su email
- El token de verificación expira después de 24 horas

**Puntos de Extensión:**  
- <<include>> Validar Datos de Usuario
- <<include>> Generar Token de Verificación

---

## UC-02: Iniciar Sesión

**Caso de Uso:** Iniciar Sesión  
**ID:** UC-02  
**De qué trata:** Permite a un usuario autenticarse en el sistema utilizando sus credenciales (email y contraseña) para acceder a las funcionalidades según su rol.  
**Actor(es):** Usuario registrado  
**Tipo de actor:** Primario  
**Descripción breve:** El usuario proporciona su email y contraseña para obtener acceso autenticado al sistema y recibir tokens JWT.  
**Disparador:** El usuario accede a la página de inicio de sesión e ingresa sus credenciales.

**Precondiciones:**  
- El usuario tiene una cuenta registrada en el sistema
- El usuario tiene su email verificado (cuenta activa)
- El sistema está disponible y operativo

**Postcondiciones:**  
- El usuario queda autenticado en el sistema
- Se generan tokens JWT (access y refresh) para el usuario
- Se registra la sesión del usuario
- Se actualiza la última actividad del usuario
- Se crea un registro de auditoría del inicio de sesión

**Flujo Principal:**  
1. El usuario accede a la página de inicio de sesión
2. El usuario ingresa su email y contraseña
3. El sistema valida que los campos no estén vacíos
4. El sistema busca el usuario por email
5. El sistema verifica que el usuario exista y esté activo
6. El sistema valida la contraseña
7. El sistema genera tokens JWT (access y refresh)
8. El sistema actualiza la última actividad del usuario
9. El sistema registra el inicio de sesión en el log de auditoría
10. El sistema redirige al usuario a su dashboard según su rol

**Flujos Alternativos:**  
A1. Recordar sesión: El usuario puede seleccionar "Recordar sesión" para mantener su autenticación por un período extendido.  
A2. Recuperar contraseña: Si el usuario olvidó su contraseña, puede acceder al flujo de recuperación desde la página de login.

**Flujos de Excepción:**  
E1. Credenciales incorrectas: Si el email o contraseña son incorrectos, el sistema muestra un mensaje genérico de error sin revelar cuál campo es incorrecto.  
E2. Usuario inactivo: Si el usuario no ha verificado su email, el sistema muestra un mensaje indicando que debe verificar su cuenta.  
E3. Múltiples intentos fallidos: Si el usuario excede el límite de intentos fallidos (5), el sistema bloquea temporalmente el acceso y requiere esperar o recuperar contraseña.  
E4. Error de autenticación: Si hay un error técnico, el sistema muestra un mensaje de error y solicita intentar más tarde.

**Reglas de Negocio:**  
- El email y contraseña son obligatorios
- La contraseña se valida mediante hash almacenado en la base de datos
- El token de acceso expira después de 60 minutos
- El token de refresh expira después de 7 días
- Se permite un máximo de 5 intentos fallidos antes de bloquear temporalmente

**Puntos de Extensión:**  
- <<include>> Validar Credenciales
- <<include>> Generar Tokens JWT

---

## UC-03: Subir Imagen

**Caso de Uso:** Subir Imagen  
**ID:** UC-03  
**De qué trata:** Permite al usuario cargar una imagen de granos de cacao al sistema para su posterior análisis mediante inteligencia artificial.  
**Actor(es):** Usuario autenticado (Agricultor, Técnico, Administrador)  
**Tipo de actor:** Primario  
**Descripción breve:** El usuario selecciona y sube un archivo de imagen desde su dispositivo al sistema, el cual valida el formato y tamaño antes de almacenarla.  
**Disparador:** El usuario accede a la funcionalidad de análisis y selecciona una imagen para subir.

**Precondiciones:**  
- El usuario está autenticado en el sistema
- El usuario tiene una sesión activa
- El sistema tiene espacio disponible para almacenar imágenes
- El usuario tiene una imagen válida en su dispositivo

**Postcondiciones:**  
- La imagen se almacena en el sistema
- Se crea un registro de CacaoImage asociado al usuario
- La imagen queda disponible para procesamiento
- Se registra el evento en el log de auditoría

**Flujo Principal:**  
1. El usuario accede a la sección de análisis de imágenes
2. El usuario selecciona el botón o área para subir imagen
3. El usuario selecciona un archivo de imagen desde su dispositivo
4. El sistema valida que el archivo sea una imagen (formato: JPG, PNG, BMP, TIFF)
5. El sistema valida que el tamaño del archivo no exceda 20MB
6. El sistema valida que la imagen tenga dimensiones mínimas válidas
7. El sistema almacena la imagen en el directorio de medios
8. El sistema crea un registro de CacaoImage con metadatos
9. El sistema asocia la imagen al usuario actual
10. El sistema muestra confirmación de carga exitosa
11. El sistema registra el evento en auditoría

**Flujos Alternativos:**  
A1. Subida múltiple: El usuario puede seleccionar múltiples imágenes para subir en un lote, el sistema procesa cada una individualmente.  
A2. Arrastrar y soltar: El usuario puede arrastrar imágenes directamente al área de carga sin usar el selector de archivos.

**Flujos de Excepción:**  
E1. Formato no válido: Si el archivo no es una imagen válida, el sistema muestra un mensaje de error y solicita seleccionar otro archivo.  
E2. Tamaño excedido: Si el archivo excede 20MB, el sistema muestra un mensaje indicando el límite y solicita comprimir o seleccionar otra imagen.  
E3. Error de almacenamiento: Si hay un error al guardar la imagen, el sistema muestra un mensaje de error y solicita intentar nuevamente.  
E4. Imagen corrupta: Si la imagen está dañada o no se puede leer, el sistema muestra un mensaje de error y solicita otra imagen.

**Reglas de Negocio:**  
- Formatos permitidos: JPG, JPEG, PNG, BMP, TIFF
- Tamaño máximo: 20MB por imagen
- Cada imagen debe estar asociada a un usuario
- Las imágenes se almacenan con nombres únicos para evitar conflictos

**Puntos de Extensión:**  
- <<include>> Validar Archivo de Imagen
- <<extend>> Procesar Imagen (se ejecuta después de la subida exitosa)

---

## UC-04: Procesar Imagen

**Caso de Uso:** Procesar Imagen  
**ID:** UC-04  
**De qué trata:** Prepara la imagen subida mediante operaciones de limpieza, normalización y ajustes necesarios para el análisis mediante inteligencia artificial.  
**Actor(es):** Sistema  
**Tipo de actor:** Primario  
**Descripción breve:** El sistema aplica transformaciones a la imagen (segmentación de fondo, normalización, redimensionamiento) para prepararla para el análisis de IA.  
**Disparador:** Una imagen ha sido subida exitosamente al sistema.

**Precondiciones:**  
- La imagen existe y está almacenada en el sistema
- La imagen tiene un formato válido y se puede leer
- El modelo de segmentación U-Net está disponible (si se usa segmentación automática)

**Postcondiciones:**  
- Se genera una versión procesada de la imagen (crop sin fondo)
- Se calculan los factores de calibración de píxeles
- La imagen procesada se almacena en el directorio de crops
- Los metadatos de procesamiento se guardan

**Flujo Principal:**  
1. El sistema carga la imagen original desde el almacenamiento
2. El sistema valida que la imagen sea legible y tenga formato RGB
3. El sistema aplica segmentación de fondo usando U-Net o OpenCV
4. El sistema elimina el fondo de la imagen
5. El sistema genera un crop (recorte) del grano de cacao sin fondo
6. El sistema normaliza las dimensiones de la imagen procesada
7. El sistema calcula los factores de escala píxel a milímetros
8. El sistema almacena la imagen procesada en el directorio de crops
9. El sistema guarda los metadatos de procesamiento (dimensiones, factor de escala)
10. El sistema registra el tiempo de procesamiento

**Flujos Alternativos:**  
A1. Segmentación con OpenCV: Si el modelo U-Net no está disponible, el sistema usa técnicas de OpenCV para segmentación básica.  
A2. Procesamiento en lote: Si hay múltiples imágenes, el sistema procesa cada una secuencialmente aplicando el mismo flujo.

**Flujos de Excepción:**  
E1. Error al cargar imagen: Si la imagen no se puede leer, el sistema registra el error y marca la imagen como fallida.  
E2. Error en segmentación: Si la segmentación falla, el sistema intenta con método alternativo (OpenCV) o marca la imagen para revisión manual.  
E3. Error de almacenamiento: Si no se puede guardar la imagen procesada, el sistema registra el error y notifica al usuario.

**Reglas de Negocio:**  
- La imagen procesada debe mantener las proporciones del grano original
- El fondo debe eliminarse completamente para análisis preciso
- Los factores de calibración se calculan basándose en un objeto de referencia conocido
- El procesamiento debe completarse en menos de 30 segundos por imagen

**Puntos de Extensión:**  
- <<include>> Segmentar Fondo de Imagen
- <<include>> Calcular Calibración de Píxeles
- <<extend>> Analizar Imagen (se ejecuta después del procesamiento exitoso)

---

## UC-05: Analizar Imagen

**Caso de Uso:** Analizar Imagen  
**ID:** UC-05  
**De qué trata:** Procesa la imagen mediante modelos de inteligencia artificial (YOLOv8, modelos de regresión) para predecir las dimensiones (alto, ancho, grosor) y peso del grano de cacao.  
**Actor(es):** Sistema  
**Tipo de actor:** Primario  
**Descripción breve:** El sistema utiliza modelos de machine learning entrenados para analizar la imagen procesada y generar predicciones de dimensiones físicas y peso del grano.  
**Disparador:** La imagen ha sido procesada exitosamente y está lista para análisis.

**Precondiciones:**  
- La imagen procesada (crop) existe y está disponible
- Los modelos de IA están cargados y operativos
- Los factores de calibración de píxeles están calculados
- El sistema tiene recursos computacionales disponibles

**Postcondiciones:**  
- Se generan predicciones de dimensiones (alto, ancho, grosor en mm)
- Se genera predicción de peso (en gramos)
- Se crea un registro de CacaoPrediction asociado a la imagen
- Se almacenan los resultados del análisis
- Se registra el tiempo de procesamiento del análisis

**Flujo Principal:**  
1. El sistema carga la imagen procesada (crop sin fondo)
2. El sistema carga los modelos de IA necesarios (YOLOv8, modelo de regresión híbrido)
3. El sistema aplica transformaciones de normalización a la imagen (ImageNet)
4. El sistema extrae características de píxeles de la imagen
5. El sistema ejecuta el modelo de regresión híbrido (CNN + características de píxeles)
6. El sistema obtiene predicciones normalizadas (alto, ancho, grosor, peso)
7. El sistema desnormaliza las predicciones usando los escaladores guardados
8. El sistema aplica los factores de calibración para convertir a milímetros
9. El sistema crea un registro de CacaoPrediction con los resultados
10. El sistema asocia la predicción a la imagen original
11. El sistema almacena los resultados en la base de datos
12. El sistema registra el tiempo total de análisis

**Flujos Alternativos:**  
A1. Análisis con modelo básico: Si el modelo híbrido no está disponible, el sistema usa un modelo de regresión básico.  
A2. Análisis en lote: Si hay múltiples imágenes, el sistema procesa cada una y agrega los resultados a un lote de análisis.

**Flujos de Excepción:**  
E1. Modelo no disponible: Si los modelos de IA no están cargados, el sistema muestra un error y solicita al administrador cargar los modelos.  
E2. Error en predicción: Si el modelo falla al generar predicciones, el sistema registra el error y marca la imagen para revisión manual.  
E3. Resultados fuera de rango: Si las predicciones están fuera de rangos esperados, el sistema marca el análisis como sospechoso para validación.

**Reglas de Negocio:**  
- Las dimensiones se expresan en milímetros (mm)
- El peso se expresa en gramos (g)
- Los valores deben estar dentro de rangos físicamente posibles para granos de cacao
- El tiempo de análisis no debe exceder 60 segundos por imagen

**Puntos de Extensión:**  
- <<include>> Cargar Modelos de IA
- <<include>> Ejecutar Predicción
- <<include>> Validar Resultados

---

## UC-06: Ver Resultados

**Caso de Uso:** Ver Resultados  
**ID:** UC-06  
**De qué trata:** Permite al usuario visualizar los resultados del análisis de una imagen, incluyendo las dimensiones predichas, peso estimado y visualización de la imagen procesada.  
**Actor(es):** Usuario autenticado  
**Tipo de actor:** Primario  
**Descripción breve:** El usuario accede a la vista de resultados donde se muestran las predicciones del análisis de IA de forma clara y visual.  
**Disparador:** El análisis de una imagen ha sido completado exitosamente.

**Precondiciones:**  
- El usuario está autenticado en el sistema
- Existe un análisis completado para la imagen
- El usuario tiene permisos para ver el análisis (es el propietario o tiene rol adecuado)

**Postcondiciones:**  
- El usuario visualiza los resultados del análisis
- Se registra el acceso a los resultados en auditoría

**Flujo Principal:**  
1. El usuario accede a la sección de resultados o historial de análisis
2. El sistema lista los análisis disponibles para el usuario
3. El usuario selecciona un análisis específico
4. El sistema carga los datos del análisis (dimensiones, peso, imagen)
5. El sistema muestra la imagen original y la imagen procesada (crop)
6. El sistema muestra las dimensiones predichas (alto, ancho, grosor en mm)
7. El sistema muestra el peso estimado (en gramos)
8. El sistema muestra la fecha y hora del análisis
9. El sistema muestra información adicional (tiempo de procesamiento, confianza del modelo)
10. El usuario puede navegar entre diferentes análisis

**Flujos Alternativos:**  
A1. Vista de comparación: El usuario puede seleccionar múltiples análisis para comparar resultados lado a lado.  
A2. Vista de galería: El usuario puede ver los resultados en formato de galería con miniaturas de las imágenes.

**Flujos de Excepción:**  
E1. Análisis no encontrado: Si el análisis no existe o fue eliminado, el sistema muestra un mensaje de error.  
E2. Sin permisos: Si el usuario no tiene permisos para ver el análisis, el sistema muestra un mensaje de acceso denegado.  
E3. Imagen no disponible: Si la imagen asociada no está disponible, el sistema muestra los datos numéricos pero indica que la imagen no está disponible.

**Reglas de Negocio:**  
- Los usuarios solo pueden ver análisis de sus propias imágenes o de fincas/lotes a los que tienen acceso
- Los administradores pueden ver todos los análisis
- Los resultados se muestran con precisión de 2 decimales para dimensiones y peso

**Puntos de Extensión:**  
- <<include>> Validar Permisos de Acceso
- <<extend>> Descargar Reporte (el usuario puede descargar un reporte desde la vista de resultados)

---

## UC-07: Descargar Reporte

**Caso de Uso:** Descargar Reporte  
**ID:** UC-07  
**De qué trata:** Permite al usuario exportar los resultados de un análisis o conjunto de análisis en formato PDF para su almacenamiento o distribución.  
**Actor(es):** Usuario autenticado  
**Tipo de actor:** Primario  
**Descripción breve:** El usuario solicita la generación y descarga de un reporte en PDF que contiene los resultados del análisis con formato profesional.  
**Disparador:** El usuario hace clic en el botón "Descargar Reporte" desde la vista de resultados.

**Precondiciones:**  
- El usuario está autenticado en el sistema
- Existe al menos un análisis completado
- El usuario tiene permisos para acceder a los análisis incluidos en el reporte

**Postcondiciones:**  
- Se genera un archivo PDF con el reporte
- El archivo PDF se descarga al dispositivo del usuario
- Se registra la descarga del reporte en auditoría

**Flujo Principal:**  
1. El usuario accede a la vista de resultados de un análisis
2. El usuario selecciona la opción "Descargar Reporte"
3. El sistema valida los permisos del usuario para el análisis
4. El sistema genera el contenido del reporte (datos del análisis, imágenes, gráficos)
5. El sistema formatea el contenido en estructura de PDF
6. El sistema incluye encabezado con información del sistema y fecha
7. El sistema incluye los datos del análisis (dimensiones, peso, fecha)
8. El sistema incluye las imágenes (original y procesada) en el PDF
9. El sistema genera el archivo PDF
10. El sistema inicia la descarga del archivo al dispositivo del usuario
11. El sistema registra la descarga en auditoría

**Flujos Alternativos:**  
A1. Reporte de múltiples análisis: El usuario puede seleccionar múltiples análisis para generar un reporte consolidado.  
A2. Reporte de lote completo: El usuario puede generar un reporte de todos los análisis asociados a un lote específico.

**Flujos de Excepción:**  
E1. Error al generar PDF: Si hay un error al generar el PDF, el sistema muestra un mensaje de error y solicita intentar más tarde.  
E2. Sin permisos: Si el usuario no tiene permisos, el sistema muestra un mensaje de acceso denegado.  
E3. Análisis no disponible: Si el análisis fue eliminado, el sistema muestra un mensaje de error.

**Reglas de Negocio:**  
- El reporte debe incluir información completa del análisis
- El formato PDF debe ser legible y profesional
- El tamaño del archivo PDF no debe exceder 10MB
- Los reportes se generan con marca de tiempo

**Puntos de Extensión:**  
- <<include>> Generar Contenido de Reporte
- <<include>> Formatear PDF

---

## UC-08: Crear Finca

**Caso de Uso:** Crear Finca  
**ID:** UC-08  
**De qué trata:** Permite a un agricultor o administrador registrar una nueva finca en el sistema con su información de ubicación, dimensiones y datos del propietario.  
**Actor(es):** Agricultor, Administrador  
**Tipo de actor:** Primario  
**Descripción breve:** El usuario completa un formulario con los datos de la finca (nombre, ubicación, municipio, departamento, hectáreas, coordenadas GPS) para registrarla en el sistema.  
**Disparador:** El usuario accede a la sección de gestión de fincas y selecciona "Crear Nueva Finca".

**Precondiciones:**  
- El usuario está autenticado en el sistema
- El usuario tiene rol de Agricultor o Administrador
- El usuario tiene los datos de la finca disponibles

**Postcondiciones:**  
- Se crea un nuevo registro de Finca en el sistema
- La finca queda asociada al agricultor propietario
- La finca queda disponible para crear lotes
- Se registra el evento en auditoría

**Flujo Principal:**  
1. El usuario accede a la sección de gestión de fincas
2. El usuario selecciona "Crear Nueva Finca"
3. El sistema muestra el formulario de creación de finca
4. El usuario completa los campos: nombre, ubicación (dirección), municipio, departamento, hectáreas
5. El usuario opcionalmente ingresa coordenadas GPS (latitud, longitud)
6. El usuario opcionalmente ingresa una descripción
7. El sistema valida que todos los campos obligatorios estén completos
8. El sistema valida que el nombre de la finca sea único para el agricultor
9. El sistema valida que las hectáreas sean un número positivo
10. El sistema valida el formato de coordenadas GPS (si se proporcionan)
11. El sistema crea el registro de Finca
12. El sistema asocia la finca al agricultor actual (si es agricultor) o al agricultor especificado (si es admin)
13. El sistema muestra mensaje de confirmación
14. El sistema registra el evento en auditoría

**Flujos Alternativos:**  
A1. Crear desde mapa: El usuario puede seleccionar la ubicación en un mapa interactivo y el sistema captura automáticamente las coordenadas.  
A2. Asignar a otro agricultor (admin): Si el usuario es administrador, puede seleccionar a qué agricultor asignar la finca.

**Flujos de Excepción:**  
E1. Campos incompletos: Si faltan campos obligatorios, el sistema muestra mensajes de error específicos.  
E2. Nombre duplicado: Si ya existe una finca con el mismo nombre para el agricultor, el sistema muestra un error y solicita un nombre único.  
E3. Coordenadas inválidas: Si las coordenadas GPS no son válidas, el sistema muestra un error y permite corregirlas o omitirlas.

**Reglas de Negocio:**  
- El nombre de la finca debe ser único por agricultor
- Las hectáreas deben ser un valor positivo mayor a cero
- Las coordenadas GPS son opcionales pero deben ser válidas si se proporcionan
- Un agricultor puede tener múltiples fincas

**Puntos de Extensión:**  
- <<include>> Validar Datos de Finca
- <<include>> Validar Coordenadas GPS

---

## UC-09: Editar Finca

**Caso de Uso:** Editar Finca  
**ID:** UC-09  
**De qué trata:** Permite actualizar la información de una finca existente, modificando sus datos de ubicación, dimensiones u otros atributos.  
**Actor(es):** Agricultor (propietario), Administrador  
**Tipo de actor:** Primario  
**Descripción breve:** El usuario accede a los datos de una finca existente y modifica los campos que desea actualizar, guardando los cambios.  
**Disparador:** El usuario selecciona una finca de la lista y hace clic en "Editar".

**Precondiciones:**  
- El usuario está autenticado en el sistema
- La finca existe en el sistema
- El usuario tiene permisos para editar la finca (es el propietario o es administrador)

**Postcondiciones:**  
- Los datos de la finca se actualizan en el sistema
- Se mantiene el historial de cambios (si está habilitado)
- Se registra el evento de edición en auditoría

**Flujo Principal:**  
1. El usuario accede a la lista de fincas
2. El usuario selecciona la finca que desea editar
3. El sistema valida los permisos del usuario
4. El sistema carga los datos actuales de la finca
5. El sistema muestra el formulario de edición con los datos precargados
6. El usuario modifica los campos que desea actualizar
7. El sistema valida los datos modificados
8. El sistema valida que el nombre siga siendo único (si se modificó)
9. El sistema actualiza el registro de Finca
10. El sistema actualiza la fecha de modificación
11. El sistema muestra mensaje de confirmación
12. El sistema registra el evento en auditoría

**Flujos Alternativos:**  
A1. Edición parcial: El usuario puede modificar solo algunos campos sin necesidad de completar todo el formulario.  
A2. Cambio de propietario (admin): Un administrador puede cambiar el agricultor propietario de la finca.

**Flujos de Excepción:**  
E1. Sin permisos: Si el usuario no tiene permisos para editar la finca, el sistema muestra un mensaje de acceso denegado.  
E2. Finca no encontrada: Si la finca fue eliminada, el sistema muestra un error.  
E3. Nombre duplicado: Si el nuevo nombre ya existe para otro agricultor, el sistema muestra un error.

**Reglas de Negocio:**  
- Solo el propietario de la finca o un administrador pueden editarla
- El nombre de la finca debe seguir siendo único por agricultor
- No se pueden editar fincas que tengan lotes asociados con restricciones (depende de reglas de negocio específicas)

**Puntos de Extensión:**  
- <<include>> Validar Permisos de Edición
- <<include>> Validar Datos de Finca

---

## UC-10: Crear Lote

**Caso de Uso:** Crear Lote  
**ID:** UC-10  
**De qué trata:** Permite registrar un nuevo lote de cacao dentro de una finca existente, asociándolo con información de variedad, fechas de plantación y cosecha, y área.  
**Actor(es):** Agricultor (propietario de la finca), Administrador  
**Tipo de actor:** Primario  
**Descripción breve:** El usuario completa un formulario para crear un lote asociado a una finca, incluyendo identificador, nombre, variedad de cacao, fechas y área en hectáreas.  
**Disparador:** El usuario accede a la gestión de lotes de una finca y selecciona "Crear Nuevo Lote".

**Precondiciones:**  
- El usuario está autenticado en el sistema
- Existe una finca a la cual asociar el lote
- El usuario tiene permisos para crear lotes en la finca (es propietario o administrador)

**Postcondiciones:**  
- Se crea un nuevo registro de Lote en el sistema
- El lote queda asociado a la finca especificada
- El lote queda disponible para asociar análisis de imágenes
- Se registra el evento en auditoría

**Flujo Principal:**  
1. El usuario accede a la gestión de lotes de una finca
2. El usuario selecciona "Crear Nuevo Lote"
3. El sistema muestra el formulario de creación de lote
4. El usuario completa los campos: identificador (opcional), nombre, variedad de cacao
5. El usuario ingresa la fecha de plantación
6. El usuario opcionalmente ingresa la fecha de cosecha
7. El usuario ingresa el área del lote en hectáreas
8. El usuario opcionalmente ingresa coordenadas GPS del lote
9. El usuario opcionalmente ingresa una descripción
10. El sistema valida que todos los campos obligatorios estén completos
11. El sistema valida que la fecha de plantación sea anterior a la fecha de cosecha (si ambas están presentes)
12. El sistema valida que el área sea un número positivo
13. El sistema valida que el área del lote no exceda el área total de la finca
14. El sistema crea el registro de Lote
15. El sistema asocia el lote a la finca
16. El sistema establece el estado inicial del lote como "activo"
17. El sistema muestra mensaje de confirmación
18. El sistema registra el evento en auditoría

**Flujos Alternativos:**  
A1. Crear desde plantilla: El usuario puede usar una plantilla de lote predefinida para acelerar la creación.  
A2. Crear múltiples lotes: El usuario puede crear varios lotes en secuencia sin salir del formulario.

**Flujos de Excepción:**  
E1. Campos incompletos: Si faltan campos obligatorios, el sistema muestra mensajes de error específicos.  
E2. Fechas inválidas: Si la fecha de cosecha es anterior a la de plantación, el sistema muestra un error.  
E3. Área excedida: Si el área del lote excede el área disponible de la finca, el sistema muestra un error y sugiere ajustar el área.

**Reglas de Negocio:**  
- El identificador del lote debe ser único dentro de la finca
- La fecha de plantación es obligatoria
- La fecha de cosecha puede ser futura (lote en crecimiento)
- El área total de todos los lotes de una finca no debe exceder el área total de la finca
- El estado inicial del lote es "activo"

**Puntos de Extensión:**  
- <<include>> Validar Datos de Lote
- <<include>> Validar Área de Lote

---

## UC-11: Editar Lote

**Caso de Uso:** Editar Lote  
**ID:** UC-11  
**De qué trata:** Permite actualizar la información de un lote existente, modificando sus datos de variedad, fechas, área u otros atributos.  
**Actor(es):** Agricultor (propietario de la finca), Administrador  
**Tipo de actor:** Primario  
**Descripción breve:** El usuario accede a los datos de un lote existente y modifica los campos que desea actualizar, guardando los cambios.  
**Disparador:** El usuario selecciona un lote de la lista y hace clic en "Editar".

**Precondiciones:**  
- El usuario está autenticado en el sistema
- El lote existe en el sistema
- El usuario tiene permisos para editar el lote (es propietario de la finca o es administrador)

**Postcondiciones:**  
- Los datos del lote se actualizan en el sistema
- Se mantiene el historial de cambios (si está habilitado)
- Se registra el evento de edición en auditoría

**Flujo Principal:**  
1. El usuario accede a la lista de lotes de una finca
2. El usuario selecciona el lote que desea editar
3. El sistema valida los permisos del usuario
4. El sistema carga los datos actuales del lote
5. El sistema muestra el formulario de edición con los datos precargados
6. El usuario modifica los campos que desea actualizar
7. El sistema valida los datos modificados
8. El sistema valida que las fechas sigan siendo coherentes
9. El sistema valida que el área no exceda el área disponible de la finca
10. El sistema actualiza el registro de Lote
11. El sistema actualiza la fecha de modificación
12. El sistema muestra mensaje de confirmación
13. El sistema registra el evento en auditoría

**Flujos Alternativos:**  
A1. Cambiar estado: El usuario puede cambiar el estado del lote (activo, inactivo, cosechado, renovado) desde la edición.  
A2. Actualizar fecha de cosecha: El usuario puede actualizar la fecha de cosecha cuando el lote es cosechado.

**Flujos de Excepción:**  
E1. Sin permisos: Si el usuario no tiene permisos para editar el lote, el sistema muestra un mensaje de acceso denegado.  
E2. Lote no encontrado: Si el lote fue eliminado, el sistema muestra un error.  
E3. Fechas inválidas: Si las fechas modificadas son inconsistentes, el sistema muestra un error.

**Reglas de Negocio:**  
- Solo el propietario de la finca o un administrador pueden editar el lote
- No se puede editar un lote que tenga análisis asociados con restricciones (depende de reglas específicas)
- El estado del lote puede cambiar según su ciclo de vida

**Puntos de Extensión:**  
- <<include>> Validar Permisos de Edición
- <<include>> Validar Datos de Lote

---

## UC-12: Eliminar Lote

**Caso de Uso:** Eliminar Lote  
**ID:** UC-12  
**De qué trata:** Permite remover un lote del sistema cuando ya no es válido o necesario, eliminando su registro y asociaciones.  
**Actor(es):** Agricultor (propietario de la finca), Administrador  
**Tipo de actor:** Primario  
**Descripción breve:** El usuario selecciona un lote y solicita su eliminación, el sistema valida y procede a eliminar el registro del lote.  
**Disparador:** El usuario selecciona un lote y hace clic en "Eliminar".

**Precondiciones:**  
- El usuario está autenticado en el sistema
- El lote existe en el sistema
- El usuario tiene permisos para eliminar el lote (es propietario de la finca o es administrador)

**Postcondiciones:**  
- El lote se elimina del sistema (o se marca como eliminado si es eliminación lógica)
- Se eliminan o actualizan las asociaciones del lote
- Se registra el evento de eliminación en auditoría

**Flujo Principal:**  
1. El usuario accede a la lista de lotes de una finca
2. El usuario selecciona el lote que desea eliminar
3. El sistema valida los permisos del usuario
4. El sistema muestra un diálogo de confirmación con advertencia
5. El usuario confirma la eliminación
6. El sistema valida si el lote tiene análisis asociados
7. El sistema verifica si se permite la eliminación (según reglas de negocio)
8. El sistema elimina el registro del lote (o marca como eliminado)
9. El sistema actualiza las referencias asociadas
10. El sistema muestra mensaje de confirmación
11. El sistema registra el evento en auditoría

**Flujos Alternativos:**  
A1. Eliminación lógica: El sistema puede marcar el lote como eliminado en lugar de borrarlo físicamente, preservando el historial.  
A2. Eliminación con preservación de análisis: El sistema puede mantener los análisis asociados pero desasociarlos del lote eliminado.

**Flujos de Excepción:**  
E1. Sin permisos: Si el usuario no tiene permisos, el sistema muestra un mensaje de acceso denegado.  
E2. Lote no encontrado: Si el lote ya fue eliminado, el sistema muestra un error.  
E3. Lote con restricciones: Si el lote tiene análisis asociados que no pueden eliminarse, el sistema muestra un error y explica la restricción.

**Reglas de Negocio:**  
- Solo el propietario de la finca o un administrador pueden eliminar el lote
- Si el lote tiene análisis asociados, se debe evaluar si se permite la eliminación o se requiere desasociar primero
- La eliminación debe ser confirmada explícitamente por el usuario
- Se recomienda usar eliminación lógica para preservar el historial

**Puntos de Extensión:**  
- <<include>> Validar Permisos de Eliminación
- <<include>> Validar Restricciones de Eliminación

---

## UC-13: Ver Historial

**Caso de Uso:** Ver Historial  
**ID:** UC-13  
**De qué trata:** Permite al usuario consultar y visualizar todos los análisis de imágenes realizados anteriormente, organizados por fecha, lote o finca.  
**Actor(es):** Usuario autenticado  
**Tipo de actor:** Primario  
**Descripción breve:** El usuario accede a una vista que muestra el historial completo de análisis, permitiendo filtrar y navegar por los resultados pasados.  
**Disparador:** El usuario accede a la sección de "Historial de Análisis" desde el menú principal.

**Precondiciones:**  
- El usuario está autenticado en el sistema
- Existe al menos un análisis completado en el sistema (para el usuario o accesible según permisos)

**Postcondiciones:**  
- El usuario visualiza el historial de análisis
- Se registra el acceso al historial en auditoría

**Flujo Principal:**  
1. El usuario accede a la sección de "Historial de Análisis"
2. El sistema carga los análisis disponibles según los permisos del usuario
3. El sistema muestra la lista de análisis ordenada por fecha (más recientes primero)
4. Para cada análisis, el sistema muestra: fecha, imagen miniatura, dimensiones, peso, lote asociado
5. El usuario puede hacer clic en un análisis para ver detalles completos
6. El usuario puede aplicar filtros (por fecha, lote, finca, rango de peso)
7. El sistema actualiza la lista según los filtros aplicados
8. El usuario puede navegar entre páginas si hay muchos resultados
9. El sistema registra el acceso al historial en auditoría

**Flujos Alternativos:**  
A1. Filtro por lote: El usuario puede filtrar el historial para ver solo análisis de un lote específico.  
A2. Vista de calendario: El usuario puede ver el historial organizado por calendario mensual.  
A3. Exportar historial: El usuario puede exportar el historial completo a Excel o PDF.

**Flujos de Excepción:**  
E1. Sin análisis: Si no hay análisis disponibles, el sistema muestra un mensaje indicando que no hay historial.  
E2. Error al cargar: Si hay un error al cargar el historial, el sistema muestra un mensaje de error y solicita recargar.

**Reglas de Negocio:**  
- Los usuarios solo pueden ver análisis de sus propias imágenes o de fincas/lotes a los que tienen acceso
- Los administradores pueden ver todos los análisis del sistema
- El historial se ordena por defecto por fecha descendente (más recientes primero)
- Se aplica paginación si hay más de 20 resultados por página

**Puntos de Extensión:**  
- <<include>> Validar Permisos de Acceso
- <<extend>> Buscar Análisis (el usuario puede buscar análisis específicos desde el historial)

---

## UC-14: Buscar Análisis

**Caso de Uso:** Buscar Análisis  
**ID:** UC-14  
**De qué trata:** Permite al usuario filtrar y localizar análisis específicos utilizando criterios de búsqueda como fecha, lote, rango de dimensiones o peso.  
**Actor(es):** Usuario autenticado  
**Tipo de actor:** Primario  
**Descripción breve:** El usuario ingresa criterios de búsqueda y el sistema filtra los análisis que coinciden con esos criterios, mostrando los resultados relevantes.  
**Disparador:** El usuario accede a la funcionalidad de búsqueda desde el historial o desde el menú principal.

**Precondiciones:**  
- El usuario está autenticado en el sistema
- Existen análisis en el sistema (accesibles según permisos del usuario)

**Postcondiciones:**  
- El usuario visualiza los análisis que coinciden con los criterios de búsqueda
- Se registra la búsqueda en auditoría (opcional)

**Flujo Principal:**  
1. El usuario accede a la funcionalidad de búsqueda de análisis
2. El sistema muestra el formulario de búsqueda con campos disponibles
3. El usuario ingresa criterios de búsqueda (uno o varios):
   - Rango de fechas
   - Lote específico
   - Finca específica
   - Rango de peso (mínimo y máximo en gramos)
   - Rango de dimensiones (alto, ancho, grosor)
   - Variedad de cacao
4. El usuario hace clic en "Buscar"
5. El sistema valida los criterios de búsqueda
6. El sistema ejecuta la consulta filtrando los análisis según los criterios
7. El sistema aplica los filtros de permisos (solo análisis accesibles por el usuario)
8. El sistema muestra los resultados de la búsqueda
9. El sistema muestra el número total de resultados encontrados
10. El usuario puede hacer clic en un resultado para ver detalles
11. El usuario puede refinar la búsqueda modificando los criterios

**Flujos Alternativos:**  
A1. Búsqueda rápida: El usuario puede usar un campo de búsqueda rápida que busca en múltiples campos simultáneamente.  
A2. Búsqueda guardada: El usuario puede guardar criterios de búsqueda frecuentes para reutilizarlos.  
A3. Búsqueda avanzada: El usuario puede acceder a opciones de búsqueda avanzada con más criterios y operadores lógicos.

**Flujos de Excepción:**  
E1. Criterios inválidos: Si los criterios de búsqueda son inválidos (ej: fecha inicial mayor que fecha final), el sistema muestra un mensaje de error.  
E2. Sin resultados: Si no se encuentran análisis que coincidan, el sistema muestra un mensaje indicando que no hay resultados y sugiere ajustar los criterios.

**Reglas de Negocio:**  
- Los resultados deben respetar los permisos del usuario
- Los rangos numéricos deben ser coherentes (mínimo <= máximo)
- Las fechas deben estar en formato válido
- La búsqueda es case-insensitive para campos de texto

**Puntos de Extensión:**  
- <<include>> Validar Criterios de Búsqueda
- <<include>> Aplicar Filtros de Permisos

---

## UC-15: Entrenar Modelo

**Caso de Uso:** Entrenar Modelo  
**ID:** UC-15  
**De qué trata:** Permite a un administrador o técnico iniciar el proceso de entrenamiento automático de los modelos de inteligencia artificial del sistema para mejorar la precisión de las predicciones.  
**Actor(es):** Administrador, Técnico  
**Tipo de actor:** Primario  
**Descripción breve:** El usuario inicia el proceso de entrenamiento de los modelos de IA (U-Net para segmentación, modelos de regresión para predicción) usando el dataset disponible en el sistema.  
**Disparador:** El administrador accede a la sección de entrenamiento de modelos y selecciona "Iniciar Entrenamiento".

**Precondiciones:**  
- El usuario está autenticado y tiene rol de Administrador o Técnico
- Existe un dataset de imágenes etiquetadas disponible en el sistema
- El sistema tiene recursos computacionales disponibles (GPU opcional pero recomendada)
- Los modelos base están disponibles para entrenamiento

**Postcondiciones:**  
- Se inicia el proceso de entrenamiento en segundo plano
- Se genera un identificador de tarea (task_id) para seguimiento
- Los modelos entrenados se guardan cuando el entrenamiento completa
- Se actualiza la fecha de último entrenamiento en la configuración del sistema
- Se registra el evento en auditoría

**Flujo Principal:**  
1. El administrador accede a la sección de "Entrenamiento de Modelos"
2. El sistema muestra el estado actual de los modelos y el dataset disponible
3. El administrador configura los parámetros de entrenamiento:
   - Número de épocas
   - Tamaño de batch
   - Modelo a entrenar (U-Net, regresión híbrida, etc.)
   - Usar características de píxeles (sí/no)
4. El administrador inicia el entrenamiento
5. El sistema valida que el dataset esté disponible y sea válido
6. El sistema valida que los parámetros sean coherentes
7. El sistema crea una tarea asíncrona para el entrenamiento
8. El sistema genera un task_id para seguimiento
9. El sistema inicia el entrenamiento en segundo plano
10. El sistema muestra el task_id y permite monitorear el progreso
11. El sistema procesa el dataset (carga imágenes, normalización, splits)
12. El sistema entrena el modelo con los datos
13. El sistema guarda los checkpoints durante el entrenamiento
14. El sistema evalúa el modelo al finalizar
15. El sistema guarda el modelo entrenado final
16. El sistema actualiza la configuración del sistema con la fecha de último entrenamiento
17. El sistema registra el evento en auditoría

**Flujos Alternativos:**  
A1. Entrenamiento solo de U-Net: El administrador puede entrenar solo el modelo de segmentación U-Net.  
A2. Entrenamiento solo de regresión: El administrador puede entrenar solo los modelos de regresión sin reentrenar U-Net.  
A3. Entrenamiento con validación cruzada: El administrador puede activar validación cruzada para evaluación más robusta.

**Flujos de Excepción:**  
E1. Dataset insuficiente: Si el dataset no tiene suficientes muestras, el sistema muestra un error y solicita agregar más datos.  
E2. Error durante entrenamiento: Si ocurre un error durante el entrenamiento, el sistema registra el error, guarda el último checkpoint y notifica al administrador.  
E3. Recursos insuficientes: Si no hay recursos computacionales disponibles, el sistema muestra un error y sugiere usar GPU o reducir el tamaño de batch.

**Reglas de Negocio:**  
- El entrenamiento debe tener al menos 100 muestras en el dataset
- El modelo entrenado debe superar un umbral mínimo de precisión (R² > 0.7) para ser aceptado
- El entrenamiento puede tomar varias horas dependiendo del tamaño del dataset y recursos disponibles
- Se recomienda usar GPU para entrenamientos grandes

**Puntos de Extensión:**  
- <<include>> Validar Dataset
- <<include>> Validar Parámetros de Entrenamiento
- <<include>> Monitorear Progreso de Entrenamiento

---

## UC-16: Crear Agricultor

**Caso de Uso:** Crear Agricultor  
**ID:** UC-16  
**De qué trata:** Permite a un administrador registrar un nuevo agricultor en el sistema, creando su cuenta de usuario y asociándolo con su información personal y de contacto.  
**Actor(es):** Administrador  
**Tipo de actor:** Primario  
**Descripción breve:** El administrador completa un formulario con los datos del agricultor (nombre, apellido, email, documento, teléfono) para crear su cuenta y asignarle el rol de agricultor.  
**Disparador:** El administrador accede a la gestión de usuarios y selecciona "Crear Nuevo Agricultor".

**Precondiciones:**  
- El usuario está autenticado y tiene rol de Administrador
- El email del agricultor no está registrado previamente en el sistema
- El sistema está disponible y operativo

**Postcondiciones:**  
- Se crea un nuevo usuario con rol de agricultor
- Se crea un registro de Persona (si aplica) asociado al usuario
- El agricultor queda disponible para asociar fincas
- Se registra el evento en auditoría

**Flujo Principal:**  
1. El administrador accede a la sección de gestión de usuarios/agricultores
2. El administrador selecciona "Crear Nuevo Agricultor"
3. El sistema muestra el formulario de creación de agricultor
4. El administrador completa los campos obligatorios:
   - Nombre
   - Apellido
   - Email (será usado como username)
   - Contraseña temporal (o se genera automáticamente)
   - Número de documento de identidad
   - Teléfono (opcional)
5. El administrador opcionalmente completa campos adicionales:
   - Dirección
   - Municipio
   - Departamento
6. El sistema valida que todos los campos obligatorios estén completos
7. El sistema valida que el email no esté registrado previamente
8. El sistema valida el formato del email
9. El sistema valida que el documento sea único (si aplica)
10. El sistema crea el usuario con rol de "agricultor"
11. El sistema establece la contraseña (temporal o generada)
12. El sistema marca al usuario como activo (o requiere verificación según configuración)
13. El sistema crea registro de Persona si aplica
14. El sistema envía email de bienvenida con credenciales (si está configurado)
15. El sistema muestra mensaje de confirmación
16. El sistema registra el evento en auditoría

**Flujos Alternativos:**  
A1. Crear desde importación: El administrador puede importar múltiples agricultores desde un archivo Excel.  
A2. Crear con verificación de email: El sistema puede requerir que el agricultor verifique su email antes de activar la cuenta.

**Flujos de Excepción:**  
E1. Email duplicado: Si el email ya está registrado, el sistema muestra un error y solicita otro email.  
E2. Documento duplicado: Si el documento ya existe, el sistema muestra un error.  
E3. Error al crear usuario: Si hay un error técnico, el sistema muestra un mensaje de error y solicita intentar nuevamente.

**Reglas de Negocio:**  
- El email debe ser único en el sistema
- El documento de identidad debe ser único (si se valida)
- El rol asignado es "agricultor" por defecto
- El administrador puede establecer si el usuario requiere cambio de contraseña en primer login

**Puntos de Extensión:**  
- <<include>> Validar Datos de Agricultor
- <<include>> Crear Usuario
- <<include>> Asignar Rol

---

## UC-17: Editar Agricultor

**Caso de Uso:** Editar Agricultor  
**ID:** UC-17  
**De qué trata:** Permite a un administrador actualizar la información de un agricultor existente, modificando sus datos personales, de contacto o estado de cuenta.  
**Actor(es):** Administrador  
**Tipo de actor:** Primario  
**Descripción breve:** El administrador accede a los datos de un agricultor y modifica los campos que desea actualizar, guardando los cambios.  
**Disparador:** El administrador selecciona un agricultor de la lista y hace clic en "Editar".

**Precondiciones:**  
- El usuario está autenticado y tiene rol de Administrador
- El agricultor existe en el sistema
- El sistema está disponible y operativo

**Postcondiciones:**  
- Los datos del agricultor se actualizan en el sistema
- Se mantiene el historial de cambios (si está habilitado)
- Se registra el evento de edición en auditoría

**Flujo Principal:**  
1. El administrador accede a la lista de agricultores
2. El administrador selecciona el agricultor que desea editar
3. El sistema carga los datos actuales del agricultor
4. El sistema muestra el formulario de edición con los datos precargados
5. El administrador modifica los campos que desea actualizar:
   - Datos personales (nombre, apellido)
   - Información de contacto (teléfono, dirección)
   - Estado de la cuenta (activo/inactivo)
   - Contraseña (si se desea cambiar)
6. El sistema valida los datos modificados
7. El sistema valida que el email siga siendo único (si se modificó)
8. El sistema actualiza el registro del usuario
9. El sistema actualiza el registro de Persona si aplica
10. El sistema actualiza la fecha de modificación
11. El sistema muestra mensaje de confirmación
12. El sistema registra el evento en auditoría

**Flujos Alternativos:**  
A1. Cambiar estado de cuenta: El administrador puede activar o desactivar la cuenta del agricultor.  
A2. Resetear contraseña: El administrador puede generar una nueva contraseña temporal para el agricultor.  
A3. Cambiar rol: El administrador puede cambiar el rol del usuario (aunque esto sería parte de "Asignar Rol").

**Flujos de Excepción:**  
E1. Agricultor no encontrado: Si el agricultor fue eliminado, el sistema muestra un error.  
E2. Email duplicado: Si el nuevo email ya está en uso, el sistema muestra un error.  
E3. Error de validación: Si los datos no son válidos, el sistema muestra mensajes de error específicos.

**Reglas de Negocio:**  
- Solo un administrador puede editar agricultores
- El email debe seguir siendo único si se modifica
- No se puede desactivar un agricultor que tenga fincas activas (depende de reglas específicas)
- Los cambios se registran en auditoría

**Puntos de Extensión:**  
- <<include>> Validar Datos de Agricultor
- <<include>> Validar Estado de Cuenta

---

## UC-18: Asignar Rol

**Caso de Uso:** Asignar Rol  
**ID:** UC-18  
**De qué trata:** Permite a un administrador definir y modificar los permisos de un usuario asignándole un rol específico (Administrador, Técnico, Agricultor) que determina sus capacidades en el sistema.  
**Actor(es):** Administrador  
**Tipo de actor:** Primario  
**Descripción breve:** El administrador selecciona un usuario y le asigna o modifica su rol, lo cual determina qué funcionalidades puede acceder y qué operaciones puede realizar.  
**Disparador:** El administrador accede a la gestión de usuarios y selecciona "Asignar Rol" para un usuario específico.

**Precondiciones:**  
- El usuario está autenticado y tiene rol de Administrador
- El usuario objetivo existe en el sistema
- El sistema está disponible y operativo

**Postcondiciones:**  
- El rol del usuario se actualiza en el sistema
- Los permisos del usuario se actualizan según el nuevo rol
- Se registra el cambio de rol en auditoría

**Flujo Principal:**  
1. El administrador accede a la gestión de usuarios
2. El administrador selecciona un usuario de la lista
3. El administrador selecciona la opción "Asignar Rol" o "Cambiar Rol"
4. El sistema muestra el rol actual del usuario
5. El sistema muestra los roles disponibles:
   - Administrador (acceso completo al sistema)
   - Técnico/Analista (puede analizar imágenes y gestionar lotes)
   - Agricultor (puede gestionar sus fincas y lotes, analizar imágenes)
6. El administrador selecciona el nuevo rol para el usuario
7. El sistema valida que el cambio de rol sea permitido
8. El sistema valida que no se esté removiendo el último administrador del sistema
9. El sistema actualiza el rol del usuario
10. El sistema actualiza los permisos asociados al rol
11. El sistema invalida las sesiones activas del usuario (si aplica)
12. El sistema muestra mensaje de confirmación
13. El sistema registra el cambio de rol en auditoría

**Flujos Alternativos:**  
A1. Asignar múltiples roles: El sistema puede soportar usuarios con múltiples roles (aunque el sistema actual puede usar un solo rol).  
A2. Permisos personalizados: El administrador puede asignar permisos específicos además del rol base.

**Flujos de Excepción:**  
E1. Usuario no encontrado: Si el usuario fue eliminado, el sistema muestra un error.  
E2. Último administrador: Si se intenta cambiar el rol del último administrador, el sistema muestra un error y previene la acción.  
E3. Rol inválido: Si el rol seleccionado no existe, el sistema muestra un error.

**Reglas de Negocio:**  
- Solo un administrador puede asignar roles
- Debe haber al menos un administrador activo en el sistema
- El cambio de rol afecta inmediatamente los permisos del usuario
- Los roles disponibles son: Administrador, Técnico, Agricultor
- Un usuario no puede asignarse o quitarse su propio rol de administrador

**Puntos de Extensión:**  
- <<include>> Validar Cambio de Rol
- <<include>> Actualizar Permisos

---

## UC-19: Editar Perfil

**Caso de Uso:** Editar Perfil  
**ID:** UC-19  
**De qué trata:** Permite a un usuario autenticado actualizar sus propios datos personales, información de contacto y preferencias de cuenta sin necesidad de intervención administrativa.  
**Actor(es):** Usuario autenticado  
**Tipo de actor:** Primario  
**Descripción breve:** El usuario accede a su perfil personal y modifica sus datos (nombre, apellido, teléfono, dirección) y opcionalmente cambia su contraseña.  
**Disparador:** El usuario accede a la sección "Mi Perfil" o "Configuración de Cuenta" desde el menú de usuario.

**Precondiciones:**  
- El usuario está autenticado en el sistema
- El usuario tiene una sesión activa
- El sistema está disponible y operativo

**Postcondiciones:**  
- Los datos personales del usuario se actualizan en el sistema
- Si se cambió la contraseña, la sesión puede requerir reautenticación
- Se registra la actualización en auditoría

**Flujo Principal:**  
1. El usuario accede a la sección "Mi Perfil" o "Configuración"
2. El sistema carga los datos actuales del usuario
3. El sistema muestra el formulario de edición con los datos precargados
4. El usuario modifica los campos que desea actualizar:
   - Nombre
   - Apellido
   - Teléfono
   - Dirección
   - Municipio
   - Departamento
5. El usuario opcionalmente cambia su contraseña:
   - Ingresa contraseña actual
   - Ingresa nueva contraseña
   - Confirma nueva contraseña
6. El sistema valida los datos modificados
7. El sistema valida que la contraseña actual sea correcta (si se cambió contraseña)
8. El sistema valida la fortaleza de la nueva contraseña (si se cambió)
9. El sistema valida que las nuevas contraseñas coincidan (si se cambió)
10. El sistema actualiza el registro del usuario
11. El sistema actualiza la fecha de modificación
12. El sistema muestra mensaje de confirmación
13. Si se cambió la contraseña, el sistema puede requerir reautenticación
14. El sistema registra la actualización en auditoría

**Flujos Alternativos:**  
A1. Cambiar solo contraseña: El usuario puede acceder directamente a "Cambiar Contraseña" sin editar otros datos.  
A2. Actualizar foto de perfil: El usuario puede subir o cambiar su foto de perfil (si está habilitado).

**Flujos de Excepción:**  
E1. Contraseña actual incorrecta: Si la contraseña actual es incorrecta, el sistema muestra un error y no permite el cambio.  
E2. Contraseña débil: Si la nueva contraseña no cumple con los requisitos de fortaleza, el sistema muestra un error con los requisitos.  
E3. Contraseñas no coinciden: Si las nuevas contraseñas no coinciden, el sistema muestra un error.

**Reglas de Negocio:**  
- El usuario solo puede editar su propio perfil
- El email no se puede cambiar desde el perfil (requiere proceso administrativo)
- La contraseña debe cumplir con los requisitos de fortaleza (mínimo 8 caracteres, mayúsculas, números)
- Los cambios se aplican inmediatamente después de guardar

**Puntos de Extensión:**  
- <<include>> Validar Contraseña Actual
- <<include>> Validar Fortaleza de Contraseña

---

## Relaciones entre Casos de Uso

### Relaciones <<include>>
- **Validar Datos de Usuario** es incluido por: UC-01 (Registrar Usuario)
- **Generar Token de Verificación** es incluido por: UC-01 (Registrar Usuario)
- **Validar Credenciales** es incluido por: UC-02 (Iniciar Sesión)
- **Generar Tokens JWT** es incluido por: UC-02 (Iniciar Sesión)
- **Validar Archivo de Imagen** es incluido por: UC-03 (Subir Imagen)
- **Segmentar Fondo de Imagen** es incluido por: UC-04 (Procesar Imagen)
- **Calcular Calibración de Píxeles** es incluido por: UC-04 (Procesar Imagen)
- **Cargar Modelos de IA** es incluido por: UC-05 (Analizar Imagen)
- **Ejecutar Predicción** es incluido por: UC-05 (Analizar Imagen)
- **Validar Resultados** es incluido por: UC-05 (Analizar Imagen)
- **Validar Permisos de Acceso** es incluido por: UC-06 (Ver Resultados), UC-13 (Ver Historial)
- **Generar Contenido de Reporte** es incluido por: UC-07 (Descargar Reporte)
- **Formatear PDF** es incluido por: UC-07 (Descargar Reporte)
- **Validar Datos de Finca** es incluido por: UC-08 (Crear Finca), UC-09 (Editar Finca)
- **Validar Coordenadas GPS** es incluido por: UC-08 (Crear Finca)
- **Validar Permisos de Edición** es incluido por: UC-09 (Editar Finca), UC-11 (Editar Lote)
- **Validar Datos de Lote** es incluido por: UC-10 (Crear Lote), UC-11 (Editar Lote)
- **Validar Área de Lote** es incluido por: UC-10 (Crear Lote)
- **Validar Permisos de Eliminación** es incluido por: UC-12 (Eliminar Lote)
- **Validar Restricciones de Eliminación** es incluido por: UC-12 (Eliminar Lote)
- **Validar Criterios de Búsqueda** es incluido por: UC-14 (Buscar Análisis)
- **Aplicar Filtros de Permisos** es incluido por: UC-14 (Buscar Análisis)
- **Validar Dataset** es incluido por: UC-15 (Entrenar Modelo)
- **Validar Parámetros de Entrenamiento** es incluido por: UC-15 (Entrenar Modelo)
- **Monitorear Progreso de Entrenamiento** es incluido por: UC-15 (Entrenar Modelo)
- **Validar Datos de Agricultor** es incluido por: UC-16 (Crear Agricultor), UC-17 (Editar Agricultor)
- **Crear Usuario** es incluido por: UC-16 (Crear Agricultor)
- **Asignar Rol** (como función) es incluido por: UC-16 (Crear Agricultor)
- **Validar Estado de Cuenta** es incluido por: UC-17 (Editar Agricultor)
- **Validar Cambio de Rol** es incluido por: UC-18 (Asignar Rol)
- **Actualizar Permisos** es incluido por: UC-18 (Asignar Rol)
- **Validar Contraseña Actual** es incluido por: UC-19 (Editar Perfil)
- **Validar Fortaleza de Contraseña** es incluido por: UC-19 (Editar Perfil)

### Relaciones <<extend>>
- **Procesar Imagen** extiende a: UC-03 (Subir Imagen) - se ejecuta después de subida exitosa
- **Analizar Imagen** extiende a: UC-04 (Procesar Imagen) - se ejecuta después de procesamiento exitoso
- **Descargar Reporte** extiende a: UC-06 (Ver Resultados) - opción disponible desde la vista de resultados
- **Buscar Análisis** extiende a: UC-13 (Ver Historial) - funcionalidad disponible desde el historial

---

## Notas Finales

- Todos los casos de uso respetan los principios de seguridad y auditoría del sistema
- Los permisos se validan en cada operación según el rol del usuario
- Todos los eventos importantes se registran en el sistema de auditoría
- Los casos de uso están diseñados para ser claros, accionables y orientados al usuario final
- El sistema soporta operaciones tanto individuales como en lote según el caso de uso

