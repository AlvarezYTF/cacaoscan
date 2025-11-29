<template>
  <div class="bg-white rounded-2xl border-2 border-gray-200 p-8 shadow-lg">
    <!-- Header del formulario -->
    <div class="text-center mb-8">
      <h2 class="text-3xl font-bold text-gray-900 mb-2">Datos Personales</h2>
      <p class="text-gray-600 text-base">Actualiza tu información personal</p>
    </div>

    <!-- Foto de perfil -->
    <div class="flex items-center justify-center gap-4 mb-8">
      <div class="relative">
        <div class="w-24 h-24 bg-gradient-to-br from-green-500 to-green-600 rounded-2xl flex items-center justify-center text-white text-3xl font-bold shadow-lg">
          {{ userInitials }}
        </div>
        <button class="absolute -bottom-1 -right-1 p-2.5 bg-green-600 rounded-full text-white hover:bg-green-700 transition-colors shadow-lg">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
        </button>
      </div>
      <div>
        <p class="font-semibold text-gray-900 text-lg">{{ fullName }}</p>
        <p class="text-sm text-gray-500">Sube una foto para personalizar tu perfil</p>
      </div>
    </div>

    <form class="space-y-6">
      <!-- Nombres -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <!-- Primer Nombre -->
        <div>
          <label for="profile-primer-nombre" class="block text-sm font-semibold text-gray-700 mb-2 flex items-center gap-2">
            <svg class="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
            Primer Nombre *
          </label>
          <input 
            id="profile-primer-nombre"
            type="text" 
            v-model="form.primer_nombre"
            placeholder="Juan" 
            :disabled="isLoading"
            class="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500/50 focus:border-green-500 disabled:bg-gray-100 transition-all"
            :class="{'border-red-500': errors.primer_nombre, 'border-green-300': form.primer_nombre && !errors.primer_nombre}"
          />
          <p v-if="errors.primer_nombre" class="text-red-600 text-xs mt-1">{{ errors.primer_nombre }}</p>
        </div>

        <!-- Segundo Nombre -->
        <div>
          <label for="profile-segundo-nombre" class="block text-sm font-semibold text-gray-700 mb-2">
            Segundo Nombre
          </label>
          <input 
            id="profile-segundo-nombre"
            type="text" 
            v-model="form.segundo_nombre"
            placeholder="Carlos (opcional)" 
            :disabled="isLoading"
            class="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500/50 focus:border-green-500 disabled:bg-gray-100 transition-all"
          />
        </div>
      </div>

      <!-- Apellidos -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <!-- Primer Apellido -->
        <div>
          <label for="profile-primer-apellido" class="block text-sm font-semibold text-gray-700 mb-2">
            Primer Apellido *
          </label>
          <input 
            id="profile-primer-apellido"
            type="text" 
            v-model="form.primer_apellido"
            placeholder="Pérez" 
            :disabled="isLoading"
            class="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500/50 focus:border-green-500 disabled:bg-gray-100 transition-all"
            :class="{'border-red-500': errors.primer_apellido, 'border-green-300': form.primer_apellido && !errors.primer_apellido}"
          />
          <p v-if="errors.primer_apellido" class="text-red-600 text-xs mt-1">{{ errors.primer_apellido }}</p>
        </div>

        <!-- Segundo Apellido -->
        <div>
          <label for="profile-segundo-apellido" class="block text-sm font-semibold text-gray-700 mb-2">
            Segundo Apellido
          </label>
          <input 
            id="profile-segundo-apellido"
            type="text" 
            v-model="form.segundo_apellido"
            placeholder="García (opcional)" 
            :disabled="isLoading"
            class="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500/50 focus:border-green-500 disabled:bg-gray-100 transition-all"
          />
        </div>
      </div>

      <!-- Tipo de Documento y Número -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <!-- Tipo de Documento -->
        <div>
          <label for="profile-tipo-documento" class="block text-sm font-semibold text-gray-700 mb-2">
            Tipo de Documento *
          </label>
          <select
            id="profile-tipo-documento"
            v-model="form.tipo_documento"
            :disabled="isLoading"
            class="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500/50 focus:border-green-500 disabled:bg-gray-100 transition-all"
          >
            <option value="">Seleccionar...</option>
            <option v-for="tipo in tiposDocumento" :key="tipo.codigo" :value="tipo.codigo">
              {{ tipo.nombre }}
            </option>
          </select>
          <p v-if="errors.tipo_documento" class="text-red-600 text-xs mt-1">{{ errors.tipo_documento }}</p>
        </div>

        <!-- Número de Documento -->
        <div>
          <label for="profile-numero-documento" class="block text-sm font-semibold text-gray-700 mb-2">
            Número de Documento *
          </label>
          <input 
            id="profile-numero-documento"
            type="text" 
            v-model="form.numero_documento"
            placeholder="1012345678" 
            :disabled="isLoading"
            class="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500/50 focus:border-green-500 disabled:bg-gray-100 transition-all"
            :class="{'border-red-500': errors.numero_documento, 'border-green-300': form.numero_documento && !errors.numero_documento}"
          />
          <p v-if="errors.numero_documento" class="text-red-600 text-xs mt-1">{{ errors.numero_documento }}</p>
        </div>
      </div>

      <!-- Género y Fecha de Nacimiento -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <!-- Género -->
        <div>
          <label for="profile-genero" class="block text-sm font-semibold text-gray-700 mb-2">
            Género *
          </label>
          <select
            id="profile-genero"
            v-model="form.genero"
            :disabled="isLoading"
            class="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500/50 focus:border-green-500 disabled:bg-gray-100 transition-all"
          >
            <option value="">Seleccionar...</option>
            <option v-for="genero in generos" :key="genero.codigo" :value="genero.codigo">
              {{ genero.nombre }}
            </option>
          </select>
          <p v-if="errors.genero" class="text-red-600 text-xs mt-1">{{ errors.genero }}</p>
        </div>

        <!-- Fecha de Nacimiento -->
        <div>
          <label for="profile-fecha-nacimiento" class="block text-sm font-semibold text-gray-700 mb-2">
            Fecha de Nacimiento
          </label>
          <input 
            id="profile-fecha-nacimiento"
            type="date" 
            v-model="form.fecha_nacimiento"
            :disabled="isLoading"
            :max="maxBirthdate"
            :min="minBirthdate"
            class="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500/50 focus:border-green-500 disabled:bg-gray-100 transition-all"
            :class="{'border-red-500': errors.fecha_nacimiento}"
          />
          <p v-if="errors.fecha_nacimiento" class="text-red-600 text-xs mt-1">{{ errors.fecha_nacimiento }}</p>
          <p class="text-gray-500 text-xs mt-1">Debes tener al menos 14 años</p>
        </div>
      </div>

      <!-- Email (solo lectura) -->
      <div>
        <label for="profile-email" class="block text-sm font-semibold text-gray-700 mb-2 flex items-center gap-2">
          <svg class="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
          </svg>
          Email (no modificable)
        </label>
        <div class="relative">
          <input 
            id="profile-email"
            type="email" 
            :value="form.email" 
            readonly 
            class="w-full px-4 py-3 border-2 border-gray-200 rounded-lg bg-gray-100 cursor-not-allowed"
          />
          <div v-if="isVerified" class="absolute right-3 top-1/2 -translate-y-1/2 flex items-center gap-1">
            <svg class="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
        </div>
        <p class="mt-1.5 text-sm text-gray-500 flex items-center gap-1">
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          Contacta al administrador para cambiar tu email
        </p>
      </div>

      <!-- Teléfono -->
      <div>
        <label for="profile-telefono" class="block text-sm font-semibold text-gray-700 mb-2 flex items-center gap-2">
          <svg class="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
          </svg>
          Teléfono *
        </label>
        <input 
          id="profile-telefono"
          type="tel" 
          v-model="form.telefono"
          autocomplete="tel"
          placeholder="+57 300 123 4567" 
          :disabled="isLoading"
          class="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500/50 focus:border-green-500 disabled:bg-gray-100 transition-all"
          :class="{'border-red-500': errors.telefono, 'border-green-300': form.telefono && !errors.telefono}"
        />
        <p v-if="errors.telefono" class="text-red-600 text-xs mt-1">{{ errors.telefono }}</p>
      </div>

      <!-- Dirección -->
      <div>
        <label for="profile-direccion" class="block text-sm font-semibold text-gray-700 mb-2">
          Dirección
        </label>
        <input 
          id="profile-direccion"
          name="direccion"
          type="text"
          v-model="form.direccion"
          autocomplete="address-line1"
          placeholder="Calle 10 #5-20" 
          :disabled="isLoading"
          class="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500/50 focus:border-green-500 disabled:bg-gray-100 transition-all"
        />
      </div>

      <!-- Ubicación -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <!-- Departamento -->
        <div>
          <label for="profile-departamento" class="block text-sm font-semibold text-gray-700 mb-2">
            Departamento
          </label>
          <select
            id="profile-departamento"
            v-model="form.departamento"
            @change="onDepartamentoChange"
            :disabled="isLoading"
            class="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500/50 focus:border-green-500 disabled:bg-gray-100 transition-all"
          >
            <option value="">Seleccionar...</option>
            <option v-for="depto in departamentos" :key="depto.id" :value="depto.id">
              {{ depto.nombre }}
            </option>
          </select>
        </div>

        <!-- Municipio -->
        <div>
          <label for="profile-municipio" class="block text-sm font-semibold text-gray-700 mb-2">
            Municipio
          </label>
          <select
            id="profile-municipio"
            v-model="form.municipio"
            :disabled="isLoading || !form.departamento"
            class="w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500/50 focus:border-green-500 disabled:bg-gray-100 transition-all"
          >
            <option value="">Seleccionar...</option>
            <option v-for="mun in municipios" :key="mun.id" :value="mun.id">
              {{ mun.nombre }}
            </option>
          </select>
        </div>
      </div>

      <!-- Mensaje de estado -->
      <Transition enter-active-class="transform ease-out duration-300 transition"
        enter-from-class="opacity-0 translate-y-2" enter-to-class="opacity-100 translate-y-0"
        leave-active-class="transition ease-in duration-200" leave-from-class="opacity-100" leave-to-class="opacity-0">
        <div v-if="statusMessage" class="p-4 rounded-xl flex items-start gap-3 shadow-md" :class="statusMessageClass">
          <svg v-if="statusType === 'success'" class="w-5 h-5 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor"
            viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <svg v-else class="w-5 h-5 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <p class="text-sm font-medium">{{ statusMessage }}</p>
        </div>
      </Transition>

      <!-- Botón de guardar -->
      <div>
        <button 
          @click.prevent="handleSave"
          :disabled="isLoading || !isFormValid"
          class="w-full flex justify-center items-center gap-2 py-3.5 px-4 border border-transparent rounded-xl shadow-lg text-base font-semibold text-white bg-gradient-to-r from-green-600 to-green-700 hover:from-green-700 hover:to-green-800 focus:outline-none focus:ring-4 focus:ring-green-500/50 disabled:opacity-60 disabled:cursor-not-allowed transition-all duration-200 hover:shadow-xl active:scale-[0.97] group"
        >
          <svg
            v-if="isLoading"
            class="animate-spin h-5 w-5 text-white"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
          </svg>
          <span>{{ isLoading ? 'Guardando...' : 'Guardar Cambios' }}</span>
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { catalogosApi } from '@/services'

