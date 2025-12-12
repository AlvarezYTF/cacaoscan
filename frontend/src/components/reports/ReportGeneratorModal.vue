<template>
  <div
    v-if="true"
    class="fixed inset-0 z-50 overflow-y-auto backdrop-blur-sm"
    aria-labelledby="modal-title"
    role="dialog"
    aria-modal="true"
    @click.self="closeModal"
  >
    <!-- Backdrop -->
    <div class="fixed inset-0 bg-black/30 backdrop-blur-sm transition-opacity" @click="closeModal"></div>

    <!-- Modal -->
    <div class="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">
      <div
        class="relative transform overflow-hidden rounded-2xl bg-white text-left shadow-2xl transition-all sm:my-8 sm:w-full sm:max-w-5xl max-h-[90vh] flex flex-col"
        @click.stop
      >
        <!-- Header -->
        <div class="bg-gradient-to-r from-green-50 to-green-50 px-6 py-5 border-b border-gray-200">
          <div class="flex items-start justify-between">
            <div class="flex items-center gap-4">
              <div class="bg-green-100 p-3 rounded-xl">
                <i class="fas fa-chart-bar text-green-600 text-2xl"></i>
              </div>
              <div>
                <h3 class="text-2xl font-bold text-gray-900" id="modal-title">
                  Generar Nuevo Reporte
                </h3>
                <p class="text-sm text-gray-600 mt-1">
                  Configura los parámetros para generar tu reporte personalizado
                </p>
              </div>
            </div>
            <button
              type="button"
              class="text-gray-400 hover:text-gray-600 transition-all duration-200 p-2 rounded-lg hover:bg-gray-100"
              @click="closeModal"
            >
              <span class="sr-only">Cerrar</span>
              <i class="fas fa-times text-xl"></i>
            </button>
          </div>
        </div>

        <!-- Content -->
        <div class="bg-white px-6 py-6 overflow-y-auto flex-1">
        <!-- Indicador de progreso -->
        <div class="progress-indicator">
          <div class="progress-steps">
            <div 
              v-for="(step, index) in steps" 
              :key="index"
              class="progress-step"
              :class="{ 
                'active': currentStep === index + 1,
                'completed': currentStep > index + 1,
                'disabled': currentStep < index + 1
              }"
            >
              <div class="step-number">
                <i v-if="currentStep > index + 1" class="fas fa-check"></i>
                <span v-else>{{ index + 1 }}</span>
              </div>
              <div class="step-label">{{ step.label }}</div>
            </div>
          </div>
        </div>

        <form @submit.prevent="generateReport" class="report-form">
          <!-- Paso 1: Tipo y Formato -->
          <div v-if="currentStep === 1" class="step-content">
            <div class="step-header">
              <h4>
                <i class="fas fa-cog"></i>
                Tipo y Formato
              </h4>
              <p>Selecciona el tipo de reporte y el formato de salida</p>
            </div>
            
            <div class="form-grid">
              <div class="form-group">
                <label for="tipo_reporte" class="form-label required">
                  Tipo de Reporte
                </label>
                <select 
                  id="tipo_reporte"
                  v-model="formData.tipo_reporte"
                  :class="{ 'error': errors.tipo_reporte }"
                  @change="onTypeChange"
                  class="form-select"
                  required
                >
                  <option value="">Seleccionar tipo</option>
                  <option value="CALIDAD">Reporte de Calidad</option>
                  <option value="FINCA">Reporte de Finca</option>
                  <option value="LOTE">Reporte de Lote</option>
                  <option value="USUARIO">Reporte de Usuario</option>
                  <option value="AUDITORIA">Reporte de Auditoría</option>
                  <option value="PERSONALIZADO">Reporte Personalizado</option>
                </select>
                <span v-if="errors.tipo_reporte" class="error-message">
                  {{ errors.tipo_reporte }}
                </span>
                <div class="form-help">
                  El tipo de reporte determina qué datos se incluirán
                </div>
              </div>
              
              <div class="form-group">
                <label for="formato" class="form-label required">
                  Formato de Salida
                </label>
                <div class="format-options">
                  <label 
                    v-for="format in formatOptions" 
                    :key="format.value"
                    class="format-option"
                    :class="{ 'selected': formData.formato === format.value }"
                  >
                    <input 
                      type="radio" 
                      :value="format.value"
                      v-model="formData.formato"
                      :class="{ 'error': errors.formato }"
                    >
                    <div class="format-icon">
                      <i :class="format.icon"></i>
                    </div>
                    <div class="format-info">
                      <div class="format-name">{{ format.name }}</div>
                      <div class="format-desc">{{ format.description }}</div>
                    </div>
                  </label>
                </div>
                <span v-if="errors.formato" class="error-message">
                  {{ errors.formato }}
                </span>
              </div>
            </div>
          </div>

          <!-- Paso 2: Información Básica -->
          <div v-if="currentStep === 2" class="step-content">
            <div class="step-header">
              <h4>
                <i class="fas fa-info-circle"></i>
                Información Básica
              </h4>
              <p>Proporciona los detalles básicos del reporte</p>
            </div>
            
            <div class="form-group">
              <label for="titulo" class="form-label required">
                Título del Reporte
              </label>
              <input 
                type="text" 
                id="titulo"
                v-model="formData.titulo"
                :class="{ 'error': errors.titulo }"
                placeholder="Ej: Reporte de Calidad - Enero 2024"
                class="form-input"
                required
              >
              <span v-if="errors.titulo" class="error-message">
                {{ errors.titulo }}
              </span>
            </div>
            
            <div class="form-group">
              <label for="descripcion" class="form-label">
                Descripción
              </label>
              <textarea 
                id="descripcion"
                v-model="formData.descripcion"
                rows="4"
                placeholder="Descripción opcional del reporte..."
                class="form-textarea"
              ></textarea>
              <div class="form-help">
                Proporciona contexto adicional sobre el propósito del reporte
              </div>
            </div>

            <!-- Opciones de personalización -->
            <div class="form-group">
              <div class="form-label" id="personalization-options-label">Opciones de Personalización</div>
              <fieldset class="checkbox-grid" aria-labelledby="personalization-options-label">
                <label class="checkbox-option">
                  <input 
                    type="checkbox" 
                    v-model="formData.parametros.include_charts"
                  >
                  <span class="checkmark"></span>
                  <div class="checkbox-content">
                    <div class="checkbox-title">Incluir Gráficos</div>
                    <div class="checkbox-desc">Añade visualizaciones de datos</div>
                  </div>
                </label>
                
                <label class="checkbox-option">
                  <input 
                    type="checkbox" 
                    v-model="formData.parametros.include_recommendations"
                  >
                  <span class="checkmark"></span>
                  <div class="checkbox-content">
                    <div class="checkbox-title">Incluir Recomendaciones</div>
                    <div class="checkbox-desc">Añade sugerencias basadas en los datos</div>
                  </div>
                </label>

                <label class="checkbox-option">
                  <input 
                    type="checkbox" 
                    v-model="formData.parametros.include_raw_data"
                  >
                  <span class="checkmark"></span>
                  <div class="checkbox-content">
                    <div class="checkbox-title">Incluir Datos Crudos</div>
                    <div class="checkbox-desc">Añade tablas con datos detallados</div>
                  </div>
                </label>

                <label class="checkbox-option">
                  <input 
                    type="checkbox" 
                    v-model="formData.parametros.include_summary"
                  >
                  <span class="checkmark"></span>
                  <div class="checkbox-content">
                    <div class="checkbox-title">Incluir Resumen Ejecutivo</div>
                    <div class="checkbox-desc">Añade un resumen de alto nivel</div>
                  </div>
                </label>
              </fieldset>
            </div>
          </div>

          <!-- Paso 3: Parámetros Específicos -->
          <div v-if="currentStep === 3" class="step-content">
            <div class="step-header">
              <h4>
                <i class="fas fa-sliders-h"></i>
                Parámetros Específicos
              </h4>
              <p>Configura los parámetros específicos según el tipo de reporte</p>
            </div>
            
            <!-- Parámetros para Reporte de Finca -->
            <div v-if="formData.tipo_reporte === 'FINCA'" class="parameter-section">
              <h5>Configuración de Finca</h5>
              <div class="form-grid">
                <div class="form-group">
                  <label for="finca_id" class="form-label required">
                    Finca
                  </label>
                  <select 
                    id="finca_id"
                    v-model="formData.parametros.finca_id"
                    :class="{ 'error': errors.finca_id }"
                    class="form-select"
                    required
                  >
                    <option value="">Seleccionar finca</option>
                    <option v-for="finca in fincas" :key="finca.id" :value="finca.id">
                      {{ finca.nombre }}{{ finca.municipio ? ` - ${finca.municipio}` : '' }}{{ finca.departamento ? `, ${finca.departamento}` : '' }}
                    </option>
                  </select>
                  <div v-if="fincas.length === 0" class="text-sm text-gray-500 mt-1">
                    Cargando fincas...
                  </div>
                  <div v-else class="text-sm text-gray-500 mt-1">
                    {{ fincas.length }} finca(s) disponible(s)
                  </div>
                  <span v-if="errors.finca_id" class="error-message">
                    {{ errors.finca_id }}
                  </span>
                </div>

                <div class="form-group">
                  <label for="include_lotes" class="form-label">
                    Incluir Información de Lotes
                  </label>
                  <div class="toggle-switch">
                    <input 
                      type="checkbox" 
                      id="include_lotes"
                      v-model="formData.parametros.include_lotes"
                    >
                    <div class="toggle-label">
                      <span class="toggle-slider"></span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Parámetros para Reporte de Lote -->
            <div v-if="formData.tipo_reporte === 'LOTE'" class="parameter-section">
              <h5>Configuración de Lote</h5>
              <div class="form-grid">
                <div class="form-group">
                  <label for="finca_id_lote" class="form-label">
                    Finca
                  </label>
                  <select 
                    id="finca_id_lote"
                    v-model="formData.parametros.finca_id"
                    @change="loadLotes"
                    class="form-select"
                  >
                    <option value="">Todas las fincas</option>
                    <option v-for="finca in fincas" :key="finca.id" :value="finca.id">
                      {{ finca.nombre }}
                    </option>
                  </select>
                </div>
                
                <div class="form-group">
                  <label for="lote_id" class="form-label">
                    Lote
                  </label>
                  <select 
                    id="lote_id"
                    v-model="formData.parametros.lote_id"
                    class="form-select"
                  >
                    <option value="">Todos los lotes</option>
                    <option v-for="lote in lotes" :key="lote.id" :value="lote.id">
                      {{ lote.identificador }} - {{ lote.variedad }}
                    </option>
                  </select>
                </div>
              </div>
            </div>

            <!-- Parámetros para Reporte Personalizado -->
            <div v-if="formData.tipo_reporte === 'PERSONALIZADO'" class="parameter-section">
              <h5>Configuración Personalizada</h5>
              <div class="form-grid">
                <div class="form-group">
                  <label for="custom_type" class="form-label">
                    Tipo de Análisis
                  </label>
                  <select 
                    id="custom_type"
                    v-model="formData.parametros.custom_type"
                    class="form-select"
                  >
                    <option value="CALIDAD">Análisis de Calidad</option>
                    <option value="RENDIMIENTO">Análisis de Rendimiento</option>
                  </select>
                </div>

                <div class="form-group">
                  <label for="analysis_depth" class="form-label">
                    Profundidad del Análisis
                  </label>
                  <select 
                    id="analysis_depth"
                    v-model="formData.parametros.analysis_depth"
                    class="form-select"
                  >
                    <option value="basic">Básico</option>
                    <option value="intermediate">Intermedio</option>
                    <option value="advanced">Avanzado</option>
                  </select>
                </div>
              </div>
            </div>
          </div>

          <!-- Paso 4: Filtros -->
          <div v-if="currentStep === 4" class="step-content">
            <div class="step-header">
              <h4>
                <i class="fas fa-filter"></i>
                Filtros de Datos
              </h4>
              <p>Especifica qué datos incluir en el reporte</p>
            </div>
            
            <div class="filters-grid">
              <div class="form-group">
                <label for="fecha_desde" class="form-label">
                  Fecha Desde
                </label>
                <input 
                  type="date" 
                  id="fecha_desde"
                  v-model="formData.filtros.fecha_desde"
                  class="form-input"
                >
                <div class="form-help">
                  Deja vacío para incluir todos los datos
                </div>
              </div>
              
              <div class="form-group">
                <label for="fecha_hasta" class="form-label">
                  Fecha Hasta
                </label>
                <input 
                  type="date" 
                  id="fecha_hasta"
                  v-model="formData.filtros.fecha_hasta"
                  class="form-input"
                >
                <div class="form-help">
                  Deja vacío para incluir todos los datos
                </div>
              </div>

              <div class="form-group">
                <label for="usuario_id" class="form-label">
                  Usuario
                </label>
                <select 
                  id="usuario_id"
                  v-model="formData.filtros.usuario_id"
                  class="form-select"
                >
                  <option value="">Todos los usuarios</option>
                  <option v-for="user in users" :key="user.id" :value="user.id">
                    {{ user.first_name }} {{ user.last_name }} ({{ user.username }})
                  </option>
                </select>
              </div>
              
              <div class="form-group">
                <label for="calidad_minima" class="form-label">
                  Calidad Mínima (%)
                </label>
                <input 
                  type="number" 
                  id="calidad_minima"
                  v-model="formData.filtros.calidad_minima"
                  min="0"
                  max="100"
                  step="0.1"
                  class="form-input"
                >
                <div class="form-help">
                  Solo incluir análisis con calidad superior al porcentaje especificado
                </div>
              </div>

              <div class="form-group">
                <label for="confianza_minima" class="form-label">
                  Confianza Mínima (%)
                </label>
                <input 
                  type="number" 
                  id="confianza_minima"
                  v-model="formData.filtros.confianza_minima"
                  min="0"
                  max="100"
                  step="0.1"
                  class="form-input"
                >
                <div class="form-help">
                  Solo incluir predicciones con confianza superior al porcentaje especificado
                </div>
              </div>

              <div class="form-group">
                <label for="variedad" class="form-label">
                  Variedad de Cacao
                </label>
                <select 
                  id="variedad"
                  v-model="formData.filtros.variedad"
                  class="form-select"
                >
                  <option value="">Todas las variedades</option>
                  <option value="criollo">Criollo</option>
                  <option value="forastero">Forastero</option>
                  <option value="trinitario">Trinitario</option>
                  <option value="nacional">Nacional</option>
                </select>
              </div>
            </div>

            <!-- Filtros avanzados -->
            <div class="advanced-filters">
              <button 
                type="button"
                @click="showAdvancedFilters = !showAdvancedFilters"
                class="toggle-advanced-btn"
              >
                <i class="fas fa-cog"></i>
                {{ showAdvancedFilters ? 'Ocultar' : 'Mostrar' }} Filtros Avanzados
              </button>

              <div v-if="showAdvancedFilters" class="advanced-filters-content">
                <div class="form-grid">
                  <div class="form-group">
                    <label for="region" class="form-label">
                      Región
                    </label>
                    <input 
                      type="text" 
                      id="region"
                      v-model="formData.filtros.region"
                      placeholder="Ej: Huila, Tolima"
                      class="form-input"
                    >
                  </div>

                  <div class="form-group">
                    <label for="municipio" class="form-label">
                      Municipio
                    </label>
                    <input 
                      type="text" 
                      id="municipio"
                      v-model="formData.filtros.municipio"
                      placeholder="Ej: Neiva, Ibagué"
                      class="form-input"
                    >
                  </div>

                  <div class="form-group">
                    <label for="altitud_minima" class="form-label">
                      Altitud Mínima (msnm)
                    </label>
                    <input 
                      type="number" 
                      id="altitud_minima"
                      v-model="formData.filtros.altitud_minima"
                      min="0"
                      step="10"
                      class="form-input"
                    >
                  </div>

                  <div class="form-group">
                    <label for="altitud_maxima" class="form-label">
                      Altitud Máxima (msnm)
                    </label>
                    <input 
                      type="number" 
                      id="altitud_maxima"
                      v-model="formData.filtros.altitud_maxima"
                      min="0"
                      step="10"
                      class="form-input"
                    >
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Paso 5: Programación -->
          <div v-if="currentStep === 5" class="step-content">
            <div class="step-header">
              <h4>
                <i class="fas fa-clock"></i>
                Programación (Opcional)
              </h4>
              <p>Configura la generación automática del reporte</p>
            </div>
            
            <div class="scheduling-section">
              <div class="form-group">
                <label class="checkbox-option large">
                  <input 
                    type="checkbox" 
                    v-model="formData.parametros.scheduled"
                    @change="onScheduledChange"
                  >
                  <span class="checkmark"></span>
                  <div class="checkbox-content">
                    <div class="checkbox-title">Programar reporte recurrente</div>
                    <div class="checkbox-desc">
                      Genera este reporte automáticamente según la frecuencia especificada
                    </div>
                  </div>
                </label>
              </div>

              <div v-if="formData.parametros.scheduled" class="scheduling-options">
                <div class="form-grid">
                  <div class="form-group">
                    <label for="schedule_frequency" class="form-label">
                      Frecuencia
                    </label>
                    <select 
                      id="schedule_frequency"
                      v-model="formData.parametros.schedule_frequency"
                      class="form-select"
                    >
                      <option value="daily">Diario</option>
                      <option value="weekly">Semanal</option>
                      <option value="monthly">Mensual</option>
                      <option value="quarterly">Trimestral</option>
                      <option value="yearly">Anual</option>
                    </select>
                  </div>
                  
                  <div class="form-group">
                    <label for="schedule_time" class="form-label">
                      Hora de Generación
                    </label>
                    <input 
                      type="time" 
                      id="schedule_time"
                      v-model="formData.parametros.schedule_time"
                      class="form-input"
                    >
                  </div>

                  <div class="form-group">
                    <label for="schedule_email" class="form-label">
                      Email de Notificación
                    </label>
                    <input 
                      type="email" 
                      id="schedule_email"
                      v-model="formData.parametros.schedule_email"
                      placeholder="usuario@ejemplo.com"
                      class="form-input"
                    >
                    <div class="form-help">
                      Email donde se enviará el reporte generado
                    </div>
                  </div>

                  <div class="form-group">
                    <label for="schedule_retention" class="form-label">
                      Retención (días)
                    </label>
                    <input 
                      type="number" 
                      id="schedule_retention"
                      v-model="formData.parametros.schedule_retention"
                      min="1"
                      max="365"
                      class="form-input"
                    >
                    <div class="form-help">
                      Días que se mantendrá el reporte antes de eliminarlo
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </form>
        </div>

        <!-- Footer -->
        <div class="bg-gray-50 px-6 py-4 border-t border-gray-200 flex items-center justify-between">
          <div class="flex items-center gap-3">
            <button 
              v-if="currentStep > 1"
              type="button" 
              class="px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-lg font-medium flex items-center gap-2 transition-colors"
              @click="previousStep"
            >
              <i class="fas fa-arrow-left"></i>
              Anterior
            </button>
          </div>

          <div class="flex items-center gap-3">
            <button 
              type="button" 
              class="px-4 py-2 bg-white border border-gray-300 text-gray-700 rounded-lg font-medium hover:bg-gray-50 transition-colors"
              @click="closeModal"
            >
              Cancelar
            </button>
            <button 
              v-if="currentStep < totalSteps"
              type="button" 
              class="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium flex items-center gap-2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              @click="nextStep"
              :disabled="!canProceed"
              :title="!canProceed ? `Faltan campos requeridos: tipo_reporte=${!!formData.tipo_reporte}, formato=${!!formData.formato}` : 'Continuar al siguiente paso'"
            >
              Siguiente
              <i class="fas fa-arrow-right"></i>
            </button>
            <button 
              v-else
              type="submit" 
              class="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium flex items-center gap-2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              @click="generateReport"
              :disabled="loading || !canProceed"
            >
              <i v-if="loading" class="fas fa-spinner fa-spin"></i>
              <i v-else class="fas fa-chart-bar"></i>
              Generar Reporte
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useReportsStore } from '@/stores/reports'
import { useReports } from '@/composables/useReports'
import { useEmailValidation } from '@/composables/useEmailValidation'
import { useNotifications } from '@/composables/useNotifications'
import { getFincas } from '@/services/fincasApi'

