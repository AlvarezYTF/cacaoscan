<template>
  <BaseModal
    :show="isOpen"
    title="Editar Agricultor"
    subtitle="Modifica la información del agricultor y gestiona sus fincas"
    max-width="4xl"
    @close="closeModal"
    @update:show="(value) => { if (!value) closeModal() }"
  >
    <template #header>
      <div class="flex items-center">
        <div class="bg-green-100 p-3 rounded-lg mr-4">
          <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z">
            </path>
          </svg>
        </div>
        <div>
          <h3 class="text-xl font-bold text-gray-900">Editar Agricultor</h3>
          <p class="text-sm text-gray-600 mt-1">Modifica la información del agricultor y gestiona sus fincas</p>
        </div>
      </div>
    </template>

    <div class="max-h-[calc(90vh-200px)] overflow-y-auto">
          <!-- Tabs -->
          <ul class="flex flex-wrap text-sm font-medium text-center text-gray-500 border-b border-gray-200 mb-6">
            <li class="mr-2">
              <button @click="activeTab = 'info'"
                :class="activeTab === 'info' ? 'text-green-600 border-green-600' : 'text-gray-500 border-transparent'"
                class="inline-block p-4 border-b-2 rounded-t-lg hover:text-gray-600 transition-all duration-200"
                type="button">
                Información Personal
              </button>
            </li>
            <li>
              <button @click="activeTab = 'fincas'"
                :class="activeTab === 'fincas' ? 'text-green-600 border-green-600' : 'text-gray-500 border-transparent'"
                class="inline-block p-4 border-b-2 rounded-t-lg hover:text-gray-600 transition-all duration-200"
                type="button">
                Fincas ({{ fincasList.length }})
              </button>
            </li>
          </ul>

          <!-- Tab Content: Information -->
          <div v-if="activeTab === 'info'" class="space-y-6">
            <PersonFormFields
              v-model="personaForm"
              :email-model="formData.email"
              :errors="errors"
              :tipos-documento="tiposDocumento"
              :generos="generos"
              :departamentos="departamentos"
              :municipios="municipios"
              :max-birthdate="maxBirthdate"
              :min-birthdate="minBirthdate"
              :base-input-classes="baseInputClasses"
              :get-input-classes="getInputClasses"
              field-prefix="edit-farmer"
              :on-departamento-change="onDepartamentoChange"
              @update:email-model="formData.email = $event"
            />
          </div>

          <!-- Tab Content: Fincas -->
          <div v-else-if="activeTab === 'fincas'">
            <div class="mb-6">
              <div class="flex items-center justify-between mb-4">
                <h4 class="text-lg font-bold text-gray-900">Fincas Registradas</h4>
                <button @click="showCreateFinca = !showCreateFinca"
                  class="inline-flex items-center px-4 py-2 text-sm font-semibold text-white bg-green-600 rounded-lg hover:bg-green-700 transition-all duration-200"
                  type="button">
                  <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
                  </svg>
                  Nueva Finca
                </button>
              </div>

              <!-- Formulario para crear finca -->
              <div v-if="showCreateFinca" class="bg-green-50 border-2 border-green-200 rounded-lg p-6 mb-6">
                <h5 class="text-base font-bold text-gray-900 mb-4">Crear Nueva Finca</h5>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label for="finca_nombre" class="block mb-2 text-sm font-semibold text-gray-700">
                      Nombre de la Finca <span class="text-red-500">*</span>
                    </label>
                    <input type="text" id="finca_nombre" v-model="newFinca.nombre"
                      class="bg-white border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 block w-full px-4 py-3 transition-all duration-200"
                      placeholder="Ej: Finca El Paraíso" required />
                  </div>

                  <div>
                    <label for="finca_municipio" class="block mb-2 text-sm font-semibold text-gray-700">
                      Municipio <span class="text-red-500">*</span>
                    </label>
                    <input type="text" id="finca_municipio" v-model="newFinca.municipio"
                      class="bg-white border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 block w-full px-4 py-3 transition-all duration-200"
                      placeholder="Ej: Medellín" required />
                  </div>

                  <div>
                    <label for="finca_departamento" class="block mb-2 text-sm font-semibold text-gray-700">
                      Departamento <span class="text-red-500">*</span>
                    </label>
                    <input type="text" id="finca_departamento" v-model="newFinca.departamento"
                      class="bg-white border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 block w-full px-4 py-3 transition-all duration-200"
                      placeholder="Ej: Antioquia" required />
                  </div>

                  <div>
                    <label for="finca_hectareas" class="block mb-2 text-sm font-semibold text-gray-700">
                      Hectáreas <span class="text-red-500">*</span>
                    </label>
                    <input type="number" id="finca_hectareas" v-model.number="newFinca.hectareas"
                      class="bg-white border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 block w-full px-4 py-3 transition-all duration-200"
                      placeholder="0.00" step="0.01" min="0.01" required />
                  </div>

                  <div class="md:col-span-2">
                    <label for="finca_ubicacion" class="block mb-2 text-sm font-semibold text-gray-700">
                      Ubicación
                    </label>
                    <input type="text" id="finca_ubicacion" v-model="newFinca.ubicacion"
                      class="bg-white border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 block w-full px-4 py-3 transition-all duration-200"
                      placeholder="Dirección específica o referencia" />
                  </div>

                  <div>
                    <label for="finca_coordenadas_lat" class="block mb-2 text-sm font-semibold text-gray-700">
                      Latitud GPS
                    </label>
                    <input type="number" id="finca_coordenadas_lat" v-model.number="newFinca.coordenadas_lat"
                      class="bg-white border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 block w-full px-4 py-3 transition-all duration-200"
                      placeholder="Ej: 4.6097" step="0.0000001" />
                  </div>

                  <div>
                    <label for="finca_coordenadas_lng" class="block mb-2 text-sm font-semibold text-gray-700">
                      Longitud GPS
                    </label>
                    <input type="number" id="finca_coordenadas_lng" v-model.number="newFinca.coordenadas_lng"
                      class="bg-white border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 block w-full px-4 py-3 transition-all duration-200"
                      placeholder="Ej: -74.0817" step="0.0000001" />
                  </div>
                </div>

                <div class="flex items-center justify-end gap-3 mt-4">
                  <button @click="showCreateFinca = false; resetNewFinca()"
                    class="px-4 py-2 text-sm font-semibold text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-all duration-200"
                    type="button">
                    Cancelar
                  </button>
                  <button @click="handleCreateFinca" :disabled="isCreatingFinca"
                    class="inline-flex items-center px-4 py-2 text-sm font-semibold text-white bg-green-600 rounded-lg hover:bg-green-700 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
                    type="button">
                    <span v-if="!isCreatingFinca">Crear Finca</span>
                    <span v-else class="flex items-center">
                      <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg"
                        fill="none" viewBox="0 0 24 24">
                        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4">
                        </circle>
                        <path class="opacity-75" fill="currentColor"
                          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z">
                        </path>
                      </svg>
                      Guardando...
                    </span>
                  </button>
                </div>
              </div>

              <!-- Lista de fincas -->
              <div v-if="fincasList.length > 0" class="space-y-3">
                <div v-for="finca in fincasList" :key="finca.id || finca.nombre"
                  class="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition-all duration-200">
                  <div class="flex items-start justify-between">
                    <div class="flex-1">
                      <div class="flex items-center gap-3 mb-2">
                        <div class="w-10 h-10 rounded-lg bg-green-100 flex items-center justify-center">
                          <svg class="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                              d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4">
                            </path>
                          </svg>
                        </div>
                        <div>
                          <h5 class="text-base font-bold text-gray-900">{{ finca.nombre }}</h5>
                          <p class="text-sm text-gray-600">{{ finca.municipio }}, {{ finca.departamento }}</p>
                        </div>
                      </div>
                      <div class="flex items-center gap-4 text-sm flex-wrap">
                        <span class="flex items-center gap-2 text-gray-600 bg-gray-50 px-3 py-1.5 rounded-lg">
                          <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                              d="M3 21v-4m0 0V5a2 2 0 012-2h6.5l1 1H21l-3 6 3 6h-8.5l-1-1H5a2 2 0 00-2 2zm9-13.5V9">
                            </path>
                          </svg>
                          {{ finca.hectareas }} hectáreas
                        </span>
                        <span :class="finca.activa ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'"
                          class="px-3 py-1.5 rounded-lg font-semibold flex items-center gap-1.5">
                          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7">
                            </path>
                          </svg>
                          {{ finca.activa ? 'Activa' : 'Inactiva' }}
                        </span>
                      </div>

                      <!-- Coordenadas GPS -->
                      <div v-if="finca.coordenadas_lat && finca.coordenadas_lng"
                        class="mt-2 flex items-center gap-2 text-xs text-gray-500">
                        <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                            d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z">
                          </path>
                        </svg>
                        <span>📍 GPS: {{ finca.coordenadas_lat }}, {{ finca.coordenadas_lng }}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Empty state -->
              <div v-else class="bg-gray-50 border border-gray-200 rounded-lg p-8 text-center">
                <svg class="w-16 h-16 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4">
                  </path>
                </svg>
                <h4 class="text-lg font-bold text-gray-900 mb-2">Sin fincas registradas</h4>
                <p class="text-gray-600">Este agricultor no tiene fincas asociadas aún</p>
              </div>
            </div>
          </div>
    </div>

    <template #footer>
      <div class="flex items-center justify-end gap-3">
        <button 
          type="button" 
          @click="closeModal"
          class="px-6 py-3 text-sm font-semibold text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 transition-all duration-200"
        >
          Cancelar
        </button>
        <button 
          type="button" 
          @click="handleUpdate" 
          :disabled="isSubmitting"
          class="inline-flex items-center px-6 py-3 text-sm font-semibold text-white bg-green-600 border border-transparent rounded-lg hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed shadow-md hover:shadow-lg"
        >
          <span v-if="!isSubmitting">Guardar Cambios</span>
          <span v-else class="flex items-center">
            <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none"
              viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z">
              </path>
            </svg>
            Guardando...
          </span>
        </button>
      </div>
    </template>
  </BaseModal>
