<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Sidebar -->
    <Sidebar 
      :brand-name="'CacaoScan'"
      :user-name="userName"
      :user-role="userRole"
      :current-route="$route.path"
      :active-section="activeSection"
      :collapsed="isSidebarCollapsed"
      @menu-click="handleMenuClick"
      @logout="handleLogout"
      @toggle-collapse="toggleSidebarCollapse"
    />

    <!-- Main Content -->
    <div :class="isSidebarCollapsed ? 'lg:pl-20' : 'lg:pl-64'">
      <main class="py-6 px-4 sm:px-6 lg:px-8">
        <div class="max-w-7xl mx-auto">
          <!-- Header -->
          <div class="mb-8">
            <div class="bg-white rounded-xl shadow-lg border border-gray-200 p-6">
              <div class="flex justify-between items-center">
                <div>
              <h1 class="text-3xl font-bold text-gray-900">Reportes</h1>
              <p class="text-gray-600 mt-1">Genera y visualiza reportes detallados de tus análisis</p>
                </div>
                <button
                  @click="showGeneratorModal = true"
                  class="bg-green-600 hover:bg-green-700 text-white px-6 py-3 rounded-lg font-medium flex items-center gap-2 transition-colors"
                >
                  <i class="fas fa-plus"></i>
                  Nuevo Reporte
                </button>
              </div>
            </div>
          </div>

          <!-- Loading State -->
          <div v-if="loading" class="bg-white rounded-xl shadow-lg border border-gray-200 p-6">
            <div class="flex items-center justify-center py-12">
              <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600"></div>
            </div>
          </div>

          <!-- Error State -->
          <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-xl p-6 mb-6">
            <div class="flex items-center gap-3">
              <i class="fas fa-exclamation-circle text-red-600"></i>
              <p class="text-red-800">{{ error }}</p>
            </div>
          </div>

          <!-- Reports List -->
          <div v-else-if="reports.length > 0" class="space-y-4">
            <div
              v-for="report in reports"
              :key="report.id"
              class="bg-white rounded-xl shadow-lg border border-gray-200 p-6 hover:shadow-xl transition-shadow"
            >
              <div class="flex justify-between items-start">
                <div class="flex-1">
                  <div class="flex items-center gap-3 mb-2">
                    <h3 class="text-xl font-semibold text-gray-900">{{ report.titulo }}</h3>
                    <span
                      :class="getStatusBadgeClass(report.estado)"
                      class="px-3 py-1 rounded-full text-xs font-medium"
                    >
                      {{ getStatusLabel(report.estado) }}
                    </span>
                    <span
                      class="px-3 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800"
                    >
                      {{ getFormatLabel(report.formato) }}
                    </span>
                  </div>
                  <p v-if="report.descripcion" class="text-gray-600 mb-3">{{ report.descripcion }}</p>
                  <div class="flex flex-wrap gap-4 text-sm text-gray-500">
                    <span>
                      <i class="fas fa-calendar mr-1"></i>
                      Solicitado: {{ formatDate(report.fecha_solicitud) }}
                    </span>
                    <span v-if="report.fecha_generacion">
                      <i class="fas fa-check-circle mr-1"></i>
                      Generado: {{ formatDate(report.fecha_generacion) }}
                    </span>
                    <span v-if="report.tamano_archivo_mb">
                      <i class="fas fa-file mr-1"></i>
                      {{ formatFileSize(report.tamano_archivo_mb * 1024 * 1024) }}
                    </span>
                  </div>
                </div>
                <div class="flex gap-2 ml-4">
                  <button
                    v-if="report.estado === 'COMPLETADO'"
                    @click="downloadReport(report.id)"
                    class="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg text-sm font-medium flex items-center gap-2 transition-colors"
                  >
                    <i class="fas fa-download"></i>
                    Descargar
                  </button>
                  <button
                    v-if="report.estado === 'GENERANDO' || report.estado === 'PENDIENTE'"
                    @click="checkReportStatus(report.id)"
                    class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium flex items-center gap-2 transition-colors"
                  >
                    <i class="fas fa-sync-alt"></i>
                    Actualizar
                  </button>
                </div>
              </div>
            </div>

            <!-- Pagination -->
            <div v-if="pagination.totalPages > 1" class="flex justify-center items-center gap-4 mt-6">
              <button
                @click="loadReports(pagination.currentPage - 1)"
                :disabled="pagination.currentPage === 1"
                class="px-4 py-2 rounded-lg border border-gray-300 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
              >
                Anterior
              </button>
              <span class="text-gray-600">
                Página {{ pagination.currentPage }} de {{ pagination.totalPages }}
              </span>
              <button
                @click="loadReports(pagination.currentPage + 1)"
                :disabled="pagination.currentPage === pagination.totalPages"
                class="px-4 py-2 rounded-lg border border-gray-300 disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
              >
                Siguiente
              </button>
            </div>
          </div>
        
          <!-- Empty State -->
          <div v-else class="bg-white rounded-xl shadow-lg border border-gray-200 p-12 text-center">
            <i class="fas fa-file-alt text-6xl text-gray-400 mb-4"></i>
            <h3 class="text-xl font-semibold text-gray-900 mb-2">No hay reportes aún</h3>
            <p class="text-gray-600 mb-6">Genera tu primer reporte para comenzar</p>
            <button
              @click="showGeneratorModal = true"
              class="bg-green-600 hover:bg-green-700 text-white px-6 py-3 rounded-lg font-medium inline-flex items-center gap-2 transition-colors"
            >
              <i class="fas fa-plus"></i>
              Crear Reporte
            </button>
          </div>
        </div>
      </main>
    </div>

    <!-- Report Generator Modal -->
    <Teleport to="body">
      <ReportGeneratorModal
        v-if="showGeneratorModal"
        @close="showGeneratorModal = false"
        @created="handleReportCreated"
      />
    </Teleport>
  </div>
