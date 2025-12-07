# Manual de Usuario - CacaoScan

## Información de Versionado del Manual

**Versión:** 1.0  
**Fecha:** 2024  
**Autor(es):** Equipo de Desarrollo CacaoScan

---

## Introducción

### Breve Explicación del Módulo

CacaoScan es una plataforma digital diseñada para el análisis automatizado de granos de cacao mediante inteligencia artificial. El sistema permite a agricultores, técnicos y administradores subir imágenes de granos de cacao, procesarlas automáticamente y obtener predicciones precisas sobre las dimensiones físicas (alto, ancho, grosor) y el peso de cada grano.

La plataforma integra modelos de machine learning avanzados (U-Net para segmentación y modelos de regresión híbridos) que analizan las imágenes y generan resultados confiables en segundos, facilitando la evaluación de la calidad del cacao de manera eficiente y precisa.

### Objetivo del Módulo

El objetivo principal de CacaoScan es proporcionar una herramienta tecnológica que permita:

- Analizar granos de cacao de forma automatizada mediante inteligencia artificial
- Gestionar fincas y lotes de cacao de manera organizada
- Registrar y consultar el historial completo de análisis realizados
- Generar reportes profesionales en formato PDF para documentación y análisis
- Facilitar la toma de decisiones basada en datos precisos sobre la calidad del cacao

### Qué Puede Hacer el Usuario en Este Módulo

Los usuarios pueden realizar las siguientes acciones según su rol:

**Para todos los usuarios autenticados:**
- Subir imágenes de granos de cacao para análisis
- Ver resultados detallados de los análisis realizados
- Descargar reportes en PDF de los análisis
- Consultar el historial completo de análisis
- Buscar análisis específicos mediante filtros avanzados
- Editar su perfil personal y cambiar su contraseña

**Para Agricultores:**
- Crear y gestionar sus fincas
- Crear, editar y eliminar lotes dentro de sus fincas
- Asociar análisis de imágenes a sus lotes

**Para Administradores y Técnicos:**
- Todas las funcionalidades anteriores
- Crear y gestionar cuentas de agricultores
- Asignar roles a los usuarios del sistema
- Entrenar y actualizar los modelos de inteligencia artificial

---

## Requisitos Previos

### Permisos Necesarios

Para acceder y utilizar CacaoScan, los usuarios deben cumplir con los siguientes requisitos:

1. **Usuario Registrado:**
   - Tener una cuenta creada en el sistema
   - Haber verificado su email (cuenta activa)
   - Tener credenciales de acceso válidas (email y contraseña)

2. **Permisos por Rol:**
   - **Agricultor:** Puede gestionar sus propias fincas y lotes, subir imágenes y ver sus análisis
   - **Técnico:** Puede realizar análisis, gestionar lotes y entrenar modelos
   - **Administrador:** Acceso completo al sistema, incluyendo gestión de usuarios y configuración

### Navegadores Soportados

CacaoScan es compatible con los siguientes navegadores web:

- **Google Chrome** (versión 90 o superior) - Recomendado
- **Mozilla Firefox** (versión 88 o superior)
- **Microsoft Edge** (versión 90 o superior)
- **Safari** (versión 14 o superior) - Solo para macOS/iOS

**Nota:** Se recomienda utilizar la versión más reciente del navegador para una experiencia óptima.

### Consideraciones Importantes

Antes de utilizar el sistema, tenga en cuenta:

1. **Conexión a Internet:** Se requiere una conexión estable a internet para acceder al sistema
2. **Formato de Imágenes:** Las imágenes deben estar en formato JPG, JPEG, PNG, BMP o TIFF
3. **Tamaño de Archivos:** El tamaño máximo por imagen es de 20MB
4. **Sesión Activa:** La sesión expira después de 60 minutos de inactividad
5. **Tokens de Acceso:** Los tokens de acceso tienen una validez de 60 minutos; los tokens de refresh duran 7 días
6. **Verificación de Email:** Los usuarios nuevos deben verificar su email antes de poder iniciar sesión
7. **Intentos de Login:** Después de 5 intentos fallidos, el acceso se bloquea temporalmente

---

## Acceso al Módulo

### Pasos para Ingresar al Sistema

1. Abra su navegador web preferido
2. Ingrese la URL del sistema CacaoScan en la barra de direcciones
3. Será redirigido a la página de inicio de sesión
4. Ingrese su email y contraseña en los campos correspondientes
5. Haga clic en el botón "Iniciar Sesión"
6. Si las credenciales son correctas, será redirigido a su dashboard según su rol

**Nota:** Si no tiene una cuenta, puede registrarse haciendo clic en el enlace "Registrarse" o "Crear cuenta" en la página de inicio de sesión.

### Rutas Directas del Módulo

Las siguientes son las rutas principales del sistema:

- **Página de Inicio de Sesión:** `/login`
- **Página de Registro:** `/register`
- **Dashboard Principal:** `/dashboard`
- **Análisis de Imágenes:** `/analysis`
- **Gestión de Fincas:** `/farms`
- **Gestión de Lotes:** `/lots`
- **Historial de Análisis:** `/history`
- **Búsqueda de Análisis:** `/search`
- **Gestión de Usuarios (Admin):** `/admin/users`
- **Entrenamiento de Modelos (Admin/Técnico):** `/admin/training`
- **Mi Perfil:** `/profile`

### Descripción Visual del Ingreso

Al acceder al sistema, verá:

1. **Barra Superior:** Contiene el logo de CacaoScan, menú de navegación y opciones de usuario
2. **Menú Lateral (si aplica):** Navegación principal con acceso a todas las secciones
3. **Área de Contenido Principal:** Donde se muestran las funcionalidades y datos
4. **Pie de Página:** Información del sistema y enlaces de soporte

El diseño es responsivo y se adapta a diferentes tamaños de pantalla, permitiendo su uso desde computadoras de escritorio, tablets y dispositivos móviles.

---

## Funcionalidades Principales

### 1. Registrar Usuario

**Qué permite hacer:** Permite a un usuario nuevo crear una cuenta en el sistema proporcionando sus datos personales y credenciales de acceso.

**Entre qué vistas se usa:** 
- Página de registro (`/register`)
- Página de verificación de email
- Página de inicio de sesión (después del registro)

**Descripción:** El usuario completa un formulario con su información personal (nombre, apellido, email) y crea una contraseña segura. El sistema valida los datos, crea la cuenta y envía un email de verificación. Una vez verificado el email, el usuario puede iniciar sesión.

---

### 2. Iniciar Sesión

**Qué permite hacer:** Permite a un usuario autenticarse en el sistema utilizando sus credenciales (email y contraseña) para acceder a las funcionalidades según su rol.

**Entre qué vistas se usa:**
- Página de inicio de sesión (`/login`)
- Dashboard principal (`/dashboard`)
- Todas las secciones del sistema (después de autenticarse)

**Descripción:** El usuario ingresa su email y contraseña. El sistema valida las credenciales, genera tokens JWT y redirige al usuario a su dashboard personalizado según su rol (Agricultor, Técnico o Administrador).

---

### 3. Subir Imagen

**Qué permite hacer:** Permite al usuario cargar una imagen de granos de cacao al sistema para su posterior análisis mediante inteligencia artificial.

**Entre qué vistas se usa:**
- Sección de análisis de imágenes (`/analysis`)
- Vista de carga de imágenes
- Vista de resultados (después del análisis)

**Descripción:** El usuario selecciona una o múltiples imágenes desde su dispositivo. El sistema valida el formato y tamaño, almacena la imagen y la procesa automáticamente. También se puede arrastrar y soltar imágenes directamente al área de carga.

---

### 4. Ver Resultados

**Qué permite hacer:** Permite al usuario visualizar los resultados del análisis de una imagen, incluyendo las dimensiones predichas, peso estimado y visualización de la imagen procesada.

**Entre qué vistas se usa:**
- Vista de resultados de análisis (`/analysis/results/:id`)
- Historial de análisis (`/history`)
- Vista de detalles de análisis

**Descripción:** El usuario accede a la vista de resultados donde se muestran las predicciones del análisis de IA: dimensiones (alto, ancho, grosor en mm), peso estimado (en gramos), imágenes original y procesada, fecha del análisis y métricas adicionales. También puede comparar múltiples análisis lado a lado.

---

### 5. Descargar Reporte

