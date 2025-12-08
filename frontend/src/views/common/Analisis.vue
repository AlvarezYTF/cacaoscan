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

    <!-- Main Content with Navbar -->
    <div :class="isSidebarCollapsed ? 'lg:pl-20' : 'lg:pl-64'">
      <!-- Page Content -->
      <main class="py-6 px-4 sm:px-6 lg:px-8">
        <div class="max-w-5xl mx-auto">
          <!-- Page Header -->
          <div class="mb-8">
            <div class="bg-gradient-to-r from-white to-green-50 rounded-2xl border-2 border-gray-200 hover:shadow-xl hover:border-green-300 transition-all duration-300">
              <div class="px-8 py-6">
                <div class="flex items-center gap-4">
                  <div class="p-3 bg-gradient-to-br from-green-500 to-green-600 rounded-2xl shadow-lg">
                    <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                    </svg>
                  </div>
                  <div>
                    <h1 class="text-3xl font-bold text-gray-900 mb-1">Nuevo Análisis de Lote</h1>
                    <p class="text-gray-600 text-base">Sube imágenes de granos de cacao y completa la información del lote para iniciar un análisis de calidad detallado y preciso.</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Main Content Card -->
          <div class="bg-white shadow-lg border-2 border-gray-200 rounded-2xl overflow-hidden">
            <div class="p-8 space-y-8">
              <!-- Progress Indicator (solo mientras se sube/procesa) -->
              <ProgressIndicator v-if="isUploading || isSubmitting" :progress="uploadProgress" label="Procesando imágenes..." />

              <!-- Success Alert (mostrar resultados cuando existan) -->
              <div v-if="analysisResult && !isUploading && !isSubmitting" class="bg-gradient-to-br from-green-50 to-emerald-50 border-2 border-green-300 rounded-xl p-8 shadow-lg">
                <div class="flex items-start">
                  <div class="flex-shrink-0">
                    <div class="flex items-center justify-center w-16 h-16 bg-green-500 rounded-full">
                      <svg class="h-10 w-10 text-white" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                      </svg>
                    </div>
                  </div>
                  <div class="ml-6 flex-1">
                    <h3 class="text-2xl font-bold text-green-900 mb-4">
                      Análisis completado exitosamente
                    </h3>
                    
                    <!-- Estadísticas principales -->
                    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
                      <div class="bg-white rounded-lg p-4 border border-green-200">
                        <p class="text-sm text-gray-600 mb-1">Lote Analizado</p>
                        <p class="text-lg font-semibold text-green-900">{{ analysisResult.lote_name }}</p>
                      </div>
                      
                      <div class="bg-white rounded-lg p-4 border border-green-200">
                        <p class="text-sm text-gray-600 mb-1">Imágenes Procesadas</p>
                        <p class="text-lg font-semibold text-green-900">
                          {{ analysisResult.processed_images }}/{{ analysisResult.total_images }}
                        </p>
                      </div>
                      
                      <div class="bg-white rounded-lg p-4 border border-green-200">
                        <p class="text-sm text-gray-600 mb-1">Confianza Promedio</p>
                        <p class="text-lg font-semibold text-green-900">
                          {{ (analysisResult.average_confidence * 100).toFixed(1) }}%
                        </p>
                      </div>
                    </div>

                    <!-- Estadísticas adicionales -->
                    <div v-if="analysisResult.average_dimensions || analysisResult.total_weight" class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                      <div v-if="analysisResult.average_dimensions && analysisResult.average_dimensions.alto" class="bg-white rounded-lg p-3 border border-green-200">
                        <p class="text-xs text-gray-600 mb-1">Alto Promedio</p>
                        <p class="text-base font-semibold text-green-900">{{ (analysisResult.average_dimensions.alto || 0).toFixed(2) }} mm</p>
                      </div>
                      
                      <div v-if="analysisResult.average_dimensions && analysisResult.average_dimensions.ancho" class="bg-white rounded-lg p-3 border border-green-200">
                        <p class="text-xs text-gray-600 mb-1">Ancho Promedio</p>
                        <p class="text-base font-semibold text-green-900">{{ (analysisResult.average_dimensions.ancho || 0).toFixed(2) }} mm</p>
                      </div>
                      
                      <div v-if="analysisResult.average_dimensions && analysisResult.average_dimensions.grosor" class="bg-white rounded-lg p-3 border border-green-200">
                        <p class="text-xs text-gray-600 mb-1">Grosor Promedio</p>
                        <p class="text-base font-semibold text-green-900">{{ (analysisResult.average_dimensions.grosor || 0).toFixed(2) }} mm</p>
                      </div>
                      
                      <div v-if="analysisResult.total_weight" class="bg-white rounded-lg p-3 border border-green-200">
                        <p class="text-xs text-gray-600 mb-1">Peso Total</p>
                        <p class="text-base font-semibold text-green-900">{{ (analysisResult.total_weight || 0).toFixed(2) }} g</p>
                      </div>
                    </div>

                    <!-- Tiempo de procesamiento -->
                    <div v-if="analysisResult.processing_time_seconds" class="mb-4">
                      <p class="text-sm text-green-700">
                        <svg class="inline w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        Tiempo de procesamiento: {{ analysisResult.processing_time_seconds }} segundos
                      </p>
                    </div>

                    <!-- Resultados individuales por imagen -->
                    <div v-if="analysisResult.predictions && analysisResult.predictions.length > 0" class="mt-6">
                      <h4 class="text-lg font-semibold text-green-900 mb-4">Resultados Individuales</h4>
                      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 max-h-96 overflow-y-auto">
                        <div 
                          v-for="(prediction, index) in analysisResult.predictions" 
                          :key="index"
                          :class="[
                            'bg-white rounded-lg p-4 border-2 transition-all duration-200',
                            prediction.success === false || !prediction || prediction.error
                              ? 'border-red-300 bg-red-50' 
                              : 'border-green-200 hover:border-green-400 shadow-sm'
                          ]"
                        >
                          <div class="flex items-center justify-between mb-2">
                            <span class="text-sm font-semibold text-gray-700">Imagen #{{ index + 1 }}</span>
                            <span 
                              v-if="prediction.success === false || prediction.error"
                              class="px-2 py-1 bg-red-500 text-white text-xs rounded-full"
                            >
                              Error
                            </span>
                            <span 
                              v-else-if="prediction.model_version"
                              class="px-2 py-1 bg-blue-500 text-white text-xs rounded-full"
                            >
                              v{{ prediction.model_version }}
                            </span>
                          </div>
                          
                          <div v-if="prediction.success === false || prediction.error" class="text-sm text-red-600">
                            {{ prediction.error || 'Error desconocido' }}
                          </div>
                          
                          <div v-else-if="prediction && !prediction.error" class="space-y-2">
                            <div class="grid grid-cols-2 gap-2">
                              <div>
                                <p class="text-xs text-gray-600">Alto</p>
                                <p class="text-sm font-semibold text-green-900">{{ (prediction.alto_mm || 0).toFixed(2) }} mm</p>
                                <p v-if="prediction.confidences && prediction.confidences.alto" class="text-xs text-gray-500">
                                  Conf: {{ ((prediction.confidences.alto || 0) * 100).toFixed(0) }}%
                                </p>
                              </div>
                              <div>
                                <p class="text-xs text-gray-600">Ancho</p>
                                <p class="text-sm font-semibold text-green-900">{{ (prediction.ancho_mm || 0).toFixed(2) }} mm</p>
                                <p v-if="prediction.confidences && prediction.confidences.ancho" class="text-xs text-gray-500">
                                  Conf: {{ ((prediction.confidences.ancho || 0) * 100).toFixed(0) }}%
                                </p>
                              </div>
                              <div>
                                <p class="text-xs text-gray-600">Grosor</p>
                                <p class="text-sm font-semibold text-green-900">{{ (prediction.grosor_mm || 0).toFixed(2) }} mm</p>
                                <p v-if="prediction.confidences && prediction.confidences.grosor" class="text-xs text-gray-500">
                                  Conf: {{ ((prediction.confidences.grosor || 0) * 100).toFixed(0) }}%
                                </p>
                              </div>
                              <div>
                                <p class="text-xs text-gray-600">Peso</p>
                                <p class="text-sm font-semibold text-green-900">{{ (prediction.peso_g || 0).toFixed(2) }} g</p>
                                <p v-if="prediction.confidences && prediction.confidences.peso" class="text-xs text-gray-500">
                                  Conf: {{ ((prediction.confidences.peso || 0) * 100).toFixed(0) }}%
                                </p>
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>

                    <!-- Botones de acción -->
                    <div class="flex flex-col sm:flex-row gap-3 mt-6">
                      <router-link 
                        :to="{ name: 'LoteDetail', params: { id: analysisResult.lote_id } }"
                        class="inline-flex items-center justify-center px-6 py-3 bg-green-600 text-white text-base font-semibold rounded-lg hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 transition-colors duration-200 shadow-md"
                      >
                        Ver resultados detallados
                        <svg class="ml-2 h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
                        </svg>
                      </router-link>
                      
                      <button
                        @click="resetAndCreateNew"
                        type="button"
                        class="inline-flex items-center justify-center px-6 py-3 bg-white text-green-700 text-base font-semibold rounded-lg hover:bg-green-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 transition-colors duration-200 border-2 border-green-300 shadow-md"
                      >
                        Crear nuevo análisis
                        <svg class="ml-2 h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                        </svg>
                      </button>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Batch Info Form mejorado (ocultar cuando hay resultados) -->
              <div v-if="!analysisResult && !isSubmitting && !isUploading" class="bg-gradient-to-br from-gray-50 to-white border-2 border-gray-200 rounded-2xl p-8 shadow-sm">
                <div class="flex items-center gap-3 mb-6">
                  <div class="p-2 bg-green-100 rounded-xl">
                    <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                    </svg>
                  </div>
                  <h2 class="text-2xl font-bold text-gray-900">Información del Lote</h2>
                </div>
                <BatchInfoForm 
                  v-model="batchData" 
                  :errors="formErrors" 
                  :user-role="userRole"
                  :user-name="userName"
                  :user-id="authStore.user?.id"
                  @update:modelValue="updateBatchData" 
                />
              </div>

              <!-- Image Capture Section (ocultar cuando hay resultados) -->
              <div v-if="!analysisResult && !isSubmitting && !isUploading" class="space-y-6">
                <div class="text-center">
                  <h2 class="text-2xl font-semibold text-gray-900 mb-3">Imágenes del Lote</h2>
                  <p class="text-gray-600 text-lg">Captura fotos de alta calidad de los granos de cacao para un análisis preciso</p>
                </div>

                <!-- Tabs -->
                <div class="bg-gray-50 border-2 border-gray-200 rounded-2xl p-2">
                  <nav class="flex space-x-2">
                    <button
                      v-for="tab in tabs"
                      :key="tab.name"
                      @click="currentTab = tab.name"
                      type="button"
                      :class="[
                        currentTab === tab.name
                          ? 'bg-gradient-to-r from-green-600 to-green-700 text-white shadow-lg'
                          : 'text-gray-600 hover:text-green-600 hover:bg-white',
                        'flex-1 py-3 px-4 text-base font-semibold rounded-xl transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500'
                      ]"
                    >
                      {{ tab.label }}
                    </button>
                  </nav>
                </div>

                <!-- Tab Content -->
                <div class="mt-6">
                  <!-- File Upload Tab -->
                  <div v-if="currentTab === 'upload'" class="bg-gray-50 border border-gray-200 rounded-2xl p-8">
                    <ImageUploader
                      :model-value="images"
                      @update:modelValue="handleImageUpdate"
                    />
                  </div>

                  <!-- Camera Capture Tab -->
                  <div v-else-if="currentTab === 'camera'" class="space-y-6">
                    <div class="bg-gray-50 rounded-lg p-6">
                      <CameraCapture @capture="handleCapturedImage" />
                    </div>

                    <!-- All Images Preview -->
                    <div v-if="images.length > 0" class="bg-white border-2 border-gray-200 rounded-2xl p-8 shadow-sm">
                      <div class="flex items-center gap-3 mb-6">
                        <div class="p-2 bg-green-100 rounded-xl">
                          <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                          </svg>
                        </div>
                        <h3 class="text-xl font-bold text-gray-900">Todas las imágenes</h3>
                        <span class="px-3 py-1 bg-green-600 text-white rounded-full text-sm font-bold">{{ images.length }}</span>
                      </div>
                      <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
                        <div v-for="(img, index) in images" :key="getImageKey(img, index)" class="relative group">
                          <div class="aspect-square rounded-2xl overflow-hidden bg-gray-200 border-2 border-gray-200 group-hover:border-green-300 transition-all duration-300">
                            <img 
                              :src="getImageUrl(img, index)" 
                              :alt="`Imagen ${index + 1} del análisis de cacao`" 
                              class="w-full h-full object-cover group-hover:scale-110 transition-transform duration-300"
                              @error="handleImageError"
                              @load="handleImageLoad"
                            />
                          </div>
                          <button
                            @click.stop="removeImageByIndex(index)"
                            type="button"
                            class="absolute -top-2 -right-2 bg-red-500 text-white rounded-full w-7 h-7 flex items-center justify-center shadow-lg hover:bg-red-600 hover:scale-110 transition-all duration-200 z-10"
                            title="Eliminar foto"
                          >
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                            </svg>
                          </button>
                          <div class="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-10 transition-all duration-200 rounded-2xl pointer-events-none"></div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
          </div>

              <!-- Botón de acción final (ocultar cuando hay resultados) -->
              <div v-if="!analysisResult && !isSubmitting && !isUploading" class="bg-gradient-to-br from-green-50 to-emerald-50 border-2 border-green-300 rounded-2xl p-8 shadow-sm">
                <div class="text-center mb-6">
                  <div class="flex items-center justify-center mb-3">
                    <div class="p-2 bg-green-600 rounded-full">
                      <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"></path>
                      </svg>
                    </div>
                  </div>
                  <h3 class="text-2xl font-bold text-green-900 mb-2">¿Listo para analizar?</h3>
                  <p class="text-green-700 text-lg">Revisa que toda la información esté completa antes de continuar</p>
                </div>
                
                <button
                  type="button"
                  @click="submitAnalysis"
                  :disabled="isSubmitting || !isFormValid"
                  class="group w-full flex justify-center items-center gap-2 py-4 px-6 border border-transparent rounded-xl shadow-xl text-base font-bold text-white bg-gradient-to-r from-green-600 to-green-700 hover:from-green-700 hover:to-green-800 focus:outline-none focus:ring-4 focus:ring-green-500/50 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300 hover:shadow-2xl active:scale-[0.98]"
                >
                  <svg v-if="isSubmitting" class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  
                  <svg v-else class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                  </svg>
                  
                  {{ isSubmitting ? 'Procesando análisis...' : 'Iniciar Análisis de Calidad' }}
                </button>
                
                <div v-if="!isFormValid && (isSubmitting || Object.keys(formErrors).length > 0)" class="mt-4 text-center">
                  <div class="inline-flex items-center px-5 py-3 bg-amber-50 border-2 border-amber-300 rounded-xl shadow-sm">
                    <div class="p-1.5 bg-amber-200 rounded-lg mr-3">
                      <svg class="w-5 h-5 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
                      </svg>
                    </div>
                    <p class="text-sm text-amber-800 font-bold">
                      Falta: {{ 
                        !batchData.name || !batchData.name.trim() ? 'Nombre del lote' :
                        !batchData.collectionDate ? 'Fecha de recolección' :
                        !batchData.farm ? 'Finca' :
                        !batchData.genetics || !batchData.genetics.trim() ? 'Genética' :
                        !images.length ? 'Al menos una imagen' : ''
                      }}
                    </p>
                  </div>
                </div>
              </div>

              <!-- Error Alert -->
              <div v-if="error" class="bg-red-50 border-2 border-red-300 rounded-2xl p-8 shadow-sm">
                <div class="flex items-start gap-4">
                  <div class="p-2 bg-red-100 rounded-xl">
                    <svg class="h-7 w-7 text-red-600" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                      <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
                    </svg>
                  </div>
                  <div class="flex-1">
                    <h3 class="text-xl font-bold text-red-900 mb-2">
                      Error en el análisis
                    </h3>
                    <p class="text-base text-red-800">
                      {{ error }}
                    </p>
                  </div>
                </div>
              </div>
        </div>
      </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
