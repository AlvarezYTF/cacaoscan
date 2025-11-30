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
              <option
                v-for="tipo in tipoReporteOpciones"
                :key="tipo.value"
                :value="tipo.value"
              >
                {{ tipo.label }}
              </option>
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
              <option
                v-for="formato in formatoOpciones"
                :key="formato.value"
                :value="formato.value"
              >
                {{ formato.label }}
              </option>
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
            <div class="form-label" id="custom-params-label">Parámetros Personalizados</div>
            <fieldset class="row" aria-labelledby="custom-params-label">
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
            </fieldset>
          </div>

          <!-- Botones -->
          <div class="d-flex gap-2">
            <button
              type="submit"
              :disabled="generating"
              class="btn btn-primary"
              :class="{ 'loading': generating }"
            >
              <i v-if="generating" class="fas fa-spinner fa-spin"></i>
              <i v-else class="fas fa-file-alt"></i>
              {{ generating ? 'Generando...' : 'Generar Reporte' }}
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
            Estado: {{ reporteGenerado.estado_display || reporteGenerado.estado }} |
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

<script setup>
import { onMounted, computed } from 'vue'
import { useReports } from '@/composables/useReports'
import { useFincas } from '@/composables/useFincas'

const emit = defineEmits(['reporte-generado', 'ver-detalles'])

const {
  formData,
  generating,
  error,
  reportTypes,
  reportFormats,
  generateReport: generateReportFromComposable,
  resetForm
} = useReports()

// Use fincas composable
const { fincas, loadFincas } = useFincas()

const reporteGenerado = ref(null)

const tipoReporteOpciones = computed(() => reportTypes.value.map(type => ({
  value: type.value,
  label: type.label
})))

const formatoOpciones = computed(() => reportFormats.value.map(format => ({
  value: format.value,
  label: format.label
})))

const cargarFincas = async () => {
  try {
    await loadFincas({}, 1, 100) // Load first 100 fincas
  } catch (err) {
    console.error('Error cargando fincas:', err)
  }
}

const generarReporte = async () => {
  try {
    const result = await generateReportFromComposable()
    reporteGenerado.value = result
    emit('reporte-generado', result)
  } catch (err) {
    console.error('Error generando reporte:', err)
  }
}

const limpiarFormulario = () => {
  resetForm()
  reporteGenerado.value = null
}

const verDetalles = () => {
  if (reporteGenerado.value) {
    emit('ver-detalles', reporteGenerado.value.id)
  }
}

onMounted(() => {
  cargarFincas()
})
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
  background-color: #2563eb;
  color: #ffffff;
}

.btn-primary:hover:not(:disabled) {
  background-color: #2563eb;
}

.btn-secondary {
  background-color: #6b7280;
  color: #ffffff;
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
  color: #991b1b;
}

.alert i {
  margin-right: 0.5rem;
}

.gap-2 {
  gap: 0.5rem;
}
</style>
