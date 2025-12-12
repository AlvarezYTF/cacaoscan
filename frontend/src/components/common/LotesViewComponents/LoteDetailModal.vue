<template>
  <div
    v-if="show"
    class="fixed inset-0 z-50 overflow-y-auto backdrop-blur-sm"
    aria-labelledby="modal-title"
    role="dialog"
    aria-modal="true"
    @click.self="close"
  >
    <!-- Backdrop -->
    <div class="fixed inset-0 bg-black/30 backdrop-blur-sm transition-opacity" @click="close"></div>

    <!-- Modal -->
    <div class="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">
      <div
        class="relative transform overflow-hidden rounded-2xl bg-white text-left shadow-2xl transition-all sm:my-8 sm:w-full sm:max-w-5xl max-h-[90vh] flex flex-col"
        @click.stop
      >
        <!-- Header mejorado -->
        <div class="bg-gradient-to-r from-green-50 to-green-50 px-6 py-5 border-b border-gray-200">
          <div class="flex items-start justify-between">
            <div class="flex items-center gap-4">
              <div class="bg-green-100 p-3 rounded-xl">
                <i class="fas fa-seedling text-green-600 text-2xl"></i>
              </div>
              <div>
                <h3 class="text-2xl font-bold text-gray-900" id="modal-title">
                  {{ lote?.identificador || lote?.nombre || 'Detalle de Lote' }}
                </h3>
                <div class="flex items-center gap-3 mt-2">
                  <p class="text-sm text-gray-600 flex items-center gap-1.5">
                    <i class="fas fa-map-marker-alt text-green-600"></i>
                    <span v-if="finca?.nombre">{{ finca.nombre }}</span>
                    <span v-else-if="lote?.finca_nombre">{{ lote.finca_nombre }}</span>
                    <span v-else-if="loading">Cargando...</span>
                  </p>
                  <span
                    v-if="lote?.estado"
                    class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold transition-all"
                    :class="getEstadoBadgeClass(lote)"
                  >
                    <i 
                      :class="{
                        'fas fa-check-circle': getEstadoDisplay(lote).toLowerCase() === 'activo',
                        'fas fa-pause-circle': getEstadoDisplay(lote).toLowerCase() === 'inactivo',
                        'fas fa-check-double': getEstadoDisplay(lote).toLowerCase().includes('cosecha')
                      }"
                    ></i>
                    {{ getEstadoDisplay(lote) }}
                  </span>
                </div>
              </div>
            </div>
            <button
              type="button"
              class="text-gray-400 hover:text-gray-600 transition-all duration-200 p-2 rounded-lg hover:bg-gray-100"
              @click="close"
            >
              <span class="sr-only">Cerrar</span>
              <i class="fas fa-times text-xl"></i>
            </button>
          </div>
        </div>

        <!-- Content -->
        <div class="bg-white px-6 py-6 overflow-y-auto flex-1">
          <!-- Loading State -->
          <div v-if="loading" class="flex flex-col items-center justify-center py-16">
            <div class="relative">
              <svg class="animate-spin h-12 w-12 text-green-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            </div>
            <p class="mt-4 text-gray-600 font-medium">Cargando información del lote...</p>
          </div>

          <!-- Error State -->
          <div v-else-if="error" class="bg-red-50 border-l-4 border-red-500 rounded-r-lg p-4 mb-4">
            <div class="flex items-start">
              <div class="flex-shrink-0">
                <i class="fas fa-exclamation-circle text-red-400 text-xl"></i>
              </div>
              <div class="ml-3 flex-1">
                <h3 class="text-sm font-semibold text-red-800">Error al cargar el lote</h3>
                <p class="mt-1 text-sm text-red-700">{{ error }}</p>
                <button
                  @click="loadLoteData"
                  class="mt-3 text-sm text-red-600 hover:text-red-800 underline font-medium"
                >
                  Intentar nuevamente
                </button>
              </div>
            </div>
          </div>

          <!-- Lote Information -->
          <div v-else-if="lote" class="space-y-6">
            <!-- Estadísticas mejoradas con cards individuales -->
            <div class="border-b border-gray-200 pb-6">
              <h3 class="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
                <svg class="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
                </svg>
                Estadísticas
              </h3>
              <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                <!-- Card: Análisis Realizados -->
                <div class="bg-blue-50 rounded-xl p-5 border border-blue-200 hover:shadow-md transition-all duration-200 text-center group">
                  <div class="flex justify-center mb-2">
                    <div class="bg-blue-100 p-2 rounded-lg group-hover:scale-110 transition-transform duration-200">
                      <i class="fas fa-microscope text-blue-600 text-lg"></i>
                    </div>
                  </div>
                  <div class="text-3xl font-bold text-blue-600 mb-1">
                    {{ statistics.find(s => s.label === 'Análisis Realizados')?.value || 0 }}
                  </div>
                  <div class="text-xs font-semibold text-gray-600 uppercase tracking-wider">Análisis Realizados</div>
                </div>

                <!-- Card: Análisis Exitosos -->
                <div class="bg-green-50 rounded-xl p-5 border border-green-200 hover:shadow-md transition-all duration-200 text-center group">
                  <div class="flex justify-center mb-2">
                    <div class="bg-green-100 p-2 rounded-lg group-hover:scale-110 transition-transform duration-200">
                      <i class="fas fa-check-circle text-green-600 text-lg"></i>
                    </div>
                  </div>
                  <div class="text-3xl font-bold text-green-600 mb-1">
                    {{ statistics.find(s => s.label === 'Análisis Exitosos')?.value || 0 }}
                  </div>
                  <div class="text-xs font-semibold text-gray-600 uppercase tracking-wider">Análisis Exitosos</div>
                </div>

                <!-- Card: Calidad Promedio -->
                <div class="bg-yellow-50 rounded-xl p-5 border border-yellow-200 hover:shadow-md transition-all duration-200 text-center group">
                  <div class="flex justify-center mb-2">
                    <div class="bg-yellow-100 p-2 rounded-lg group-hover:scale-110 transition-transform duration-200">
                      <i class="fas fa-star text-yellow-600 text-lg"></i>
                    </div>
                  </div>
                  <div class="text-3xl font-bold text-yellow-600 mb-1">
                    {{ statistics.find(s => s.label === 'Calidad Promedio')?.value || '0%' }}
                  </div>
                  <div class="text-xs font-semibold text-gray-600 uppercase tracking-wider">Calidad Promedio</div>
                </div>

                <!-- Card: Último Análisis -->
                <div class="bg-purple-50 rounded-xl p-5 border border-purple-200 hover:shadow-md transition-all duration-200 text-center group">
                  <div class="flex justify-center mb-2">
                    <div class="bg-purple-100 p-2 rounded-lg group-hover:scale-110 transition-transform duration-200">
                      <i class="fas fa-clock text-purple-600 text-lg"></i>
                    </div>
                  </div>
                  <div class="text-lg font-bold text-purple-600 mb-1">
                    {{ statistics.find(s => s.label === 'Último Análisis')?.value || 'N/A' }}
                  </div>
                  <div class="text-xs font-semibold text-gray-600 uppercase tracking-wider">Último Análisis</div>
                </div>
              </div>
            </div>

            <!-- Información principal en cards mejoradas -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <!-- Card: Variedad -->
              <div class="bg-gray-50 rounded-2xl p-6 border border-gray-200 hover:shadow-md transition-all duration-200">
                <div class="flex items-start gap-4">
                  <div class="bg-green-100 p-3 rounded-xl flex-shrink-0">
                    <i class="fas fa-leaf text-green-600 text-xl"></i>
                  </div>
                  <div class="flex-1 min-w-0">
                    <h3 class="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Variedad</h3>
                    <p class="text-gray-900 font-medium text-base">{{ variedadDisplay || 'N/A' }}</p>
                  </div>
                </div>
              </div>

              <!-- Card: Peso -->
              <div class="bg-gray-50 rounded-2xl p-6 border border-gray-200 hover:shadow-md transition-all duration-200">
                <div class="flex items-start gap-4">
                  <div class="bg-green-100 p-3 rounded-xl flex-shrink-0">
                    <i class="fas fa-weight text-green-600 text-xl"></i>
                  </div>
                  <div class="flex-1 min-w-0">
                    <h3 class="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Peso</h3>
                    <p class="text-gray-900 font-medium text-base">{{ lote?.peso_kg || 0 }} <span class="text-gray-600 text-sm">kg</span></p>
                  </div>
                </div>
              </div>

              <!-- Card: Finca -->
              <div class="bg-gray-50 rounded-2xl p-6 border border-gray-200 hover:shadow-md transition-all duration-200">
                <div class="flex items-start gap-4">
                  <div class="bg-green-100 p-3 rounded-xl flex-shrink-0">
                    <i class="fas fa-map-marker-alt text-green-600 text-xl"></i>
                  </div>
                  <div class="flex-1 min-w-0">
                    <h3 class="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Finca</h3>
                    <p class="text-gray-900 font-medium text-base">
                      <router-link
                        v-if="finca?.id"
                        :to="`/fincas/${finca.id}`"
                        class="text-green-600 hover:text-green-800 underline"
                        @click="close"
                      >
                        {{ finca.nombre || 'N/A' }}
                      </router-link>
                      <span v-else-if="lote?.finca_nombre">{{ lote.finca_nombre }}</span>
                      <span v-else>N/A</span>
                    </p>
                  </div>
                </div>
              </div>

              <!-- Card: Fecha de Recepción -->
              <div class="bg-gray-50 rounded-2xl p-6 border border-gray-200 hover:shadow-md transition-all duration-200">
                <div class="flex items-start gap-4">
                  <div class="bg-green-100 p-3 rounded-xl flex-shrink-0">
                    <i class="fas fa-calendar-check text-green-600 text-xl"></i>
                  </div>
                  <div class="flex-1 min-w-0">
                    <h3 class="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Fecha de Recepción</h3>
                    <p class="text-gray-900 font-medium text-base">{{ formatDate(lote?.fecha_recepcion) }}</p>
                  </div>
                </div>
              </div>

              <!-- Card: Fecha de Plantación (si existe) -->
              <div v-if="lote?.fecha_plantacion" class="bg-gray-50 rounded-2xl p-6 border border-gray-200 hover:shadow-md transition-all duration-200">
                <div class="flex items-start gap-4">
                  <div class="bg-green-100 p-3 rounded-xl flex-shrink-0">
                    <i class="fas fa-seedling text-green-600 text-xl"></i>
                  </div>
                  <div class="flex-1 min-w-0">
                    <h3 class="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Fecha de Plantación</h3>
                    <p class="text-gray-900 font-medium text-base">{{ formatDate(lote?.fecha_plantacion) }}</p>
                  </div>
                </div>
              </div>

              <!-- Card: Fecha de Cosecha (si existe) -->
              <div v-if="lote?.fecha_cosecha" class="bg-gray-50 rounded-2xl p-6 border border-gray-200 hover:shadow-md transition-all duration-200">
                <div class="flex items-start gap-4">
                  <div class="bg-green-100 p-3 rounded-xl flex-shrink-0">
                    <i class="fas fa-hands-helping text-green-600 text-xl"></i>
                  </div>
                  <div class="flex-1 min-w-0">
                    <h3 class="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Fecha de Cosecha</h3>
                    <p class="text-gray-900 font-medium text-base">{{ formatDate(lote?.fecha_cosecha) }}</p>
                  </div>
                </div>
              </div>

              <!-- Card: Fecha de Procesamiento (si existe) -->
              <div v-if="lote?.fecha_procesamiento" class="bg-gray-50 rounded-2xl p-6 border border-gray-200 hover:shadow-md transition-all duration-200">
                <div class="flex items-start gap-4">
                  <div class="bg-green-100 p-3 rounded-xl flex-shrink-0">
                    <i class="fas fa-cogs text-green-600 text-xl"></i>
                  </div>
                  <div class="flex-1 min-w-0">
                    <h3 class="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Fecha de Procesamiento</h3>
                    <p class="text-gray-900 font-medium text-base">{{ formatDate(lote?.fecha_procesamiento) }}</p>
                  </div>
                </div>
              </div>

              <!-- Card: Fecha de Registro -->
              <div class="bg-gray-50 rounded-2xl p-6 border border-gray-200 hover:shadow-md transition-all duration-200">
                <div class="flex items-start gap-4">
                  <div class="bg-green-100 p-3 rounded-xl flex-shrink-0">
                    <i class="fas fa-calendar-plus text-green-600 text-xl"></i>
                  </div>
                  <div class="flex-1 min-w-0">
                    <h3 class="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Fecha de Registro</h3>
                    <p class="text-gray-900 font-medium text-base">{{ formatDate(lote?.fecha_registro || lote?.created_at) }}</p>
                  </div>
                </div>
              </div>
            </div>

            <!-- Descripción en card destacada -->
            <div v-if="lote?.descripcion" class="bg-green-50 rounded-2xl p-6 border border-green-200">
              <div class="flex items-start gap-4">
                <div class="bg-green-100 p-3 rounded-xl flex-shrink-0">
                  <i class="fas fa-file-alt text-green-600 text-xl"></i>
                </div>
                <div class="flex-1">
                  <h3 class="text-sm font-semibold text-gray-700 uppercase tracking-wider mb-2">Descripción</h3>
                  <p class="text-gray-700 leading-relaxed">{{ lote.descripcion }}</p>
                </div>
              </div>
            </div>

            <!-- Análisis Recientes -->
            <div v-if="analisisRecientes.length > 0" class="border-t border-gray-200 pt-6">
              <h3 class="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
                <i class="fas fa-history text-green-600"></i>
                Análisis Recientes
              </h3>
              <div class="space-y-3">
                <div
                  v-for="analisis in analisisRecientes"
                  :key="analisis.id"
                  class="bg-white rounded-xl p-4 border border-gray-200 hover:shadow-md transition-all duration-200"
                >
                  <div class="flex items-center justify-between">
                    <div class="flex items-center gap-4">
                      <div 
                        class="p-3 rounded-lg"
                        :class="{
                          'bg-green-100': analisis.calidad >= 80,
                          'bg-yellow-100': analisis.calidad >= 60 && analisis.calidad < 80,
                          'bg-red-100': analisis.calidad < 60
                        }"
                      >
                        <i 
                          class="fas fa-microscope text-lg"
                          :class="{
                            'text-green-600': analisis.calidad >= 80,
                            'text-yellow-600': analisis.calidad >= 60 && analisis.calidad < 80,
                            'text-red-600': analisis.calidad < 60
                          }"
                        ></i>
                      </div>
                      <div>
                        <p class="text-sm font-semibold text-gray-900">
                          {{ formatDate(analisis.fecha_analisis) }}
                        </p>
                        <p class="text-xs text-gray-500 mt-1">{{ analisis.tipo_analisis || 'Análisis de Imagen' }}</p>
                      </div>
                    </div>
                    <span
                      class="inline-flex items-center px-4 py-2 rounded-full text-sm font-semibold"
                      :class="{
                        'bg-green-100 text-green-800': analisis.calidad >= 80,
                        'bg-yellow-100 text-yellow-800': analisis.calidad >= 60 && analisis.calidad < 80,
                        'bg-red-100 text-red-800': analisis.calidad < 60
                      }"
                    >
                      {{ analisis.calidad }}%
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Footer Actions mejorado -->
        <div class="bg-gray-50 px-6 py-4 border-t border-gray-200 flex items-center justify-between gap-3">
          <div class="text-sm text-gray-600">
            <span class="font-medium">ID:</span> {{ lote?.id || 'N/A' }}
          </div>
          <div class="flex items-center gap-3">
            <button
              type="button"
              class="px-5 py-2.5 bg-green-600 hover:bg-green-700 text-white rounded-xl text-sm font-semibold transition-all duration-200 flex items-center gap-2 shadow-md hover:shadow-lg hover:scale-[1.02] active:scale-[0.98] focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2"
              @click="analyzeLote"
            >
              <i class="fas fa-microscope"></i>
              Realizar Análisis
            </button>
            <button
              v-if="(lote?.total_analisis || 0) > 0"
              type="button"
              class="px-5 py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-sm font-semibold transition-all duration-200 flex items-center gap-2 shadow-md hover:shadow-lg hover:scale-[1.02] active:scale-[0.98] focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
              @click="viewAnalisis"
            >
              <i class="fas fa-chart-line"></i>
              Ver Análisis
            </button>
            <button
              v-if="canEdit"
              type="button"
              class="px-5 py-2.5 bg-yellow-600 hover:bg-yellow-700 text-white rounded-xl text-sm font-semibold transition-all duration-200 flex items-center gap-2 shadow-md hover:shadow-lg hover:scale-[1.02] active:scale-[0.98] focus:outline-none focus:ring-2 focus:ring-yellow-500 focus:ring-offset-2"
              @click="editLote"
            >
              <i class="fas fa-edit"></i>
              Editar
            </button>
            <button
              type="button"
              class="px-5 py-2.5 bg-gray-200 hover:bg-gray-300 text-gray-700 rounded-xl text-sm font-semibold transition-all duration-200 shadow-sm hover:shadow-md hover:scale-[1.02] active:scale-[0.98] focus:outline-none focus:ring-2 focus:ring-gray-400 focus:ring-offset-2"
              @click="close"
            >
              Cerrar
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useDateFormatting } from '@/composables/useDateFormatting'
import { useAuthStore } from '@/stores/auth'
import api from '@/services/api'
import * as lotesApi from '@/services/lotesApi'
import { getFincaById } from '@/services/fincasApi'

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  loteId: {
    type: [Number, String],
    default: null
  }
})