// 1. Vue core
import { ref, computed, onMounted, watch, nextTick } from 'vue'

// 2. Vue router
import { useRouter, useRoute } from 'vue-router'

// 3. Components
import Sidebar from '@/components/layout/Common/Sidebar.vue'
import ProgressIndicator from '@/components/admin/AdminAnalisisComponents/ProgressIndicator.vue'
import BatchInfoForm from '@/components/admin/AdminAnalisisComponents/BatchInfoForm.vue'
import ImageUploader from '@/components/admin/AdminAnalisisComponents/ImageUploader.vue'
import CameraCapture from '@/components/admin/AdminAnalisisComponents/CameraCapture.vue'

// 4. Stores
import { useAuthStore } from '@/stores/auth'
import { useAnalysisStore } from '@/stores/analysis'

// 5. Composables
import { useSidebarNavigation } from '@/composables/useSidebarNavigation'

// Router and stores
const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()
const analysisStore = useAnalysisStore()

// Sidebar navigation composable
const {
  isSidebarCollapsed,
  userName,
  userRole: computedUserRole,
  handleMenuClick,
  toggleSidebarCollapse,
  handleLogout
} = useSidebarNavigation()

// Local state
const batchData = ref({
  name: '',
  collectionDate: '',
  origin: '',
  notes: '',
  farm: '',
  originPlace: '',
  genetics: '',
  farmer: ''
})