</template>

<script setup>
// 1. Vue core
import { ref, reactive, watch } from 'vue'

// 2. Services
import { createFinca, getFincas } from '@/services/fincasApi'
import authApi from '@/services/authApi'
import { personasApi } from '@/services'

// 3. Composables
import { usePersonForm } from '@/composables/usePersonForm'
import { useNotifications } from '@/composables/useNotifications'
import BaseModal from '@/components/common/BaseModal.vue'
import PersonFormFields from '@/components/common/PersonFormFields.vue'

// Props
const props = defineProps({
  farmer: {
    type: Object,
    default: () => ({
      id: null,
      name: '',
      email: '',
      first_name: '',
      last_name: '',
      phone_number: '',
      region: '',
      municipality: '',
      fincas: []
    })
  }
})

// Emits
const emit = defineEmits(['farmer-updated', 'close'])

// Composables
const {
  tiposDocumento,
  generos,
  departamentos,
  municipios,
  isLoadingCatalogos,
  cargarCatalogos,
  cargarMunicipios,
  limpiarMunicipios,
  errors,
  isValidEmail,
  isValidPhone,
  isValidDocument,
  clearErrors,
  maxBirthdate,
  minBirthdate,
  onDepartamentoChange: baseOnDepartamentoChange
} = usePersonForm()
const { showSuccess, showError } = useNotifications()