const emit = defineEmits(['close'])

const router = useRouter()

// Use composables
const { formatDate } = useDateFormatting()
const authStore = useAuthStore()

// Local state - use local state instead of shared composable state
const loading = ref(false)
const error = ref(null)
const lote = ref(null)
const finca = ref(null)
const analisisRecientes = ref([])

// Computed
const canEdit = computed(() => {
  if (!lote.value) return false
  if (authStore.userRole === 'admin') return true
  if ((authStore.userRole === 'farmer' || authStore.userRole === 'agricultor') && lote.value.finca) {
    const fincaData = typeof lote.value.finca === 'object' ? lote.value.finca : finca.value
    if (fincaData) {
      return fincaData.agricultor === authStore.user?.id || fincaData.agricultor_id === authStore.user?.id
    }
  }
  return false
})

const variedadDisplay = computed(() => {
  const variedad = lote.value?.variedad
  if (!variedad) return null
  if (typeof variedad === 'object' && variedad.nombre) {
    return variedad.nombre
  }
  if (typeof variedad === 'object' && variedad.codigo) {
    return variedad.codigo
  }
  if (typeof variedad === 'string') {
    return variedad
  }
  return String(variedad)
})

const statistics = computed(() => {
  if (!lote.value) {
    return [
      {
        label: 'Análisis Realizados',
        value: 0,
        color: 'primary'
      },
      {
        label: 'Análisis Exitosos',
        value: 0,
        color: 'success'
      },
      {
        label: 'Calidad Promedio',
        value: '0%',
        color: 'info'
      },
      {
        label: 'Último Análisis',
        value: 'N/A',
        color: 'warning'
      }
    ]
  }

  const stats = lote.value.estadisticas || {}
  const totalAnalisis = stats.total_analisis ?? lote.value.total_analisis ?? 0
  const analisisProcesados = stats.analisis_procesados ?? lote.value.analisis_procesados ?? lote.value.analisis_exitosos ?? 0
  const calidadPromedio = stats.calidad_promedio ?? lote.value.promedio_calidad ?? 0
  const ultimoAnalisis = lote.value.ultimo_analisis || 'N/A'

  return [
    {
      label: 'Análisis Realizados',
      value: totalAnalisis,
      color: 'primary'
    },
    {
      label: 'Análisis Exitosos',
      value: analisisProcesados,
      color: 'success'
    },
    {
      label: 'Calidad Promedio',
      value: calidadPromedio ? `${calidadPromedio}%` : '0%',
      color: 'info'
    },
    {
      label: 'Último Análisis',
      value: ultimoAnalisis,
      color: 'warning'
    }
  ]
})

