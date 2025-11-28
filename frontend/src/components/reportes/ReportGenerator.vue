<template>
  <div class="report-generator">
    <div class="card">
      <div class="card-header">
        <h5 class="card-title">
          <i class="fas fa-file-alt"></i>
          Generar Reporte
        </h5>
      </div>
      <div class="card-body">
        <form @submit.prevent="generarReporte">
          <!-- Tipo de Reporte -->
          <div class="form-group mb-3">
            <label for="tipo_reporte" class="form-label">Tipo de Reporte</label>
            <select
              id="tipo_reporte"
              v-model="formulario.tipo_reporte"
              class="form-select"
              required
            >
              <option value="">Seleccione un tipo</option>
              <option value="calidad">Reporte de Calidad</option>
              <option value="finca">Reporte de Finca</option>
              <option value="auditoria">Reporte de Auditoría</option>
              <option value="personalizado">Reporte Personalizado</option>
            </select>
          </div>

          <!-- Formato -->
          <div class="form-group mb-3">
            <label for="formato" class="form-label">Formato</label>
            <select
              id="formato"
              v-model="formulario.formato"
              class="form-select"
              required
            >
              <option value="">Seleccione un formato</option>
              <option value="pdf">PDF</option>
              <option value="excel">Excel</option>
              <option value="csv">CSV</option>
              <option value="json">JSON</option>
            </select>
          </div>

          <!-- Título -->
          <div class="form-group mb-3">
            <label for="titulo" class="form-label">Título del Reporte</label>
            <input
              id="titulo"
              v-model="formulario.titulo"
              type="text"
              class="form-control"
              placeholder="Ej: Reporte de Calidad - Enero 2024"
              required
            />
          </div>

          <!-- Descripción -->
          <div class="form-group mb-3">
            <label for="descripcion" class="form-label">Descripción (Opcional)</label>
            <textarea
              id="descripcion"
              v-model="formulario.descripcion"
              class="form-control"
              rows="3"
              placeholder="Descripción adicional del reporte..."
            ></textarea>
          </div>

          <!-- Filtros de Fecha -->
          <div v-if="formulario.tipo_reporte" class="row mb-3">
            <div class="col-md-6">
              <label for="fecha_desde" class="form-label">Fecha Desde</label>
              <input
                id="fecha_desde"
                v-model="formulario.filtros.fecha_desde"
                type="date"
                class="form-control"
              />
            </div>
            <div class="col-md-6">
              <label for="fecha_hasta" class="form-label">Fecha Hasta</label>
              <input
                id="fecha_hasta"
                v-model="formulario.filtros.fecha_hasta"
                type="date"
                class="form-control"
              />
            </div>
          </div>

          <!-- Parámetros específicos por tipo -->
          <div v-if="formulario.tipo_reporte === 'finca'" class="form-group mb-3">
            <label for="finca_id" class="form-label">Finca</label>
            <select
              id="finca_id"
              v-model="formulario.parametros.finca_id"
              class="form-select"
              required
            >
              <option value="">Seleccione una finca</option>
              <option
                v-for="finca in fincas"
                :key="finca.id"
                :value="finca.id"
              >
                {{ finca.nombre }} - {{ finca.ubicacion }}
              </option>
            </select>
          </div>

          <div v-if="formulario.tipo_reporte === 'personalizado'" class="form-group mb-3">
            <label class="form-label" id="custom-params-label">Parámetros Personalizados</label>
            <div class="row" role="group" aria-labelledby="custom-params-label">
              <div class="col-md-4">
                <div class="form-check">
                  <input
                    id="include_dimensions"
                    v-model="formulario.parametros.include_dimensions"
                    type="checkbox"
                    class="form-check-input"
                  />
                  <label for="include_dimensions" class="form-check-label">
                    Incluir Dimensiones
                  </label>
                </div>
              </div>
              <div class="col-md-4">
                <div class="form-check">
                  <input
                    id="include_weight"
                    v-model="formulario.parametros.include_weight"
                    type="checkbox"
                    class="form-check-input"
                  />
                  <label for="include_weight" class="form-check-label">
                    Incluir Peso
                  </label>
                </div>
              </div>
              <div class="col-md-4">
                <div class="form-check">
                  <input
                    id="include_confidence"
                    v-model="formulario.parametros.include_confidence"
                    type="checkbox"
                    class="form-check-input"
                  />
                  <label for="include_confidence" class="form-check-label">
                    Incluir Confianza
                  </label>
                </div>
              </div>
            </div>
          </div>

          <!-- Botones -->
          <div class="d-flex gap-2">
            <button
              type="submit"
              :disabled="generando"
              class="btn btn-primary"
              :class="{ 'loading': generando }"
            >
              <i v-if="generando" class="fas fa-spinner fa-spin"></i>
              <i v-else class="fas fa-file-alt"></i>
              {{ generando ? 'Generando...' : 'Generar Reporte' }}
            </button>
            <button
              type="button"
              @click="limpiarFormulario"
              class="btn btn-secondary"
            >
              <i class="fas fa-eraser"></i>
              Limpiar
            </button>
          </div>
        </form>

        <!-- Mensaje de éxito -->
        <div v-if="reporteGenerado" class="alert alert-success mt-3">
          <i class="fas fa-check-circle"></i>
          <strong>¡Reporte generado exitosamente!</strong><br>
          <small>
            ID: {{ reporteGenerado.id }} | 
            Estado: {{ reporteGenerado.estado }} |
            <a href="#" @click.prevent="verDetalles">Ver detalles</a>
          </small>
        </div>

        <!-- Mensaje de error -->
        <div v-if="error" class="alert alert-danger mt-3">
          <i class="fas fa-exclamation-circle"></i>
          {{ error }}
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useNotificationStore } from '@/stores/notifications'