// State
const isOpen = ref(false)
const isSubmitting = ref(false)
const isCreatingFinca = ref(false)
const activeTab = ref('info')
const showCreateFinca = ref(false)
const fincasList = ref([])

const formData = reactive({
  first_name: '',
  last_name: '',
  email: '',
  phone_number: '',
  region: '',
  municipality: ''
})

const personaForm = reactive({
  primer_nombre: '',
  segundo_nombre: '',
  primer_apellido: '',
  segundo_apellido: '',
  tipo_documento: '',
  numero_documento: '',
  genero: '',
  fecha_nacimiento: '',
  telefono: '',
  direccion: '',
  departamento: null,
  municipio: null
})

const newFinca = reactive({
  nombre: '',
  municipio: '',
  departamento: '',
  hectareas: '',
  ubicacion: '',
  coordenadas_lat: null,
  coordenadas_lng: null
})

// Functions
const loadFarmersFincas = async (agricultorId) => {
  try {
    const response = await getFincas({ agricultor: agricultorId })
    fincasList.value = response.results || []
  } catch (error) {
    console.error('Error cargando fincas:', error)
    fincasList.value = []
  }
}

// Load farmer data when prop changes
watch(() => props.farmer, async (newFarmer) => {
  if (newFarmer && newFarmer.id) {
    // Extract first_name and last_name from name
    const nameParts = newFarmer.name?.split(' ') || []
    formData.first_name = nameParts[0] || ''
    formData.last_name = nameParts.slice(1).join(' ') || ''
    formData.email = newFarmer.email || ''
    formData.phone_number = newFarmer.phone_number || ''
    formData.region = newFarmer.region || ''
    formData.municipality = newFarmer.municipality || ''

    // Load fincas
    await loadFarmersFincas(newFarmer.id)

    // Load persona data
    try {
      const personaData = await personasApi.getPersonaByUserId(newFarmer.id)
      personaForm.primer_nombre = personaData.primer_nombre || ''
      personaForm.segundo_nombre = personaData.segundo_nombre || ''
      personaForm.primer_apellido = personaData.primer_apellido || ''
      personaForm.segundo_apellido = personaData.segundo_apellido || ''
      personaForm.tipo_documento = personaData.tipo_documento_info?.codigo || ''
      personaForm.numero_documento = personaData.numero_documento || ''
      personaForm.genero = personaData.genero_info?.codigo || ''
      personaForm.fecha_nacimiento = personaData.fecha_nacimiento || ''
      personaForm.telefono = personaData.telefono || ''
      personaForm.direccion = personaData.direccion || ''
      personaForm.departamento = personaData.departamento_info?.id || null
      personaForm.municipio = personaData.municipio_info?.id || null

      // Load municipios if there's a departamento
      if (personaForm.departamento) {
        await onDepartamentoChange()
      }
    } catch (error) {
      const statusCode = error?.response?.status
      const errorData = error?.response?.data
      const errorMessage = errorData?.message || errorData?.detail || error?.message || 'Error al cargar los datos de la persona'

      if (statusCode === 404) {
        // 404 is expected - persona doesn't exist yet and will be created on save
        console.warn('Persona no encontrada para el usuario, se podrá crear al guardar')
      } else {
        // Handle unexpected errors by showing notification to user
        console.error('Error al cargar datos de persona:', errorMessage, error)
        showError(errorMessage)
      }
    }
  }
}, { immediate: true })