**Qué permite hacer:** Permite al usuario exportar los resultados de un análisis o conjunto de análisis en formato PDF para su almacenamiento o distribución.

**Entre qué vistas se usa:**
- Vista de resultados de análisis (`/analysis/results/:id`)
- Historial de análisis (`/history`)
- Vista de comparación de análisis

**Descripción:** Desde la vista de resultados, el usuario puede generar y descargar un reporte profesional en PDF que incluye todos los datos del análisis, imágenes, gráficos y metadatos. También puede generar reportes consolidados de múltiples análisis o de un lote completo.

---

### 6. Crear Finca

**Qué permite hacer:** Permite a un agricultor o administrador registrar una nueva finca en el sistema con su información de ubicación, dimensiones y datos del propietario.

**Entre qué vistas se usa:**
- Gestión de fincas (`/farms`)
- Formulario de creación de finca (`/farms/create`)
- Lista de fincas del agricultor

**Descripción:** El usuario completa un formulario con los datos de la finca: nombre, ubicación (dirección, municipio, departamento), hectáreas, coordenadas GPS (opcional) y descripción. La finca queda asociada al agricultor y disponible para crear lotes.

---

### 7. Editar Finca

**Qué permite hacer:** Permite actualizar la información de una finca existente, modificando sus datos de ubicación, dimensiones u otros atributos.

**Entre qué vistas se usa:**
- Lista de fincas (`/farms`)
- Formulario de edición de finca (`/farms/edit/:id`)
- Detalles de finca

**Descripción:** El usuario accede a los datos de una finca existente y modifica los campos que desea actualizar. El sistema valida los cambios y actualiza el registro. Solo el propietario de la finca o un administrador pueden editarla.

---

### 8. Crear Lote

**Qué permite hacer:** Permite registrar un nuevo lote de cacao dentro de una finca existente, asociándolo con información de variedad, fechas de plantación y cosecha, y área.

**Entre qué vistas se usa:**
- Gestión de lotes de una finca (`/farms/:id/lots`)
- Formulario de creación de lote (`/farms/:id/lots/create`)
- Detalles de finca

**Descripción:** El usuario completa un formulario para crear un lote asociado a una finca, incluyendo identificador (opcional), nombre, variedad de cacao, fecha de plantación, fecha de cosecha (opcional), área en hectáreas, coordenadas GPS (opcional) y descripción. El lote queda disponible para asociar análisis de imágenes.

---

### 9. Editar Lote

**Qué permite hacer:** Permite actualizar la información de un lote existente, modificando sus datos de variedad, fechas, área u otros atributos.

**Entre qué vistas se usa:**
- Lista de lotes de una finca (`/farms/:id/lots`)
- Formulario de edición de lote (`/farms/:id/lots/edit/:lotId`)
- Detalles de lote

**Descripción:** El usuario accede a los datos de un lote existente y modifica los campos que desea actualizar. También puede cambiar el estado del lote (activo, inactivo, cosechado, renovado). El sistema valida que las fechas sean coherentes y que el área no exceda el área disponible de la finca.

---

### 10. Eliminar Lote

**Qué permite hacer:** Permite remover un lote del sistema cuando ya no es válido o necesario, eliminando su registro y asociaciones.

**Entre qué vistas se usa:**
- Lista de lotes de una finca (`/farms/:id/lots`)
- Detalles de lote
- Formulario de confirmación de eliminación

**Descripción:** El usuario selecciona un lote y solicita su eliminación. El sistema muestra un diálogo de confirmación con advertencia. Si el lote tiene análisis asociados, el sistema evalúa si se permite la eliminación o se requiere desasociar primero. La eliminación se registra en auditoría.

---

### 11. Ver Historial

**Qué permite hacer:** Permite al usuario consultar y visualizar todos los análisis de imágenes realizados anteriormente, organizados por fecha, lote o finca.

**Entre qué vistas se usa:**
- Historial de análisis (`/history`)
- Vista de lista de análisis
- Vista de detalles de análisis individual

**Descripción:** El usuario accede a una vista que muestra el historial completo de análisis, permitiendo filtrar por fecha, lote, finca o rango de peso. Los análisis se muestran ordenados por fecha (más recientes primero) con paginación. También puede exportar el historial completo a Excel o PDF.

---

### 12. Buscar Análisis

**Qué permite hacer:** Permite al usuario filtrar y localizar análisis específicos utilizando criterios de búsqueda como fecha, lote, rango de dimensiones o peso.

**Entre qué vistas se usa:**
- Búsqueda de análisis (`/search`)
- Historial de análisis (`/history`) - con opción de búsqueda
- Formulario de búsqueda avanzada

**Descripción:** El usuario ingresa criterios de búsqueda (rango de fechas, lote, finca, rango de peso, rango de dimensiones, variedad de cacao) y el sistema filtra los análisis que coinciden. Los resultados respetan los permisos del usuario y se pueden refinar modificando los criterios.

---

### 13. Entrenar Modelo

**Qué permite hacer:** Permite a un administrador o técnico iniciar el proceso de entrenamiento automático de los modelos de inteligencia artificial del sistema para mejorar la precisión de las predicciones.

**Entre qué vistas se usa:**
- Entrenamiento de modelos (`/admin/training`)
- Configuración de parámetros de entrenamiento
- Monitoreo de progreso de entrenamiento

**Descripción:** El administrador configura los parámetros de entrenamiento (número de épocas, tamaño de batch, modelo a entrenar) y inicia el proceso. El sistema valida el dataset, crea una tarea asíncrona y permite monitorear el progreso. El entrenamiento puede tomar varias horas dependiendo del tamaño del dataset.

---

### 14. Crear Agricultor

**Qué permite hacer:** Permite a un administrador registrar un nuevo agricultor en el sistema, creando su cuenta de usuario y asociándolo con su información personal y de contacto.

**Entre qué vistas se usa:**
- Gestión de usuarios/agricultores (`/admin/users`)
- Formulario de creación de agricultor (`/admin/users/create`)
- Lista de agricultores

**Descripción:** El administrador completa un formulario con los datos del agricultor (nombre, apellido, email, documento, teléfono, dirección) y crea su cuenta con rol de agricultor. El sistema genera una contraseña temporal y envía un email de bienvenida con las credenciales.

---

### 15. Editar Agricultor

**Qué permite hacer:** Permite a un administrador actualizar la información de un agricultor existente, modificando sus datos personales, de contacto o estado de cuenta.

**Entre qué vistas se usa:**
- Lista de agricultores (`/admin/users`)
- Formulario de edición de agricultor (`/admin/users/edit/:id`)
- Detalles de agricultor

**Descripción:** El administrador accede a los datos de un agricultor y modifica los campos que desea actualizar, incluyendo datos personales, información de contacto, estado de la cuenta (activo/inactivo) y contraseña. También puede resetear la contraseña del agricultor.

---

### 16. Asignar Rol

**Qué permite hacer:** Permite a un administrador definir y modificar los permisos de un usuario asignándole un rol específico (Administrador, Técnico, Agricultor) que determina sus capacidades en el sistema.

**Entre qué vistas se usa:**
- Gestión de usuarios (`/admin/users`)
- Formulario de asignación de rol
- Detalles de usuario

**Descripción:** El administrador selecciona un usuario y le asigna o modifica su rol. Los roles disponibles son: Administrador (acceso completo), Técnico/Analista (puede analizar imágenes y gestionar lotes) y Agricultor (puede gestionar sus fincas y lotes, analizar imágenes). El cambio de rol afecta inmediatamente los permisos del usuario.

---

### 17. Editar Perfil

**Qué permite hacer:** Permite a un usuario autenticado actualizar sus propios datos personales, información de contacto y preferencias de cuenta sin necesidad de intervención administrativa.

**Entre qué vistas se usa:**
- Mi Perfil (`/profile`)
- Configuración de cuenta
- Formulario de cambio de contraseña

**Descripción:** El usuario accede a su perfil personal y modifica sus datos (nombre, apellido, teléfono, dirección, municipio, departamento) y opcionalmente cambia su contraseña. El email no se puede cambiar desde el perfil (requiere proceso administrativo). Los cambios se aplican inmediatamente después de guardar.

---

## Guías Paso a Paso

### Guía 1: Registrar Usuario

**Objetivo:** Crear una nueva cuenta en el sistema CacaoScan para poder acceder a todas las funcionalidades.

**Pasos detallados:**

