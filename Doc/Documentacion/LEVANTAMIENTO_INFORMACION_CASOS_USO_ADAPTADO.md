# LEVANTAMIENTO DE INFORMACIÓN - CASOS DE USO CACAOSCAN
## Entrevista Profesional - Sistema Django + Vue.js + ML
## Adaptado para Agricultores e Ingenieros de Agroindustria

---

## Caso de Uso 01: Registrar Usuario

### 2.1 Planeación de la Recolección

**Objetivo:**

Recolectar información clave sobre cómo debe funcionar el proceso de registro de usuarios, considerando seguridad, facilidad de uso y accesibilidad para usuarios de campo y profesionales del sector agroindustrial.

**Stakeholders Entrevistados:**

•	Ingeniero de Agroindustria: Responsable del control de cuentas, permisos y validaciones críticas. Usa el sistema para análisis técnicos y gestión de datos.

•	Agricultor/Productor: Usuario con menor experiencia tecnológica, frecuentemente desde zonas rurales. Requiere procesos simples y claros.

**Complejidad:**

Este caso exige seguridad, validación de datos, facilidad de uso y soporte para usuarios con bajo nivel digital.

### 2.2 Instrumento – Preguntas aplicadas

•	¿Qué espera que haga el sistema cuando un usuario desea registrarse?

•	¿Qué información debe solicitarse?

•	¿Qué errores deben notificarse?

•	¿Cómo debe confirmarse que el usuario es real?

•	¿Qué problemas ha tenido en sistemas anteriores?

•	¿Qué requisitos de seguridad considera importantes?

### Respuestas obtenidas

**Ingeniero de Agroindustria**

"El sistema debe validar que el correo no exista, evitar registros falsos y tener verificación segura. Requiero auditoría de cada registro. Los usuarios nuevos deben asignarse automáticamente como agricultores, y solo los administradores pueden cambiar roles posteriormente."

**Agricultor**

"Pues mire joven, yo casi no manejo mucho estos teléfonos, entonces quiero que eso sea fácil… que me diga claro qué llenar y que no me saque errores raros. Y si la señal está floja, que no me toque empezar todo otra vez."

### 2.3 Evidencia y Análisis

**Hallazgos clave:**

•	Se requiere una interfaz sencilla y clara.

•	Validación previa evitará frustraciones.

•	La verificación por correo debe ser confiable.

•	Usuarios rurales necesitan tolerancia a fallos de conectividad.

•	El sistema asigna automáticamente el rol de "farmer" (agricultor) a todos los usuarios nuevos.

**Problemas y oportunidades:**

•	Problema: Muchos usuarios no entienden mensajes técnicos.

 Oportunidad: Diseñar mensajes simples y pedagógicos.

•	Problema: En zonas rurales, la conexión es inestable.

 Oportunidad: Guardar el formulario temporalmente (offline-first).

•	Problema: Riesgo de cuentas falsas.

 Oportunidad: Implementar verificación por email con token UUID que expira en 24 horas y auditoría completa.

---

## Caso de Uso 02: Iniciar Sesión

### 2.1 Planeación de la Recolección

**Objetivo:**

Obtener información sobre el funcionamiento esperado para el inicio de sesión, incorporando seguridad, facilidad de uso y necesidades de usuarios con conectividad limitada.

**Stakeholders:**

•	Ingeniero de Agroindustria: Exige control total de accesos y auditoría completa.

•	Agricultor: Puede tener dificultades con contraseñas complejas y necesita procesos simples.

**Complejidad:**

Incluye autenticación segura mediante JWT, manejo de errores, protección contra ataques y experiencia de usuario amigable.

### 2.2 Instrumento – Preguntas realizadas

•	¿Qué espera al iniciar sesión?

•	¿Qué problemas ha tenido con contraseñas?

•	¿Qué mensajes deben aparecer si hay error?

•	¿Desea recordar la sesión?

•	¿Qué nivel de seguridad espera el sistema?

### Respuestas obtenidas

**Ingeniero de Agroindustria**

"Necesitamos registro de intentos de login, auditoría completa, y control de permisos según rol. El sistema debe generar tokens JWT automáticamente y registrar cada intento en LoginHistory."

**Agricultor**

"A veces uno se confunde con tantas claves… si se me olvida, quiero poder recuperarla fácil. Y ojalá pueda entrar sin que la señal moleste tanto, porque aquí en la finca la red va y viene."

### 2.3 Evidencia y Análisis

**Hallazgos claves:**

•	Alta necesidad de simplicidad en la interfaz.

