<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Sidebar -->
    <Sidebar
      :brand-name="'CacaoScan'"
      :user-name="userName"
      :user-role="userRole"
      :current-route="route.path"
      :active-section="'fincas'"
      :collapsed="isSidebarCollapsed"
      @menu-click="handleMenuClick"
      @logout="handleLogout"
      @toggle-collapse="toggleSidebarCollapse"
    />

    <!-- Main Content -->
    <div :class="isSidebarCollapsed ? 'lg:pl-20' : 'lg:pl-64'" class="w-full relative">
      <div class="min-h-screen bg-gray-50 py-6 px-4 sm:px-6 lg:px-8">
        <div class="max-w-7xl mx-auto">
          <!-- Header -->
          <div class="mb-8">
            <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
              <div>
                <h1 class="text-3xl font-bold text-gray-900 flex items-center gap-3">
                  <div class="p-2 bg-green-100 rounded-lg">
                    <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"></path>
                    </svg>
                  </div>
                  Lotes de {{ finca?.nombre || 'Finca' }}
                </h1>
                <p class="mt-2 text-gray-600">Gestiona y visualiza los lotes de esta finca</p>
              </div>
              <button 
                v-if="canCreate"
                @click="createLote" 
                class="inline-flex items-center gap-2 px-4 py-2.5 bg-green-600 text-white font-semibold rounded-lg shadow-sm hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 transition-all duration-200"
              >
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
                </svg>
                Nuevo Lote
              </button>
            </div>
          </div>

          <!-- Loading State -->
          <div v-if="loading" class="flex flex-col items-center justify-center py-20">
            <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600 mb-4"></div>
            <p class="text-gray-600">Cargando lotes...</p>
          </div>

          <!-- Error State -->
          <div v-else-if="error" class="bg-red-50 border-l-4 border-red-400 p-6 rounded-lg mb-6">
            <div class="flex items-start">
              <div class="flex-shrink-0">
                <svg class="h-6 w-6 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
              </div>
              <div class="ml-3 flex-1">
                <h3 class="text-lg font-semibold text-red-800 mb-2">Error al cargar lotes</h3>
                <p class="text-red-700 mb-4">{{ error }}</p>
                <button 
                  @click="loadLotes" 
                  class="inline-flex items-center gap-2 px-4 py-2 bg-red-600 text-white font-medium rounded-lg hover:bg-red-700 transition-colors"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
                  </svg>
                  Intentar nuevamente
                </button>
              </div>
            </div>
          </div>

          <!-- Content -->
          <div v-else>
            <!-- Stats Cards -->
            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
              <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow">
                <div class="flex items-center justify-between">
                  <div>
                    <p class="text-sm font-medium text-gray-600 mb-1">Total Lotes</p>
                    <p class="text-3xl font-bold text-gray-900">{{ stats.total }}</p>
                  </div>
                  <div class="p-3 bg-blue-100 rounded-lg">
                    <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                    </svg>
                  </div>
                </div>
              </div>

              <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow">
                <div class="flex items-center justify-between">
                  <div>
                    <p class="text-sm font-medium text-gray-600 mb-1">Activos</p>
                    <p class="text-3xl font-bold text-green-600">{{ stats.activos }}</p>
                  </div>
                  <div class="p-3 bg-green-100 rounded-lg">
                    <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                    </svg>
                  </div>
                </div>
              </div>

              <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow">
                <div class="flex items-center justify-between">
                  <div>
                    <p class="text-sm font-medium text-gray-600 mb-1">Cosechados</p>
                    <p class="text-3xl font-bold text-amber-600">{{ stats.cosechados }}</p>
                  </div>
                  <div class="p-3 bg-amber-100 rounded-lg">
                    <svg class="w-6 h-6 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                    </svg>
                  </div>
                </div>
              </div>

              <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow">
                <div class="flex items-center justify-between">
                  <div>
                    <p class="text-sm font-medium text-gray-600 mb-1">Con Análisis</p>
                    <p class="text-3xl font-bold text-purple-600">{{ stats.analisis }}</p>
                  </div>
                  <div class="p-3 bg-purple-100 rounded-lg">
                    <svg class="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
                    </svg>
                  </div>
                </div>
              </div>
            </div>

            <!-- Filters -->
            <div class="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mb-6">
              <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div class="md:col-span-2">
                  <label for="search" class="block text-sm font-medium text-gray-700 mb-2">
                    Buscar
                  </label>
                  <div class="relative">
                    <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                      <svg class="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
                      </svg>
                    </div>
                    <input 
                      type="text" 
                      id="search" 
                      v-model="filters.search" 
                      class="block w-full pl-10 pr-3 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 transition-colors"
                      placeholder="Buscar por identificador o variedad..."
                      @input="debouncedSearch"
                    >
                  </div>
                </div>

                <div>
                  <label for="estado" class="block text-sm font-medium text-gray-700 mb-2">
                    Estado
                  </label>
                  <select 
                    id="estado" 
                    v-model="filters.estado" 
                    class="block w-full px-3 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 transition-colors"
                  >
                    <option value="">Todos</option>
                    <option value="activo">Activo</option>
                    <option value="inactivo">Inactivo</option>
                    <option value="cosechado">Cosechado</option>
                  </select>
                </div>

                <div>
                  <label for="variedad" class="block text-sm font-medium text-gray-700 mb-2">
                    Variedad
                  </label>
                  <select 
                    id="variedad" 
                    v-model="filters.variedad" 
                    class="block w-full px-3 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 transition-colors"
                  >
                    <option value="">Todas</option>
                    <option v-for="variedad in variedades" :key="variedad" :value="variedad">
                      {{ variedad }}
                    </option>
                  </select>
                </div>
              </div>

              <div class="mt-4 flex justify-end">
                <button 
                  @click="clearFilters" 
                  class="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
                >
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                  </svg>
                  Limpiar filtros
                </button>
              </div>
            </div>

            <!-- Lotes Table -->
            <div class="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
              <div class="px-6 py-4 border-b border-gray-200 bg-gray-50">
                <h2 class="text-lg font-semibold text-gray-900">Lista de Lotes</h2>
              </div>

              <!-- Empty State -->
              <div v-if="filteredLotes.length === 0" class="text-center py-16 px-4">
                <div class="mx-auto w-24 h-24 bg-gray-100 rounded-full flex items-center justify-center mb-4">
                  <svg class="w-12 h-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"></path>
                  </svg>
                </div>
                <h3 class="text-lg font-semibold text-gray-900 mb-2">No se encontraron lotes</h3>
                <p class="text-gray-600 mb-6">Intenta ajustar los filtros de búsqueda o crea un nuevo lote</p>
                <button 
                  v-if="canCreate"
                  @click="createLote" 
                  class="inline-flex items-center gap-2 px-4 py-2 bg-green-600 text-white font-medium rounded-lg hover:bg-green-700 transition-colors"
                >
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
                  </svg>
                  Crear primer lote
                </button>
              </div>

              <!-- Table -->
              <div v-else class="overflow-x-auto">
                <table class="min-w-full divide-y divide-gray-200">
                  <thead class="bg-gray-50">
                    <tr>
                      <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Identificador
                      </th>
                      <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Variedad
                      </th>
                      <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Área (ha)
                      </th>
                      <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Estado
                      </th>
                      <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Plantación
                      </th>
                      <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Análisis
                      </th>
                      <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Acciones
                      </th>
                    </tr>
                  </thead>
                  <tbody class="bg-white divide-y divide-gray-200">
                    <tr v-for="lote in displayedLotes" :key="lote.id" class="hover:bg-gray-50 transition-colors">
                      <td class="px-6 py-4 whitespace-nowrap">
                        <div class="flex items-center gap-2">
                          <div class="p-1.5 bg-green-100 rounded">
                            <svg class="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"></path>
                            </svg>
                          </div>
                          <span class="font-semibold text-gray-900">{{ lote.identificador }}</span>
                        </div>
                      </td>
                      <td class="px-6 py-4 whitespace-nowrap">
                        <span class="text-gray-900">{{ lote.variedad }}</span>
                      </td>
                      <td class="px-6 py-4 whitespace-nowrap">
                        <span class="text-gray-900">{{ lote.area_hectareas }} ha</span>
                      </td>
                      <td class="px-6 py-4 whitespace-nowrap">
                        <span 
                          class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
                          :class="{
                            'bg-green-100 text-green-800': lote.estado === 'activo',
                            'bg-yellow-100 text-yellow-800': lote.estado === 'inactivo',
                            'bg-blue-100 text-blue-800': lote.estado === 'cosechado'
                          }"
                        >
                          {{ lote.estado_display || lote.estado }}
                        </span>
                      </td>
                      <td class="px-6 py-4 whitespace-nowrap text-gray-600">
                        {{ formatDate(lote.fecha_plantacion) }}
                      </td>
                      <td class="px-6 py-4 whitespace-nowrap">
                        <span 
                          v-if="lote.total_analisis > 0"
                          class="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800"
                        >
                          <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
                          </svg>
                          {{ lote.total_analisis }}
                        </span>
                        <span v-else class="text-gray-400 text-sm">Sin análisis</span>
                      </td>
                      <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <div class="flex items-center justify-end gap-2">
                          <button 
                            @click="viewLote(lote.id)" 
                            class="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                            title="Ver detalles"
                          >
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
                              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path>
                            </svg>
                          </button>
                          <button 
                            v-if="canEdit"
                            @click="editLote(lote.id)" 
                            class="p-2 text-gray-600 hover:bg-gray-50 rounded-lg transition-colors"
                            title="Editar"
                          >
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
                            </svg>
                          </button>
                          <button 
                            @click="analyzeLote(lote.id)" 
                            class="p-2 text-green-600 hover:bg-green-50 rounded-lg transition-colors"
                            title="Analizar"
                          >
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"></path>
                            </svg>
                          </button>
                        </div>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>

              <!-- Pagination -->
              <div v-if="totalPages > 1" class="px-6 py-4 border-t border-gray-200 bg-gray-50">
                <div class="flex items-center justify-between">
                  <div class="text-sm text-gray-700">
                    Mostrando página <span class="font-medium">{{ currentPage }}</span> de <span class="font-medium">{{ totalPages }}</span>
                  </div>
                  <div class="flex items-center gap-2">
                    <button 
                      @click="changePage(currentPage - 1)" 
                      :disabled="currentPage === 1"
                      class="px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    >
                      Anterior
                    </button>
                    <div class="flex items-center gap-1">
                      <button 
                        v-for="page in visiblePages" 
                        :key="page"
                        @click="changePage(page)" 
                        class="px-3 py-2 text-sm font-medium rounded-lg transition-colors"
                        :class="page === currentPage 
                          ? 'bg-green-600 text-white' 
                          : 'text-gray-700 bg-white border border-gray-300 hover:bg-gray-50'"
                      >
                        {{ page }}
                      </button>
                    </div>
                    <button 
                      @click="changePage(currentPage + 1)" 
                      :disabled="currentPage === totalPages"
                      class="px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    >
                      Siguiente
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useNotificationStore } from '@/stores/notifications'
import { usePagination } from '@/composables/usePagination'
import { useSidebarNavigation } from '@/composables/useSidebarNavigation'
import { getLotesByFinca, getFincaById } from '@/services/fincasApi'
import Sidebar from '@/components/layout/Common/Sidebar.vue'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const notificationStore = useNotificationStore()

