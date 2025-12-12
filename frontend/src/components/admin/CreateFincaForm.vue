<template>
  <div class="fixed inset-0 bg-black bg-opacity-50 backdrop-blur-sm flex items-center justify-center z-50 p-4 w-full h-full">
    <div class="bg-white rounded-xl shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
      <!-- Header -->
      <div class="bg-gradient-to-r from-green-50 to-green-50 px-6 py-4 border-b border-gray-200">
        <div class="flex items-center justify-between">
          <div class="flex items-center">
            <div class="bg-green-100 p-2 rounded-lg mr-3">
              <svg class="text-xl text-green-600 w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
              </svg>
            </div>
            <div>
              <h2 class="text-xl font-bold text-gray-900">Nueva Finca</h2>
              <p class="text-sm text-gray-600">Registra una nueva finca en el sistema</p>
            </div>
          </div>
          <button
            @click="$emit('close')"
            class="text-gray-400 hover:text-gray-600 transition-all duration-200 p-2 rounded-lg hover:bg-gray-100"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </div>
      </div>

      <!-- Form -->
      <form @submit.prevent="submitForm" class="p-6">
        <div class="space-y-8">
          <!-- Información básica -->
          <div class="bg-gray-50 rounded-lg p-6">
            <div class="flex items-center mb-4">
              <div class="bg-green-100 p-2 rounded-lg mr-3">
                <svg class="text-lg text-green-600 w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                </svg>
              </div>
              <h3 class="text-lg font-bold text-gray-900">Información Básica</h3>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label for="create-finca-nombre" class="block text-sm font-semibold text-gray-700 mb-2">
                  Nombre de la Finca *
                </label>
                <input
                  id="create-finca-nombre"
                  v-model="form.nombre"
                  type="text"
                  required
                  class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent transition-colors"
                  placeholder="Ingresa el nombre de la finca"
                />
              </div>

              <div v-if="auth.user?.role === 'admin'" class="col-span-1 md:col-span-2">
                <label for="create-finca-agricultor" class="block text-sm font-semibold text-gray-700 mb-2">
                  Agricultor asignado *
                </label>
                <select
                  id="create-finca-agricultor"
                  v-model="form.agricultor"
                  required
                  class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent transition-colors"
                >
                  <option value="">Selecciona un agricultor</option>
                  <option v-for="a in agricultores" :key="a.id" :value="a.id">
                    {{ a.username }}
                  </option>
                </select>
              </div>
            </div>
          </div>
        </div>

        <!-- Botones de acción -->
        <div class="flex items-center justify-end gap-3 mt-8 border-t border-gray-200 pt-6">
          <button
            type="button"
            @click="$emit('close')"
            class="px-6 py-3 bg-gray-200 hover:bg-gray-300 text-gray-700 rounded-lg transition-all duration-200 flex items-center gap-2 font-medium shadow-sm hover:shadow-md"
          >
            Cancelar
          </button>
          <button
            type="submit"
            :disabled="loading"
            class="px-6 py-3 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 font-medium shadow-sm hover:shadow-md"
          >
            <div v-if="loading" class="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
            <svg v-if="!loading" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
            </svg>
            {{ loading ? 'Guardando...' : 'Crear Finca' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useFincasStore } from '@/stores/fincas'
import { createFinca, getAgricultores } from '@/services/fincasApi'
import { useNotifications } from '@/composables/useNotifications'

const emit = defineEmits(['close', 'saved'])

const auth = useAuthStore()
const fincasStore = useFincasStore()
const { showSuccess, showError } = useNotifications()

const form = ref({ nombre: '', agricultor: '' })
const agricultores = ref([])
const loading = ref(false)

// Usamos SweetAlert2 para notificaciones
onMounted(async () => {
  if (auth.user?.role === 'admin') {
    try {
      const res = await getAgricultores()
      // El endpoint devuelve axios response; tomamos los resultados (paginados o no)
      const data = res.data
      if (Array.isArray(data?.results)) {
        agricultores.value = data.results
      } else if (Array.isArray(data)) {
        agricultores.value = data
      } else {
        agricultores.value = data?.results || []
      }
      } catch (e) {
      showError('No se pudo cargar la lista de agricultores')
    }
  }
})

const submitForm = async () => {
  loading.value = true
  try {
    await createFinca(form.value)
    showSuccess('Finca creada correctamente')
    form.value = { nombre: '', agricultor: '' }
    emit('saved')
  } catch (error) {
    showError('Error al crear la finca')
  } finally {
    loading.value = false
  }
}
</script>


