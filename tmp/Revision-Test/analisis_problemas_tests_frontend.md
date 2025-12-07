# Análisis de Problemas en Tests Frontend

## Resumen
- **42 archivos de prueba fallidos**
- **241 pruebas fallidas**
- **4870 pruebas pasadas**
- **5 errores**

## Problemas Identificados

### 1. Mock de BaseCard en AuditCard.test.js

**Problema**: El mock de `BaseCard` en el test no coincide con la estructura real del componente.

**Componente Real** (`BaseCard.vue`):
- Usa slots: `header`, `icon`, `title`, `meta`, `headerActions`, `footer`, `actions`
- Estructura: `base-card-header`, `base-card-body`, `base-card-footer`

**Mock en Test**:
- Estructura simplificada que no coincide con la real
- Los slots pueden no estar siendo manejados correctamente

**Solución**: Actualizar el mock para que coincida con la estructura real del componente, especialmente el manejo de slots.

### 2. Uso de Composables Mockeados

**Verificado**: Los composables `useDateFormatting` y `useAuditHelpers` existen y están correctamente implementados.

**Estructura de `useDateFormatting`**:
- Exporta funciones: `formatDateTime`, `formatDate`, `formatDuration`, etc.
- Exporta composable: `useDateFormatting()` que retorna todas las funciones

**Estructura de `useAuditHelpers`**:
- Exporta funciones: `getAuditActionIcon`, `getAuditItemTitle`, etc.
- Exporta composable: `useAuditHelpers()` que retorna todas las funciones

**Observación**: Los mocks en los tests parecen estar correctos, pero deberían verificarse en ejecución.

### 3. Problemas Identificados

#### 3.1 **PROBLEMA CRÍTICO: Métodos no Expuestos en AuditCard.vue**

**Problema**: El componente `AuditCard.vue` usa `<script setup>` y no expone sus métodos usando `defineExpose()`.

El test intenta acceder a:
- `wrapper.vm.truncateText()`
- `wrapper.vm.formatDateTime()`
- `wrapper.vm.formatDuration()`
- `wrapper.vm.cardVariant` (computed)
- `wrapper.vm.cardIcon` (computed)

**Causa**: En Vue 3 con `<script setup>`, las funciones y variables no se exponen automáticamente a `wrapper.vm` en los tests a menos que se use `defineExpose()`.

**Solución**: Agregar `defineExpose()` al final del `<script setup>` en `AuditCard.vue`:

```javascript
// Al final del script setup
defineExpose({
  formatDateTime,
  formatDuration,
  truncateText,
  cardVariant,
  cardIcon
})
```

#### 3.2 Mocks no Reseteados Entre Tests
Algunos tests pueden tener problemas de estado compartido si los mocks no se limpian correctamente entre pruebas.

**Solución**: Verificar que todos los tests usen `beforeEach(() => vi.clearAllMocks())`

**Estado**: ✅ El test de `AuditCard` ya tiene esto implementado.

#### 3.3 Aserciones en Computed Properties
Algunos tests verifican computed properties directamente:
- `wrapper.vm.cardVariant`
- `wrapper.vm.cardIcon`

**Posible problema**: Estas propiedades computed podrían no estar siendo evaluadas correctamente durante el montaje.

### 4. Estructura del Componente AuditCard

**Análisis del componente**:
- ✅ Usa `useDateFormatting()` correctamente
- ✅ Usa `useAuditHelpers()` correctamente
- ✅ Define métodos: `formatDateTime`, `formatDuration`, `truncateText`
- ✅ Define computed: `cardTitle`, `itemType`, `itemStatus`, `statusClass`, `cardVariant`, `cardIcon`

**Nota**: Los métodos `formatDateTime` y `formatDuration` son wrappers que llaman a las funciones del composable. Esto podría causar problemas si los mocks no están configurados correctamente.

## Problemas Resueltos

✅ **CORREGIDO**: `AuditCard.vue` - Agregado `defineExpose()` para exponer métodos y computed properties necesarios para los tests.

## Recomendaciones

### Prioridad Alta

1. **✅ RESUELTO - Verificar Exposición de Métodos**: Se agregó `defineExpose()` en `AuditCard.vue` para exponer métodos y computed properties.

2. **Actualizar Mock de BaseCard**: Asegurar que el mock refleje la estructura real del componente con todos los slots. El mock actual podría no estar manejando correctamente los slots `meta`, `header`, `icon`, etc.

3. **Revisar Otros Componentes con `<script setup>`**: Verificar si otros componentes que usan `<script setup>` también necesitan `defineExpose()` si sus tests acceden a `wrapper.vm.*`.

4. **Verificar Tests de Acceso a Métodos**: Buscar en todos los archivos de prueba fallidos referencias a `wrapper.vm.*` y verificar que los componentes correspondientes expongan esas propiedades.

### Prioridad Media

4. **Revisar Tests de Otros Componentes**: Analizar los otros 41 archivos de prueba que están fallando para identificar patrones comunes.

5. **Verificar Mocks de Stores**: Asegurar que los stores mockeados tengan toda la estructura necesaria.

6. **Revisar Configuración de Vitest**: Verificar que la configuración de `vitest.config.js` y `setup.js` esté correcta.

### Prioridad Baja

7. **Mejorar Mensajes de Error**: Asegurar que los tests proporcionen mensajes de error claros para facilitar la depuración.

8. **Documentar Mocks**: Documentar la estructura esperada de los mocks para facilitar el mantenimiento.

## Archivos Clave a Revisar

1. `frontend/src/components/audit/__tests__/AuditCard.test.js`
2. `frontend/src/components/common/BaseCard.vue`
3. `frontend/src/test/setup.js`
4. `frontend/vitest.config.js`
5. Otros archivos de prueba que están fallando

## Próximos Pasos

1. Ejecutar un test específico para ver el error exacto (cuando sea posible)
2. Revisar los logs de error de las pruebas fallidas
3. Corregir los problemas identificados uno por uno
4. Verificar que las correcciones no rompan otras pruebas