1. Acceda a la página de registro del sistema haciendo clic en "Registrarse" o "Crear cuenta" desde la página de inicio de sesión
2. Complete el formulario de registro con la siguiente información:
   - **Nombre:** Ingrese su nombre de pila
   - **Apellido:** Ingrese su apellido
   - **Email:** Ingrese su dirección de correo electrónico (será usado como nombre de usuario)
   - **Contraseña:** Cree una contraseña segura (mínimo 8 caracteres, debe incluir mayúsculas, minúsculas y números)
   - **Confirmar Contraseña:** Vuelva a ingresar la contraseña para confirmarla
3. Revise que todos los campos estén completos y correctos
4. Haga clic en el botón "Registrarse" o "Crear Cuenta"
5. El sistema validará los datos ingresados
6. Si la validación es exitosa, recibirá un mensaje indicando que debe verificar su email
7. Revise su bandeja de entrada (y carpeta de spam si es necesario) para encontrar el email de verificación
8. Haga clic en el enlace de verificación incluido en el email
9. Será redirigido a una página de confirmación indicando que su cuenta ha sido activada
10. Ahora puede iniciar sesión con sus credenciales

**Validaciones del sistema:**

- El email debe ser único en el sistema (no puede estar registrado previamente)
- El formato del email debe ser válido
- La contraseña debe tener mínimo 8 caracteres
- La contraseña debe incluir al menos una mayúscula, una minúscula y un número
- Las contraseñas deben coincidir exactamente
- Todos los campos obligatorios deben estar completos

**Resultado esperado:**

- Se crea un nuevo usuario en el sistema con estado inactivo inicialmente
- Se genera un token de verificación de email
- Se envía un email de verificación al usuario
- Después de verificar el email, el usuario puede iniciar sesión
- Se crea un registro de auditoría del evento de registro

---

### Guía 2: Iniciar Sesión

**Objetivo:** Autenticarse en el sistema para acceder a las funcionalidades según el rol del usuario.

**Pasos detallados:**

1. Acceda a la página de inicio de sesión del sistema
2. Ingrese su email en el campo "Email" o "Usuario"
3. Ingrese su contraseña en el campo "Contraseña"
4. (Opcional) Marque la casilla "Recordar sesión" si desea mantener su autenticación por un período extendido
5. Haga clic en el botón "Iniciar Sesión"
6. El sistema validará sus credenciales
7. Si las credenciales son correctas, será redirigido automáticamente a su dashboard según su rol:
   - **Agricultor:** Dashboard con acceso a fincas, lotes y análisis
   - **Técnico:** Dashboard con acceso a análisis y entrenamiento de modelos
   - **Administrador:** Dashboard con acceso completo al sistema
8. Su sesión quedará activa durante 60 minutos de inactividad

**Validaciones del sistema:**

- El email y contraseña son obligatorios
- El usuario debe existir en el sistema
- El usuario debe estar activo (email verificado)
- La contraseña debe ser correcta
- No se pueden exceder 5 intentos fallidos (se bloquea temporalmente el acceso)

**Resultado esperado:**

- El usuario queda autenticado en el sistema
- Se generan tokens JWT (access y refresh) para el usuario
- Se registra la sesión del usuario
- Se actualiza la última actividad del usuario
- Se crea un registro de auditoría del inicio de sesión
- El usuario es redirigido a su dashboard personalizado

---

### Guía 3: Subir Imagen

**Objetivo:** Cargar una imagen de granos de cacao al sistema para su análisis mediante inteligencia artificial.

**Pasos detallados:**

1. Inicie sesión en el sistema
2. Acceda a la sección de "Análisis de Imágenes" desde el menú principal o dashboard
3. Haga clic en el botón "Subir Imagen" o "Nuevo Análisis"
4. Seleccione el método de carga:
   - **Opción A:** Haga clic en el área de carga para abrir el selector de archivos
   - **Opción B:** Arrastre y suelte la imagen directamente en el área de carga
5. Si selecciona múltiples imágenes, puede elegir varias a la vez manteniendo presionada la tecla Ctrl (Windows) o Cmd (Mac)
6. El sistema comenzará a validar y procesar la(s) imagen(es) automáticamente
7. Verá un indicador de progreso mientras se carga y procesa la imagen
8. Una vez completada la carga, recibirá una confirmación de éxito
9. La imagen quedará disponible para análisis automático
10. Será redirigido automáticamente a la vista de resultados cuando el análisis esté completo

**Validaciones del sistema:**

- El archivo debe ser una imagen válida (formatos: JPG, JPEG, PNG, BMP, TIFF)
- El tamaño del archivo no debe exceder 20MB por imagen
- La imagen debe tener dimensiones mínimas válidas
- El usuario debe estar autenticado
- El sistema debe tener espacio disponible para almacenar imágenes

**Resultado esperado:**

- La imagen se almacena en el sistema
- Se crea un registro de CacaoImage asociado al usuario
- La imagen queda disponible para procesamiento automático
- Se inicia el procesamiento y análisis automático de la imagen
- Se registra el evento en el log de auditoría
- El usuario puede ver los resultados del análisis una vez completado

---

### Guía 4: Ver Resultados

**Objetivo:** Visualizar los resultados detallados del análisis de una imagen, incluyendo dimensiones predichas, peso estimado e imágenes procesadas.

**Pasos detallados:**

1. Inicie sesión en el sistema
2. Acceda a la sección de "Historial de Análisis" o "Resultados" desde el menú principal
3. La lista mostrará todos los análisis disponibles según sus permisos
4. Haga clic en el análisis que desea ver en detalle
5. Se abrirá la vista de resultados con la siguiente información:
   - **Imagen Original:** La imagen que subió inicialmente
   - **Imagen Procesada:** La imagen del grano sin fondo (crop)
   - **Dimensiones Predichas:**
     - Alto (en milímetros)
     - Ancho (en milímetros)
     - Grosor (en milímetros)
   - **Peso Estimado:** En gramos
   - **Fecha y Hora del Análisis**
   - **Tiempo de Procesamiento**
   - **Información del Lote:** Si está asociado a un lote
6. Puede navegar entre diferentes análisis usando las flechas de navegación
7. (Opcional) Puede seleccionar múltiples análisis para comparar resultados lado a lado
8. (Opcional) Puede descargar el reporte en PDF desde esta vista

**Validaciones del sistema:**

- El usuario debe estar autenticado
- Debe existir un análisis completado para la imagen
- El usuario debe tener permisos para ver el análisis (es el propietario o tiene rol adecuado)
- Los administradores pueden ver todos los análisis

**Resultado esperado:**

- El usuario visualiza los resultados del análisis de forma clara y organizada
- Se muestran las predicciones con precisión de 2 decimales
- Las imágenes se muestran correctamente
- Se registra el acceso a los resultados en auditoría
- El usuario puede tomar decisiones basadas en los datos mostrados

---

### Guía 5: Descargar Reporte

**Objetivo:** Exportar los resultados de un análisis o conjunto de análisis en formato PDF para almacenamiento o distribución.

**Pasos detallados:**

1. Acceda a la vista de resultados de un análisis (ver Guía 4)
2. Haga clic en el botón "Descargar Reporte" o "Exportar PDF"
3. Si desea generar un reporte de múltiples análisis:
   - Desde el historial, seleccione los análisis que desea incluir marcando las casillas
   - Haga clic en "Generar Reporte Consolidado"
4. El sistema validará sus permisos para los análisis seleccionados
5. Se mostrará un indicador de progreso mientras se genera el PDF
6. Una vez generado, el archivo PDF se descargará automáticamente a su dispositivo
7. El archivo se guardará en la carpeta de descargas predeterminada de su navegador
8. Puede abrir el PDF para verificar que contiene toda la información esperada

**Validaciones del sistema:**

- El usuario debe estar autenticado
- Debe existir al menos un análisis completado
- El usuario debe tener permisos para acceder a los análisis incluidos en el reporte
- El tamaño del archivo PDF no debe exceder 10MB

**Resultado esperado:**

- Se genera un archivo PDF con el reporte completo
- El archivo PDF incluye:
  - Encabezado con información del sistema y fecha
  - Datos del análisis (dimensiones, peso, fecha)
  - Imágenes (original y procesada)
  - Gráficos y métricas adicionales
  - Información del lote (si aplica)