const images = ref([])
const capturedImages = ref([])
const currentTab = ref('upload')
const isSubmitting = ref(false)
const formErrors = ref({})
const analysisResult = ref(null)
const activeSection = ref('analysis')
const imageUrls = ref({})

// Tabs configuration
const tabs = [
  { name: 'upload', label: 'Subir imágenes' },
  { name: 'camera', label: 'Tomar foto' }
]

// Watch for changes in captured images and update the main images array
watch(capturedImages, (newVal, oldVal) => {
  // Crear claves para comparar
  const newCapturedKeys = newVal.map(img => {
    if (img instanceof File) {
      return `${img.name}-${img.size}-${img.lastModified}`
    }
    return ''
  }).filter(key => key !== '')
  
  // Filtrar imágenes que no son capturadas (son archivos subidos)
  const uploadedImages = images.value.filter(img => {
    if (img instanceof File) {
      const imgKey = `${img.name}-${img.size}-${img.lastModified}`
      return !newCapturedKeys.includes(imgKey)
    }
    return true
  })
  
  // Combinar imágenes subidas con capturadas
  images.value = [...uploadedImages, ...newVal]
  
  // Actualizar URLs cuando cambian las imágenes
  nextTick(() => {
    updateImageUrls()
  })
}, { deep: true })