const props = defineProps({
  personaData: {
    type: Object,
    default: () => ({})
  },
  isLoading: {
    type: Boolean,
    default: false
  },
  isVerified: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['save'])

// Datos del formulario
const form = ref({
  primer_nombre: '',
  segundo_nombre: '',
  primer_apellido: '',
  segundo_apellido: '',
  tipo_documento: '',
  numero_documento: '',
  genero: '',
  fecha_nacimiento: '',
  email: '',
  telefono: '',
  direccion: '',
  departamento: null,
  municipio: null
})

// Catálogos
const tiposDocumento = ref([])
const generos = ref([])
const departamentos = ref([])
const municipios = ref([])

// Errores y mensajes
const errors = ref({})
const statusMessage = ref('')
const statusType = ref('success')

// Computed para las fechas
const maxBirthdate = computed(() => {
  const today = new Date()
  const maxDate = new Date(today.getFullYear() - 14, today.getMonth(), today.getDate())
  return maxDate.toISOString().split('T')[0]
})

const minBirthdate = computed(() => {
  const today = new Date()
  const minDate = new Date(today.getFullYear() - 120, today.getMonth(), today.getDate())
  return minDate.toISOString().split('T')[0]
})

// Computed para nombre completo
const fullName = computed(() => {
  const parts = [
    form.value.primer_nombre,
    form.value.segundo_nombre,
    form.value.primer_apellido,
    form.value.segundo_apellido
  ].filter(Boolean)
  return parts.join(' ') || 'Sin nombre'
})

// Computed para iniciales
const userInitials = computed(() => {
  const firstName = form.value.primer_nombre || ''
  const lastName = form.value.primer_apellido || ''
  if (firstName && lastName) {
    return (firstName[0] + lastName[0]).toUpperCase()
  }
  return firstName ? firstName[0].toUpperCase() : 'U'
})

// Computed para clase de mensaje de estado
const statusMessageClass = computed(() => {
  return statusType.value === 'success'
    ? 'bg-green-50 text-green-800 border-2 border-green-200'
    : 'bg-red-50 text-red-800 border-2 border-red-200'
})

// Validación del formulario
const isFormValid = computed(() => {
  return !!(
    form.value.primer_nombre &&
    form.value.primer_apellido &&
    form.value.tipo_documento &&
    form.value.numero_documento &&
    form.value.genero &&
    form.value.telefono
  )
})

// Cargar catálogos
const cargarCatalogos = async () => {
  try {
    // Cargar tipos de documento
    const tiposDoc = await catalogosApi.getParametrosByTema('TIPO_DOC')
    tiposDocumento.value = tiposDoc

    // Cargar géneros
    const generosData = await catalogosApi.getParametrosByTema('SEXO')
    generos.value = generosData

    // Cargar departamentos
    const deptos = await catalogosApi.getDepartamentos()
    departamentos.value = deptos
  } catch (error) {
    console.error('Error cargando catálogos:', error)
    setStatusMessage('Error al cargar los catálogos', 'error')
  }
}

// Cargar municipios cuando cambia el departamento
const onDepartamentoChange = async () => {
  form.value.municipio = null
  municipios.value = []
  
  if (form.value.departamento) {
    try {
      const munis = await catalogosApi.getMunicipiosByDepartamento(form.value.departamento)
      municipios.value = munis
    } catch (error) {
      console.error('Error cargando municipios:', error)
      setStatusMessage('Error al cargar los municipios', 'error')
    }
  }
}

// Inicializar datos
watch(() => props.personaData, async (newData) => {
  if (newData && Object.keys(newData).length > 0) {
    console.log('📥 Datos recibidos de persona:', newData)
    
    form.value = {
      primer_nombre: newData.primer_nombre || '',
      segundo_nombre: newData.segundo_nombre || '',
      primer_apellido: newData.primer_apellido || '',
      segundo_apellido: newData.segundo_apellido || '',
      // tipo_documento_info contiene {id, codigo, nombre}
      tipo_documento: newData.tipo_documento_info?.codigo || '',
      numero_documento: newData.numero_documento || '',
      // genero_info contiene {id, codigo, nombre}
      genero: newData.genero_info?.codigo || '',
      fecha_nacimiento: newData.fecha_nacimiento || '',
      email: newData.email || '',
      telefono: newData.telefono || '',
      direccion: newData.direccion || '',
      // departamento_info contiene {id, codigo, nombre}
      departamento: newData.departamento_info?.id || null,
      // municipio_info contiene {id, codigo, nombre}
      municipio: newData.municipio_info?.id || null
    }

    console.log('📝 Formulario inicializado:', form.value)

    // Cargar municipios si hay departamento
    if (form.value.departamento) {
      await onDepartamentoChange()
    }
  }
}, { immediate: true, deep: true })

// Manejar guardado
const handleSave = () => {
  errors.value = {}
  
  // Validaciones básicas
  if (!form.value.primer_nombre) {
    errors.value.primer_nombre = 'El primer nombre es requerido'
  }
  if (!form.value.primer_apellido) {
    errors.value.primer_apellido = 'El primer apellido es requerido'
  }
  if (!form.value.tipo_documento) {
    errors.value.tipo_documento = 'El tipo de documento es requerido'
  }
  if (!form.value.numero_documento) {
    errors.value.numero_documento = 'El número de documento es requerido'
  }
  if (!form.value.genero) {
    errors.value.genero = 'El género es requerido'
  }
  if (!form.value.telefono) {
    errors.value.telefono = 'El teléfono es requerido'
  }

  if (Object.keys(errors.value).length === 0) {
    emit('save', form.value)
  }
}

// Método para mostrar mensajes de estado
const setStatusMessage = (message, type = 'success') => {
  statusMessage.value = message
  statusType.value = type
  setTimeout(() => {
    statusMessage.value = ''
  }, 5000)
}

// Cargar catálogos al montar
onMounted(() => {
  cargarCatalogos()
})

// Exponer método para mostrar mensajes desde el padre
defineExpose({
  setStatusMessage
})
</script>

<style scoped>
@keyframes fade-in {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fade-in {
  animation: fade-in 0.6s ease-out;
}
</style>