const emit = defineEmits(['close', 'created'])

const reportsStore = useReportsStore()
const { isValidEmail } = useEmailValidation()
const { showSuccess, showError } = useNotifications()
const { pollForCompletion, downloadReport: downloadReportFromComposable } = useReports()

const loading = ref(false)
const errors = ref({})
const currentStep = ref(1)
const showAdvancedFilters = ref(false)
const fincas = ref([])
const lotes = ref([])
const users = ref([])

const totalSteps = 5

const steps = [
  { label: 'Tipo y Formato' },
  { label: 'Información' },
  { label: 'Parámetros' },
  { label: 'Filtros' },
  { label: 'Programación' }
]

const formatOptions = [
      {
        value: 'EXCEL',
        name: 'Excel',
        description: 'Hoja de cálculo con datos',
        icon: 'fas fa-file-excel'
      },
      {
        value: 'PDF',
        name: 'PDF',
        description: 'Documento portátil con gráficos',
        icon: 'fas fa-file-pdf'
      },
      {
        value: 'CSV',
        name: 'CSV',
        description: 'Datos separados por comas',
        icon: 'fas fa-file-csv'
      },
      {
        value: 'JSON',
        name: 'JSON',
        description: 'Datos estructurados',
        icon: 'fas fa-file-code'
      }
    ]