const resetNewFinca = () => {
  newFinca.nombre = ''
  newFinca.municipio = ''
  newFinca.departamento = ''
  newFinca.hectareas = ''
  newFinca.ubicacion = ''
  newFinca.coordenadas_lat = null
  newFinca.coordenadas_lng = null
}

const handleCreateFinca = async () => {
  // Validate required fields
  if (!newFinca.nombre || !newFinca.municipio || !newFinca.departamento || !newFinca.hectareas) {
    showError('Por favor completa todos los campos requeridos')
    return
  }

  isCreatingFinca.value = true

  try {
    const fincaData = {
      nombre: newFinca.nombre,
      municipio: newFinca.municipio,
      departamento: newFinca.departamento,
      hectareas: Number.parseFloat(newFinca.hectareas),
      ubicacion: newFinca.ubicacion || '',
      agricultor: props.farmer.id,
      coordenadas_lat: newFinca.coordenadas_lat || null,
      coordenadas_lng: newFinca.coordenadas_lng || null
    }

    await createFinca(fincaData)

    showSuccess('La finca ha sido registrada exitosamente')

    resetNewFinca()
    showCreateFinca.value = false

    // Reload fincas
    await loadFarmersFincas(props.farmer.id)

    emit('farmer-updated', { type: 'finca-created' })

  } catch (error) {
    console.error('Error creando finca:', error)

    let errorMessage = 'Error al crear la finca'
    if (error.response?.data) {
      const data = error.response.data
      errorMessage = data.message || data.error || errorMessage
      if (data.details) {
        const details = Object.entries(data.details)
          .map(([key, value]) => `${key}: ${Array.isArray(value) ? value[0] : value}`)
          .join(', ')
        if (details) {
          errorMessage += `\n\nDetalles: ${details}`
        }
      }
    }

    showError(errorMessage.replaceAll('\n', ' '))
  } finally {
    isCreatingFinca.value = false
  }
}