// Sidebar navigation composable
const {
  isSidebarCollapsed,
  userName,
  userRole,
  handleMenuClick,
  toggleSidebarCollapse,
  handleLogout
} = useSidebarNavigation()

// Reactive data
const finca = ref(null)
const lotes = ref([])
const variedades = ref([])
const loading = ref(true)
const error = ref(null)

// Paginación usando composable
const pagination = usePagination(1, 10)

// Filters
const filters = reactive({
  search: '',
  estado: '',
  variedad: ''
})

// Computed
const fincaId = computed(() => route.params.id)

const canCreate = computed(() => {
  return authStore.userRole === 'admin' || 
         (authStore.userRole === 'farmer' && finca.value?.agricultor === authStore.user?.id)
})

const canEdit = computed(() => {
  return authStore.userRole === 'admin' || 
         (authStore.userRole === 'farmer' && finca.value?.agricultor === authStore.user?.id)
})

const filteredLotes = computed(() => {
  let filtered = lotes.value

  if (filters.search) {
    const search = filters.search.toLowerCase()
    filtered = filtered.filter(lote => 
      lote.identificador?.toLowerCase().includes(search) ||
      lote.variedad?.toLowerCase().includes(search)
    )
  }

  if (filters.estado) {
    filtered = filtered.filter(lote => lote.estado === filters.estado)
  }

  if (filters.variedad) {
    filtered = filtered.filter(lote => lote.variedad === filters.variedad)
  }

  return filtered
})