// Methods
const close = () => {
  emit('close')
}

const loadLoteData = async () => {
  if (!props.loteId) {
    console.warn('[LoteDetailModal] No loteId provided')
    return
  }

  try {
    loading.value = true
    error.value = null
    
    console.log('[LoteDetailModal] Loading lote:', props.loteId)
    const loteIdNum = Number(props.loteId)
    const data = await lotesApi.getLoteById(loteIdNum)
    lote.value = data
    
    console.log('[LoteDetailModal] Lote loaded:', lote.value)
    
    // Load finca if included or referenced
    if (data.finca) {
      if (typeof data.finca === 'object') {
        finca.value = data.finca
      } else {
        // Load finca separately if only ID provided
        try {
          finca.value = await getFincaById(data.finca)
        } catch (err) {
          console.warn('[LoteDetailModal] Could not load finca:', err)
        }
      }
    }
    
    await loadAnalisisRecientes()
  } catch (err) {
    console.error('[LoteDetailModal] Error loading lote:', err)
    let errorMessage = 'Error al cargar el lote'
    
    if (err.code === 'ERR_NETWORK' || err.message === 'Network Error' || err.message?.includes('CONNECTION_REFUSED')) {
      errorMessage = 'No se pudo conectar al servidor. Asegúrate de que el backend esté corriendo en http://localhost:8000'
    } else if (err.response) {
      if (err.response.status === 500) {
        errorMessage = err.response.data?.error || err.response.data?.detail || 'Error interno del servidor'
      } else if (err.response.data?.detail) {
        errorMessage = err.response.data.detail
      } else if (err.response.data?.error) {
        errorMessage = err.response.data.error
      } else {
        errorMessage = `Error ${err.response.status}: ${err.response.statusText}`
      }
    } else if (err.message) {
      errorMessage = err.message
    }
    
    error.value = errorMessage
  } finally {
    loading.value = false
  }
}