// Watcher para actualizar URLs cuando cambia el tab
watch(currentTab, async () => {
  await nextTick()
  updateImageUrls()
})

// Función para actualizar todas las URLs de imágenes
const updateImageUrls = async () => {
  // Limpiar URLs antiguas (solo blob URLs, no data URLs)
  Object.keys(imageUrls.value).forEach((key) => {
    const index = parseInt(key)
    const url = imageUrls.value[index]
    if (url && typeof url === 'string' && url.startsWith('blob:')) {
      try {
        URL.revokeObjectURL(url)
      } catch (error) {
        // Ignorar errores al revocar
      }
      delete imageUrls.value[index]
    }
  })
  
  // Crear nuevas URLs para todas las imágenes usando FileReader (data URLs)
  const promises = images.value.map(async (img, index) => {
    if (img instanceof File) {
      // Si ya tenemos una data URL, no regenerarla
      if (imageUrls.value[index] && imageUrls.value[index].startsWith('data:')) {
        return
      }
      
      // Generar data URL usando FileReader
      return new Promise((resolve) => {
        const reader = new FileReader()
        reader.onload = (e) => {
          if (e.target?.result) {
            imageUrls.value[index] = e.target.result
            resolve()
          } else {
            resolve()
          }
        }
        reader.onerror = () => {
          // Fallback a blob URL si FileReader falla
          try {
            const blobUrl = URL.createObjectURL(img)
            imageUrls.value[index] = blobUrl
          } catch (error) {
            // Ignorar errores
          }
          resolve()
        }
        reader.readAsDataURL(img)
      })
    }
  })
  
  await Promise.all(promises)
}