// Form data
const formData = reactive({
      tipo_reporte: '',
      formato: '',
      titulo: '',
      descripcion: '',
      parametros: {
        finca_id: '',
        lote_id: '',
        custom_type: 'CALIDAD',
        analysis_depth: 'intermediate',
        include_charts: true,
        include_recommendations: true,
        include_raw_data: false,
        include_summary: true,
        include_lotes: false,
        scheduled: false,
        schedule_frequency: 'monthly',
        schedule_time: '09:00',
        schedule_email: '',
        schedule_retention: 30
      },
      filtros: {
        fecha_desde: '',
        fecha_hasta: '',
        usuario_id: '',
        calidad_minima: '',
        confianza_minima: '',
        variedad: '',
        region: '',
        municipio: '',
        altitud_minima: '',
        altitud_maxima: ''
      }
    })

// Computed
const canProceed = computed(() => {
      switch (currentStep.value) {
        case 1:
          const step1Valid = !!(formData.tipo_reporte && formData.formato)
          return step1Valid
        case 2:
          return !!formData.titulo.trim()
        case 3:
          if (formData.tipo_reporte === 'FINCA') {
            return !!formData.parametros.finca_id
          }
          return true
        case 4:
          return true
        case 5:
          return true
        default:
          return false
      }
    })