export default {
  name: 'ReportGenerator',
  emits: ['reporte-generado'],
  setup(props, { emit }) {
    const authStore = useAuthStore()
    const notificationStore = useNotificationStore()
    
    const generando = ref(false)
    const error = ref('')
    const reporteGenerado = ref(null)
    const fincas = ref([])
    
    const formulario = reactive({
      tipo_reporte: '',
      formato: '',
      titulo: '',
      descripcion: '',
      parametros: {
        finca_id: '',
        include_dimensions: true,
        include_weight: true,
        include_confidence: true
      },
      filtros: {
        fecha_desde: '',
        fecha_hasta: ''
      }
    })
    
    const cargarFincas = async () => {
      try {
        const response = await fetch('/api/fincas/', {
          headers: {
            'Authorization': `Bearer ${authStore.token}`
          }
        })
        
        if (response.ok) {
          const data = await response.json()
          fincas.value = data.results || []
        }
      } catch (err) {
        console.error('Error cargando fincas:', err)
      }
    }
    
    const generarReporte = async () => {
      try {
        generando.value = true
        error.value = ''
        reporteGenerado.value = null
        
        const response = await fetch('/api/reportes/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${authStore.token}`
          },
          body: JSON.stringify(formulario)
        })
        
        const data = await response.json()
        
        if (!response.ok) {
          throw new Error(data.error || 'Error al generar el reporte')
        }
        
        reporteGenerado.value = data
        emit('reporte-generado', data)
        
        notificationStore.addNotification({
          type: 'success',
          title: 'Reporte generado',
          message: `El reporte "${data.titulo}" se está generando en segundo plano.`
        })
        
      } catch (err) {
        console.error('Error generando reporte:', err)
        error.value = err.message
        notificationStore.addNotification({
          type: 'error',
          title: 'Error al generar reporte',
          message: err.message
        })
      } finally {
        generando.value = false
      }
    }
    
    const limpiarFormulario = () => {
      Object.assign(formulario, {
        tipo_reporte: '',
        formato: '',
        titulo: '',
        descripcion: '',
        parametros: {
          finca_id: '',
          include_dimensions: true,
          include_weight: true,
          include_confidence: true
        },
        filtros: {
          fecha_desde: '',
          fecha_hasta: ''
        }
      })
      error.value = ''
      reporteGenerado.value = null
    }
    
    const verDetalles = () => {
      // Emitir evento para mostrar detalles del reporte
      emit('ver-detalles', reporteGenerado.value.id)
    }
    
    onMounted(() => {
      cargarFincas()
    })
    
    return {
      generando,
      error,
      reporteGenerado,
      fincas,
      formulario,
      generarReporte,
      limpiarFormulario,
      verDetalles
    }
  }
}
</script>

<style scoped>
.report-generator {
  max-width: 800px;
  margin: 0 auto;
}

.card {
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
}

.card-header {
  background-color: #f9fafb;
  border-bottom: 1px solid #e5e7eb;
  padding: 1rem 1.5rem;
}

.card-title {
  margin: 0;
  font-size: 1.125rem;
  font-weight: 600;
  color: #111827;
}

.card-title i {
  margin-right: 0.5rem;
  color: #3b82f6;
}

.card-body {
  padding: 1.5rem;
}

.form-label {
  font-weight: 500;
  color: #374151;
  margin-bottom: 0.5rem;
}

.form-control,
.form-select {
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  padding: 0.5rem 0.75rem;
  font-size: 0.875rem;
}

.form-control:focus,
.form-select:focus {
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-check-input:checked {
  background-color: #3b82f6;
  border-color: #3b82f6;
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  font-weight: 500;
  text-decoration: none;
  cursor: pointer;
  transition: all 0.2s ease-in-out;
}

.btn:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.btn-primary {
  background-color: #3b82f6;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background-color: #2563eb;
}

.btn-secondary {
  background-color: #6b7280;
  color: white;
}

.btn-secondary:hover:not(:disabled) {
  background-color: #4b5563;
}

.loading {
  opacity: 0.7;
}

.alert {
  padding: 0.75rem;
  border-radius: 0.375rem;
  font-size: 0.875rem;
}

.alert-success {
  background-color: #f0fdf4;
  border: 1px solid #bbf7d0;
  color: #166534;
}

.alert-danger {
  background-color: #fef2f2;
  border: 1px solid #fecaca;
  color: #dc2626;
}

.alert i {
  margin-right: 0.5rem;
}

.gap-2 {
  gap: 0.5rem;
}
</style>