// Computed properties
const isFormValid = computed(() => {
  return (
    batchData.value.name && batchData.value.name.trim() !== '' &&
    batchData.value.collectionDate &&
    batchData.value.farm &&
    batchData.value.genetics && batchData.value.genetics.trim() !== '' &&
    images.value.length > 0
  )
})

const uploadProgress = computed(() => {
  return analysisStore.uploadProgress
})

const isUploading = computed(() => {
  return analysisStore.isUploading
})

const error = computed(() => {
  return analysisStore.uploadError
})

const userRole = computedUserRole

const userEmail = computed(() => {
  return authStore.user?.email || ''
})

// Helper function to generate unique keys for images
const getImageKey = (img, index) => {
  if (img instanceof File) {
    return img.name + '-' + img.size + '-' + img.lastModified || `img-${index}`
  }
  return img.id || img.url || `img-${index}`
}

// Helper function to create object URL for File objects
// Cache de URLs para evitar crear múltiples URLs para el mismo archivo
const imageUrlCache = new Map()

const getImageUrl = (img, index = null) => {
  if (!img) return ''
  
  if (img instanceof File) {
    // Prioridad 1: Si tenemos un índice y existe en imageUrls, usar esa URL
    if (index !== null && imageUrls.value[index]) {
      const cachedUrl = imageUrls.value[index]
      if (cachedUrl) {
        return cachedUrl
      }
    }
    
    // Prioridad 2: Crear una clave única para el archivo y buscar en cache
    const cacheKey = `${img.name}-${img.size}-${img.lastModified}`
    if (imageUrlCache.has(cacheKey)) {
      const cachedUrl = imageUrlCache.get(cacheKey)
      // Si tenemos índice, también guardarlo en imageUrls
      if (index !== null && cachedUrl) {
        imageUrls.value[index] = cachedUrl
      }
      return cachedUrl
    }
    
    // Prioridad 3: Crear blob URL inmediatamente (síncrono)
    try {
      const blobUrl = URL.createObjectURL(img)
      imageUrlCache.set(cacheKey, blobUrl)
      
      if (index !== null) {
        imageUrls.value[index] = blobUrl
      }
      
      // Generar data URL en segundo plano usando FileReader
      const reader = new FileReader()
      reader.onload = (e) => {
        if (e.target?.result) {
          // Revocar blob URL
          URL.revokeObjectURL(blobUrl)
          // Guardar data URL
          const dataUrl = e.target.result
          imageUrlCache.set(cacheKey, dataUrl)
          if (index !== null) {
            // Actualizar reactivamente
            imageUrls.value[index] = dataUrl
          }
        }
      }
      reader.onerror = () => {
        // Si falla FileReader, mantener el blob URL
      }
      reader.readAsDataURL(img)
      
      return blobUrl
    } catch (error) {
      return ''
    }
  }
  
  if (typeof img === 'string') {
    return img
  }
  
  return img.url || img || ''
}

