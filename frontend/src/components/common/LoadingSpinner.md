# LoadingSpinner Component

Componente reutilizable para mostrar estados de carga en toda la aplicación.

## Ubicación
`frontend/src/components/common/LoadingSpinner.vue`

## Uso Básico

```vue
<template>
  <LoadingSpinner />
</template>

<script>
import LoadingSpinner from '@/components/common/LoadingSpinner.vue'

export default {
  components: {
    LoadingSpinner
  }
}
</script>
```

## Props

| Prop | Tipo | Default | Valores | Descripción |
|------|------|---------|---------|--------------|
| `size` | String | `'md'` | `'xs'`, `'sm'`, `'md'`, `'lg'`, `'xl'` | Tamaño del spinner |
| `color` | String | `'white'` | `'white'`, `'gray'`, `'blue'`, `'green'`, `'red'`, `'yellow'`, `'purple'` | Color del spinner |
| `strokeWidth` | String | `'4'` | Cualquier valor válido | Grosor del trazo del círculo |
| `className` | String | `''` | Cualquier clase CSS | Clases adicionales |

## Ejemplos de Uso

### Spinner en Botón
```vue
<button :disabled="loading">
  <LoadingSpinner 
    v-if="loading"
    size="sm" 
    color="white" 
    className="-ml-1 mr-3"
  />
  {{ loading ? 'Cargando...' : 'Enviar' }}
</button>
```

### Spinner en Overlay
```vue
<div v-if="loading" class="fixed inset-0 bg-gray-900 bg-opacity-50 flex items-center justify-center z-50">
  <div class="bg-white rounded-lg p-6 flex items-center space-x-3">
    <LoadingSpinner size="md" color="blue" />
    <span class="text-gray-700">Cargando datos...</span>
  </div>
</div>
```

### Spinner en Botón de Acción
```vue
<button @click="refresh" :disabled="loading">
  <LoadingSpinner 
    v-if="loading" 
    size="sm" 
    color="gray" 
  />
  <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
  </svg>
</button>
```

## Tamaños Disponibles

- **xs**: 12px (h-3 w-3)
- **sm**: 16px (h-4 w-4)
- **md**: 20px (h-5 w-5) - Default
- **lg**: 24px (h-6 w-6)
- **xl**: 32px (h-8 w-8)

## Colores Disponibles

- **white**: Blanco (text-white)
- **gray**: Gris (text-gray-600)
- **blue**: Azul (text-blue-600)
- **green**: Verde (text-green-600)
- **red**: Rojo (text-red-600)
- **yellow**: Amarillo (text-yellow-600)
- **purple**: Morado (text-purple-600)

## Características

- ✅ Animación suave con CSS
- ✅ Responsive y escalable
- ✅ Accesible
- ✅ Personalizable
- ✅ Reutilizable en toda la aplicación
- ✅ Consistente con el diseño del sistema

## Implementación Actual

El componente ya está implementado en:

- ✅ `LoginForm.vue` - Botón de inicio de sesión
- ✅ `AdminDashboard.vue` - Overlay de carga
- ✅ `DashboardCharts.vue` - Botones de refresh

## Migración

Para migrar spinners existentes:

1. Importar el componente:
```javascript
import LoadingSpinner from '@/components/common/LoadingSpinner.vue'
```

2. Registrar en components:
```javascript
components: {
  LoadingSpinner
}
```

3. Reemplazar el SVG existente:
```vue
<!-- Antes -->
<svg class="animate-spin h-5 w-5 text-white" ...>
  <!-- SVG content -->
</svg>

<!-- Después -->
<LoadingSpinner size="md" color="white" />
```