•	Es esencial la recuperación de contraseña.

•	El rol define lo que cada usuario ve en el sistema (farmer o analyst).

•	Algunos usuarios necesitan persistencia de sesión mediante tokens JWT (access: 60 min, refresh: 7 días).

**Problemas y oportunidades:**

•	Problema: Usuarios rurales pierden la sesión por mala señal.

 Oportunidad: Manejar reintentos y persistencia local de tokens.

•	Problema: Contraseñas difíciles de recordar.

 Oportunidad: Usar autenticación amigable (verificación por correo/SMS).

•	Problema: Riesgo de accesos no autorizados.

 Oportunidad: Registro completo de intentos de login en LoginHistory y ActivityLog.

---

## Caso de Uso 03: Subir Imagen

### 2.1 Planeación de la Recolección

**Objetivo:**

Recolectar información completa sobre cómo debe funcionar la carga de imágenes al sistema, garantizando facilidad de uso, validaciones, control de errores, seguridad y compatibilidad con dispositivos móviles.

**Stakeholders Entrevistados:**

•	Ingeniero de Agroindustria: Define restricciones técnicas y políticas de almacenamiento. Requiere validaciones estrictas y auditoría.

•	Agricultor/Productor: Toma las fotos en campo, con dispositivos móviles y poca conectividad.

**Complejidad:**

Caso crítico del sistema: implica archivos grandes, conexiones inestables, seguridad, validación de formato y retroalimentación visual del progreso.

### 2.2 Instrumento – Preguntas aplicadas

•	¿Qué espera el usuario al subir una imagen?

•	¿Qué formatos deben permitirse?

•	¿Qué errores deben detectarse y notificarse?

•	¿Qué información debe mostrar el sistema mientras sube la imagen?

•	¿Qué limitaciones de red o dispositivo enfrenta normalmente?

•	¿Qué acciones realiza después de subir la imagen?

### Respuestas obtenidas

**Ingeniero de Agroindustria**

"Debe validarse el tamaño (máximo 10MB), el tipo de archivo (jpg, jpeg, png, bmp, tiff, tif) y registrar cada subida. Necesitamos auditoría completa y evitar que suban archivos corruptos o peligrosos. Las imágenes deben asociarse opcionalmente a fincas y lotes."

**Agricultor**

"Muchacho, cuando uno está por allá en la finca, la señal sube y baja. Yo necesito que eso suba la foto sin que me toque repetir todo si se corta el internet. Y que si la foto está muy pesada, pues que me diga clarito qué hacer."

### 2.3 Evidencia y Análisis

**Hallazgos clave**

•	Necesidad de tolerancia a fallos de red.

•	Validaciones estrictas de seguridad y formato (PIL/Pillow para validar imágenes válidas).

•	Información clara durante el proceso: porcentaje, estado, errores.

•	Usuarios rurales requieren manejo de archivos comprimidos.

•	El sistema soporta subida múltiple de imágenes en una sola petición.

**Problemas y oportunidades**

•	Problema: Fallos frecuentes en zonas rurales.

 Oportunidad: Implementar reintentos automáticos y subida segmentada.

•	Problema: Archivos grandes pueden ralentizar el sistema.

 Oportunidad: Compresión automatizada previa al procesamiento.

•	Problema: Usuarios no comprenden errores técnicos.

 Oportunidad: Mensajes simples como: "La foto es muy pesada, trate de tomarla un poquito más cerca o con menos zoom".

---

## Caso de Uso 04: Procesar Imagen

### 2.1 Planeación de la Recolección

**Objetivo:**

Definir cómo debe comportarse el sistema al preparar una imagen para análisis: normalización, segmentación, mejora de calidad, validación y generación de versiones aptas para IA.

**Stakeholders:**

•	Ingeniero de Agroindustria: Requiere trazabilidad del procesamiento y uso de modelos U-Net o OpenCV para segmentación.

•	Agricultor: Necesita claridad sobre qué está pasando y si la foto sirve o no.

**Complejidad:**

Caso altamente técnico, requiere IA, procesamiento en segundo plano, segmentación del grano (eliminación de fondo) y creación de crops (imágenes recortadas sin fondo).

### 2.2 Instrumento – Preguntas realizadas

•	¿Qué debe hacer el sistema antes del análisis?

•	¿Cuánto debe tardar el procesamiento?

•	¿Qué información debe mostrarse al usuario durante el proceso?

•	¿Qué pasa si la imagen no es válida?

•	¿Qué errores deben notificarse?