const handleImageError = (event) => {
  // Si hay un error cargando la imagen, mostrar un placeholder
  event.target.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="200" height="200"%3E%3Crect width="200" height="200" fill="%23e5e7eb"/%3E%3Ctext x="50%25" y="50%25" text-anchor="middle" dy=".3em" fill="%239ca3af" font-family="sans-serif" font-size="14"%3EError al cargar%3C/text%3E%3C/svg%3E'
}

const handleImageLoad = (event) => {
  // Imagen cargada correctamente - no hacer nada
}

// Functions
const updateBatchData = (data) => {
  batchData.value = { ...data }
}

const handleImageUpdate = (newImages) => {
  // Crear claves de imágenes capturadas
  const capturedImageKeys = capturedImages.value.map(img => {
    if (img instanceof File) {
      return `${img.name}-${img.size}-${img.lastModified}`
    }
    return ''
  }).filter(key => key !== '')
  
  // Separar imágenes subidas de las capturadas
  const uploadedImages = newImages.filter(img => {
    if (img instanceof File) {
      const imgKey = `${img.name}-${img.size}-${img.lastModified}`
      return !capturedImageKeys.includes(imgKey)
    }
    return true
  })
  
  // Si se eliminó una imagen, verificar si era una capturada
  const currentImageKeys = images.value.map(img => {
    if (img instanceof File) {
      return `${img.name}-${img.size}-${img.lastModified}`
    }
    return ''
  }).filter(key => key !== '')
  
  const newImageKeys = newImages.map(img => {
    if (img instanceof File) {
      return `${img.name}-${img.size}-${img.lastModified}`
    }
    return ''
  }).filter(key => key !== '')
  
  // Encontrar imágenes eliminadas que eran capturadas
  const removedKeys = currentImageKeys.filter(key => !newImageKeys.includes(key) && capturedImageKeys.includes(key))
  
  // Eliminar de capturedImages las que fueron removidas
  if (removedKeys.length > 0) {
    capturedImages.value = capturedImages.value.filter(img => {
      if (img instanceof File) {
        const imgKey = `${img.name}-${img.size}-${img.lastModified}`
        return !removedKeys.includes(imgKey)
      }
      return true
    })
  }
  
  // Combinar imágenes subidas con capturadas actualizadas
  images.value = [...uploadedImages, ...capturedImages.value]
}

