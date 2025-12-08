<template>
  <BaseModal
    :show="show"
    :title="fincaDetalle ? fincaDetalle.nombre : 'Detalles de la Finca'"
    subtitle="Información completa de la finca"
    max-width="5xl"
    @close="closeModal"
  >
    <!-- Loading state -->
    <div v-if="loading" class="flex flex-col items-center justify-center p-16">
      <div class="relative">
        <svg class="animate-spin h-12 w-12 text-green-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
      </div>
      <p class="mt-4 text-gray-600 font-medium">Cargando información de la finca...</p>
    </div>

    <template #header>
      <div v-if="fincaDetalle" class="flex items-center justify-between w-full">
        <div class="flex items-center gap-3">
          <div class="bg-green-100 p-2 rounded-xl">
            <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path>
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path>
            </svg>
          </div>
          <div>
            <h2 class="text-3xl font-bold text-gray-900">{{ fincaDetalle.nombre }}</h2>
            <div class="flex items-center gap-3 mt-2">
              <p class="text-sm text-gray-600 flex items-center gap-1.5">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path>
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path>
                </svg>
                {{ fincaDetalle.municipio }}, {{ fincaDetalle.departamento }}
              </p>
              <span
                :class="[
                  'inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold transition-all',
                  fincaDetalle.activa 
                    ? 'bg-green-100 text-green-700 border border-green-200' 
                    : 'bg-red-100 text-red-700 border border-red-200'
                ]"
              >
                <svg 
                  v-if="fincaDetalle.activa" 
                  class="w-3 h-3" 
                  fill="currentColor" 
                  viewBox="0 0 20 20"
                >
                  <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path>
                </svg>
                <svg 
                  v-else 
                  class="w-3 h-3" 
                  fill="currentColor" 
                  viewBox="0 0 20 20"
                >
                  <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"></path>
                </svg>
                {{ fincaDetalle.activa ? 'Activa' : 'Inactiva' }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </template>

    <!-- Contenido principal -->
    <div v-if="!loading && fincaDetalle" class="overflow-hidden">
      <div class="space-y-6">
                <!-- Información principal en cards mejoradas -->
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <!-- Card de ubicación -->
                  <div class="bg-gray-50 rounded-2xl p-6 border border-gray-200 hover:shadow-md transition-all duration-200">
                    <div class="flex items-start gap-4">
                      <div class="bg-green-100 p-3 rounded-xl flex-shrink-0">
                        <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path>
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path>
                        </svg>
                      </div>
                      <div class="flex-1 min-w-0">
                        <h3 class="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Ubicación</h3>
                        <p class="text-gray-900 font-medium text-base">{{ fincaDetalle.ubicacion }}</p>
                      </div>
                    </div>
                  </div>

                  <!-- Card de agricultor -->
                  <div class="bg-gray-50 rounded-2xl p-6 border border-gray-200 hover:shadow-md transition-all duration-200">
                    <div class="flex items-start gap-4">
                      <div class="bg-green-100 p-3 rounded-xl flex-shrink-0">
                        <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
                        </svg>
                      </div>
                      <div class="flex-1 min-w-0">
                        <h3 class="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Agricultor</h3>
                        <p class="text-gray-900 font-medium text-base">{{ fincaDetalle.agricultor_name || 'N/A' }}</p>
                      </div>
                    </div>
                  </div>

                  <!-- Card de área -->
                  <div class="bg-gray-50 rounded-2xl p-6 border border-gray-200 hover:shadow-md transition-all duration-200">
                    <div class="flex items-start gap-4">
                      <div class="bg-green-100 p-3 rounded-xl flex-shrink-0">
                        <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4"></path>
                        </svg>
                      </div>
                      <div class="flex-1 min-w-0">
                        <h3 class="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Área</h3>
                        <p class="text-gray-900 font-medium text-base">{{ fincaDetalle.hectareas }} <span class="text-gray-600 text-sm">hectáreas</span></p>
                      </div>
                    </div>
                  </div>

                  <!-- Card de fecha de registro -->
                  <div class="bg-gray-50 rounded-2xl p-6 border border-gray-200 hover:shadow-md transition-all duration-200">
                    <div class="flex items-start gap-4">
                      <div class="bg-green-100 p-3 rounded-xl flex-shrink-0">
                        <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                        </svg>
                      </div>
                      <div class="flex-1 min-w-0">
                        <h3 class="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Fecha de Registro</h3>
                        <p class="text-gray-900 font-medium text-base">
                          {{ fincaDetalle.fecha_registro ? new Date(fincaDetalle.fecha_registro).toLocaleDateString('es-CO', { year: 'numeric', month: 'long', day: 'numeric' }) : 'N/A' }}
                        </p>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Descripción en card destacada -->
                <div v-if="fincaDetalle.descripcion" class="bg-green-50 rounded-2xl p-6 border border-green-200">
                  <div class="flex items-start gap-4">
                    <div class="bg-green-100 p-3 rounded-xl flex-shrink-0">
                      <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                      </svg>
                    </div>
                    <div class="flex-1">
                      <h3 class="text-sm font-semibold text-gray-700 uppercase tracking-wider mb-2">Descripción</h3>
                      <p class="text-gray-700 leading-relaxed">{{ fincaDetalle.descripcion }}</p>
                    </div>
                  </div>
                </div>

                <!-- Mapa de ubicación con card wrapper -->
                <div class="bg-white rounded-2xl border border-gray-200 overflow-hidden shadow-sm">
                  <FincaLocationMap
                    :nombre="fincaDetalle.nombre"
                    :latitud="fincaDetalle.coordenadas_lat"
                    :longitud="fincaDetalle.coordenadas_lng"
                  />
                </div>

                <!-- Estadísticas mejoradas con cards individuales y iconos -->
                <div class="border-t border-gray-200 pt-6">
                  <h3 class="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
                    <svg class="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
                    </svg>
                    Estadísticas
                  </h3>
                  <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <!-- Card: Total Lotes -->
                    <div class="bg-blue-50 rounded-xl p-5 border border-blue-200 hover:shadow-md transition-all duration-200 text-center group">
                      <div class="flex justify-center mb-2">
                        <div class="bg-blue-100 p-2 rounded-lg group-hover:scale-110 transition-transform duration-200">
                          <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 10h16M4 14h16M4 18h16"></path>
                          </svg>
                        </div>
                      </div>
                      <div class="text-3xl font-bold text-blue-600 mb-1">{{ fincaDetalle.estadisticas?.total_lotes || 0 }}</div>
                      <div class="text-xs font-semibold text-gray-600 uppercase tracking-wider">Total de Lotes</div>
                    </div>

                    <!-- Card: Lotes Activos -->
                    <div class="bg-green-50 rounded-xl p-5 border border-green-200 hover:shadow-md transition-all duration-200 text-center group">
                      <div class="flex justify-center mb-2">
                        <div class="bg-green-100 p-2 rounded-lg group-hover:scale-110 transition-transform duration-200">
                          <svg class="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                          </svg>
                        </div>
                      </div>
                      <div class="text-3xl font-bold text-green-600 mb-1">{{ fincaDetalle.estadisticas?.lotes_activos || 0 }}</div>
                      <div class="text-xs font-semibold text-gray-600 uppercase tracking-wider">Lotes Activos</div>
                    </div>

                    <!-- Card: Análisis -->
                    <div class="bg-purple-50 rounded-xl p-5 border border-purple-200 hover:shadow-md transition-all duration-200 text-center group">
                      <div class="flex justify-center mb-2">
                        <div class="bg-purple-100 p-2 rounded-lg group-hover:scale-110 transition-transform duration-200">
                          <svg class="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
                          </svg>
                        </div>
                      </div>
                      <div class="text-3xl font-bold text-purple-600 mb-1">{{ fincaDetalle.estadisticas?.total_analisis || 0 }}</div>
                      <div class="text-xs font-semibold text-gray-600 uppercase tracking-wider">Análisis</div>
                    </div>

                    <!-- Card: Calidad Promedio -->
                    <div class="bg-yellow-50 rounded-xl p-5 border border-yellow-200 hover:shadow-md transition-all duration-200 text-center group">
                      <div class="flex justify-center mb-2">
                        <div class="bg-yellow-100 p-2 rounded-lg group-hover:scale-110 transition-transform duration-200">
                          <svg class="w-5 h-5 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z"></path>
                          </svg>
                        </div>
                      </div>
                      <div class="text-3xl font-bold text-yellow-600 mb-1">{{ fincaDetalle.estadisticas?.calidad_promedio || 0 }}%</div>
                      <div class="text-xs font-semibold text-gray-600 uppercase tracking-wider">Calidad Promedio</div>
                    </div>
                  </div>
                </div>
      </div>
    </div>

    <template #footer>
      <div class="flex items-center justify-between gap-3 w-full">
        <div class="text-sm text-gray-600">
          <span class="font-medium">ID:</span> {{ fincaDetalle?.id }}
        </div>
        <div class="flex items-center gap-3">
          <button
            @click="handleEdit"
            v-if="fincaDetalle && (fincaDetalle.activa || userRole === 'admin')"
            type="button"
            class="px-5 py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-sm font-semibold transition-all duration-200 flex items-center gap-2 shadow-md hover:shadow-lg hover:scale-[1.02] active:scale-[0.98] focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
            </svg>
            Editar
          </button>
          <button
            @click="handleViewLotes"
            v-if="fincaDetalle && (fincaDetalle.activa || userRole === 'admin')"
            type="button"
            class="px-5 py-2.5 bg-green-600 hover:bg-green-700 text-white rounded-xl text-sm font-semibold transition-all duration-200 flex items-center gap-2 shadow-md hover:shadow-lg hover:scale-[1.02] active:scale-[0.98] focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2"
          >
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 10h16M4 14h16M4 18h16"></path>
            </svg>
            Ver Lotes
          </button>
          <button
            @click="closeModal"
            type="button"
            class="px-5 py-2.5 bg-gray-200 hover:bg-gray-300 text-gray-700 rounded-xl text-sm font-semibold transition-all duration-200 shadow-sm hover:shadow-md hover:scale-[1.02] active:scale-[0.98] focus:outline-none focus:ring-2 focus:ring-gray-400 focus:ring-offset-2"
          >
            Cerrar
          </button>
        </div>
      </div>
    </template>
  </BaseModal>
</template>

<script setup>
// 1. Vue core
import { watch } from 'vue'

// 2. Stores
import { useAuthStore } from '@/stores/auth'

// 3. Components
import FincaLocationMap from '@/components/fincas/FincaLocationMap.vue'
import BaseModal from '@/components/common/BaseModal.vue'

// 4. Composables
import { useFincas } from '@/composables/useFincas'

// Props
const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  finca: {
    type: Object,
    default: null
  },
  userRole: {
    type: String,
    default: 'agricultor'
  }
})