- El archivo PDF se descarga al dispositivo del usuario
- Se registra la descarga del reporte en auditoría
- El formato PDF es legible y profesional

---

### Guía 6: Crear Finca

**Objetivo:** Registrar una nueva finca en el sistema con su información de ubicación, dimensiones y datos del propietario.

**Pasos detallados:**

1. Inicie sesión en el sistema con rol de Agricultor o Administrador
2. Acceda a la sección de "Gestión de Fincas" desde el menú principal
3. Haga clic en el botón "Crear Nueva Finca" o "Nueva Finca"
4. Complete el formulario con los siguientes datos obligatorios:
   - **Nombre:** Ingrese un nombre único para la finca
   - **Ubicación/Dirección:** Ingrese la dirección de la finca
   - **Municipio:** Seleccione o ingrese el municipio
   - **Departamento:** Seleccione o ingrese el departamento
   - **Hectáreas:** Ingrese el área total de la finca en hectáreas (debe ser un número positivo)
5. Complete los campos opcionales si los tiene disponibles:
   - **Coordenadas GPS - Latitud:** Ingrese la latitud (opcional)
   - **Coordenadas GPS - Longitud:** Ingrese la longitud (opcional)
   - **Descripción:** Agregue cualquier información adicional relevante
6. (Opcional) Si el sistema tiene integración con mapas, puede seleccionar la ubicación en un mapa interactivo
7. Revise que todos los datos estén correctos
8. Haga clic en el botón "Guardar" o "Crear Finca"
9. El sistema validará los datos ingresados
10. Si la validación es exitosa, verá un mensaje de confirmación
11. La finca quedará disponible en su lista de fincas y podrá crear lotes asociados a ella

**Validaciones del sistema:**

- Todos los campos obligatorios deben estar completos
- El nombre de la finca debe ser único para el agricultor
- Las hectáreas deben ser un número positivo mayor a cero
- Las coordenadas GPS deben ser válidas si se proporcionan (formato decimal)
- El usuario debe tener rol de Agricultor o Administrador

**Resultado esperado:**

- Se crea un nuevo registro de Finca en el sistema
- La finca queda asociada al agricultor propietario (o al agricultor especificado si es admin)
- La finca queda disponible para crear lotes
- Se registra el evento en auditoría
- El usuario puede ver la finca en su lista de fincas

---

### Guía 7: Editar Finca

**Objetivo:** Actualizar la información de una finca existente, modificando sus datos de ubicación, dimensiones u otros atributos.

**Pasos detallados:**

1. Inicie sesión en el sistema
2. Acceda a la sección de "Gestión de Fincas" desde el menú principal
3. Localice la finca que desea editar en la lista
4. Haga clic en el botón "Editar" o en el icono de edición junto a la finca
5. El sistema cargará los datos actuales de la finca en el formulario
6. Modifique los campos que desea actualizar:
   - Nombre (debe seguir siendo único)
   - Ubicación/Dirección
   - Municipio
   - Departamento
   - Hectáreas
   - Coordenadas GPS
   - Descripción
7. (Opcional) Si es administrador, puede cambiar el agricultor propietario de la finca
8. Revise los cambios realizados
9. Haga clic en el botón "Guardar" o "Actualizar"
10. El sistema validará los datos modificados
11. Si la validación es exitosa, verá un mensaje de confirmación
12. Los cambios se aplicarán inmediatamente

**Validaciones del sistema:**

- El usuario debe tener permisos para editar la finca (es el propietario o es administrador)
- El nombre de la finca debe seguir siendo único por agricultor (si se modificó)
- Las hectáreas deben ser un número positivo
- Las coordenadas GPS deben ser válidas si se proporcionan
- La finca debe existir en el sistema

**Resultado esperado:**

- Los datos de la finca se actualizan en el sistema
- Se mantiene el historial de cambios (si está habilitado)
- Se actualiza la fecha de modificación
- Se registra el evento de edición en auditoría
- Los cambios son visibles inmediatamente en la lista de fincas

---

### Guía 8: Crear Lote

**Objetivo:** Registrar un nuevo lote de cacao dentro de una finca existente, asociándolo con información de variedad, fechas de plantación y cosecha, y área.

**Pasos detallados:**

1. Inicie sesión en el sistema
2. Acceda a la sección de "Gestión de Fincas" desde el menú principal
3. Seleccione la finca a la cual desea asociar el lote
4. Acceda a la sección de "Lotes" de esa finca
5. Haga clic en el botón "Crear Nuevo Lote" o "Nuevo Lote"
6. Complete el formulario con los siguientes datos:
   - **Identificador:** Ingrese un identificador único para el lote dentro de la finca (opcional)
   - **Nombre:** Ingrese un nombre descriptivo para el lote
   - **Variedad de Cacao:** Seleccione la variedad de cacao del lote
   - **Fecha de Plantación:** Seleccione la fecha en que se plantó el lote (obligatorio)
   - **Fecha de Cosecha:** Seleccione la fecha de cosecha (opcional, puede ser futura)
   - **Área en Hectáreas:** Ingrese el área del lote en hectáreas (debe ser un número positivo)
   - **Coordenadas GPS:** Ingrese las coordenadas del lote si las tiene (opcional)
   - **Descripción:** Agregue cualquier información adicional relevante (opcional)
7. Revise que todos los datos estén correctos
8. Verifique que el área del lote no exceda el área disponible de la finca
9. Haga clic en el botón "Guardar" o "Crear Lote"
10. El sistema validará los datos ingresados
11. Si la validación es exitosa, verá un mensaje de confirmación
12. El lote quedará disponible en la lista de lotes de la finca y podrá asociar análisis de imágenes a él

**Validaciones del sistema:**

- Todos los campos obligatorios deben estar completos
- El identificador del lote debe ser único dentro de la finca (si se proporciona)
- La fecha de plantación es obligatoria
- La fecha de plantación debe ser anterior a la fecha de cosecha (si ambas están presentes)
- El área debe ser un número positivo
- El área del lote no debe exceder el área total de la finca
- El área total de todos los lotes de una finca no debe exceder el área total de la finca
- El usuario debe tener permisos para crear lotes en la finca

**Resultado esperado:**

- Se crea un nuevo registro de Lote en el sistema
- El lote queda asociado a la finca especificada
- El lote queda disponible para asociar análisis de imágenes
- El estado inicial del lote se establece como "activo"
- Se registra el evento en auditoría
- El usuario puede ver el lote en la lista de lotes de la finca

---

### Guía 9: Editar Lote

**Objetivo:** Actualizar la información de un lote existente, modificando sus datos de variedad, fechas, área u otros atributos.

**Pasos detallados:**

1. Inicie sesión en el sistema
2. Acceda a la sección de "Gestión de Fincas" desde el menú principal
3. Seleccione la finca que contiene el lote
4. Acceda a la sección de "Lotes" de esa finca
5. Localice el lote que desea editar en la lista
6. Haga clic en el botón "Editar" o en el icono de edición junto al lote
7. El sistema cargará los datos actuales del lote en el formulario
8. Modifique los campos que desea actualizar:
   - Identificador
   - Nombre
   - Variedad de cacao
   - Fecha de plantación
   - Fecha de cosecha
   - Área en hectáreas
   - Coordenadas GPS
   - Descripción
   - Estado del lote (activo, inactivo, cosechado, renovado)
9. Revise los cambios realizados
10. Verifique que las fechas sigan siendo coherentes
11. Verifique que el área no exceda el área disponible de la finca
12. Haga clic en el botón "Guardar" o "Actualizar"
13. El sistema validará los datos modificados
14. Si la validación es exitosa, verá un mensaje de confirmación
15. Los cambios se aplicarán inmediatamente

**Validaciones del sistema:**

- El usuario debe tener permisos para editar el lote (es propietario de la finca o es administrador)
- Las fechas deben ser coherentes (plantación anterior a cosecha)
- El área no debe exceder el área disponible de la finca
- El lote debe existir en el sistema
- No se puede editar un lote que tenga análisis asociados con restricciones (depende de reglas específicas)

**Resultado esperado:**

- Los datos del lote se actualizan en el sistema
- Se mantiene el historial de cambios (si está habilitado)
- Se actualiza la fecha de modificación
- Se registra el evento de edición en auditoría
- Los cambios son visibles inmediatamente en la lista de lotes

---

### Guía 10: Eliminar Lote

**Objetivo:** Remover un lote del sistema cuando ya no es válido o necesario, eliminando su registro y asociaciones.