•	¿Qué estadísticas o resultados preliminares deben generarse?

### Respuestas obtenidas

**Ingeniero de Agroindustria**

"Se debe registrar cada versión de la imagen, evitar archivos inválidos y garantizar que el procesamiento cumple los estándares de calidad. El sistema debe usar U-Net si está disponible, sino OpenCV. El crop debe guardarse como PNG transparente."

**Agricultor**

"A veces uno toma la foto y queda medio borrosa. Sería bueno que el sistema le diga a uno: 'Esa foto no sirve, tómela otra vez'. Y que uno vea en la pantalla si ya terminó o si sigue pensando."

### 2.3 Evidencia y Análisis

**Hallazgos clave**

•	Se necesitan mensajes claros sobre la calidad de la imagen.

•	El procesamiento debe ser visual y entendible: "en cola", "procesando", "listo".

•	Validación temprana evita análisis erróneos.

•	El sistema debe segmentar el grano correctamente y crear crop sin fondo.

**Problemas y oportunidades**

•	Problema: Procesamientos fallidos por mala calidad.

 Oportunidad: Implementar filtro de calidad automático (blur detection).

•	Problema: Usuarios no entienden procesos internos.

 Oportunidad: Barra de progreso + mensajes con lenguaje cotidiano.

•	Problema: Retrasos al procesar varias imágenes.

 Oportunidad: Paralelización y colas con prioridad.

---

## Caso de Uso 05: Analizar Imagen

### 2.1 Planeación de la Recolección

**Objetivo:**

Recolectar requisitos funcionales y técnicos sobre cómo debe ejecutarse el análisis mediante inteligencia artificial para clasificar cacao, detectar defectos y obtener métricas.

**Stakeholders:**

•	Ingeniero de Agroindustria: Exige trazabilidad completa, modelos actualizados y resultados precisos con visualizaciones técnicas.

•	Agricultor: Necesita interpretaciones claras, no datos técnicos.

**Complejidad:**

Proceso complejo: IA, predicciones, segmentación, conteos, defectos y cálculos.

### 2.2 Instrumento – Preguntas aplicadas

•	¿Qué resultados debe entregar el sistema?

•	¿Cómo deben visualizarse las predicciones?

•	¿Qué nivel de precisión se espera?

•	¿Qué información necesita el agricultor para tomar decisiones?

•	¿Qué errores deben notificarse?

•	¿Qué pasa si el sistema no tiene confianza en su resultado?

### Respuestas obtenidas

**Ingeniero de Agroindustria**

"Necesito guardar cada análisis, versión del modelo, métricas utilizadas y confianza. Todo debe ser auditable. Quiero ver los defectos marcados sobre la imagen, los conteos y un resumen claro."

**Agricultor**

"A mí me sirve que me diga si el cacao está bueno o está regular… y si tiene algún daño, que me muestre dónde. Si el sistema no está muy seguro, pues que me diga pa' yo revisar con calma."

### 2.3 Evidencia y Análisis

**Hallazgos clave**

•	El resultado debe ser visual, no solo numérico.

•	Niveles de confianza deben mostrarse de forma entendible.

•	Explicar por qué el grano se consideró defectuoso.

•	Los análisis deben asociarse a fincas y lotes para trazabilidad.

**Problemas y oportunidades**

•	Problema: Agricultores no interpretan métricas técnicas.

 Oportunidad: Traducción a lenguaje cotidiano ("calidad alta / media / baja").

•	Problema: A veces la IA no acierta con imágenes raras.

 Oportunidad: Mostrar advertencia "baja confianza".

•	Problema: Ingenieros requieren ver detalles más avanzados.

 Oportunidad: Modo de análisis extendido para expertos con métricas técnicas completas.

---

## Caso de Uso 06: Ver Resultados

### 2.1 Planeación de la Recolección

**Objetivo:**

Recopilar información sobre cómo los usuarios deben visualizar los resultados generados por el análisis de imágenes, garantizando claridad, accesibilidad, velocidad y trazabilidad.

**Stakeholders entrevistados:**

•	Ingeniero de Agroindustria: Requiere visualizar métricas y detalles técnicos completos.

•	Agricultor/Productor: Necesita interpretaciones claras y fáciles de entender.

**Complejidad:**

Caso clave para la toma de decisiones. Debe mostrar imágenes procesadas, anotaciones, métricas y conclusiones sin confundir al usuario.

### 2.2 Instrumento – Preguntas aplicadas

•	¿Qué información desea ver primero al abrir los resultados?