const handleUpdate = async () => {
  // Validate required fields
  clearErrors()

  if (!formData.first_name || !formData.last_name || !formData.email) {
    showError('Por favor completa todos los campos requeridos')
    return
  }

  isSubmitting.value = true

  try {
    const updateData = {
      first_name: formData.first_name,
      last_name: formData.last_name,
      email: formData.email
    }

    const response = await authApi.updateUser(props.farmer.id, updateData)

    // Update/create persona data
    const personaPayload = {
      primer_nombre: personaForm.primer_nombre,
      segundo_nombre: personaForm.segundo_nombre || '',
      primer_apellido: personaForm.primer_apellido,
      segundo_apellido: personaForm.segundo_apellido || '',
      tipo_documento: personaForm.tipo_documento,
      numero_documento: personaForm.numero_documento,
      genero: personaForm.genero,
      fecha_nacimiento: personaForm.fecha_nacimiento || null,
      telefono: personaForm.telefono,
      direccion: personaForm.direccion || '',
      departamento: personaForm.departamento || null,
      municipio: personaForm.municipio || null
    }

    if (Object.keys(personaPayload).length > 0) {
      try {
        await personasApi.updatePersonaByUserId(props.farmer.id, personaPayload)
      } catch (e) {
        console.warn('Error actualizando persona (continuando):', e)
      }
    }

    showSuccess('La información del agricultor ha sido actualizada exitosamente')

    emit('farmer-updated', { type: 'user-updated', user: response.user })
    closeModal()
  } catch (error) {
    console.error('Error actualizando agricultor:', error)

    let errorMessage = 'Error al actualizar el agricultor'
    if (error.response?.data) {
      const data = error.response.data
      errorMessage = data.message || data.error || errorMessage
      if (data.details) {
        const details = Object.entries(data.details)
          .map(([key, value]) => `${key}: ${Array.isArray(value) ? value[0] : value}`)
          .join(', ')
        if (details) {
          errorMessage += `\n\nDetalles: ${details}`
        }
      }
    }

    showError(errorMessage.replaceAll('\n', ' '))
  } finally {
    isSubmitting.value = false
  }
}

const onDepartamentoChange = async () => {
  personaForm.municipio = null
  await baseOnDepartamentoChange()
  if (personaForm.departamento) {
    await cargarMunicipios(personaForm.departamento)
  }
}

const closeModal = () => {
  isOpen.value = false
  showCreateFinca.value = false
  resetNewFinca()
  emit('close')
}

const openModal = async () => {
  isOpen.value = true
  await cargarCatalogos()
}

defineExpose({
  openModal
})
</script>

<style scoped>
/* Solo estilos que no están en Tailwind si es necesario */
</style>