**Pasos detallados:**

1. Inicie sesión en el sistema
2. Acceda a la sección de "Gestión de Fincas" desde el menú principal
3. Seleccione la finca que contiene el lote
4. Acceda a la sección de "Lotes" de esa finca
5. Localice el lote que desea eliminar en la lista
6. Haga clic en el botón "Eliminar" o en el icono de eliminación junto al lote
7. El sistema mostrará un diálogo de confirmación con una advertencia
8. Lea cuidadosamente el mensaje de advertencia
9. Si el lote tiene análisis asociados, el sistema le informará sobre las restricciones
10. Confirme la eliminación haciendo clic en "Confirmar" o "Eliminar"
11. Si cambia de opinión, puede cancelar haciendo clic en "Cancelar"
12. El sistema validará si se permite la eliminación según las reglas de negocio
13. Si la eliminación es permitida, el lote será eliminado del sistema
14. Verá un mensaje de confirmación de eliminación exitosa

**Validaciones del sistema:**

- El usuario debe tener permisos para eliminar el lote (es propietario de la finca o es administrador)
- El lote debe existir en el sistema
- Si el lote tiene análisis asociados, se debe evaluar si se permite la eliminación o se requiere desasociar primero
- La eliminación debe ser confirmada explícitamente por el usuario

**Resultado esperado:**

- El lote se elimina del sistema (o se marca como eliminado si es eliminación lógica)
- Se eliminan o actualizan las asociaciones del lote
- Se registra el evento de eliminación en auditoría
- El lote ya no aparece en la lista de lotes de la finca
- Si hay análisis asociados, pueden mantenerse pero desasociados del lote eliminado

---

### Guía 11: Ver Historial

**Objetivo:** Consultar y visualizar todos los análisis de imágenes realizados anteriormente, organizados por fecha, lote o finca.

**Pasos detallados:**

1. Inicie sesión en el sistema
2. Acceda a la sección de "Historial de Análisis" desde el menú principal o dashboard
3. El sistema cargará automáticamente los análisis disponibles según sus permisos
4. La lista mostrará los análisis ordenados por fecha (más recientes primero)
5. Para cada análisis, verá la siguiente información:
   - Fecha y hora del análisis
   - Imagen miniatura del grano
   - Dimensiones predichas (alto, ancho, grosor)
   - Peso estimado
   - Lote asociado (si aplica)
   - Finca asociada (si aplica)
6. Puede aplicar filtros para encontrar análisis específicos:
   - **Por Fecha:** Seleccione un rango de fechas
   - **Por Lote:** Seleccione un lote específico
   - **Por Finca:** Seleccione una finca específica
   - **Por Rango de Peso:** Ingrese peso mínimo y máximo en gramos
7. Haga clic en "Aplicar Filtros" para actualizar la lista
8. Haga clic en un análisis específico para ver los detalles completos
9. Si hay muchos resultados, use la paginación para navegar entre páginas
10. (Opcional) Puede exportar el historial completo a Excel o PDF

**Validaciones del sistema:**

- El usuario debe estar autenticado
- Los usuarios solo pueden ver análisis de sus propias imágenes o de fincas/lotes a los que tienen acceso
- Los administradores pueden ver todos los análisis del sistema
- Los filtros deben ser válidos (fechas coherentes, rangos numéricos válidos)

**Resultado esperado:**

- El usuario visualiza el historial de análisis de forma organizada
- Los análisis se muestran ordenados por fecha descendente
- Los filtros funcionan correctamente y actualizan la lista
- Se aplica paginación si hay más de 20 resultados por página
- Se registra el acceso al historial en auditoría
- El usuario puede encontrar y acceder a análisis específicos fácilmente

---

### Guía 12: Buscar Análisis

**Objetivo:** Filtrar y localizar análisis específicos utilizando criterios de búsqueda como fecha, lote, rango de dimensiones o peso.

**Pasos detallados:**

1. Inicie sesión en el sistema
2. Acceda a la funcionalidad de "Búsqueda de Análisis" desde el menú principal o desde el historial
3. El sistema mostrará el formulario de búsqueda con los siguientes campos disponibles:
   - **Rango de Fechas:** Seleccione fecha inicial y fecha final
   - **Lote Específico:** Seleccione un lote de la lista desplegable
   - **Finca Específica:** Seleccione una finca de la lista desplegable
   - **Rango de Peso:** Ingrese peso mínimo y máximo en gramos
   - **Rango de Dimensiones:**
     - Alto mínimo y máximo (en mm)
     - Ancho mínimo y máximo (en mm)
     - Grosor mínimo y máximo (en mm)
   - **Variedad de Cacao:** Seleccione una variedad específica
4. Complete uno o varios criterios de búsqueda según sus necesidades
5. Revise que los rangos numéricos sean coherentes (mínimo <= máximo)
6. Revise que las fechas sean válidas (fecha inicial <= fecha final)
7. Haga clic en el botón "Buscar" o "Aplicar Búsqueda"
8. El sistema ejecutará la búsqueda y mostrará los resultados
9. Verá el número total de resultados encontrados
10. Los resultados se mostrarán en una lista similar al historial
11. Haga clic en un resultado para ver los detalles completos
12. Puede refinar la búsqueda modificando los criterios y buscando nuevamente
13. (Opcional) Puede guardar los criterios de búsqueda para uso futuro

**Validaciones del sistema:**

- Los criterios de búsqueda deben ser válidos
- Los rangos numéricos deben ser coherentes (mínimo <= máximo)
- Las fechas deben estar en formato válido
- La fecha inicial no debe ser mayor que la fecha final
- Los resultados respetan los permisos del usuario

**Resultado esperado:**

- El usuario visualiza los análisis que coinciden con los criterios de búsqueda
- Los resultados se muestran de forma clara y organizada
- Se muestra el número total de resultados encontrados
- El usuario puede acceder a los detalles de cada análisis encontrado
- Si no hay resultados, se muestra un mensaje indicando que no se encontraron análisis y se sugieren ajustar los criterios
- Se registra la búsqueda en auditoría (opcional)

---

### Guía 13: Entrenar Modelo

**Objetivo:** Iniciar el proceso de entrenamiento automático de los modelos de inteligencia artificial del sistema para mejorar la precisión de las predicciones.

**Pasos detallados:**

1. Inicie sesión en el sistema con rol de Administrador o Técnico
2. Acceda a la sección de "Entrenamiento de Modelos" desde el menú de administración
3. El sistema mostrará el estado actual de los modelos y el dataset disponible
4. Revise la información del dataset:
   - Número de muestras disponibles
   - Fecha del último entrenamiento
   - Precisión actual del modelo
5. Configure los parámetros de entrenamiento:
   - **Número de Épocas:** Ingrese el número de épocas (iteraciones) para el entrenamiento
   - **Tamaño de Batch:** Seleccione el tamaño del lote para el procesamiento
   - **Modelo a Entrenar:** Seleccione qué modelo entrenar:
     - U-Net (segmentación)
     - Regresión híbrida (predicción de dimensiones y peso)
     - Ambos
   - **Usar Características de Píxeles:** Marque esta opción si desea incluir características de píxeles en el modelo
6. Revise que los parámetros sean coherentes
7. Haga clic en el botón "Iniciar Entrenamiento"
8. El sistema validará que el dataset esté disponible y sea válido
9. El sistema validará que los parámetros sean coherentes
10. Si la validación es exitosa, se creará una tarea asíncrona para el entrenamiento
11. Se generará un task_id (identificador de tarea) para seguimiento
12. El sistema mostrará el task_id y permitirá monitorear el progreso
13. El entrenamiento se ejecutará en segundo plano
14. Puede monitorear el progreso en tiempo real:
   - Porcentaje completado
   - Época actual
   - Pérdida (loss) actual
   - Tiempo estimado restante
15. El sistema guardará checkpoints durante el entrenamiento
16. Al finalizar, el sistema evaluará el modelo
17. Si el modelo supera el umbral mínimo de precisión (R² > 0.7), se guardará como modelo final
18. Se actualizará la fecha de último entrenamiento en la configuración del sistema
19. Recibirá una notificación cuando el entrenamiento haya completado

**Validaciones del sistema:**