// Emits
const emit = defineEmits(['close', 'edit', 'view-lotes'])

// Stores
const authStore = useAuthStore()

// Use fincas composable
const { currentFinca: fincaDetalle, isLoading: loading, loadFinca, clearCurrentFinca } = useFincas()

// Methods
const loadFincaDetails = async (fincaId) => {
  if (!fincaId) return
  try {
    await loadFinca(fincaId)
  } catch (error) {
    }
}

const closeModal = () => {
  emit('close')
  // Reset después de un pequeño delay para la animación
  setTimeout(() => {
    clearCurrentFinca()
  }, 300)
}

const handleEdit = () => {
  emit('edit', fincaDetalle.value)
  closeModal()
}

const handleViewLotes = () => {
  emit('view-lotes', fincaDetalle.value)
  closeModal()
}

// Watch para cargar detalles cuando cambie la finca
watch(() => props.finca, (newFinca) => {
  if (newFinca && props.show) {
    loadFincaDetails(newFinca.id)
  }
}, { immediate: true })

// Watch para cargar cuando se muestra el modal
watch(() => props.show, (isShowing) => {
  if (isShowing && props.finca) {
    loadFincaDetails(props.finca.id)
  }
})
</script>

<style scoped>
/* Animaciones mejoradas para el modal */
/* Las transiciones están manejadas por Vue Transition component */
</style>