•	¿Qué elementos visuales facilitan la comprensión del análisis?

•	¿Qué nivel de detalle es necesario para técnicos?

•	¿Qué mensajes deben mostrarse si el análisis no es concluyente?

•	¿Cómo deberían organizarse los resultados (por fecha, finca, lote)?

•	¿Qué dispositivos usa para consultar los resultados?

### Respuestas obtenidas

**Ingeniero de Agroindustria**

"Debemos asegurar que solo el dueño del análisis o un usuario autorizado pueda verlo. También se requiere auditoría completa. Quiero ver la imagen original junto a la procesada, los defectos señalados, y un resumen numérico. Es importante que pueda ampliar cada dato cuando lo necesito."

**Agricultor**

"Yo quiero que me muestre clarito si el cacao está bueno o malo. Si hay daños, pues que se vean en la foto con un círculo o algo. Y que me diga en palabras sencillas qué significa el resultado."

### 2.3 Evidencia y Análisis

**Hallazgos clave**

•	Necesidad de visualizaciones claras y comparativas.

•	Interpretación en lenguaje técnico para especialistas y en lenguaje cotidiano para el agricultor.

•	Importancia de filtros por fecha, finca, lote o categoría.

•	Control de acceso: solo el propietario o usuarios autorizados pueden ver los resultados.

**Problemas y oportunidades**

•	Problema: Agricultores no entienden métricas complejas.

 Oportunidad: Traducción a niveles de calidad ("Excelente", "Aceptable", "Crítico").

•	Problema: Resultados dispersos o difíciles de encontrar.

 Oportunidad: Historial organizado, buscador y filtros avanzados.

•	Problema: Ingenieros requieren análisis más profundos.

 Oportunidad: Modo "vista detallada" para expertos con métricas técnicas completas.

---

## Caso de Uso 07: Descargar Reporte

### 2.1 Planeación de la Recolección

**Objetivo:**

Identificar las necesidades y expectativas de los usuarios al descargar reportes PDF o documentos con los resultados del análisis.

**Stakeholders entrevistados:**

•	Ingeniero de Agroindustria: Define formato, retención de archivos y seguridad. Usa reportes para auditorías o entregas técnicas.

•	Agricultor: Utiliza reportes para ventas, clasificaciones y control de calidad.

**Complejidad:**

Debe generar documentos formales, precisos, y compatibles con cualquier dispositivo.

### 2.2 Instrumento – Preguntas aplicadas

•	¿Qué información debe incluir un reporte?

•	¿En qué formato debe descargarse?

•	¿Qué nivel de detalle se requiere?

•	¿Qué información necesita el agricultor para sus registros?

•	¿Qué tan rápido debe generarse un reporte?

•	¿Qué elementos visuales deben incluirse?

### Respuestas obtenidas

**Ingeniero de Agroindustria**

"Debe ser un PDF formal, con logos, fecha, usuario, y datos del análisis. Todo debe quedar registrado en auditoría. Necesito métricas exactas, gráficas, la imagen anotada y un resumen técnico. A veces también exporto en Excel."

**Agricultor**

"El reporte me sirve pa' mostrarle a quien me compra el cacao. O sea, que se vea bonito y claro. Que diga cuántos granos salieron buenos y malos, y que tenga la foto pa' que uno pueda comparar."

### 2.3 Evidencia y Análisis

**Hallazgos clave**

•	Necesidad de plantillas limpias, ordenadas y entendibles.

•	El PDF debe incluir imágenes marcadas, gráficas y texto explicativo.

•	Exportación en varios formatos (PDF, Excel, CSV).

•	Auditoría completa de cada descarga de reporte.

**Problemas y oportunidades**

•	Problema: Generación lenta de reportes cuando son masivos.

 Oportunidad: Generación en segundo plano + notificación de descarga.

•	Problema: Agricultores requieren lenguaje simple.

 Oportunidad: Incluir sección "Interpretación del resultado en palabras sencillas".

---

## Caso de Uso 08: Crear Finca

### 2.1 Planeación de la Recolección

**Objetivo:**

Conocer las necesidades de los usuarios al registrar una nueva finca, para garantizar precisión geográfica, facilidad de uso y control de datos.

**Stakeholders entrevistados:**

•	Ingeniero de Agroindustria: Define permisos y estructura de datos. Gestiona múltiples fincas y requiere organización eficiente.

•	Agricultor: Dueño o responsable del terreno.

**Complejidad:**

Implica datos geográficos, relaciones con lotes, restricciones y validaciones.