// Methods
const loadInitialData = async () => {
      try {
        // Load fincas using the same service as other components
        const fincasResponse = await getFincas({ page_size: 1000, activa: true })
        fincas.value = fincasResponse?.results || fincasResponse?.data?.results || []
        
        // Load users if needed (optional for now)
        try {
          const { apiGet } = await import('@/services/apiClient')
          const usersResponse = await apiGet('/auth/users/', { page_size: 1000 })
          users.value = usersResponse?.results || usersResponse?.data?.results || []
        } catch (userError) {
          console.warn('Could not load users:', userError)
          users.value = []
        }
        
        console.log('Fincas loaded:', fincas.value.length)
      } catch (error) {
        console.error('Error loading initial data:', error)
        showError('Error al cargar las fincas. Por favor, intenta nuevamente.')
      }
    }

const loadLotes = async () => {
  if (!formData.parametros.finca_id) {
    lotes.value = []
    return
  }

  try {
    const { apiGet } = await import('@/services/apiClient')
    const response = await apiGet(`/fincas/${formData.parametros.finca_id}/lotes/`, { page_size: 1000 })
    lotes.value = response?.results || response?.data?.results || []
  } catch (error) {
    console.error('Error loading lotes:', error)
    lotes.value = []
  }
}

const onTypeChange = () => {
  // Reset parameters when type changes
  formData.parametros = {
    finca_id: '',
    lote_id: '',
    custom_type: 'CALIDAD',
    analysis_depth: 'intermediate',
    include_charts: true,
    include_recommendations: true,
    include_raw_data: false,
    include_summary: true,
    include_lotes: false,
    scheduled: false,
    schedule_frequency: 'monthly',
    schedule_time: '09:00',
    schedule_email: '',
    schedule_retention: 30
  }
  
  // Generate default title based on type
  if (formData.tipo_reporte && !formData.titulo) {
    const typeNames = {
      'CALIDAD': 'Reporte de Calidad',
      'FINCA': 'Reporte de Finca',
      'LOTE': 'Reporte de Lote',
      'USUARIO': 'Reporte de Usuario',
      'AUDITORIA': 'Reporte de Auditoría',
      'PERSONALIZADO': 'Reporte Personalizado'
    }
    formData.titulo = `${typeNames[formData.tipo_reporte] || 'Reporte'} - ${new Date().toLocaleDateString('es-ES')}`
  }
}

