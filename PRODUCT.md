# Product

## Register

product

## Users

Agricultores y técnicos agrícolas en Colombia y Latinoamérica. Usan la plataforma en contexto de campo o planta de beneficio — tablet o computador con conectividad variable. El agricultor tiene familiaridad básica con tecnología; el técnico es más avanzado y supervisa múltiples fincas. Ambos necesitan resultados claros y rápidos, sin ambigüedad.

## Product Purpose

CacaoScan mide dimensiones y peso de granos de cacao usando visión computacional (YOLOv8 + PyTorch). El técnico sube imágenes de los granos, el sistema los analiza y genera un informe de calidad que informa decisiones de comercialización y fermentación. El éxito es: el técnico confía en el resultado sin tener que entenderlo técnicamente.

## Brand Personality

Natural, cálido, accesible. Una herramienta hecha por y para el campo — no un SaaS genérico. Evoca la seriedad del trabajo agrícola sin frialdad corporativa. Como el técnico que llega a la finca con el instrumento correcto: confiable, sin pretensiones.

## Anti-references

- SaaS startup genérico: sin gradiente purple-to-blue, sin cards idénticas en grilla, sin hero con métricas flotantes, sin "10x your yield" marketing speak
- Enterprise frío: sin azul SAP/Oracle, sin dashboards tipo Salesforce con todo gris
- Green-nature cliché: el verde viene del producto (hoja de cacao), no de "naturaleza = verde = eco". Evitar paleta smoothie / hoja con fondo crema

## Design Principles

1. **Resultado primero.** Cada pantalla responde una pregunta concreta antes de mostrar opciones. El resultado del escaneo es lo primero visible, no el menú de acciones.
2. **Confianza sin complejidad.** Los modelos ML son opacos; el diseño debe hacer que el output parezca sólido y verificable. Datos precisos, jerarquía clara, sin decoración que distraiga.
3. **Campo, no oficina.** La UI funciona en pantallas con luz solar directa, dedos con tierra, conexión lenta. Contraste alto, tap targets generosos, sin interacciones dependientes de hover.
4. **Calidez sin costumbre.** El producto es técnico pero no frío. La calidez viene del color, no del tono — copy directo, no corporativo ni condescendiente.
5. **Un flujo, no un menú.** El técnico tiene una tarea principal: escanear y obtener el informe. Todo lo demás es secundario.

## Accessibility & Inclusion

- WCAG AA mínimo en toda la interfaz; apuntar a AAA en texto de resultados (ratio ≥7:1)
- Contraste alto prioritario: la plataforma se usa en campo con luz solar directa
- Tap targets mínimo 44×44px — uso con guantes o dedos amplios
- `prefers-reduced-motion` respetado en todas las animaciones
- Español como idioma principal; nombres técnicos sin jerga innecesaria
