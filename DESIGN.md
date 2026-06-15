---
name: CacaoScan
description: Plataforma de visión computacional para medir calidad de granos de cacao en campo
colors:
  primary: "#10b981"
  primary-deep: "#27ae60"
  primary-surface: "#e3f9e5"
  ink: "#2c3e50"
  muted: "#7f8c8d"
  surface: "#f8f9fa"
  border: "#e9ecef"
  bg: "#ffffff"
  success-text: "#065f46"
  success-bg: "#e3f9e5"
  warning-text: "#8a4b00"
  warning-bg: "#fff8e1"
  error-text: "#b71c1c"
  error-bg: "#ffebee"
  error-inline: "#e74c3c"
typography:
  display:
    fontFamily: "system-ui, -apple-system, 'Segoe UI', sans-serif"
    fontSize: "2rem"
    fontWeight: 700
    lineHeight: 1.2
    letterSpacing: "-0.02em"
  headline:
    fontFamily: "system-ui, -apple-system, 'Segoe UI', sans-serif"
    fontSize: "1.5rem"
    fontWeight: 600
    lineHeight: 1.3
  title:
    fontFamily: "system-ui, -apple-system, 'Segoe UI', sans-serif"
    fontSize: "1rem"
    fontWeight: 600
    lineHeight: 1.4
  body:
    fontFamily: "system-ui, -apple-system, 'Segoe UI', sans-serif"
    fontSize: "0.875rem"
    fontWeight: 400
    lineHeight: 1.6
  label:
    fontFamily: "system-ui, -apple-system, 'Segoe UI', sans-serif"
    fontSize: "0.75rem"
    fontWeight: 500
    lineHeight: 1.4
rounded:
  sm: "4px"
  md: "8px"
  lg: "12px"
  pill: "9999px"
spacing:
  xs: "4px"
  sm: "8px"
  md: "16px"
  lg: "24px"
  xl: "32px"
  "2xl": "48px"
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.bg}"
    rounded: "{rounded.md}"
    padding: "10px 20px"
  button-primary-hover:
    backgroundColor: "{colors.primary-deep}"
    textColor: "{colors.bg}"
  button-secondary:
    backgroundColor: "{colors.bg}"
    textColor: "{colors.primary}"
    rounded: "{rounded.md}"
    padding: "10px 20px"
  button-ghost:
    backgroundColor: "transparent"
    textColor: "{colors.ink}"
    rounded: "{rounded.md}"
    padding: "10px 20px"
  card:
    backgroundColor: "{colors.bg}"
    rounded: "{rounded.lg}"
    padding: "{spacing.lg}"
  input:
    backgroundColor: "{colors.bg}"
    textColor: "{colors.ink}"
    rounded: "{rounded.md}"
    padding: "10px 14px"
  badge-success:
    backgroundColor: "{colors.success-bg}"
    textColor: "{colors.success-text}"
    rounded: "{rounded.pill}"
    padding: "2px 10px"
  badge-warning:
    backgroundColor: "{colors.warning-bg}"
    textColor: "{colors.warning-text}"
    rounded: "{rounded.pill}"
    padding: "2px 10px"
  badge-error:
    backgroundColor: "{colors.error-bg}"
    textColor: "{colors.error-text}"
    rounded: "{rounded.pill}"
    padding: "2px 10px"
---

# Design System: CacaoScan

## 1. Overview

**Creative North Star: "El Laboratorio del Cacao"**

CacaoScan es la herramienta que le pone número al ojo del técnico. El sistema de diseño refleja eso: rigor científico con calidez agrícola. Cada pantalla tiene un trabajo concreto — mostrar un resultado, pedir una imagen, generar un informe — y la UI desaparece para que el dato ocupe el primer plano. No hay decoración que no tenga función.

El sistema usa una sola familia tipográfica del sistema (system-ui / Segoe UI) en distintos pesos. La paleta es restringida: verde esmeralda como color de marca, blanco puro como fondo, tono oscuro azulado como tinta. Los colores semánticos (success, warning, error) son predecibles y no sorprenden. Las sombras no existen en reposo — la profundidad se comunica con bordes y tonos de superficie, no con efectos.

Este sistema rechaza explícitamente: gradientes purple-to-blue de SaaS genérico, cards idénticas en grilla, héroe con métricas flotantes, glassmorphism decorativo, y cualquier elemento que haga pensar en Salesforce, HubSpot, o un dashboard enterprise frío. La referencia correcta es una hoja de resultados de laboratorio: clara, densa donde debe ser densa, con una jerarquía que no requiere explicación.