const onScheduledChange = () => {
  if (!formData.parametros.scheduled) {
    formData.parametros.schedule_frequency = 'monthly'
    formData.parametros.schedule_time = '09:00'
    formData.parametros.schedule_email = ''
    formData.parametros.schedule_retention = 30
  }
}

const nextStep = () => {
  console.log('nextStep called:', {
    canProceed: canProceed.value,
    currentStep: currentStep.value,
    totalSteps: totalSteps,
    tipo_reporte: formData.tipo_reporte,
    formato: formData.formato
  })
  if (canProceed.value && currentStep.value < totalSteps) {
    currentStep.value++
  }
}

const previousStep = () => {
  if (currentStep.value > 1) {
    currentStep.value--
  }
}

// Email validation is now handled by useEmailValidation composable
const hasValidScheduleEmailFormat = (value) => {
  return isValidEmail(value)
}

const validateForm = () => {
  errors.value = {}

  // Required fields
  if (!formData.tipo_reporte) {
    errors.value.tipo_reporte = 'El tipo de reporte es requerido'
  }

  if (!formData.formato) {
    errors.value.formato = 'El formato es requerido'
  }

  if (!formData.titulo.trim()) {
    errors.value.titulo = 'El título es requerido'
  }

  // Specific validations
  if (formData.tipo_reporte === 'FINCA' && !formData.parametros.finca_id) {
    errors.value.finca_id = 'Debe seleccionar una finca'
  }

  // Date validations
  if (formData.filtros.fecha_desde && formData.filtros.fecha_hasta) {
    if (new Date(formData.filtros.fecha_desde) > new Date(formData.filtros.fecha_hasta)) {
      errors.value.fecha_hasta = 'La fecha hasta debe ser posterior a la fecha desde'
    }
  }

  // Email validation for scheduled reports
  if (formData.parametros.scheduled && formData.parametros.schedule_email) {
    const email = formData.parametros.schedule_email.trim()
    
    // Limit email length to prevent DoS attacks
    if (email.length > 254) {
      errors.value.schedule_email = 'El email es demasiado largo'
    } else if (email.length === 0) {
      errors.value.schedule_email = 'El email es requerido'
    } else if (!hasValidScheduleEmailFormat(email)) {
      errors.value.schedule_email = 'El email no es válido'
    }
  }

  return Object.keys(errors.value).length === 0
}

