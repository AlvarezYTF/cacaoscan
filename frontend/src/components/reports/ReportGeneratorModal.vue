<template>
  <div class="modal-overlay" @click="closeModal">
    <div class="modal-container" @click.stop>
      <div class="modal-header">
        <h3>
          <i class="fas fa-chart-bar"></i>
          Generar Nuevo Reporte
        </h3>
        <button class="close-btn" @click="closeModal">
          <i class="fas fa-times"></i>
        </button>
      </div>

      <form @submit.prevent="generateReport" class="modal-body">
        <!-- Paso 1: Tipo y Formato -->
        <div class="step-section">
          <h4>
            <span class="step-number">1</span>
            Tipo y Formato
          </h4>
          
          <div class="form-row">
            <div class="form-group">
              <label for="tipo_reporte">Tipo de Reporte *</label>
              <select 
                id="tipo_reporte"
                v-model="formData.tipo_reporte"
                :class="{ 'error': errors.tipo_reporte }"
                @change="onTypeChange"
                required
              >
                <option value="">Seleccionar tipo</option>
                <option value="calidad">Reporte de Calidad</option>
                <option value="finca">Reporte de Finca</option>
                <option value="lote">Reporte de Lote</option>
                <option value="usuario">Reporte de Usuario</option>
                <option value="auditoria">Reporte de Auditoría</option>
                <option value="personalizado">Reporte Personalizado</option>
              </select>
              <span v-if="errors.tipo_reporte" class="error-message">{{ errors.tipo_reporte }}</span>
            </div>
            
            <div class="form-group">
              <label for="formato">Formato *</label>
              <select 
                id="formato"
                v-model="formData.formato"
                :class="{ 'error': errors.formato }"
                required
              >
                <option value="">Seleccionar formato</option>
                <option value="pdf">PDF</option>
                <option value="excel">Excel</option>
                <option value="csv">CSV</option>
                <option value="json">JSON</option>
              </select>
              <span v-if="errors.formato" class="error-message">{{ errors.formato }}</span>
            </div>
          </div>
        </div>

        <!-- Paso 2: Información Básica -->
        <div class="step-section">
          <h4>
            <span class="step-number">2</span>
            Información Básica
          </h4>
          
          <div class="form-group">
            <label for="titulo">Título del Reporte *</label>
            <input 
              type="text" 
              id="titulo"
              v-model="formData.titulo"
              :class="{ 'error': errors.titulo }"
              placeholder="Ej: Reporte de Calidad - Enero 2024"
              required
            >
            <span v-if="errors.titulo" class="error-message">{{ errors.titulo }}</span>
          </div>
          
          <div class="form-group">
            <label for="descripcion">Descripción</label>
            <textarea 
              id="descripcion"
              v-model="formData.descripcion"
              rows="3"
              placeholder="Descripción opcional del reporte..."
            ></textarea>
          </div>
        </div>

        <!-- Paso 3: Parámetros Específicos -->
        <div v-if="formData.tipo_reporte" class="step-section">
          <h4>
            <span class="step-number">3</span>
            Parámetros Específicos
          </h4>
          
          <!-- Parámetros para Reporte de Finca -->
          <div v-if="formData.tipo_reporte === 'finca'" class="form-group">
            <label for="finca_id">Finca *</label>
            <select 
              id="finca_id"
              v-model="formData.parametros.finca_id"
              :class="{ 'error': errors.finca_id }"
              required
            >
              <option value="">Seleccionar finca</option>
              <option v-for="finca in fincas" :key="finca.id" :value="finca.id">
                {{ finca.nombre }} - {{ finca.ubicacion }}
              </option>
            </select>
            <span v-if="errors.finca_id" class="error-message">{{ errors.finca_id }}</span>
          </div>

          <!-- Parámetros para Reporte de Lote -->
          <div v-if="formData.tipo_reporte === 'lote'" class="form-row">
            <div class="form-group">
              <label for="finca_id_lote">Finca</label>
              <select 
                id="finca_id_lote"
                v-model="formData.parametros.finca_id"
                @change="loadLotes"
              >
                <option value="">Todas las fincas</option>
                <option v-for="finca in fincas" :key="finca.id" :value="finca.id">
                  {{ finca.nombre }}
                </option>
              </select>
            </div>
            
            <div class="form-group">
              <label for="lote_id">Lote</label>
              <select 
                id="lote_id"
                v-model="formData.parametros.lote_id"
              >
                <option value="">Todos los lotes</option>
                <option v-for="lote in lotes" :key="lote.id" :value="lote.id">
                  {{ lote.identificador }} - {{ lote.variedad }}
                </option>
              </select>
            </div>
          </div>

          <!-- Parámetros para Reporte Personalizado -->
          <div v-if="formData.tipo_reporte === 'personalizado'" class="form-group">
            <label for="custom_type">Tipo Personalizado</label>
            <select 
              id="custom_type"
              v-model="formData.parametros.custom_type"
            >
              <option value="calidad">Análisis de Calidad</option>
              <option value="rendimiento">Análisis de Rendimiento</option>
              <option value="tendencias">Análisis de Tendencias</option>
              <option value="comparativo">Análisis Comparativo</option>
            </select>
          </div>

          <!-- Opciones Avanzadas -->
          <div class="form-row">
            <div class="form-group checkbox-group">
              <label class="checkbox-label">
                <input 
                  type="checkbox" 
                  v-model="formData.parametros.include_charts"
                >
                <span class="checkmark"></span>
                Incluir gráficos
              </label>
            </div>
            
            <div class="form-group checkbox-group">
              <label class="checkbox-label">
                <input 
                  type="checkbox" 
                  v-model="formData.parametros.include_recommendations"
                >
                <span class="checkmark"></span>
                Incluir recomendaciones
              </label>
            </div>
          </div>
        </div>

        <!-- Paso 4: Filtros -->
        <div class="step-section">
          <h4>
            <span class="step-number">4</span>
            Filtros
          </h4>
          
          <div class="form-row">
            <div class="form-group">
              <label for="fecha_desde">Fecha Desde</label>
              <input 
                type="date" 
                id="fecha_desde"
                v-model="formData.filtros.fecha_desde"
              >
            </div>
            
            <div class="form-group">
              <label for="fecha_hasta">Fecha Hasta</label>
              <input 
                type="date" 
                id="fecha_hasta"
                v-model="formData.filtros.fecha_hasta"
              >
            </div>
          </div>

          <div class="form-row">
            <div class="form-group">
              <label for="usuario_id">Usuario</label>
              <select 
                id="usuario_id"
                v-model="formData.filtros.usuario_id"
              >
                <option value="">Todos los usuarios</option>
                <option v-for="user in users" :key="user.id" :value="user.id">
                  {{ user.first_name }} {{ user.last_name }} ({{ user.username }})
                </option>
              </select>
            </div>
            
            <div class="form-group">
              <label for="calidad_minima">Calidad Mínima (%)</label>
              <input 
                type="number" 
                id="calidad_minima"
                v-model="formData.filtros.calidad_minima"
                min="0"
                max="100"
                step="0.1"
              >
            </div>
          </div>
        </div>

        <!-- Paso 5: Programación (Opcional) -->
        <div class="step-section">
          <h4>
            <span class="step-number">5</span>
            Programación (Opcional)
          </h4>
          
          <div class="form-group checkbox-group">
            <label class="checkbox-label">
              <input 
                type="checkbox" 
                v-model="formData.parametros.scheduled"
                @change="onScheduledChange"
              >
              <span class="checkmark"></span>
              Programar reporte recurrente
            </label>
          </div>

          <div v-if="formData.parametros.scheduled" class="form-row">
            <div class="form-group">
              <label for="schedule_frequency">Frecuencia</label>
              <select 
                id="schedule_frequency"
                v-model="formData.parametros.schedule_frequency"
              >
                <option value="daily">Diario</option>
                <option value="weekly">Semanal</option>
                <option value="monthly">Mensual</option>
                <option value="quarterly">Trimestral</option>
              </select>
            </div>
            
            <div class="form-group">
              <label for="schedule_time">Hora de Envío</label>
              <input 
                type="time" 
                id="schedule_time"
                v-model="formData.parametros.schedule_time"
              >
            </div>
          </div>
        </div>
      </form>

      <div class="modal-footer">
        <button type="button" class="btn btn-secondary" @click="closeModal">
          Cancelar
        </button>
        <button 
          type="submit" 
          class="btn btn-primary"
          @click="generateReport"
          :disabled="loading"
        >
          <i v-if="loading" class="fas fa-spinner fa-spin"></i>
          <i v-else class="fas fa-chart-bar"></i>
          Generar Reporte
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { useAdminStore } from '@/stores/admin'
import Swal from 'sweetalert2'