### 2.2 Instrumento – Preguntas aplicadas

•	¿Qué datos deben registrarse de una finca?

•	¿Qué campos son obligatorios?

•	¿Cómo debe verificarse la ubicación?

•	¿Qué errores deben notificarse?

•	¿Qué información debe mostrarse al finalizar el registro?

•	¿Qué dificultades tienen actualmente para registrar fincas?

### Respuestas obtenidas

**Ingeniero de Agroindustria**

"Debemos validar nombre único, ubicación y productor responsable. También registrar auditoría y controlar permisos por rol. Necesito filtros para buscar fincas rápido y que el formulario no permita datos incompletos. También quiero ver los lotes vinculados desde el inicio."

**Agricultor**

"Cuando uno registra la finca, es bueno que salga un mapa pa' uno señalar el lugar. A veces uno no sabe la dirección exacta, pero sí reconoce el sitio. Y ojalá el sistema no pida tantas cosas enredadas."

### 2.3 Evidencia y Análisis

**Hallazgos clave**

•	Necesidad de mapa interactivo para ubicación exacta.

•	Campos obligatorios: nombre, municipio, productor.

•	Validaciones claras y mensajes simples.

•	Control de permisos: agricultores solo pueden gestionar sus propias fincas, ingenieros pueden ver todas.

**Problemas y oportunidades**

•	Problema: Agricultores desconocen datos técnicos (coordenadas).

 Oportunidad: Selección por mapa + autocompletado geográfico.

•	Problema: Errores de duplicidad (nombres repetidos).

 Oportunidad: Verificación automática antes de registrar.

•	Problema: Formularios largos pueden frustrar al usuario.

 Oportunidad: Dividir en pasos simples con asistencia visual.

---

## Caso de Uso 09: Editar Finca

### 2.1 Planeación de la Recolección

**Objetivo:**

Identificar las necesidades de modificación de datos de una finca previamente registrada, asegurando integridad, facilidad de edición y control de cambios.

**Stakeholders entrevistados:**

•	Ingeniero de Agroindustria: Controla permisos y auditoría de ediciones. Actualiza información operativa o geográfica.

•	Agricultor: Propietario de la finca, necesita corregir datos cuando sea necesario.

**Complejidad:**

Requiere validaciones de cambios sensibles (nombre, ubicación), compatibilidad con lotes asociados y trazabilidad completa.

### 2.2 Instrumento – Preguntas aplicadas

•	¿Qué datos de una finca deben poder editarse?

•	¿Qué cambios deben requerir confirmación especial?

•	¿Qué información necesita ver el usuario antes de modificar?

•	¿Qué mensajes deben mostrarse al guardar cambios?

•	¿Qué errores deben evitarse (duplicados, ubicaciones erróneas, datos incompletos)?

•	¿Con qué frecuencia se actualiza la información de una finca?

### Respuestas obtenidas

**Ingeniero de Agroindustria**

"Los cambios en nombre, ubicación y productor deben quedar registrados. No todos los usuarios pueden editar todo; algunos campos deben estar bloqueados según el rol. Necesito ver la información previa y qué campos están siendo cambiados. Si la finca tiene lotes asociados, debe advertir que el cambio afectará trazabilidad."

**Agricultor**

"A veces uno se equivoca poniendo el nombre o el lugar. Entonces sería bueno poder corregirlo sin tanta vuelta. Pero si va a cambiar algo que afecte los lotes, pues que el sistema le diga a uno pa' no embarrarla."

### 2.3 Evidencia y Análisis

**Hallazgos clave**

•	Se deben controlar ediciones sensibles.

•	Se requiere previsualización del cambio y confirmación.

•	Agricultores necesitan mensajes claros y no técnicos.

•	Auditoría obligatoria de cada cambio.

**Problemas y oportunidades**

•	Problema: Cambios sin advertencia pueden afectar trazabilidad.

 Oportunidad: Sistema de alertas previo a edición crítica.

•	Problema: Falta de claridad para el agricultor.

 Oportunidad: Mensajes simplificados y resaltado visual de cambios.

---

## Caso de Uso 10: Crear Lote

### 2.1 Planeación de la Recolección

**Objetivo:**

Obtener información sobre cómo registrar un nuevo lote dentro de una finca, considerando datos de procedencia, fechas y características iniciales.

**Stakeholders entrevistados:**

•	Ingeniero de Agroindustria: Valida permisos y dependencias. Gestiona varios lotes y los relaciona con análisis.

