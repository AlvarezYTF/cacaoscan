# 🔧 Guía de Refactorización - Vue 3 + TailwindCSS

## 📋 Estado Actual

### ✅ Completado:
1. **Composables creados:**
   - `composables/useCatalogos.js`
   - `composables/useFormValidation.js`
   - `composables/useBirthdateRange.js`
   - `composables/useModal.js`

2. **Componentes refactorizados:**
   - `components/layout/Common/Sidebar.vue` ✅

### 🎯 Próximos Pasos

Para continuar con la refactorización, sigue este patrón para cada componente:

## 📝 Patrón de Refactorización

### 1. Componentes con `<script setup>`

**ANTES:**
```vue
<script>
export default {
  name: 'ComponentName',
  props: {
    propName: {
      type: String,
      default: ''
    }
  },
  emits: ['event-name'],
  setup(props, { emit }) {
    // lógica
    return {
      // valores expuestos
    }
  }
}
</script>
```

**DESPUÉS:**
```vue
<script setup>
const props = defineProps({
  propName: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['event-name'])

// lógica directamente
</script>
```

### 2. Uso de Composables

**Ejemplo con useCatalogos:**
```vue
<script setup>
import { useCatalogos } from '@/composables/useCatalogos'
import { useFormValidation } from '@/composables/useFormValidation'
import { useBirthdateRange } from '@/composables/useBirthdateRange'

const {
  tiposDocumento,
  generos,
  departamentos,
  municipios,
  isLoadingCatalogos,
  cargarMunicipios
} = useCatalogos()

const { errors, isValidEmail, validatePassword, clearErrors } = useFormValidation()
const { maxBirthdate, minBirthdate } = useBirthdateRange()
</script>
```

### 3. Corrección de `:key` en v-for

**ANTES:**
```vue
<div v-for="(item, index) in items" :key="index">
```

**DESPUÉS:**
```vue
<div v-for="item in items" :key="item.id">
```

### 4. Organización de Imports

**Orden sugerido:**
1. Vue core (ref, computed, watch, etc.)
2. Vue Router (useRouter, useRoute)
3. Stores (useAuthStore, etc.)
4. Services (authApi, catalogosApi, etc.)
5. Composables (useCatalogos, etc.)
6. Components locales
7. Utils/helpers

**Ejemplo:**
```vue
<script setup>
// 1. Vue core
import { ref, computed, watch, onMounted } from 'vue'

// 2. Vue Router
import { useRouter } from 'vue-router'

// 3. Stores
import { useAuthStore } from '@/stores/auth'

// 4. Services
import authApi from '@/services/authApi'
import { catalogosApi } from '@/services'

// 5. Composables
import { useCatalogos } from '@/composables/useCatalogos'
import { useFormValidation } from '@/composables/useFormValidation'

// 6. Components locales
import SomeComponent from './SomeComponent.vue'

// 7. Utils
import Swal from 'sweetalert2'
</script>
```

### 5. Eliminación de Estilos Duplicados

Si un componente tiene estilos CSS que duplican clases de Tailwind, eliminar el CSS custom y usar solo Tailwind.

**Ejemplo (KPICards.vue):**
- Eliminar líneas 248-279 que duplican clases de Tailwind
- Mantener solo animaciones CSS que no están en Tailwind

## 🎯 Prioridad de Refactorización

### Fase 1 - Componentes Críticos (🟥 Alto):
1. ✅ Sidebar.vue - COMPLETADO
2. ⏳ EditFarmerModal.vue - Dividir en subcomponentes
3. ⏳ CreateFarmerModal.vue - Usar composables
4. ⏳ AdminDashboard.vue - Dividir en múltiples componentes
5. ⏳ AdminAgricultores.vue - Extraer lógica a composables
6. ⏳ RegisterForm.vue - Dividir en subcomponentes
7. ⏳ Analisis.vue - Extraer lógica

### Fase 2 - Componentes Moderados (🟧 Medio):
- Migrar todos a `<script setup>`
- Reemplazar `:key="index"` por IDs únicos
- Implementar tipado de props
- Organizar imports

### Fase 3 - Ajustes Menores (🟩 Bajo):
- Verificar todos usen `<script setup>`
- Organizar imports
- Optimizaciones menores

## 📋 Checklist por Componente

Al refactorizar cada componente, verifica:

- [ ] Migrado a `<script setup>`
- [ ] Props definidos con `defineProps()`
- [ ] Emits definidos con `defineEmits()`
- [ ] Uso de composables donde aplica
- [ ] `:key` usa IDs únicos en v-for
- [ ] Imports organizados por categorías
- [ ] Código no usado eliminado
- [ ] Estilos con `scoped`
- [ ] No hay estilos inline (solo Tailwind)
- [ ] Funciones no inline en template

## 🔄 Actualizar README después de cada refactorización

1. Marcar componente como "✅ REFACTORIZADO"
2. Anotar cambios principales
3. Actualizar resumen ejecutivo si aplica

## 💡 Tips

1. **No cambiar rutas ni endpoints** - Solo estructura y buenas prácticas
2. **Mantener funcionalidad** - El comportamiento debe ser idéntico
3. **Probar después de cada refactorización** - Asegurar que todo funciona
4. **Hacer commits frecuentes** - Un componente por commit facilita el rollback

---

**Última actualización:** Refactorización iniciada - Sidebar.vue completado como ejemplo