- El usuario debe tener rol de Administrador o Técnico
- El dataset debe tener al menos 100 muestras
- Los parámetros deben ser coherentes (épocas > 0, batch size > 0)
- El sistema debe tener recursos computacionales disponibles
- El modelo entrenado debe superar un umbral mínimo de precisión (R² > 0.7) para ser aceptado

**Resultado esperado:**

- Se inicia el proceso de entrenamiento en segundo plano
- Se genera un identificador de tarea (task_id) para seguimiento
- El usuario puede monitorear el progreso en tiempo real
- Los modelos entrenados se guardan cuando el entrenamiento completa
- Se actualiza la fecha de último entrenamiento en la configuración del sistema
- Se registra el evento en auditoría
- El modelo mejorado estará disponible para análisis futuros

---

### Guía 14: Crear Agricultor

**Objetivo:** Registrar un nuevo agricultor en el sistema, creando su cuenta de usuario y asociándolo con su información personal y de contacto.

**Pasos detallados:**

1. Inicie sesión en el sistema con rol de Administrador
2. Acceda a la sección de "Gestión de Usuarios" o "Agricultores" desde el menú de administración
3. Haga clic en el botón "Crear Nuevo Agricultor" o "Nuevo Agricultor"
4. Complete el formulario con los siguientes campos obligatorios:
   - **Nombre:** Ingrese el nombre del agricultor
   - **Apellido:** Ingrese el apellido del agricultor
   - **Email:** Ingrese el email del agricultor (será usado como username)
   - **Contraseña Temporal:** Ingrese una contraseña temporal o deje que el sistema la genere automáticamente
   - **Número de Documento:** Ingrese el número de documento de identidad del agricultor
   - **Teléfono:** Ingrese el número de teléfono (opcional)
5. Complete los campos opcionales si los tiene disponibles:
   - **Dirección:** Ingrese la dirección del agricultor
   - **Municipio:** Ingrese o seleccione el municipio
   - **Departamento:** Ingrese o seleccione el departamento
6. Configure las opciones adicionales:
   - **Requerir Cambio de Contraseña:** Marque si el agricultor debe cambiar la contraseña en el primer login
   - **Activar Cuenta Inmediatamente:** Marque si la cuenta debe estar activa sin verificación de email
7. Revise que todos los datos estén correctos
8. Haga clic en el botón "Guardar" o "Crear Agricultor"
9. El sistema validará los datos ingresados
10. Si la validación es exitosa, se creará la cuenta del agricultor
11. El sistema enviará un email de bienvenida con las credenciales (si está configurado)
12. Verá un mensaje de confirmación con la información del agricultor creado

**Validaciones del sistema:**

- El usuario debe tener rol de Administrador
- El email debe ser único en el sistema (no puede estar registrado previamente)
- El formato del email debe ser válido
- El documento de identidad debe ser único (si se valida)
- Todos los campos obligatorios deben estar completos

**Resultado esperado:**

- Se crea un nuevo usuario con rol de agricultor
- Se crea un registro de Persona asociado al usuario (si aplica)
- El agricultor queda disponible para asociar fincas
- Se envía un email de bienvenida con credenciales (si está configurado)
- Se registra el evento en auditoría
- El agricultor puede iniciar sesión con las credenciales proporcionadas

---

### Guía 15: Editar Agricultor

**Objetivo:** Actualizar la información de un agricultor existente, modificando sus datos personales, de contacto o estado de cuenta.

**Pasos detallados:**

1. Inicie sesión en el sistema con rol de Administrador
2. Acceda a la sección de "Gestión de Usuarios" o "Agricultores" desde el menú de administración
3. Localice el agricultor que desea editar en la lista
4. Haga clic en el botón "Editar" o en el icono de edición junto al agricultor
5. El sistema cargará los datos actuales del agricultor en el formulario
6. Modifique los campos que desea actualizar:
   - **Datos Personales:** Nombre, apellido
   - **Información de Contacto:** Teléfono, dirección, municipio, departamento
   - **Estado de la Cuenta:** Active o desactive la cuenta del agricultor
   - **Contraseña:** Si desea cambiar la contraseña, ingrese una nueva contraseña temporal
7. (Opcional) Haga clic en "Resetear Contraseña" para generar una nueva contraseña temporal automáticamente
8. Revise los cambios realizados
9. Haga clic en el botón "Guardar" o "Actualizar"
10. El sistema validará los datos modificados
11. Si la validación es exitosa, verá un mensaje de confirmación
12. Los cambios se aplicarán inmediatamente

**Validaciones del sistema:**

- El usuario debe tener rol de Administrador
- El agricultor debe existir en el sistema
- El email debe seguir siendo único si se modifica
- No se puede desactivar un agricultor que tenga fincas activas (depende de reglas específicas)
- Los datos deben ser válidos

**Resultado esperado:**

- Los datos del agricultor se actualizan en el sistema
- Se mantiene el historial de cambios (si está habilitado)
- Se actualiza la fecha de modificación
- Se registra el evento de edición en auditoría
- Si se cambió la contraseña, el agricultor recibirá una notificación
- Los cambios son visibles inmediatamente en la lista de agricultores

---

### Guía 16: Asignar Rol

**Objetivo:** Definir y modificar los permisos de un usuario asignándole un rol específico (Administrador, Técnico, Agricultor) que determina sus capacidades en el sistema.

**Pasos detallados:**

1. Inicie sesión en el sistema con rol de Administrador
2. Acceda a la sección de "Gestión de Usuarios" desde el menú de administración
3. Localice el usuario al cual desea asignar o cambiar el rol
4. Haga clic en el botón "Asignar Rol" o "Cambiar Rol" junto al usuario
5. El sistema mostrará el rol actual del usuario
6. Revise los roles disponibles y sus capacidades:
   - **Administrador:** Acceso completo al sistema, puede gestionar usuarios, entrenar modelos y acceder a todas las funcionalidades
   - **Técnico/Analista:** Puede analizar imágenes, gestionar lotes y entrenar modelos
   - **Agricultor:** Puede gestionar sus fincas y lotes, analizar imágenes
7. Seleccione el nuevo rol para el usuario del menú desplegable
8. Revise la advertencia sobre el cambio de permisos
9. Haga clic en el botón "Confirmar" o "Asignar Rol"
10. El sistema validará que el cambio de rol sea permitido
11. El sistema validará que no se esté removiendo el último administrador del sistema
12. Si la validación es exitosa, el rol se actualizará
13. Verá un mensaje de confirmación
14. El cambio de rol afectará inmediatamente los permisos del usuario
15. Si el usuario tiene una sesión activa, será invalidada y deberá iniciar sesión nuevamente

**Validaciones del sistema:**

- El usuario debe tener rol de Administrador
- El usuario objetivo debe existir en el sistema
- Debe haber al menos un administrador activo en el sistema
- Un usuario no puede asignarse o quitarse su propio rol de administrador
- El rol seleccionado debe ser válido

**Resultado esperado:**

- El rol del usuario se actualiza en el sistema
- Los permisos del usuario se actualizan según el nuevo rol
- Se invalida la sesión activa del usuario (si aplica)
- Se registra el cambio de rol en auditoría
- El usuario tendrá acceso a las funcionalidades correspondientes a su nuevo rol
- El cambio es inmediato y efectivo

---

### Guía 17: Editar Perfil

**Objetivo:** Actualizar los datos personales, información de contacto y contraseña del usuario autenticado sin necesidad de intervención administrativa.

**Pasos detallados:**

1. Inicie sesión en el sistema
2. Acceda a la sección "Mi Perfil" o "Configuración de Cuenta" desde el menú de usuario (generalmente en la esquina superior derecha)
3. El sistema cargará automáticamente sus datos actuales
4. Modifique los campos que desea actualizar:
   - **Nombre:** Modifique su nombre si es necesario
   - **Apellido:** Modifique su apellido si es necesario
   - **Teléfono:** Actualice su número de teléfono
   - **Dirección:** Actualice su dirección
   - **Municipio:** Actualice el municipio
   - **Departamento:** Actualice el departamento
5. Si desea cambiar su contraseña:
   - Haga clic en la sección "Cambiar Contraseña" o en el botón correspondiente
   - Ingrese su contraseña actual en el campo "Contraseña Actual"
   - Ingrese su nueva contraseña en el campo "Nueva Contraseña"
   - Confirme la nueva contraseña en el campo "Confirmar Nueva Contraseña"