const stats = computed(() => {
  return {
    total: lotes.value.length,
    activos: lotes.value.filter(l => l.estado === 'activo').length,
    cosechados: lotes.value.filter(l => l.estado === 'cosechado').length,
    analisis: lotes.value.filter(l => l.total_analisis > 0).length
  }
})

// Actualizar totalItems en paginación cuando cambian los filteredLotes
watch(() => filteredLotes.value.length, (newTotal) => {
  pagination.updatePagination({
    page: pagination.currentPage.value,
    page_size: pagination.itemsPerPage.value,
    count: newTotal
  })
}, { immediate: true })

// Computed para compatibilidad con el template
const currentPage = computed(() => pagination.currentPage.value)
const totalPages = computed(() => pagination.totalPages.value)
const itemsPerPage = computed(() => pagination.itemsPerPage.value)

const visiblePages = computed(() => {
  const pages = []
  const start = Math.max(1, pagination.currentPage.value - 2)
  const end = Math.min(pagination.totalPages.value, start + 4)
  
  for (let i = start; i <= end; i++) {
    pages.push(i)
  }
  
  return pages
})

// Lotes mostrados en la página actual (paginación en cliente)
const displayedLotes = computed(() => {
  const start = (pagination.currentPage.value - 1) * pagination.itemsPerPage.value
  const end = start + pagination.itemsPerPage.value
  return filteredLotes.value.slice(start, end)
})

