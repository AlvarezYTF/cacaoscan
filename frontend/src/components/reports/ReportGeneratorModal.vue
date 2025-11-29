<template>
  <div class="modal-overlay" @click="closeModal">
    <div class="modal-container" @click.stop>
      <div class="modal-header">
        <div class="header-content">
          <div class="header-icon">
            <i class="fas fa-chart-bar"></i>
          </div>
          <div class="header-text">
            <h3>Generar Nuevo Reporte</h3>
            <p>Configura los parámetros para generar tu reporte personalizado</p>
          </div>
        </div>
        <button class="close-btn" @click="closeModal">
          <i class="fas fa-times"></i>
        </button>
      </div>

      <div class="modal-body">
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
                  <option value="calidad">Reporte de Calidad</option>
                  <option value="finca">Reporte de Finca</option>
                  <option value="lote">Reporte de Lote</option>
                  <option value="usuario">Reporte de Usuario</option>
                  <option value="auditoria">Reporte de Auditoría</option>
                  <option value="personalizado">Reporte Personalizado</option>
                  <option value="metricas">Reporte de Métricas de Modelos</option>
                  <option value="entrenamiento">Reporte de Entrenamiento</option>
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
            <div v-if="formData.tipo_reporte === 'finca'" class="parameter-section">
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
                      {{ finca.nombre }} - {{ finca.ubicacion }}
                    </option>
                  </select>
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
            <div v-if="formData.tipo_reporte === 'lote'" class="parameter-section">
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
            <div v-if="formData.tipo_reporte === 'personalizado'" class="parameter-section">
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
                    <option value="calidad">Análisis de Calidad</option>
                    <option value="rendimiento">Análisis de Rendimiento</option>
                    <option value="tendencias">Análisis de Tendencias</option>
                    <option value="comparativo">Análisis Comparativo</option>
                    <option value="predicciones">Análisis de Predicciones</option>
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

            <!-- Parámetros para Reporte de Métricas -->
            <div v-if="formData.tipo_reporte === 'metricas'" class="parameter-section">
              <h5>Configuración de Métricas</h5>
              <div class="form-grid">
                <div class="form-group">
                  <label for="model_type" class="form-label">
                    Tipo de Modelo
                  </label>
                  <select 
                    id="model_type"
                    v-model="formData.parametros.model_type"
                    class="form-select"
                  >
                    <option value="">Todos los tipos</option>
                    <option value="regression">Regresión</option>
                    <option value="classification">Clasificación</option>
                    <option value="segmentation">Segmentación</option>
                    <option value="incremental">Incremental</option>
                  </select>
                </div>

                <div class="form-group">
                  <label for="target_metric" class="form-label">
                    Variable Objetivo
                  </label>
                  <select 
                    id="target_metric"
                    v-model="formData.parametros.target_metric"
                    class="form-select"
                  >
                    <option value="">Todas las variables</option>
                    <option value="alto">Altura</option>
                    <option value="ancho">Ancho</option>
                    <option value="grosor">Grosor</option>
                    <option value="peso">Peso</option>
                    <option value="calidad">Calidad</option>
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

      <div class="modal-footer">
        <div class="footer-left">
          <button 
            v-if="currentStep > 1"
            type="button" 
            class="btn btn-secondary"
            @click="previousStep"
          >
            <i class="fas fa-arrow-left"></i>
            Anterior
          </button>
        </div>

        <div class="footer-right">
          <button 
            type="button" 
            class="btn btn-outline"
            @click="closeModal"
          >
            Cancelar
          </button>
          <button 
            v-if="currentStep < totalSteps"
            type="button" 
            class="btn btn-primary"
            @click="nextStep"
            :disabled="!canProceed"
          >
            Siguiente
            <i class="fas fa-arrow-right"></i>
          </button>
          <button 
            v-else
            type="submit" 
            class="btn btn-primary"
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
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import { useReportsStore } from '@/stores/reports'
import Swal from 'sweetalert2'