const updateImages = handleImageUpdate

const handleCapturedImage = async (imageFile) => {
  // Verificar que el archivo sea válido
  if (!imageFile || !(imageFile instanceof File)) {
    return
  }
  
  // Usar una comparación más robusta para evitar duplicados
  const isDuplicate = capturedImages.value.some(img => {
    if (img instanceof File && imageFile instanceof File) {
      // Comparar por nombre y tamaño, o por nombre completo si tienen timestamp
      return img.name === imageFile.name && img.size === imageFile.size
    }
    return false
  })
  
  if (!isDuplicate) {
    // Generar data URL inmediatamente usando FileReader
    const dataUrl = await new Promise((resolve) => {
      const reader = new FileReader()
      reader.onload = (e) => {
        if (e.target?.result) {
          resolve(e.target.result)
        } else {
          // Fallback a blob URL si FileReader falla
          try {
            resolve(URL.createObjectURL(imageFile))
          } catch (error) {
            resolve('')
          }
        }
      }
      reader.onerror = () => {
        // Fallback a blob URL si FileReader falla
        try {
          resolve(URL.createObjectURL(imageFile))
        } catch (error) {
          resolve('')
        }
      }
      reader.readAsDataURL(imageFile)
    })
    
    if (!dataUrl) {
      return
    }
    
    // Agregar la imagen capturada
    capturedImages.value = [...capturedImages.value, imageFile]
    // También actualizar el array principal de imágenes
    const newIndex = images.value.length
    images.value = [...images.value, imageFile]
    
    // Guardar la data URL en imageUrls inmediatamente
    imageUrls.value[newIndex] = dataUrl
    
    // También guardar en el cache
    const cacheKey = `${imageFile.name}-${imageFile.size}-${imageFile.lastModified}`
    imageUrlCache.set(cacheKey, dataUrl)
    
    // Forzar reactividad adicional
    await nextTick()
  }
}