const loadAnalisisRecientes = async () => {
  if (!lote.value?.id) return

  try {
    const response = await api.get(`/lotes/${lote.value.id}/analisis/`)
    analisisRecientes.value = response.data.results?.slice(0, 5) || []
  } catch (err) {
    analisisRecientes.value = []
  }
}

const getEstadoDisplay = (loteData) => {
  if (!loteData) return 'N/A'
  if (loteData.estado_display) {
    return String(loteData.estado_display)
  }
  if (loteData.estado) {
    if (typeof loteData.estado === 'object' && loteData.estado.nombre) {
      return String(loteData.estado.nombre)
    }
    if (typeof loteData.estado === 'string') {
      return loteData.estado
    }
  }
  return 'N/A'
}

const getEstadoBadgeClass = (loteData) => {
  const estado = getEstadoDisplay(loteData).toLowerCase()
  if (estado === 'activo' || estado === 'active') {
    return 'bg-green-100 text-green-700 border border-green-200'
  }
  if (estado === 'inactivo' || estado === 'inactive') {
    return 'bg-gray-100 text-gray-700 border border-gray-200'
  }
  if (estado === 'cosechado' || estado === 'harvested' || estado.includes('cosecha')) {
    return 'bg-blue-100 text-blue-700 border border-blue-200'
  }
  return 'bg-gray-100 text-gray-700 border border-gray-200'
}

const editLote = () => {
  if (lote.value?.id) {
    close()
    router.push(`/lotes/${lote.value.id}/edit`)
  }
}

const analyzeLote = () => {
  if (lote.value?.id) {
    close()
    router.push(`/analisis?lote=${lote.value.id}`)
  }
}

const viewAnalisis = () => {
  if (lote.value?.id) {
    close()
    router.push(`/lotes/${lote.value.id}/analisis`)
  }
}

// Watch for loteId and show changes
watch([() => props.loteId, () => props.show], ([newId, newShow], [oldId, oldShow]) => {
  // Only load if modal is opening with a new loteId
  if (newShow && newId && (newId !== oldId || !oldShow)) {
    loadLoteData()
  } else if (!newShow && oldShow) {
    // Clear data when modal closes
    lote.value = null
    finca.value = null
    analisisRecientes.value = []
    error.value = null
    loading.value = false
  }
}, { immediate: true })
</script>

<style scoped>
.animate-spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>