•	Agricultor: Dueño del lote o encargado del proceso productivo.

**Complejidad:**

Incluye validación de duplicados, asociación obligatoria con una finca, datos clave y restricciones de integridad.

### 2.2 Instrumento – Preguntas aplicadas

•	¿Qué datos debe contener un lote nuevo?

•	¿Qué campos deben ser obligatorios?

•	¿Qué validaciones deben hacerse antes de registrar?

•	¿Qué relación debe existir entre el lote y la finca?

•	¿Qué errores son comunes al registrar lotes?

•	¿Qué elementos visuales ayudarían al usuario?

### Respuestas obtenidas

**Ingeniero de Agroindustria**

"El nombre del lote debe ser único dentro de cada finca. Debemos registrar fecha, finca asociada y productor. Todo debe tener auditoría y control de permisos. Quiero tener un formulario rápido con autocompletado de finca. También me sirve que verifique duplicados automáticamente."

**Agricultor**

"Yo manejo varios loticos en la finca, y muchos tienen nombres parecidos. Sería bueno que el sistema me avise si estoy repitiendo el nombre. También que no me toque llenar tantas cosas; uno no siempre tiene tiempo."

### 2.3 Evidencia y Análisis

**Hallazgos clave**

•	Validación automática de duplicados por finca.

•	Asociación obligatoria con finca existente.

•	Necesidad de interfaz sencilla.

•	Control de permisos: agricultores solo pueden crear lotes en sus fincas.

**Problemas y oportunidades**

•	Problema: Agricultores no recuerdan todos los datos técnicos.

 Oportunidad: Autocompletado y sugerencias según fincas existentes.

•	Problema: Ingenieros requieren agilidad.

 Oportunidad: Formularios mínimos + validación en tiempo real.

---

## Caso de Uso 11: Editar Lote

### 2.1 Planeación de la Recolección

**Objetivo:**

Definir cómo debe modificarse la información de un lote previo, manteniendo trazabilidad, integridad de datos y facilidad de uso para todos los actores.

**Stakeholders entrevistados:**

•	Ingeniero de Agroindustria: Vigila control de cambios y permisos. Actualiza información operativa del lote.

•	Agricultor: Puede necesitar corregir o actualizar datos del lote.

**Complejidad:**

Alta, porque un lote puede tener múltiples análisis asociados. Cualquier cambio debe manejar impacto en historial y reportes.

### 2.2 Instrumento – Preguntas aplicadas

•	¿Qué datos deben poder modificarse?

•	¿Qué campos deben estar protegidos (no editables)?

•	¿Cómo debe advertirse al usuario sobre impactos en análisis previos?

•	¿Qué mensajes deben presentarse al guardar los cambios?

•	¿Qué errores deben evitarse?

•	¿Qué información previa debe visualizar el usuario antes de editar?

### Respuestas obtenidas

**Ingeniero de Agroindustria**

"Cambiar finca asociada es delicado porque afecta auditoría. Algunas ediciones deben bloquearse si el lote tiene análisis históricos. Cuando edito un lote quiero ver cuántos análisis tiene, para saber si un cambio podría generar inconsistencias. Y debe avisar si algo no se puede cambiar."

**Agricultor**

"Si escribí mal un dato, quiero poder corregirlo, pero si eso va a dañar los análisis que ya hice, pues que el sistema me diga claro pa' no meter la pata."

### 2.3 Evidencia y Análisis

**Hallazgos clave**

•	Necesidad de advertencias claras sobre impacto en análisis previos.

•	Algunos campos deben bloquearse según estado del lote.

•	La vista previa y diferencias entre datos antiguos y nuevos son muy útiles.

•	Auditoría obligatoria de cada cambio.

**Problemas y oportunidades**

•	Problema: Cambios sin control pueden dañar trazabilidad.

 Oportunidad: Implementar "modo seguro" con confirmación obligatoria.

•	Problema: Agricultor no entiende mensajes técnicos.

 Oportunidad: Explicaciones en lenguaje simple acompañadas de detalles técnicos opcionales.

---

## Caso de Uso 15: Crear Agricultor

### 2.1 Planeación de la Recolección

**Objetivo:**

Identificar los requerimientos para registrar nuevos agricultores dentro del sistema, asegurando que la información sea completa, verificable y útil para asociarla con fincas y lotes.

**Stakeholders entrevistados:**

•	Ingeniero de Agroindustria: Controla permisos, estructura de datos y validaciones. Registra agricultores durante visitas en campo.

•	Agricultor: Usuario que desea acceder al sistema y registrar su producción.