export default {
  name: 'ReportGeneratorModal',
  emits: ['close', 'created'],
  setup(props, { emit }) {
    const adminStore = useAdminStore()

    const loading = ref(false)
    const errors = ref({})
    const fincas = ref([])
    const lotes = ref([])
    const users = ref([])

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
        include_charts: true,
        include_recommendations: true,
        scheduled: false,
        schedule_frequency: 'monthly',
        schedule_time: '09:00'
      },
      filtros: {
        fecha_desde: '',
        fecha_hasta: '',
        usuario_id: '',
        calidad_minima: ''
      }
    })

    // Methods
    const loadInitialData = async () => {
      try {
        // Load fincas
        const fincasResponse = await adminStore.getAllFincas()
        fincas.value = fincasResponse.data.results || []

        // Load users
        const usersResponse = await adminStore.getAllUsers()
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
        const response = await adminStore.getLotesByFinca(formData.parametros.finca_id)
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
        include_charts: true,
        include_recommendations: true,
        scheduled: false,
        schedule_frequency: 'monthly',
        schedule_time: '09:00'
      }
      
      // Generate default title based on type
      if (formData.tipo_reporte && !formData.titulo) {
        const typeNames = {
          'calidad': 'Reporte de Calidad',
          'finca': 'Reporte de Finca',
          'lote': 'Reporte de Lote',
          'usuario': 'Reporte de Usuario',
          'auditoria': 'Reporte de Auditoría',
          'personalizado': 'Reporte Personalizado'
        }
        formData.titulo = `${typeNames[formData.tipo_reporte]} - ${new Date().toLocaleDateString('es-ES')}`
      }
    }

    const onScheduledChange = () => {
      if (!formData.parametros.scheduled) {
        formData.parametros.schedule_frequency = 'monthly'
        formData.parametros.schedule_time = '09:00'
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

      return Object.keys(errors.value).length === 0
    }

    const generateReport = async () => {
      if (!validateForm()) {
        return
      }

      loading.value = true
      errors.value = {}

      try {
        const reportData = {
          tipo_reporte: formData.tipo_reporte,
          formato: formData.formato,
          titulo: formData.titulo.trim(),
          descripcion: formData.descripcion.trim(),
          parametros: { ...formData.parametros },
          filtros: { ...formData.filtros }
        }

        // Clean empty values
        Object.keys(reportData.parametros).forEach(key => {
          if (reportData.parametros[key] === '' || reportData.parametros[key] === null) {
            delete reportData.parametros[key]
          }
        })

        Object.keys(reportData.filtros).forEach(key => {
          if (reportData.filtros[key] === '' || reportData.filtros[key] === null) {
            delete reportData.filtros[key]
          }
        })

        const response = await adminStore.createReport(reportData)

        Swal.fire({
          icon: 'success',
          title: 'Reporte creado',
          text: 'El reporte ha sido enviado para generación. Te notificaremos cuando esté listo.',
          timer: 3000
        })

        emit('created', response.data)
        closeModal()

      } catch (error) {
        console.error('Error creating report:', error)
        
        if (error.response?.data) {
          const errorData = error.response.data
          
          // Handle field-specific errors
          if (errorData.tipo_reporte) {
            errors.value.tipo_reporte = Array.isArray(errorData.tipo_reporte) ? errorData.tipo_reporte[0] : errorData.tipo_reporte
          }
          if (errorData.formato) {
            errors.value.formato = Array.isArray(errorData.formato) ? errorData.formato[0] : errorData.formato
          }
          if (errorData.titulo) {
            errors.value.titulo = Array.isArray(errorData.titulo) ? errorData.titulo[0] : errorData.titulo
          }
          
          // Show general error if no specific field errors
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
      fincas,
      lotes,
      users,
      formData,
      loadLotes,
      onTypeChange,
      onScheduledChange,
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
}

.modal-container {
  background: white;
  border-radius: 10px;
  width: 95%;
  max-width: 800px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
}

.modal-header {
  padding: 20px;
  border-bottom: 1px solid #ecf0f1;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h3 {
  margin: 0;
  color: #2c3e50;
  font-size: 1.3rem;
}

.modal-header h3 i {
  margin-right: 10px;
  color: #3498db;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.2rem;
  color: #7f8c8d;
  cursor: pointer;
  padding: 5px;
  border-radius: 3px;
  transition: all 0.2s;
}

.close-btn:hover {
  background-color: #ecf0f1;
  color: #2c3e50;
}

.modal-body {
  padding: 20px;
}

.step-section {
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid #ecf0f1;
}

.step-section:last-child {
  border-bottom: none;
  margin-bottom: 0;
}

.step-section h4 {
  margin: 0 0 20px 0;
  color: #2c3e50;
  font-size: 1.1rem;
  display: flex;
  align-items: center;
  gap: 10px;
}

.step-number {
  background-color: #3498db;
  color: white;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.9rem;
  font-weight: bold;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.form-group.full-width {
  grid-column: 1 / -1;
}

.form-group label {
  font-weight: 500;
  color: #2c3e50;
  font-size: 0.9rem;
}

.form-group input,
.form-group select,
.form-group textarea {
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 5px;
  font-size: 14px;
  transition: border-color 0.2s;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #3498db;
  box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
}

.form-group input.error,
.form-group select.error,
.form-group textarea.error {
  border-color: #e74c3c;
}

.error-message {
  color: #e74c3c;
  font-size: 0.8rem;
}

.checkbox-group {
  display: flex;
  align-items: center;
}

.checkbox-label {
  display: flex;
  align-items: center;
  cursor: pointer;
  font-weight: normal;
  gap: 8px;
}

.checkbox-label input[type="checkbox"] {
  margin: 0;
  width: auto;
}

.modal-footer {
  padding: 20px;
  border-top: 1px solid #ecf0f1;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 5px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 5px;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-secondary {
  background-color: #95a5a6;
  color: white;
}

.btn-secondary:hover:not(:disabled) {
  background-color: #7f8c8d;
}

.btn-primary {
  background-color: #3498db;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background-color: #2980b9;
}

@media (max-width: 768px) {
  .modal-container {
    width: 98%;
    margin: 5px;
  }
  
  .form-row {
    grid-template-columns: 1fr;
    gap: 15px;
  }
  
  .modal-footer {
    flex-direction: column;
  }
  
  .btn {
    width: 100%;
    justify-content: center;
  }
}
</style>