6. Revise que todos los datos estén correctos
7. Haga clic en el botón "Guardar" o "Actualizar Perfil"
8. El sistema validará los datos modificados
9. Si cambió la contraseña, el sistema validará:
   - Que la contraseña actual sea correcta
   - Que la nueva contraseña cumpla con los requisitos de fortaleza
   - Que las nuevas contraseñas coincidan
10. Si la validación es exitosa, verá un mensaje de confirmación
11. Si cambió la contraseña, el sistema puede requerir que inicie sesión nuevamente
12. Los cambios se aplicarán inmediatamente

**Validaciones del sistema:**

- El usuario debe estar autenticado
- El usuario solo puede editar su propio perfil
- El email no se puede cambiar desde el perfil (requiere proceso administrativo)
- Si se cambia la contraseña:
  - La contraseña actual debe ser correcta
  - La nueva contraseña debe cumplir con los requisitos de fortaleza (mínimo 8 caracteres, mayúsculas, números)
  - Las nuevas contraseñas deben coincidir exactamente

**Resultado esperado:**

- Los datos personales del usuario se actualizan en el sistema
- Se actualiza la fecha de modificación
- Si se cambió la contraseña, la sesión puede requerir reautenticación
- Se registra la actualización en auditoría
- Los cambios son visibles inmediatamente
- El usuario puede continuar usando el sistema con sus datos actualizados

---

## Preguntas Frecuentes (FAQ)

### 1. ¿Qué formatos de imagen puedo subir al sistema?

Puede subir imágenes en los siguientes formatos: **JPG, JPEG, PNG, BMP y TIFF**. El tamaño máximo permitido por imagen es de **20MB**. Si su imagen excede este tamaño, puede comprimirla usando herramientas de edición de imágenes antes de subirla.

---

### 2. ¿Cuánto tiempo tarda el análisis de una imagen?

El análisis completo de una imagen (procesamiento y predicción) generalmente toma entre **30 y 60 segundos** por imagen. Este tiempo puede variar dependiendo del tamaño de la imagen y la carga del servidor. El sistema le mostrará un indicador de progreso mientras procesa su imagen.

---

### 3. ¿Puedo asociar un análisis a un lote después de haberlo realizado?

Sí, puede asociar un análisis a un lote después de haberlo realizado. Para hacerlo, acceda a la vista de resultados del análisis y busque la opción "Asociar a Lote" o "Asignar Lote". Seleccione el lote correspondiente y guarde los cambios. Esta funcionalidad le permite organizar sus análisis según sus necesidades.

---

### 4. ¿Qué pasa si olvido mi contraseña?

Si olvidó su contraseña, puede recuperarla desde la página de inicio de sesión. Haga clic en el enlace "¿Olvidó su contraseña?" o "Recuperar Contraseña". Ingrese su email y recibirá un enlace para restablecer su contraseña. Si es administrador, también puede contactar a otro administrador para que le resetee la contraseña.

---

### 5. ¿Puedo eliminar una finca que ya tiene lotes asociados?

Depende de la configuración del sistema y las reglas de negocio. Generalmente, si una finca tiene lotes asociados, el sistema le mostrará una advertencia antes de permitir la eliminación. En algunos casos, puede ser necesario eliminar o desasociar los lotes primero. Si tiene dudas, contacte al administrador del sistema.

---

### 6. ¿Cómo puedo exportar todos mis análisis a Excel?

Para exportar sus análisis a Excel, acceda a la sección de "Historial de Análisis". En la parte superior de la lista, encontrará un botón "Exportar a Excel" o "Descargar Excel". Haga clic en él y el sistema generará un archivo Excel con todos los análisis que tiene permisos para ver. El archivo se descargará automáticamente a su dispositivo.

---

### 7. ¿Qué precisión tienen las predicciones del sistema?

La precisión de las predicciones depende del modelo entrenado y la calidad de las imágenes. El sistema utiliza modelos de inteligencia artificial que han sido entrenados con datasets de granos de cacao. La precisión típica del modelo (medida por R²) debe ser superior a 0.7 para ser aceptada. Para obtener los mejores resultados, asegúrese de subir imágenes de buena calidad con buena iluminación y fondo contrastante.

---

### 8. ¿Puedo tener múltiples fincas en el sistema?

Sí, como agricultor puede registrar y gestionar múltiples fincas en el sistema. Cada finca puede tener múltiples lotes asociados. Esto le permite organizar su producción de cacao de manera eficiente y realizar análisis separados para cada finca o lote.

---

### 9. ¿Qué debo hacer si el análisis de una imagen falla?

Si el análisis de una imagen falla, el sistema le mostrará un mensaje de error explicando la causa. Las causas comunes incluyen: imagen corrupta, formato no válido, o error en el procesamiento. Intente subir la imagen nuevamente. Si el problema persiste, verifique que la imagen cumpla con los requisitos (formato válido, tamaño máximo 20MB). Si continúa teniendo problemas, contacte al soporte técnico.

---

### 10. ¿Cómo puedo ver el historial de cambios de una finca o lote?

El historial de cambios puede estar disponible dependiendo de la configuración del sistema. Si está habilitado, puede acceder al historial desde la vista de detalles de la finca o lote, buscando la pestaña o sección "Historial" o "Cambios". Allí verá un registro de todas las modificaciones realizadas, incluyendo fecha, usuario que realizó el cambio y los valores anteriores y nuevos.

---

## Solución de Problemas (Troubleshooting)

### Problema 1: No puedo iniciar sesión

**Síntomas:**
- El sistema muestra un mensaje de error al intentar iniciar sesión
- Las credenciales parecen correctas pero no funcionan

**Soluciones:**

1. **Verifique que su email esté verificado:**
   - Si acaba de registrarse, revise su bandeja de entrada (y carpeta de spam) para el email de verificación
   - Haga clic en el enlace de verificación para activar su cuenta

2. **Verifique sus credenciales:**
   - Asegúrese de que el email esté escrito correctamente (sin espacios adicionales)
   - Verifique que la contraseña sea correcta (distingue entre mayúsculas y minúsculas)
   - Si olvidó su contraseña, use la opción "Recuperar Contraseña"

3. **Verifique el bloqueo por intentos fallidos:**
   - Si ha intentado iniciar sesión 5 veces fallidas, su acceso puede estar bloqueado temporalmente
   - Espere unos minutos antes de intentar nuevamente
   - O use la opción "Recuperar Contraseña" para restablecer su contraseña

4. **Contacte al administrador:**
   - Si ninguna de las soluciones anteriores funciona, contacte al administrador del sistema
   - Proporcione su email y descripción del problema

---

### Problema 2: La imagen no se sube correctamente

**Síntomas:**
- La imagen no se carga al sistema
- Aparece un mensaje de error al intentar subir

**Soluciones:**

1. **Verifique el formato de la imagen:**
   - Asegúrese de que la imagen esté en formato JPG, JPEG, PNG, BMP o TIFF
   - Si está en otro formato, conviértala usando un editor de imágenes

2. **Verifique el tamaño del archivo:**
   - El tamaño máximo permitido es 20MB
   - Si su imagen es más grande, comprímala usando herramientas de compresión de imágenes
   - Puede usar herramientas online o software como GIMP, Photoshop, o herramientas de compresión de imágenes

3. **Verifique la conexión a internet:**
   - Asegúrese de tener una conexión estable a internet
   - Si la conexión es lenta, espere a que la carga se complete
   - No cierre la ventana mientras se carga la imagen

4. **Verifique que la imagen no esté corrupta:**
   - Intente abrir la imagen en otro programa para verificar que no esté dañada
   - Si la imagen está corrupta, use otra copia de la imagen

5. **Limpie la caché del navegador:**
   - Limpie la caché y las cookies del navegador
   - Intente subir la imagen nuevamente

---

### Problema 3: El análisis tarda mucho tiempo o no se completa

**Síntomas:**
- El análisis parece estar procesando pero no termina
- El indicador de progreso se queda en un porcentaje

**Soluciones:**

1. **Espere un tiempo razonable:**
   - El análisis puede tomar hasta 60 segundos por imagen
   - Si han pasado más de 2 minutos, puede haber un problema

2. **Recargue la página:**
   - Recargue la página del navegador (F5 o Ctrl+R)
   - Verifique si el análisis se completó en segundo plano

3. **Verifique la calidad de la imagen:**
   - Imágenes de muy baja calidad o con problemas pueden causar que el análisis falle
   - Intente con una imagen de mejor calidad