**Complejidad:**

Moderada. Involucra validación de información sensible, seguridad básica y reglas de negocio de asociación con fincas.

### 2.2 Instrumento – Preguntas aplicadas

•	¿Qué datos son necesarios para registrar a un agricultor?

•	¿Qué validaciones deben aplicarse (correo, documento, teléfono)?

•	¿Quién está autorizado para crear nuevos agricultores?

•	¿Qué errores deben notificarse al usuario?

•	¿Qué información debe confirmarse al finalizar el registro?

### Respuestas obtenidas

**Ingeniero de Agroindustria**

"Debemos validar identificación, correo y teléfono. Solo roles autorizados pueden crear agricultores. El registro debe quedar auditado. Necesito un formulario rápido. A veces estoy en campo con mala señal, así que debe ser fácil y que guarde sin errores."

**Agricultor**

"Yo quiero que me registren rápido, mijo. Que no pidan tanta cosa rara. Con mi nombre, el número y la vereda debería bastar para empezar."

### 2.3 Evidencia y Análisis

**Hallazgos clave**

•	Gran importancia en la facilidad de registro para usuarios rurales.

•	Validaciones mínimas pero seguras: identificación, teléfono, nombre.

•	Necesidad de registro offline o tolerante a fallos en campo.

•	El sistema asigna automáticamente el rol de "farmer" a usuarios nuevos.

**Problemas y oportunidades**

•	Problema: Formatos complejos pueden bloquear el proceso en campo.

 Oportunidad: Formularios simplificados y adaptados a zonas rurales.

•	Problema: Datos incompletos pueden impedir asociar fincas.

 Oportunidad: Permitir completar información más adelante.

---

## Caso de Uso 16: Editar Agricultor

### 2.1 Planeación de la Recolección

**Objetivo:**

Definir cómo los usuarios autorizados pueden actualizar datos del agricultor sin comprometer la trazabilidad ni la integridad del sistema.

**Stakeholders entrevistados:**

•	Ingeniero de Agroindustria: Controla auditoría y permisos. Corrige datos recolectados en campo.

•	Agricultor: Usuario que quiere mantener su información actualizada.

**Complejidad:**

Moderada. Involucra manejo de auditoría y edición de datos sensibles.

### 2.2 Instrumento – Preguntas aplicadas

•	¿Qué datos deben poder editarse?

•	¿Quién está autorizado a realizar modificaciones?

•	¿Qué información debe quedar registrada como auditoría?

•	¿Qué errores comunes deben manejarse?

•	¿Qué confirmaciones debe mostrar el sistema?

### Respuestas obtenidas

**Ingeniero de Agroindustria**

"Los cambios importantes como identificación o nombre deben registrarse. Solo administradores e ingenieros autorizados pueden editar información. Edición debe ser rápida. A veces un número está mal o se cambia el teléfono. Necesito corregir sin perder datos."

**Agricultor**

"Uno cambia de número o de finca. Sería bueno que me puedan actualizar eso sin tanta vuelta."

### 2.3 Evidencia y Análisis

**Hallazgos clave**

•	Auditoría obligatoria: quién cambió qué y cuándo.

•	Interfaz clara para edición parcial o total.

•	Importancia de mantener consistencia con fincas asociadas.

•	Control de permisos: agricultores pueden editar su propio perfil, ingenieros pueden editar cualquier perfil.

**Problemas y oportunidades**

•	Problema: Agricultores cambian número con frecuencia.

 Oportunidad: Flujo rápido de actualización de contacto.

•	Problema: Ediciones no auditadas generan inconsistencias.

 Oportunidad: Registro automático de cada modificación en ActivityLog.

---

## Caso de Uso 17: Asignar Rol

### 2.1 Planeación de la Recolección

**Objetivo:**

Determinar cómo se asignan roles a los usuarios para controlar permisos y accesos dentro del sistema según responsabilidades.

**Stakeholders entrevistados:**

•	Ingeniero de Agroindustria: Puede necesitar acceso a funciones especializadas. Solo administradores pueden asignar roles.

•	Agricultor: Recibe rol básico para operar funciones esenciales.

**Complejidad:**

Alta. Debe manejar permisos, seguridad, auditoría y reglas de acceso. Los roles disponibles son "farmer" (agricultor) y "analyst" (ingeniero de agroindustria).

### 2.2 Instrumento – Preguntas aplicadas

•	¿Qué roles existen en el sistema?

•	¿Qué permisos tiene cada rol?