// Methods
const loadFinca = async () => {
  try {
    const data = await getFincaById(fincaId.value)
    finca.value = data
  } catch (err) {
    }
}

const loadLotes = async () => {
  try {
    loading.value = true
    error.value = null
    
    const data = await getLotesByFinca(fincaId.value)
    
    if (data && typeof data === 'object') {
      if (data.lotes && Array.isArray(data.lotes)) {
        lotes.value = data.lotes
        if (data.finca && !finca.value) {
          finca.value = data.finca
        }
      } else if (data.results && Array.isArray(data.results)) {
        lotes.value = data.results
      } else if (Array.isArray(data)) {
        lotes.value = data
      } else {
        lotes.value = []
      }
    } else if (Array.isArray(data)) {
      lotes.value = data
    } else {
      lotes.value = []
    }
    
    variedades.value = [...new Set(lotes.value.map(l => l.variedad).filter(Boolean))].sort()
    
  } catch (err) {
    const errorMessage = err.response?.data?.error || err.response?.data?.details || err.message || 'Error al cargar los lotes'
    error.value = errorMessage
    
    if (err.response?.status === 403) {
      error.value = 'No tienes permisos para ver los lotes de esta finca'
    } else if (err.response?.status === 404) {
      error.value = 'La finca no existe o no tienes acceso a ella'
    }
  } finally {
    loading.value = false
  }
}

const createLote = () => {
  router.push(`/fincas/${fincaId.value}/lotes/new`)
}

const viewLote = (loteId) => {
  router.push(`/lotes/${loteId}`)
}

const editLote = (loteId) => {
  router.push(`/lotes/${loteId}/edit`)
}

const analyzeLote = (loteId) => {
  router.push(`/analisis/new?lote=${loteId}`)
}

const clearFilters = () => {
  filters.search = ''
  filters.estado = ''
  filters.variedad = ''
  pagination.goToPage(1)
}

const changePage = (page) => {
  if (page >= 1 && page <= totalPages.value) {
    pagination.goToPage(page)
  }
}

const formatDate = (dateString) => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleDateString('es-CO', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

// Debounced search
let searchTimeout = null
const debouncedSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    pagination.goToPage(1)
  }, 300)
}

// Watchers
watch(() => filters.estado, () => {
  pagination.goToPage(1)
})

watch(() => filters.variedad, () => {
  pagination.goToPage(1)
})

// Lifecycle
onMounted(() => {
  loadFinca()
  loadLotes()
})
</script>

<style scoped>
/* Transiciones suaves */
.transition-colors {
  transition-property: color, background-color, border-color;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 150ms;
}

.transition-shadow {
  transition-property: box-shadow;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 150ms;
}

/* Animación de carga */
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.animate-spin {
  animation: spin 1s linear infinite;
}
</style>