const cleanEmptyValues = (obj) => {
  const cleaned = { ...obj }
  for (const key of Object.keys(cleaned)) {
    if (cleaned[key] === '' || cleaned[key] === null) {
      delete cleaned[key]
    }
  }
  return cleaned
}

const buildReportData = () => {
  return {
    tipo_reporte: formData.tipo_reporte,
    formato: formData.formato,
    titulo: formData.titulo.trim(),
    descripcion: formData.descripcion.trim(),
    parametros: cleanEmptyValues(formData.parametros),
    filtros: cleanEmptyValues(formData.filtros)
  }
}

const processReportErrors = (errorData) => {
  if (errorData.tipo_reporte) {
    errors.value.tipo_reporte = Array.isArray(errorData.tipo_reporte) ? errorData.tipo_reporte[0] : errorData.tipo_reporte
  }
  if (errorData.formato) {
    errors.value.formato = Array.isArray(errorData.formato) ? errorData.formato[0] : errorData.formato
  }
  if (errorData.titulo) {
    errors.value.titulo = Array.isArray(errorData.titulo) ? errorData.titulo[0] : errorData.titulo
  }
}

const generateReport = async () => {
  if (!validateForm()) {
    return
  }

  loading.value = true
  errors.value = {}

  try {
    const reportData = buildReportData()
    const response = await reportsStore.createReport(reportData)
    const reportId = response.data?.id || response?.id

    if (!reportId) {
      throw new Error('No se pudo obtener el ID del reporte creado')
    }

    // Show initial success message
    showSuccess('El reporte se está generando. Esperando a que esté listo...')

    // Wait for report to be completed
    try {
      const completedReport = await pollForCompletion(reportId, 2000, 30) // Poll every 2 seconds, max 30 attempts (1 minute)
      
      // Report is ready, download it automatically
      showSuccess('Reporte generado exitosamente. Iniciando descarga...')
      
      // Small delay to ensure file is fully ready
      await new Promise(resolve => setTimeout(resolve, 500))
      
      // Download the report
      await downloadReportFromComposable(reportId)
      
      showSuccess('Reporte descargado exitosamente')
      
    } catch (pollError) {
      // If polling fails or times out, still emit created event
      console.warn('Error esperando reporte o descargando:', pollError)
      showError(pollError.message || 'El reporte se creó pero no se pudo descargar automáticamente. Puedes descargarlo desde la lista de reportes.')
    }

    emit('created', response.data)
    closeModal()

  } catch (error) {
    if (error.response?.data) {
      const errorData = error.response.data
      processReportErrors(errorData)
      
      if (Object.keys(errors.value).length === 0) {
        showError(errorData.detail || 'No se pudo crear el reporte')
      }
    } else {
      showError(error.message || 'No se pudo crear el reporte')
    }
  } finally {
    loading.value = false
  }
}