•	¿Quién puede asignar o cambiar roles?

•	¿Qué restricciones deben aplicarse?

•	¿Qué confirmaciones debe mostrar el sistema?

### Respuestas obtenidas

**Ingeniero de Agroindustria**

"Solo los administradores pueden asignar roles. Los roles disponibles son 'farmer' (agricultor) y 'analyst' (ingeniero de agroindustria). A veces necesito permisos para entrenar modelos o gestionar fincas. El administrador debe asignar eso según mi trabajo. Cada cambio debe ser registrado."

**Agricultor**

"Yo solo necesito lo básico: subir mis fotos, ver mis análisis. No necesito cosas complicadas."

### 2.3 Evidencia y Análisis

**Hallazgos clave**

•	Proceso restringido a administradores.

•	Seguridad crítica: cambios de roles afectan toda la operación.

•	Auditoría obligatoria.

•	Roles disponibles: "farmer" (agricultor) y "analyst" (ingeniero de agroindustria).

•	Permisos por rol:
  - **farmer**: Gestionar fincas/lotes propios, subir imágenes, ver propios análisis
  - **analyst**: Analizar imágenes, gestionar lotes, ver estadísticas, acceso a todas las fincas

**Problemas y oportunidades**

•	Problema: Cambios mal hechos pueden abrir acceso indebido.

 Oportunidad: Confirmaciones dobles o requerir autenticación adicional.

•	Problema: Agricultores no entienden roles técnicos.

 Oportunidad: Descripciones simples de cada rol en la interfaz.

---

## Caso de Uso 18: Editar Perfil

### 2.1 Planeación de la Recolección

**Objetivo:**

Entender cómo los usuarios actualizan su información personal y configuraciones del sistema de forma segura y accesible.

**Stakeholders entrevistados:**

•	Ingeniero de Agroindustria: Define restricciones de edición. Mantiene perfil actualizado según tareas.

•	Agricultor: Actualiza datos básicos para recibir reportes y notificaciones.

**Complejidad:**

Moderada. Maneja datos personales y requiere validaciones.

### 2.2 Instrumento – Preguntas aplicadas

•	¿Qué datos debe poder editar el usuario?

•	¿Qué validaciones deben aplicarse?

•	¿Qué información debe mantenerse protegida?

•	¿Cómo debe notificarse la actualización?

•	¿Qué seguridad debe aplicarse al cambiar correo o contraseña?

### Respuestas obtenidas

**Ingeniero de Agroindustria**

"Hay datos que el usuario no debe cambiar, como su rol. Pero sí puede cambiar contacto, región y contraseña. Debo actualizar mi información para recibir reportes y notificaciones sin problemas."

**Agricultor**

"A veces uno cambia de número, o se mueve de finca. Yo quiero poder cambiar eso sin pedir ayuda."

### 2.3 Evidencia y Análisis

**Hallazgos clave**

•	Campos editables: nombre, contacto, ubicación, contraseña.

•	Campos no editables por usuario: rol, permisos (solo administradores pueden cambiar roles).

•	Se requiere verificación adicional para cambios sensibles (correo, contraseña).

•	El perfil se almacena en UserProfile con información extendida (teléfono, región, municipio, finca).

**Problemas y oportunidades**

•	Problema: Agricultores olvidan contraseñas.

 Oportunidad: Recuperación simple vía correo o WhatsApp.

•	Problema: Cambios sin validar podrían generar errores en reportes.

 Oportunidad: Verificación automática antes de guardar.

---

## Resumen General

### Hallazgos Transversales

1. **Roles del Sistema:**
   - **Agricultor (farmer)**: Usuario básico que gestiona sus fincas y lotes, sube imágenes y ve sus propios análisis.
   - **Ingeniero de Agroindustria (analyst)**: Usuario técnico que analiza imágenes, gestiona lotes, ve estadísticas y tiene acceso a todas las fincas.

2. **Seguridad y Auditoría:**
   - Todos los casos de uso requieren registro en ActivityLog.
   - Control de permisos por rol en todas las operaciones.
   - Verificación de email obligatoria para nuevos usuarios.

3. **Experiencia de Usuario:**
   - Mensajes simples y claros para agricultores.
   - Interfaz técnica detallada para ingenieros.
   - Tolerancia a fallos de conectividad en zonas rurales.

4. **Trazabilidad:**
   - Todas las operaciones quedan registradas con usuario, timestamp, IP y user agent.
   - Asociación de imágenes y análisis con fincas y lotes.
   - Historial completo de cambios en entidades críticas.