4. **Contacte al soporte técnico:**
   - Si el problema persiste, puede haber un problema con el servidor o los modelos de IA
   - Contacte al soporte técnico proporcionando:
     - Fecha y hora del intento
     - ID de la imagen (si está disponible)
     - Descripción del problema

---

### Problema 4: No puedo ver los resultados de un análisis

**Síntomas:**
- El análisis aparece como completado pero no puedo ver los detalles
- Aparece un mensaje de "Acceso denegado" o "Sin permisos"

**Soluciones:**

1. **Verifique sus permisos:**
   - Solo puede ver análisis de sus propias imágenes o de fincas/lotes a los que tiene acceso
   - Si el análisis pertenece a otro usuario, necesitará permisos especiales

2. **Verifique que el análisis esté completado:**
   - Asegúrese de que el análisis haya terminado completamente
   - Busque un indicador de "Completado" o "Finalizado"

3. **Contacte al administrador:**
   - Si cree que debería tener acceso pero no lo tiene, contacte al administrador
   - Proporcione el ID del análisis y su email

---

### Problema 5: No puedo crear un lote porque excede el área de la finca

**Síntomas:**
- Al intentar crear un lote, el sistema muestra un error indicando que el área excede el área disponible de la finca

**Soluciones:**

1. **Verifique el área del lote:**
   - Asegúrese de que el área ingresada sea correcta
   - Verifique las unidades (debe estar en hectáreas)

2. **Verifique el área total de la finca:**
   - Revise el área total de la finca en la vista de detalles
   - Asegúrese de que el área del lote no exceda el área disponible

3. **Verifique los lotes existentes:**
   - Revise la suma de áreas de todos los lotes existentes en la finca
   - El área total de todos los lotes no debe exceder el área total de la finca

4. **Ajuste el área del lote:**
   - Reduzca el área del lote para que quepa en el área disponible
   - O edite la finca para aumentar su área total si es necesario

---

### Problema 6: El reporte PDF no se genera o no se descarga

**Síntomas:**
- Al hacer clic en "Descargar Reporte", no pasa nada
- El PDF no se descarga o aparece un error

**Soluciones:**

1. **Verifique los permisos del navegador:**
   - Asegúrese de que el navegador tenga permisos para descargar archivos
   - Revise la configuración de descargas del navegador

2. **Verifique el bloqueador de ventanas emergentes:**
   - Desactive temporalmente el bloqueador de ventanas emergentes
   - Los reportes pueden requerir ventanas emergentes para descargar

3. **Verifique el espacio en disco:**
   - Asegúrese de tener espacio suficiente en su dispositivo
   - Los reportes pueden ser archivos grandes (hasta 10MB)

4. **Intente con otro navegador:**
   - Si el problema persiste, intente descargar el reporte desde otro navegador
   - Esto puede ayudar a identificar si el problema es específico del navegador

5. **Contacte al soporte técnico:**
   - Si ninguna solución funciona, puede haber un problema con la generación del PDF
   - Contacte al soporte técnico con detalles del problema

---

### Problema 7: No puedo editar una finca o lote

**Síntomas:**
- El botón "Editar" no aparece o está deshabilitado
- Aparece un mensaje de "Sin permisos" al intentar editar

**Soluciones:**

1. **Verifique sus permisos:**
   - Solo el propietario de la finca o un administrador pueden editarla
   - Si la finca pertenece a otro agricultor, no podrá editarla a menos que sea administrador

2. **Verifique que la finca/lote exista:**
   - Asegúrese de que la finca o lote no haya sido eliminado
   - Recargue la página para verificar el estado actual

3. **Contacte al administrador:**
   - Si cree que debería tener permisos para editar, contacte al administrador
   - Proporcione el nombre o ID de la finca/lote y su email

---

### Problema 8: Los filtros de búsqueda no funcionan correctamente

**Síntomas:**
- Los resultados de búsqueda no coinciden con los criterios ingresados
- La búsqueda no devuelve resultados cuando debería

**Soluciones:**

1. **Verifique los criterios de búsqueda:**
   - Asegúrese de que los rangos numéricos sean coherentes (mínimo <= máximo)
   - Verifique que las fechas sean válidas (fecha inicial <= fecha final)
   - Revise que los formatos de fecha sean correctos

2. **Simplifique los criterios:**
   - Intente buscar con menos criterios para ver si alguno está causando el problema
   - Agregue criterios uno por uno para identificar cuál causa el problema

3. **Limpie los filtros:**
   - Haga clic en "Limpiar Filtros" o "Resetear" para comenzar de nuevo
   - Ingrese los criterios nuevamente

4. **Recargue la página:**
   - Recargue la página del navegador
   - Intente la búsqueda nuevamente

---

## Contacto y Soporte

### Datos de Atención

Para obtener asistencia con el sistema CacaoScan, puede contactarnos a través de los siguientes medios:

**Email de Soporte:**  
soporte@cacaoscan.com

**Teléfono de Soporte:**  
+57 (1) XXX-XXXX

**Portal de Soporte:**  
https://soporte.cacaoscan.com

**Sistema de Tickets:**  
Puede crear un ticket de soporte desde el portal de soporte o enviando un email con el asunto "Soporte CacaoScan"

### Horarios de Atención

**Lunes a Viernes:**  
8:00 AM - 6:00 PM (Hora local)

**Sábados:**  
9:00 AM - 1:00 PM (Hora local)

**Domingos y Festivos:**  
Cerrado (solo emergencias críticas)

**Nota:** Los tiempos de respuesta pueden variar según la complejidad de la consulta. Las consultas urgentes se atienden con prioridad.

### Opciones de Contacto

1. **Soporte Técnico:** Para problemas técnicos, errores del sistema o consultas sobre funcionalidades
2. **Soporte de Usuario:** Para consultas sobre cómo usar el sistema, guías y capacitación
3. **Administración:** Para solicitudes de creación de cuentas, cambios de roles o permisos especiales
4. **Reporte de Errores:** Para reportar bugs o problemas del sistema

### Información a Proporcionar al Contactar Soporte

Para agilizar la atención, por favor proporcione la siguiente información:

- **Email de su cuenta**
- **Rol en el sistema** (Agricultor, Técnico, Administrador)
- **Descripción detallada del problema o consulta**
- **Pasos para reproducir el problema** (si aplica)
- **Capturas de pantalla** (si es posible)
- **Fecha y hora** en que ocurrió el problema
- **Navegador y versión** que está utilizando

---

## Información Adicional

### Glosario de Términos

- **Análisis:** Proceso mediante el cual el sistema utiliza inteligencia artificial para predecir las dimensiones y peso de un grano de cacao a partir de una imagen
- **Crop:** Imagen procesada del grano de cacao sin fondo, resultado de la segmentación
- **Dataset:** Conjunto de datos (imágenes etiquetadas) utilizado para entrenar los modelos de inteligencia artificial
- **Finca:** Propiedad agrícola donde se cultiva cacao, puede contener múltiples lotes
- **Lote:** Área específica dentro de una finca donde se cultiva una variedad particular de cacao
- **Modelo de IA:** Algoritmo de machine learning entrenado para realizar predicciones sobre granos de cacao
- **Segmentación:** Proceso de separar el grano de cacao del fondo de la imagen
- **Token JWT:** Credencial de acceso que permite al usuario autenticarse en el sistema
- **U-Net:** Modelo de red neuronal utilizado para la segmentación de imágenes

### Recursos Adicionales

- **Documentación Técnica:** Disponible para administradores y técnicos
- **Videos Tutoriales:** Disponibles en el portal de soporte
- **Base de Conocimientos:** Artículos y guías adicionales en el portal de soporte
- **Comunidad de Usuarios:** Foro de discusión y compartir experiencias (si está disponible)

---

## Conclusión

Este manual de usuario proporciona una guía completa para utilizar todas las funcionalidades del sistema CacaoScan. Si tiene preguntas adicionales o necesita asistencia, no dude en contactar al equipo de soporte.

Recuerde que el sistema está en constante mejora, por lo que algunas funcionalidades pueden evolucionar. Le recomendamos revisar periódicamente las actualizaciones del sistema y este manual.

**Última actualización del manual:** 2024  
**Versión del sistema documentada:** 1.0

---

*Este documento es propiedad de CacaoScan y está destinado únicamente para uso interno y de usuarios autorizados del sistema.*