</template>

<script setup>
// 1. Vue core
import { ref, onMounted, computed } from 'vue'

// 2. Composables
import { useSidebarNavigation } from '@/composables/useSidebarNavigation'
import { useReports } from '@/composables/useReports'
import { useDateFormatting } from '@/composables/useDateFormatting'

// 3. Stores
import { useReportsStore } from '@/stores/reports'

// 4. Components
import Sidebar from '@/components/layout/Common/Sidebar.vue'
import ReportGeneratorModal from '@/components/reports/ReportGeneratorModal.vue'

// Sidebar navigation composable
const {
  isSidebarCollapsed,
  userName,
  userRole,
  handleMenuClick,
  toggleSidebarCollapse,
  handleLogout
} = useSidebarNavigation()

// Reports store
const reportsStore = useReportsStore()

// Reports composable for download and status check
const {
  downloadReport: downloadReportFromComposable,
  checkReportStatus: checkReportStatusFromComposable
} = useReports()

// Date formatting
const { formatDate } = useDateFormatting()

// Computed from store
const reports = computed(() => reportsStore.reports)
const loading = computed(() => reportsStore.loading)
const error = computed(() => reportsStore.error)
const pagination = computed(() => reportsStore.pagination)

// State
const activeSection = ref('reports')
const showGeneratorModal = ref(false)

// Methods
const loadReports = async (page = 1) => {
  await reportsStore.fetchReports({ page, page_size: 10 })
}

const downloadReport = async (reportId) => {
  try {
    await downloadReportFromComposable(reportId)
  } catch (err) {
    console.error('Error downloading report:', err)
  }
}

const checkReportStatus = async (reportId) => {
  try {
    await checkReportStatusFromComposable(reportId)
    // Reload reports after checking status
    await loadReports(pagination.value.currentPage)
  } catch (err) {
    console.error('Error checking report status:', err)
  }
}

const handleReportCreated = async () => {
  showGeneratorModal.value = false
  await loadReports(1)
}

const getStatusBadgeClass = (status) => {
  const classes = {
    'COMPLETADO': 'bg-green-100 text-green-800',
    'GENERANDO': 'bg-yellow-100 text-yellow-800',
    'PENDIENTE': 'bg-blue-100 text-blue-800',
    'FALLIDO': 'bg-red-100 text-red-800'
  }
  return classes[status] || 'bg-gray-100 text-gray-800'
}

const getStatusLabel = (status) => {
  const labels = {
    'COMPLETADO': 'Completado',
    'GENERANDO': 'Generando',
    'PENDIENTE': 'Pendiente',
    'FALLIDO': 'Fallido'
  }
  return labels[status] || status
}

const getFormatLabel = (format) => {
  const labels = {
    'EXCEL': 'Excel',
    'PDF': 'PDF',
    'CSV': 'CSV',
    'JSON': 'JSON'
  }
  return labels[format] || format
}

const formatFileSize = (bytes) => {
  if (!bytes || bytes === 0) return 'N/A'
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(1024))
  return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i]
}

// Lifecycle
onMounted(async () => {
  await loadReports(1)
})
</script>

<style scoped>
/* Additional styles if needed */
</style>