const closeModal = () => {
  emit('close')
}

// Debug watchers
watch(() => formData.tipo_reporte, (newVal) => {
  console.log('tipo_reporte changed:', newVal)
})

watch(() => formData.formato, (newVal) => {
  console.log('formato changed:', newVal)
})

watch(canProceed, (newVal) => {
  console.log('canProceed changed:', newVal, {
    tipo_reporte: formData.tipo_reporte,
    formato: formData.formato
  })
})

// Lifecycle
onMounted(() => {
  loadInitialData()
})
</script>

<style scoped>

/* Progress Indicator */
.progress-indicator {
  margin-bottom: 2rem;
}

.progress-steps {
  display: flex;
  justify-content: space-between;
  position: relative;
}

.progress-steps::before {
  content: '';
  position: absolute;
  top: 1rem;
  left: 0;
  right: 0;
  height: 2px;
  background: #e5e7eb;
  z-index: 1;
}

.progress-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
  z-index: 2;
}

.step-number {
  width: 2rem;
  height: 2rem;
  border-radius: 50%;
  background: #d1d5db;
  color: #374151;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 0.875rem;
  margin-bottom: 0.5rem;
  transition: all 0.3s;
}

.progress-step.active .step-number {
  background: #2563eb;
  color: #ffffff;
}

.progress-step.completed .step-number {
  background: #047857;
  color: #ffffff;
}

.step-label {
  font-size: 0.75rem;
  color: #374151;
  text-align: center;
  font-weight: 500;
}

.progress-step.active .step-label {
  color: #3b82f6;
}

.progress-step.completed .step-label {
  color: #10b981;
}

/* Form Styles */
.report-form {
  max-width: none;
}

.step-content {
  animation: fadeIn 0.3s ease-out;
}

.step-header {
  margin-bottom: 2rem;
}