**Key Characteristics:**
- Verde esmeralda único: aparece en acciones primarias y estados de éxito, nunca como decoración
- Fondo blanco puro, superficie gris-f (#f8f9fa) para diferenciar secciones
- Sin sombras en reposo — solo borde `1px solid #e9ecef`
- Tipografía del sistema, un solo peso por nivel jerárquico
- Tap targets ≥44px, contraste ≥7:1 en texto de resultados (uso en campo con luz solar)
- Componentes táctiles: feedback inmediato en press, sin animaciones de adorno

## 2. Colors: La Paleta del Campo

Estrategia **Restrained**: verde esmeralda como único acento, nunca más del 10% de la pantalla. Su rareza es la señal.

### Primary
- **Verde Esmeralda** (`#10b981` / oklch(0.697 0.191 157.0)): El color de marca. Usado exclusivamente en botones primarios, iconos de estado activo, bordes de focus, y estados de éxito confirmado. En ningún otro contexto.
- **Verde Profundo** (`#27ae60` / oklch(0.600 0.190 157.0)): Hover del primario y variante de énfasis. También en barras de progreso completadas.

### Secondary
- **Verde Éxito Texto** (`#065f46` / oklch(0.370 0.110 160.0)): Solo texto sobre fondo de éxito. Contraste ≥7:1 sobre `#e3f9e5`.

### Neutral
- **Tinta Principal** (`#2c3e50`): Todos los headings y texto de cuerpo. Azul-oscuro ligeramente desaturado — más cálido que negro puro.
- **Texto Secundario** (`#7f8c8d`): Labels, metadatos, texto de ayuda. Nunca en datos críticos del escaneo.
- **Superficie** (`#f8f9fa`): Fondos de cards, cabeceras de tabla, paneles laterales. Un paso más oscuro que el blanco puro.
- **Borde** (`#e9ecef`): Divisores y bordes de cards en reposo. El único separador entre capas.
- **Fondo Base** (`#ffffff`): Blanco puro. Sin tinte.

### Semantic (no se usan como decoración)
- **Éxito**: fondo `#e3f9e5` / texto `#065f46`
- **Advertencia**: fondo `#fff8e1` / texto `#8a4b00`
- **Error**: fondo `#ffebee` / texto `#b71c1c` / inline `#e74c3c`

**La Regla de la Señal Verde.** El color primario aparece en ≤10% de cualquier pantalla. Más verde que eso no es más marca — es ruido. Su escasez es lo que hace que un botón primario se vea como la acción correcta.

**La Regla Sin Azul de Enlace.** Los links en el dashboard usan actualmente `#3498db`. Esto debe migrarse a `#10b981` (primario) o `#2c3e50` con subrayado. Un color azul de link en un sistema de marca verde es una inconsistencia que erosiona la confianza visual.

## 3. Typography

**Display / Body Font:** system-ui, -apple-system, 'Segoe UI', Verdana, sans-serif (pila del sistema)

**Character:** Una sola familia en múltiples pesos. Sin pareja serif/sans — esto es una herramienta técnica, no un editorial. La jerarquía se comunica con peso y tamaño, no con familia tipográfica.

### Hierarchy
- **Display** (700, 2rem, lh 1.2, ls -0.02em): Títulos de página principales. Solo uno visible a la vez.
- **Headline** (600, 1.5rem, lh 1.3): Cabeceras de sección, títulos de modal.
- **Title** (600, 1rem, lh 1.4): Subtítulos, labels de card, nombres de campo.
- **Body** (400, 0.875rem, lh 1.6): Todo el texto de contenido. Máx 75ch en prose; sin límite en tablas.
- **Label** (500, 0.75rem, lh 1.4): Tags, badges, metadatos de tabla, texto de botón.

**La Regla del Peso Único.** Cada nivel jerárquico tiene un solo peso asignado. No mezclar Bold y SemiBold en el mismo nivel para "añadir énfasis" — usar el color semántico o el tamaño, no el peso.

**La Regla del Techo Display.** `letter-spacing` en headings: mínimo -0.02em, nunca más apretado. Display h1 en el dashboard usa system-ui que no necesita apertura negativa agresiva.

## 4. Elevation

Este sistema es **plano por defecto**. Las superficies no tienen sombra en reposo — la separación entre capas se comunica con el borde `1px solid #e9ecef` y la diferencia de tono entre `#ffffff` (contenido) y `#f8f9fa` (superficie).

La sombra solo aparece como respuesta a estado: hover en cards interactivas, modales, dropdowns. Nunca como decoración estática.

### Shadow Vocabulary
- **Hover elevado** (`0 4px 12px rgba(0, 0, 0, 0.08)`): Cards clicables en hover. Sutil; el card se "levanta" 4px perceptualmente.
- **Modal** (`0 16px 40px rgba(0, 0, 0, 0.16)`): Ventanas modales y drawers. La única sombra pesada permitida.
- **Tooltip** (`0 2px 8px rgba(0, 0, 0, 0.12)`): Tooltips y popovers.

**La Regla Plano-por-Defecto.** Si un elemento tiene sombra en reposo, se elimina. La sombra es un respuesta a interacción, no una decoración de identidad. Cards estáticas: `border: 1px solid #e9ecef`, sin `box-shadow`.

**La Regla Sin Ghost-Card.** Prohibido combinar `border: 1px solid` + `box-shadow` con blur ≥16px en el mismo elemento en reposo. El formulario de auth actual viola esta regla — migrar a solo borde o solo sombra mínima.

## 5. Components

### Buttons
Táctiles y directos. Press feedback inmediato (`transform: scale(0.98)` en active, 100ms). Sin animaciones de entrada. Tap target mínimo 44×44px.

- **Shape:** Gently curved (8px radius)
- **Primary:** Fondo `#10b981`, texto blanco, padding 10px 20px. En hover: `#27ae60`. En active: `scale(0.98)`.
- **Secondary:** Borde `1px solid #10b981`, texto `#10b981`, fondo transparente. En hover: fondo `#e3f9e5`.
- **Ghost:** Sin borde ni fondo en reposo, texto `#2c3e50`. En hover: fondo `#f8f9fa`.
- **Destructive:** Fondo `#b71c1c`, texto blanco. Solo en acciones de eliminación confirmadas.
- **Estados:** Disabled = 40% opacidad, cursor not-allowed. Loading = spinner de 16px inline izquierdo.

### Cards / Containers
- **Corner Style:** Gently curved (12px radius). Nunca más de 16px.
- **Background:** `#ffffff`
- **Border:** `1px solid #e9ecef` en reposo — es el único separador.
- **Shadow Strategy:** Sin sombra en reposo. Hover interactivo: `0 4px 12px rgba(0, 0, 0, 0.08)`.
- **Internal Padding:** 24px (spacing.lg). Cards compactas: 16px.

### Inputs / Fields
- **Style:** Fondo blanco, borde `1px solid #e9ecef`, radius 8px, padding 10px 14px.
- **Focus:** Borde `2px solid #10b981`, sin box-shadow adicional. Sin glow.
- **Error:** Borde `#e74c3c` + texto de error `#b71c1c` debajo del campo.
- **Disabled:** Fondo `#f8f9fa`, texto `#7f8c8d`, cursor not-allowed.
- **Tap target:** Mínimo 44px de altura.

### Badges / Status
Pills compactas, solo para estados del sistema (success, warning, error, neutral). No como decoración.

- **Success:** Fondo `#e3f9e5`, texto `#065f46`, radius pill.
- **Warning:** Fondo `#fff8e1`, texto `#8a4b00`, radius pill.
- **Error:** Fondo `#ffebee`, texto `#b71c1c`, radius pill.
- **Neutral:** Fondo `#ecf0f1`, texto `#2c3e50`, radius pill.

### Navigation
- Sidebar o top nav con fondo `#ffffff` o `#f8f9fa`, borde derecho/inferior `1px solid #e9ecef`.
- Item activo: texto `#10b981` + fondo `#e3f9e5` tenue. Nunca subrayado.
- Item hover: fondo `#f8f9fa`.
- Tipografía: Label (0.875rem, weight 500).

### Scan Result Card (Signature Component)
El componente más importante de la plataforma. Muestra dimensiones y peso del grano analizado.

- Layout en grid 2 columnas: imagen del grano izquierda, métricas derecha.
- Métricas en Display (2rem, bold): el número es lo primero que el ojo ve.
- Unidad en Label (0.75rem, muted): inmediatamente debajo del número.
- Badge de calidad en la esquina superior derecha.
- Sin sombra. Con borde `1px solid #e9ecef`. Con fondo blanco sobre superficie gris.

## 6. Do's and Don'ts

### Do:
- **Do** usar `#10b981` (verde esmeralda) exclusivamente en acciones primarias y estados de éxito — su rareza es la señal.
- **Do** usar `border: 1px solid #e9ecef` como único separador en reposo. La sombra es respuesta a estado, no decoración.
- **Do** mantener tap targets ≥44px en todos los elementos interactivos — la plataforma se usa con dedos en campo.
- **Do** mostrar el resultado del escaneo como primer elemento visible en cualquier pantalla de análisis.
- **Do** usar `transform: scale(0.98)` en active/press para dar feedback táctil inmediato.
- **Do** respetar `prefers-reduced-motion` — todas las transiciones caen a instantáneas.
- **Do** usar colores semánticos (success/warning/error) solo para comunicar estado real del sistema — nunca como decoración.
- **Do** usar body text en `#2c3e50` con contraste ≥7:1 sobre fondo blanco — crítico para lectura en luz solar directa.

### Don't:
- **Don't** usar gradiente purple-to-blue, ni ningún gradiente decorativo — es la primera señal de SaaS genérico.
- **Don't** combinar `border: 1px solid` + `box-shadow` con blur ≥16px en el mismo elemento en reposo (ghost-card ban).
- **Don't** usar `border-radius` mayor de 16px en cards o contenedores. El formulario de auth actual (24px) viola esta regla.
- **Don't** usar glassmorphism (`backdrop-filter: blur`) como estética por defecto — solo en overlays modales con propósito funcional.
- **Don't** usar `#3498db` (azul) para links en el dashboard — migrar al primario `#10b981` o al ink con subrayado.
- **Don't** poner cards idénticas en grilla (icon + heading + text × 3) como estructura por defecto de cualquier sección.
- **Don't** animar en acciones de teclado o acciones de alta frecuencia (el técnico hace decenas de escaneos por sesión).
- **Don't** usar texto muted (`#7f8c8d`) para datos de resultado del escaneo — solo para metadatos. Los datos van en ink (`#2c3e50`) o negro.
- **Don't** diseñar layouts que dependan de hover para revelar información en campo — el usuario puede estar en touch.