export default {
  name: 'ReportGeneratorModal',
  emits: ['close', 'created'],
  setup(props, { emit }) {
    const reportsStore = useReportsStore()

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
        value: 'pdf',
        name: 'PDF',
        description: 'Documento portátil con gráficos',
        icon: 'fas fa-file-pdf'
      },
      {
        value: 'excel',
        name: 'Excel',
        description: 'Hoja de cálculo con datos',
        icon: 'fas fa-file-excel'
      },
      {
        value: 'csv',
        name: 'CSV',
        description: 'Datos separados por comas',
        icon: 'fas fa-file-csv'
      },
      {
        value: 'json',
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
        custom_type: 'calidad',
        analysis_depth: 'intermediate',
        model_type: '',
        target_metric: '',
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
          return formData.tipo_reporte && formData.formato
        case 2:
          return formData.titulo.trim()
        case 3:
          if (formData.tipo_reporte === 'finca') {
            return formData.parametros.finca_id
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
        const [fincasResponse, usersResponse] = await Promise.all([
          reportsStore.fetchFincas(),
          reportsStore.fetchUsers()
        ])
        
        fincas.value = fincasResponse.data.results || []
        users.value = usersResponse.data.results || []
      } catch (error) {
        console.error('Error loading initial data:', error)
      }
    }

    const loadLotes = async () => {
      if (!formData.parametros.finca_id) {
        lotes.value = []
        return
      }

      try {
        const response = await reportsStore.fetchLotesByFinca(formData.parametros.finca_id)
        lotes.value = response.data.results || []
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
        custom_type: 'calidad',
        analysis_depth: 'intermediate',
        model_type: '',
        target_metric: '',
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
          'calidad': 'Reporte de Calidad',
          'finca': 'Reporte de Finca',
          'lote': 'Reporte de Lote',
          'usuario': 'Reporte de Usuario',
          'auditoria': 'Reporte de Auditoría',
          'personalizado': 'Reporte Personalizado',
          'metricas': 'Reporte de Métricas',
          'entrenamiento': 'Reporte de Entrenamiento'
        }
        formData.titulo = `${typeNames[formData.tipo_reporte]} - ${new Date().toLocaleDateString('es-ES')}`
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
      if (canProceed.value && currentStep.value < totalSteps) {
        currentStep.value++
      }
    }

    const previousStep = () => {
      if (currentStep.value > 1) {
        currentStep.value--
      }
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
      if (formData.tipo_reporte === 'finca' && !formData.parametros.finca_id) {
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
        } else {
          // Simple, safe email validation without catastrophic backtracking
          // Split by @ to avoid regex backtracking issues
          const parts = email.split('@')
          if (parts.length !== 2) {
            errors.value.schedule_email = 'El email no es válido'
          } else {
            const [localPart, domainPart] = parts
            
            // Validate local part (before @) - max 64 chars
            if (!localPart || localPart.length === 0 || localPart.length > 64) {
              errors.value.schedule_email = 'El email no es válido'
            } else if (localPart.includes('..') || localPart.startsWith('.') || localPart.endsWith('.')) {
              errors.value.schedule_email = 'El email no es válido'
            } else {
              // Validate domain part (after @) - max 253 chars
              if (!domainPart || domainPart.length === 0 || domainPart.length > 253) {
                errors.value.schedule_email = 'El email no es válido'
              } else {
                // Check for at least one dot in domain
                const domainParts = domainPart.split('.')
                if (domainParts.length < 2 || domainParts.some(part => part.length === 0)) {
                  errors.value.schedule_email = 'El email no es válido'
                } else {
                  // Validate characters without regex to avoid backtracking
                  // Check local part contains only valid characters
                  const isValidLocalChar = (char) => {
                    const code = char.charCodeAt(0)
                    return (code >= 48 && code <= 57) || // 0-9
                           (code >= 65 && code <= 90) || // A-Z
                           (code >= 97 && code <= 122) || // a-z
                           char === '.' || char === '_' || char === '+' || char === '-'
                  }
                  
                  // Check domain part contains only valid characters
                  const isValidDomainChar = (char) => {
                    const code = char.charCodeAt(0)
                    return (code >= 48 && code <= 57) || // 0-9
                           (code >= 65 && code <= 90) || // A-Z
                           (code >= 97 && code <= 122) || // a-z
                           char === '.' || char === '-'
                  }
                  
                  const hasInvalidLocalChar = Array.from(localPart).some(char => !isValidLocalChar(char))
                  const hasInvalidDomainChar = Array.from(domainPart).some(char => !isValidDomainChar(char))
                  
                  if (hasInvalidLocalChar || hasInvalidDomainChar) {
                    errors.value.schedule_email = 'El email no es válido'
                  }
                }
              }
            }
          }
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

        Swal.fire({
          icon: 'success',
          title: 'Reporte Creado',
          text: 'El reporte ha sido enviado para generación. Te notificaremos cuando esté listo.',
          timer: 3000
        })

        emit('created', response.data)
        closeModal()

      } catch (error) {
        console.error('Error creating report:', error)
        
        if (error.response?.data) {
          const errorData = error.response.data
          processReportErrors(errorData)
          
          if (Object.keys(errors.value).length === 0) {
            Swal.fire({
              icon: 'error',
              title: 'Error',
              text: errorData.detail || 'No se pudo crear el reporte'
            })
          }
        } else {
          Swal.fire({
            icon: 'error',
            title: 'Error',
            text: 'No se pudo crear el reporte'
          })
        }
      } finally {
        loading.value = false
      }
    }

    const closeModal = () => {
      emit('close')
    }

    // Lifecycle
    onMounted(() => {
      loadInitialData()
    })

    return {
      loading,
      errors,
      currentStep,
      totalSteps,
      steps,
      showAdvancedFilters,
      fincas,
      lotes,
      users,
      formatOptions,
      formData,
      canProceed,
      loadLotes,
      onTypeChange,
      onScheduledChange,
      nextStep,
      previousStep,
      generateReport,
      closeModal
    }
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.modal-container {
  background: white;
  border-radius: 12px;
  width: 100%;
  max-width: 900px;
  max-height: 90vh;
  overflow: hidden;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
  display: flex;
  flex-direction: column;
}

.modal-header {
  padding: 1.5rem 2rem;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  background: linear-gradient(135deg, #4c63d2 0%, #5a3d8a 100%);
  color: #ffffff;
}

.header-content {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.header-icon {
  width: 3rem;
  height: 3rem;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
}

.header-text h3 {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
}

.header-text p {
  margin: 0.25rem 0 0 0;
  opacity: 0.9;
  font-size: 0.875rem;
}

.close-btn {
  background: rgba(255, 255, 255, 0.25);
  border: none;
  color: #ffffff;
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
}

.close-btn:hover {
  background: rgba(255, 255, 255, 0.3);
}

.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 2rem;
}

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
  background: #059669;
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

/* Modal Footer */
.modal-footer {
  padding: 1.5rem 2rem;
  border-top: 1px solid #e5e7eb;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #f8fafc;
}

.footer-left,
.footer-right {
  display: flex;
  gap: 0.75rem;
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
  .modal-container {
    margin: 0.5rem;
    max-height: 95vh;
  }
  
  .modal-header {
    padding: 1rem;
  }
  
  .modal-body {
    padding: 1rem;
  }
  
  .modal-footer {
    padding: 1rem;
    flex-direction: column;
    gap: 1rem;
  }
  
  .footer-left,
  .footer-right {
    width: 100%;
    justify-content: center;
  }
  
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

@media (max-width: 480px) {
  .modal-overlay {
    padding: 0.25rem;
  }
  
  .modal-container {
    margin: 0;
    border-radius: 0;
    max-height: 100vh;
  }
  
  .header-content {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
  
  .header-icon {
    width: 2.5rem;
    height: 2.5rem;
    font-size: 1rem;
  }
  
  .header-text h3 {
    font-size: 1.25rem;
  }
  
  .btn {
    padding: 0.625rem 1rem;
    font-size: 0.8125rem;
  }
}
</style>