const removeCapturedImage = (index) => {
  if (index < 0 || index >= capturedImages.value.length) return
  
  const imageToRemove = capturedImages.value[index]
  const updatedCapturedImages = [...capturedImages.value]
  updatedCapturedImages.splice(index, 1)
  capturedImages.value = updatedCapturedImages
  
  // También eliminar del array principal de imágenes
  const imageIndex = images.value.findIndex(img => {
    if (img instanceof File && imageToRemove instanceof File) {
      return img.name === imageToRemove.name && img.size === imageToRemove.size && img.lastModified === imageToRemove.lastModified
    }
    return false
  })
  
  if (imageIndex > -1) {
    images.value.splice(imageIndex, 1)
  }
}

const removeImageByIndex = (index) => {
  if (index < 0 || index >= images.value.length) return
  
  const imageToRemove = images.value[index]
  
  // Revocar URL del objeto si es un File
  if (imageToRemove instanceof File) {
    const cacheKey = `${imageToRemove.name}-${imageToRemove.size}-${imageToRemove.lastModified}`
    if (imageUrlCache.has(cacheKey)) {
      const url = imageUrlCache.get(cacheKey)
      URL.revokeObjectURL(url)
      imageUrlCache.delete(cacheKey)
    }
  }
  
  // Eliminar del array principal
  images.value.splice(index, 1)
  
  // Si es una imagen capturada, también eliminarla de capturedImages
  const capturedIndex = capturedImages.value.findIndex(img => {
    if (img instanceof File && imageToRemove instanceof File) {
      return img.name === imageToRemove.name && img.size === imageToRemove.size && img.lastModified === imageToRemove.lastModified
    }
    return false
  })
  
  if (capturedIndex > -1) {
    capturedImages.value.splice(capturedIndex, 1)
  }
}

const validateForm = () => {
  const errors = {}

  if (!batchData.value.name || !batchData.value.name.trim()) {
    errors.name = 'El nombre del lote es requerido'
  }

  if (!batchData.value.collectionDate) {
    errors.collectionDate = 'La fecha de recolección es requerida'
  }

  if (!batchData.value.farm) {
    errors.farm = 'La finca es requerida'
  }

  if (!batchData.value.genetics || !batchData.value.genetics.trim()) {
    errors.genetics = 'La genética es requerida'
  }

  if (images.value.length === 0) {
    errors.images = 'Debes subir al menos una imagen'
  }

  formErrors.value = errors
  return Object.keys(errors).length === 0
}

const submitAnalysis = async () => {
  if (!validateForm()) return

  try {
    isSubmitting.value = true
    analysisResult.value = null

    analysisStore.setBatchData(batchData.value)
    analysisStore.images = [...images.value]

    const result = await analysisStore.submitBatch()

    analysisResult.value = result

    if (result) {
      resetForm()
    }
  } catch (error) {
    } finally {
    isSubmitting.value = false
  }
}

const resetForm = () => {
  batchData.value = {
    name: '',
    collectionDate: '',
    origin: '',
    notes: '',
    farm: '',
    originPlace: '',
    genetics: '',
    farmer: ''
  }
  images.value = []
  capturedImages.value = []
  currentTab.value = 'upload'
  formErrors.value = {}
}

// Sidebar and navbar methods are now provided by useSidebarNavigation composable

const resetAndCreateNew = () => {
  analysisResult.value = null
  resetForm()
}

// Lifecycle
onMounted(() => {
  analysisStore.clearBatch()
  // Inicializar URLs de imágenes al montar
  updateImageUrls()
})
</script>

<style scoped>
/* Solo estilos que no están en Tailwind si es necesario */
</style>