.step-header h4 {
  margin: 0 0 0.5rem 0;
  color: #1f2937;
  font-size: 1.25rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.step-header h4 i {
  color: #3b82f6;
}

.step-header p {
  margin: 0;
  color: #374151;
  font-size: 0.875rem;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 1.5rem;
}

.filters-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-label {
  font-weight: 500;
  color: #374151;
  font-size: 0.875rem;
}

.form-label.required::after {
  content: ' *';
  color: #ef4444;
}

.form-input,
.form-select,
.form-textarea {
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  transition: all 0.2s;
}

.form-input:focus,
.form-select:focus,
.form-textarea:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-input.error,
.form-select.error,
.form-textarea.error {
  border-color: #ef4444;
}

.error-message {
  color: #ef4444;
  font-size: 0.75rem;
  margin-top: 0.25rem;
}

.form-help {
  color: #6b7280;
  font-size: 0.75rem;
  margin-top: 0.25rem;
}

/* Format Options */
.format-options {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.format-option {
  border: 2px solid #e5e7eb;
  border-radius: 0.5rem;
  padding: 1rem;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.format-option:hover {
  border-color: #3b82f6;
  background: #f8fafc;
}

.format-option.selected {
  border-color: #3b82f6;
  background: #eff6ff;
}

.format-option input[type="radio"] {
  margin: 0;
}

.format-icon {
  width: 2rem;
  height: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  color: #6b7280;
}

.format-option.selected .format-icon {
  color: #3b82f6;
}

.format-name {
  font-weight: 500;
  color: #374151;
}

.format-desc {
  font-size: 0.75rem;
  color: #6b7280;
}

/* Checkbox Styles */
.checkbox-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.checkbox-option {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  cursor: pointer;
  padding: 0.75rem;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  transition: all 0.2s;
}

.checkbox-option:hover {
  border-color: #3b82f6;
  background: #f8fafc;
}

.checkbox-option.large {
  padding: 1rem;
}

.checkbox-option input[type="checkbox"] {
  margin: 0;
  width: 1rem;
  height: 1rem;
}

.checkbox-content {
  flex: 1;
}

.checkbox-title {
  font-weight: 500;
  color: #374151;
  font-size: 0.875rem;
}

.checkbox-desc {
  color: #6b7280;
  font-size: 0.75rem;
  margin-top: 0.25rem;
}

/* Toggle Switch */
.toggle-switch {
  display: flex;
  align-items: center;
}

.toggle-label {
  position: relative;
  display: inline-block;
  width: 3rem;
  height: 1.5rem;
  cursor: pointer;
}

.toggle-label input {
  opacity: 0;
  width: 0;
  height: 0;
}

.toggle-slider {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #ccc;
  transition: 0.4s;
  border-radius: 1.5rem;
}

.toggle-slider:before {
  position: absolute;
  content: "";
  height: 1.125rem;
  width: 1.125rem;
  left: 0.1875rem;
  bottom: 0.1875rem;
  background-color: white;
  transition: 0.4s;
  border-radius: 50%;
}

input:checked + .toggle-label .toggle-slider {
  background-color: #3b82f6;
}

input:checked + .toggle-label .toggle-slider:before {
  transform: translateX(1.5rem);
}

/* Parameter Sections */
.parameter-section {
  margin-bottom: 2rem;
  padding: 1.5rem;
  background: #f8fafc;
  border-radius: 0.5rem;
  border: 1px solid #e5e7eb;
}

.parameter-section h5 {
  margin: 0 0 1rem 0;
  color: #374151;
  font-size: 1rem;
  font-weight: 600;
}

/* Advanced Filters */
.advanced-filters {
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 1px solid #e5e7eb;
}

.toggle-advanced-btn {
  background: none;
  border: none;
  color: #3b82f6;
  font-size: 0.875rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0;
}

.toggle-advanced-btn:hover {
  color: #2563eb;
}

.advanced-filters-content {
  margin-top: 1rem;
  animation: slideDown 0.3s ease-out;
}

/* Scheduling */
.scheduling-section {
  background: #f8fafc;
  padding: 1.5rem;
  border-radius: 0.5rem;
  border: 1px solid #e5e7eb;
}

.scheduling-options {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #e5e7eb;
}


/* Buttons */
.btn {
  display: inline-flex;
  align-items: center;
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  text-decoration: none;
  transition: all 0.2s;
  cursor: pointer;
  border: 1px solid transparent;
  gap: 0.5rem;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-secondary {
  background-color: #6b7280;
  color: white;
  border-color: #6b7280;
}

.btn-secondary:hover:not(:disabled) {
  background-color: #4b5563;
  border-color: #4b5563;
}

.btn-outline {
  background-color: transparent;
  color: #374151;
  border-color: #d1d5db;
}

.btn-outline:hover:not(:disabled) {
  background-color: #f9fafb;
  border-color: #9ca3af;
}

.btn-primary {
  background-color: #2563eb;
  color: #ffffff;
  border-color: #2563eb;
}

.btn-primary:hover:not(:disabled) {
  background-color: #2563eb;
  border-color: #2563eb;
}

/* Animations */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes slideDown {
  from {
    opacity: 0;
    max-height: 0;
  }
  to {
    opacity: 1;
    max-height: 500px;
  }
}

/* Responsive */
@media (max-width: 768px) {
  
  .form-grid {
    grid-template-columns: 1fr;
  }
  
  .filters-grid {
    grid-template-columns: 1fr;
  }
  
  .format-options {
    grid-template-columns: 1fr;
  }
  
  .checkbox-grid {
    grid-template-columns: 1fr;
  }
  
  .progress-steps {
    flex-wrap: wrap;
    gap: 1rem;
  }
  
  .progress-step {
    flex: 1;
    min-width: 80px;
  }
}

</style>