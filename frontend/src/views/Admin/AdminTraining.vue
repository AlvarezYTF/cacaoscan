<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Sidebar -->
    <AdminSidebar :brand-name="brandName" :user-name="userName" :user-role="userRole" :current-route="$route.path"
      :collapsed="isSidebarCollapsed"
      @menu-click="handleMenuClick" @logout="handleLogout" @toggle-collapse="toggleSidebarCollapse" />

    <!-- Main content -->
    <div class="p-6 transition-all duration-300" :class="isSidebarCollapsed ? 'sm:ml-20' : 'sm:ml-64'" data-cy="admin-training">

      <!-- INSERT_YOUR_CODE -->
      <!-- Page Header -->
      <div class="mb-8">
        <div
          class="bg-white rounded-lg border border-gray-200 hover:shadow-md hover:border-green-200 transition-all duration-200">
          <div class="px-6 py-4">
            <div class="flex-1">
              <h1 class="text-3xl font-bold text-gray-900 mb-2">Entrenamiento de Modelos</h1>
              <p class="text-gray-600 text-lg">
                Administra datasets, imágenes y procesos para entrenar modelos de análisis de granos de cacao.
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- Main Content Grid -->
      <div class="grid grid-cols-1 xl:grid-cols-3 gap-8">
        <!-- Left Column: Training Management -->
        <div class="xl:col-span-2 space-y-6">
          <!-- Dataset Preparation Section -->
          <div
            class="bg-white rounded-lg border border-gray-200 hover:shadow-md hover:border-green-200 transition-all duration-200">
            <div class="px-6 py-4 border-b border-gray-200">
              <h3 class="text-xl font-bold text-gray-900">Preparar Dataset</h3>
              <p class="text-sm text-gray-600 mt-1">Sube imágenes de granos y registra sus dimensiones para entrenar
                modelos</p>
            </div>

            <div class="p-6">
              <!-- Image Upload -->
              <div class="mb-6">
                <label for="file-input" class="block text-sm font-medium text-gray-700 mb-2">Seleccionar Imágenes</label>
                <div @drop="handleImageDrop" @dragover.prevent @dragenter="handleDragEnter" @dragleave="handleDragLeave"
                  class="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-green-400 transition-colors duration-200"
                  :class="{ 'border-green-400 bg-green-50': isDragOver }">
                  <input id="file-input" ref="fileInput" type="file" multiple accept="image/*" @change="handleFileSelect"
                    class="hidden" />

                  <svg class="w-16 h-16 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor"
                    viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>

                  <p class="text-lg font-medium text-gray-700 mb-2">
                    {{ uploadedImages.length === 0 ? 'Arrastra imágenes aquí o haz clic para seleccionar' :
                      `${uploadedImages.length} imagen${uploadedImages.length !== 1 ? 'es' : ''}
                    seleccionada${uploadedImages.length !== 1 ? 's' : ''}` }}
                  </p>
                  <p class="text-sm text-gray-500 mb-4">Formatos: JPG, PNG, BMP TIFF (máx. 20MB)</p>

                  <button @click="$refs.fileInput.click()"
                    class="inline-flex items-center px-4 py-2 text-sm font-medium text-white bg-green-600 border border-transparent rounded-lg hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 transition-colors duration-200">
                    <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                        d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                    </svg>
                    {{ uploadedImages.length === 0 ? 'Seleccionar Imágenes' : 'Agregar Más' }}
                  </button>
                </div>

                <!-- Image Previews -->
                <div v-if="uploadedImages.length > 0" class="mt-4 grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div v-for="(image, index) in uploadedImages" :key="image.id" class="relative group">
                    <img :src="image.preview" :alt="`Grano ${index + 1}`"
                      class="w-full aspect-square object-cover rounded-lg border border-gray-200" />
                    <button @click="removeImage(index)"
                      class="absolute -top-2 -right-2 w-6 h-6 bg-red-500 text-white rounded-full flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-200 hover:bg-red-600">
                      <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                          d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  </div>
                </div>
              </div>

              <!-- Data Entry Form -->
              <div v-if="uploadedImages.length > 0" class="space-y-4">
                <h4 class="text-lg font-semibold text-gray-900 mb-4">Datos de los Granos</h4>

                <div v-for="(image, index) in uploadedImages" :key="image.id"
                  class="border border-gray-200 rounded-lg p-4 bg-gray-50">
                  <h5 class="font-medium text-gray-900 mb-3">Grano {{ index + 1 }}</h5>

                  <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <label :for="`height-${index}`" class="block text-sm font-medium text-gray-700 mb-1">Alto (mm)</label>
                      <input :id="`height-${index}`" v-model.number="image.height" type="number" step="0.1" placeholder="12.5"
                        class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500 transition-colors duration-200" />
                    </div>

                    <div>
                      <label :for="`width-${index}`" class="block text-sm font-medium text-gray-700 mb-1">Ancho (mm)</label>
                      <input :id="`width-${index}`" v-model.number="image.width" type="number" step="0.1" placeholder="8.3"
                        class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500 transition-colors duration-200" />
                    </div>

                    <div>
                      <label :for="`thickness-${index}`" class="block text-sm font-medium text-gray-700 mb-1">Grosor (mm)</label>
                      <input :id="`thickness-${index}`" v-model.number="image.thickness" type="number" step="0.1" placeholder="6.2"
                        class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500 transition-colors duration-200" />
                    </div>

                    <div>
                      <label :for="`weight-${index}`" class="block text-sm font-medium text-gray-700 mb-1">Peso (g)</label>
                      <input :id="`weight-${index}`" v-model.number="image.weight" type="number" step="0.01" placeholder="1.25"
                        class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500 transition-colors duration-200" />
                    </div>
                  </div>
                </div>

                <!-- Submit Button -->
                <button @click="submitDataset" :disabled="!canSubmitDataset || isSubmittingDataset"
                  class="w-full inline-flex items-center justify-center px-6 py-3 text-base font-medium text-white bg-green-600 border border-transparent rounded-lg hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200">
                  <svg v-if="isSubmittingDataset" class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none"
                    viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z">
                    </path>
                  </svg>
                  <svg v-else class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                  </svg>
                  {{ isSubmittingDataset ? 'Enviando datos...' : `Enviar ${uploadedImages.length}
                  muestra${uploadedImages.length !== 1 ? 's' : ''}` }}
                </button>
              </div>

              <!-- Empty state -->
              <div v-if="uploadedImages.length === 0" class="text-center py-8">
                <svg class="w-16 h-16 text-gray-300 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
                <p class="text-gray-500 font-medium">No hay imágenes seleccionadas</p>
                <p class="text-gray-400 text-sm">Selecciona imágenes de granos para comenzar</p>
              </div>
            </div>
          </div>

          <!-- Training History -->
          <div
            class="bg-white rounded-lg border border-gray-200 hover:shadow-md hover:border-green-200 transition-all duration-200">
            <div class="px-6 py-4 border-b border-gray-200">
              <div class="flex items-center justify-between">
                <h3 class="text-xl font-bold text-gray-900">Historial de Entrenamientos</h3>
                <div class="flex items-center space-x-3">
                  <!-- Filters -->
                  <select v-model="historyFilters.job_type"
                    class="text-sm border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-green-500 focus:border-green-500 bg-white hover:border-green-300 transition-colors duration-200">
                    <option value="">Todos los tipos</option>
                    <option value="regression">Regresión</option>
                    <option value="vision">Visión</option>
                    <option value="incremental">Incremental</option>
                  </select>

                  <select v-model="historyFilters.status"
                    class="text-sm border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-green-500 focus:border-green-500 bg-white hover:border-green-300 transition-colors duration-200">
                    <option value="">Todos los estados</option>
                    <option value="completed">Completado</option>
                    <option value="running">En ejecución</option>
                    <option value="failed">Fallido</option>
                    <option value="cancelled">Cancelado</option>
                    <option value="pending">Pendiente</option>
                  </select>
                </div>
              </div>
            </div>

            <div class="p-6">
              <!-- Training history cards -->
              <div class="space-y-4" data-cy="training-jobs">
                <div v-for="job in filteredTrainingHistory" :key="job.job_id"
                  class="border border-gray-200 rounded-lg p-4 hover:shadow-md hover:border-green-200 transition-all duration-200">
                  <div class="flex items-center justify-between">
                    <div class="flex items-center space-x-4">
                      <!-- Job icon -->
                      <div class="w-12 h-12 bg-green-50 rounded-lg flex items-center justify-center">
                        <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                            d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                        </svg>
                      </div>

                      <!-- Job info -->
                      <div>
                        <h4 class="text-lg font-semibold text-gray-900">{{ getModelTypeLabel(job.job_type) }}</h4>
                        <p class="text-sm text-gray-600">ID: {{ job.job_id }}</p>
                        <p class="text-xs text-gray-500">{{ formatDate(job.created_at) }}</p>
                      </div>
                    </div>

                    <!-- Status and actions -->
                    <div class="flex items-center space-x-4">
                      <!-- Status badge -->
                      <span :class="getStatusBadgeClass(job.status)" class="px-3 py-1 rounded-full text-sm font-medium">
                        {{ getStatusLabel(job.status) }}
                      </span>

                      <!-- Progress bar for running jobs -->
                      <div v-if="job.status === 'running'" class="w-24">
                        <div class="w-full bg-gray-200 rounded-full h-2">
                          <div class="bg-green-600 h-2 rounded-full transition-all duration-300"
                            :style="{ width: `${job.progress_percentage || 0}%` }"></div>
                        </div>
                        <p class="text-xs text-gray-500 text-center mt-1">{{ job.progress_percentage || 0 }}%</p>
                      </div>

                      <!-- Actions -->
                      <div class="flex items-center space-x-2">
                        <button @click="viewJobDetails(job)"
                          class="text-green-600 hover:text-green-700 p-2 rounded-lg hover:bg-green-50 transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-green-500"
                          title="Ver detalles"
                          data-cy="view-job-status"
                        >
                          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                              d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                              d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                          </svg>
                        </button>

                        <button v-if="job.status === 'running'" @click="cancelJob(job.job_id)"
                          class="text-red-600 hover:text-red-700 p-2 rounded-lg hover:bg-red-50 transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-red-500"
                          title="Cancelar"
                          data-cy="cancel-job"
                        >
                          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                              d="M6 18L18 6M6 6l12 12" />
                          </svg>
                        </button>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Empty state -->
                <div v-if="filteredTrainingHistory.length === 0" class="text-center py-8">
                  <svg class="w-16 h-16 text-gray-300 mx-auto mb-4" fill="none" stroke="currentColor"
                    viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                  </svg>
                  <p class="text-gray-500 font-medium">No hay entrenamientos registrados</p>
                  <p class="text-gray-400 text-sm">Los entrenamientos aparecerán aquí cuando se ejecuten</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Active Trainings Monitor -->
          <div v-if="activeTrainings.length > 0"
            class="bg-white rounded-lg border border-gray-200 hover:shadow-md hover:border-green-200 transition-all duration-200">
            <div class="px-6 py-4 border-b border-gray-200">
              <h3 class="text-xl font-bold text-gray-900">Entrenamientos Activos</h3>
            </div>

            <div class="p-6">
              <div class="space-y-4">
                <div v-for="training in activeTrainings" :key="training.job_id"
                  class="border border-green-200 rounded-lg p-3 bg-green-50">
                  <div class="flex items-center justify-between">
                    <div>
                      <h4 class="font-semibold text-green-900">{{ getModelTypeLabel(training.job_type) }}</h4>
                      <p class="text-sm text-green-600">ID: {{ training.job_id }}</p>
                    </div>

                    <div class="text-right">
                      <p class="text-sm font-medium text-green-900">{{ training.progress_percentage || 0 }}%</p>
                      <p class="text-xs text-green-600">{{ training.duration }}</p>
                    </div>
                  </div>

                  <div class="mt-3">
                    <div class="w-full bg-green-200 rounded-full h-2">
                      <div class="bg-green-600 h-2 rounded-full transition-all duration-300"
                        :style="{ width: `${training.progress_percentage || 0}%` }"></div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Right Column: Stats and Quick Actions -->
        <div class="space-y-6">
          <!-- Start Training Section -->
          <div
            class="bg-white rounded-lg border border-gray-200 hover:shadow-md hover:border-green-200 transition-all duration-200">
            <div class="px-6 py-4 border-b border-gray-200">
              <h3 class="text-xl font-bold text-gray-900">Iniciar Entrenamiento</h3>
              <p class="text-sm text-gray-600 mt-1">Entrena modelos ML con configuración mejorada</p>
            </div>

            <div class="p-6">
              <div class="space-y-4">
                <div class="bg-green-50 border border-green-200 rounded-lg p-4">
                  <h4 class="font-semibold text-green-900 mb-2">Configuración Mejorada</h4>
                  <ul class="text-sm text-green-800 space-y-1">
                    <li>✓ 150 épocas (aprendizaje profundo)</li>
                    <li>✓ Validación automática de crops</li>
                    <li>✓ Regeneración de crops malos</li>
                    <li>✓ Confianza mejorada (≥80%)</li>
                    <li>✓ Detección YOLO mejorada</li>
                  </ul>
                </div>

                <button 
                  @click="startTraining" 
                  :disabled="isStartingTraining || hasActiveTraining"
                  :title="hasActiveTraining ? `Hay ${activeTrainings.length} entrenamiento${activeTrainings.length > 1 ? 's' : ''} en ejecución. Espera a que ${activeTrainings.length > 1 ? 'terminen' : 'termine'}.` : 'Iniciar nuevo entrenamiento'"
                  class="w-full inline-flex items-center justify-center px-6 py-3 text-base font-medium text-white bg-green-600 border border-transparent rounded-lg hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200"
                  data-cy="create-training-job"
                >
                  <svg v-if="isStartingTraining" class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none"
                    viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z">
                    </path>
                  </svg>
                  <svg v-else class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                      d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  {{ isStartingTraining ? 'Iniciando entrenamiento...' : (hasActiveTraining ? `Hay ${activeTrainings.length} entrenamiento${activeTrainings.length > 1 ? 's' : ''} activo${activeTrainings.length > 1 ? 's' : ''}` : 'Iniciar Entrenamiento') }}
                </button>

                <div v-if="lastTrainingResult" class="mt-4 p-3 rounded-lg"
                  :class="lastTrainingResult.success ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'">
                  <p class="text-sm font-medium"
                    :class="lastTrainingResult.success ? 'text-green-800' : 'text-red-800'">
                    {{ lastTrainingResult.message }}
                  </p>
                  <p v-if="lastTrainingResult.job_id" class="text-xs mt-1"
                    :class="lastTrainingResult.success ? 'text-green-600' : 'text-red-600'">
                    Job ID: {{ lastTrainingResult.job_id }}
                  </p>
                </div>
              </div>
            </div>
          </div>

          <!-- Quick Statistics -->
          <div
            class="bg-white rounded-lg border border-gray-200 hover:shadow-md hover:border-green-200 transition-all duration-200">
            <div class="px-6 py-4 border-b border-gray-200">
              <h3 class="text-xl font-bold text-gray-900">Estadísticas Rápidas</h3>
            </div>

            <div class="p-6">
              <div class="grid grid-cols-2 gap-4">
                <div class="text-center p-4 bg-green-50 rounded-lg">
                  <div class="text-2xl font-bold text-green-600">{{ stats.totalJobs }}</div>
                  <div class="text-sm text-green-700">Total Trabajos</div>
                </div>

                <div class="text-center p-4 bg-blue-50 rounded-lg">
                  <div class="text-2xl font-bold text-blue-600">{{ stats.completedJobs }}</div>
                  <div class="text-sm text-blue-700">Completados</div>
                </div>

                <div class="text-center p-4 bg-red-50 rounded-lg">
                  <div class="text-2xl font-bold text-red-600">{{ stats.failedJobs }}</div>
                  <div class="text-sm text-red-700">Fallidos</div>
                </div>

                <div class="text-center p-4 bg-purple-50 rounded-lg">
                  <div class="text-2xl font-bold text-purple-600">{{ stats.avgTrainingTime }}</div>
                  <div class="text-sm text-purple-700">Tiempo Promedio</div>
                </div>
              </div>
            </div>
          </div>

          <!-- Model Comparison -->
          <div
            class="bg-white rounded-lg border border-gray-200 hover:shadow-md hover:border-green-200 transition-all duration-200">
            <div class="px-6 py-4 border-b border-gray-200">
              <h3 class="text-xl font-bold text-gray-900">Comparar Modelos</h3>
            </div>

            <div class="p-6">
              <div class="space-y-3">
                <div v-for="job in completedJobs" :key="job.job_id" class="flex items-center space-x-3">
                  <input :id="`compare-${job.job_id}`" type="checkbox" :value="job.job_id"
                    v-model="selectedJobsForComparison" class="text-green-600 focus:ring-green-500 rounded" />
                  <label :for="`compare-${job.job_id}`" class="text-sm text-gray-700">
                    {{ getModelTypeLabel(job.job_type) }} - {{ formatDate(job.completed_at) }}
                  </label>
                </div>
              </div>

              <button @click="compareModels" :disabled="selectedJobsForComparison.length < 2"
                class="w-full mt-4 inline-flex items-center justify-center px-4 py-2 text-sm font-medium text-white bg-green-600 border border-transparent rounded-lg hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200">
                <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v4a2 2 0 01-2 2h-2a2 2 0 00-2-2z" />
                </svg>
                Comparar Modelos
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted, onBeforeUnmount } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';
import AdminSidebar from '@/components/layout/Common/Sidebar.vue';
import { getTrainingHistory, cancelTrainingJob, compareModels as compareModelsApi, startMLTraining } from '@/services/adminApi.js';

export default {
  name: 'AdminTraining',
  components: {
    AdminSidebar
  },

  setup() {
    const router = useRouter();
    const authStore = useAuthStore();

    // Sidebar properties
    const brandName = computed(() => 'CacaoScan');
    const userName = computed(() => {
      const user = authStore.user;
      return user ? `${user.first_name || ''} ${user.last_name || ''}`.trim() || user.username : 'Usuario';
    });
    const userRole = computed(() => {
      const role = authStore.userRole || 'Usuario'
      // Normalize role for sidebar - Backend returns: 'admin', 'analyst', or 'farmer'
      if (role === 'admin') return 'admin'
      if (role === 'farmer') return 'agricultor'
      return 'admin' // Default to admin
    })

    // Sidebar collapse state
    const isSidebarCollapsed = ref(false);

    const toggleSidebarCollapse = () => {
      isSidebarCollapsed.value = !isSidebarCollapsed.value;
      localStorage.setItem('sidebarCollapsed', isSidebarCollapsed.value);
    };

    // Navbar properties
    const navbarTitle = ref('Entrenamiento de Modelos ML');
    const navbarSubtitle = ref('Gestiona el entrenamiento de modelos de predicción');
    const searchPlaceholder = ref('Buscar trabajos...');
    const refreshButtonText = ref('Actualizar');

    // State
    const isRefreshing = ref(false);
    const trainingHistory = ref([]);
    const historyFilters = reactive({
      job_type: '',
      status: ''
    });
    const selectedJobsForComparison = ref([]);

    // Dataset preparation state
    const uploadedImages = ref([]);
    const isDragOver = ref(false);
    const isSubmittingDataset = ref(false);
    const fileInput = ref(null);

    // Training start state
    const isStartingTraining = ref(false);
    const lastTrainingResult = ref(null);
    const refreshIntervalRef = ref(null);

    // Computed
    const filteredTrainingHistory = computed(() => {
      let filtered = trainingHistory.value;

      if (historyFilters.job_type) {
        filtered = filtered.filter(job => job.job_type === historyFilters.job_type);
      }

      if (historyFilters.status) {
        filtered = filtered.filter(job => job.status === historyFilters.status);
      }

      return filtered;
    });

    const activeTrainings = computed(() => {
      // Incluir solo entrenamientos que realmente están activos (running o pending)
      return trainingHistory.value.filter(job => 
        job.status === 'running' || job.status === 'pending'
      );
    });

    const hasActiveTraining = computed(() => {
      // Verificar que haya entrenamientos activos y que no estén completados o fallidos
      const active = activeTrainings.value.filter(job => 
        job.status !== 'completed' && 
        job.status !== 'failed' && 
        job.status !== 'cancelled'
      );
      return active.length > 0;
    });

    const completedJobs = computed(() => {
      return trainingHistory.value.filter(job => job.status === 'completed');
    });

    const stats = computed(() => {
      const jobs = trainingHistory.value;
      const completed = jobs.filter(job => job.status === 'completed');
      const failed = jobs.filter(job => job.status === 'failed');

      const avgTime = completed.length > 0
        ? Math.round(completed.reduce((sum, job) => sum + (job.training_time || 0), 0) / completed.length)
        : 0;

      return {
        totalJobs: jobs.length,
        completedJobs: completed.length,
        failedJobs: failed.length,
        avgTrainingTime: `${avgTime}min`
      };
    });

    // Methods
    const handleMenuClick = (menuItem) => {
      if (menuItem.route) {
        router.push(menuItem.route);
      }
    };

    const handleLogout = async () => {
      await authStore.logout();
      router.push('/login');
    };

    const handleSearch = (query) => {
      };

    const handleRefresh = () => {
      refreshTrainingData();
    };

    const refreshTrainingData = async () => {
      isRefreshing.value = true;

      try {
        const history = await getTrainingHistory();
        trainingHistory.value = history;
      } catch (error) {
        } finally {
        isRefreshing.value = false;
      }
    };

    const getModelTypeLabel = (jobType) => {
      const labels = {
        'regression': 'Modelo de Regresión',
        'vision': 'Modelo de Visión',
        'incremental': 'Entrenamiento Incremental'
      };
      return labels[jobType] || jobType;
    };

    const getStatusLabel = (status) => {
      const labels = {
        'completed': 'Completado',
        'running': 'En ejecución',
        'failed': 'Fallido',
        'cancelled': 'Cancelado',
        'pending': 'Pendiente'
      };
      return labels[status] || status;
    };

    const getStatusBadgeClass = (status) => {
      const classes = {
        'completed': 'bg-green-100 text-green-800',
        'running': 'bg-blue-100 text-blue-800',
        'failed': 'bg-red-100 text-red-800',
        'cancelled': 'bg-gray-100 text-gray-800',
        'pending': 'bg-amber-100 text-amber-800'
      };
      return classes[status] || 'bg-gray-100 text-gray-800';
    };

    const formatDate = (dateString) => {
      if (!dateString) return 'N/A';

      const date = new Date(dateString);
      return date.toLocaleDateString('es-ES', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    };

    const viewJobDetails = (job) => {
      // Implement job details view
    };

    const cancelJob = async (jobId) => {
      try {
        await cancelTrainingJob(jobId);
        await refreshTrainingData();
      } catch (error) {
        }
    };

    const compareModels = async () => {
      if (selectedJobsForComparison.value.length < 2) return;

      try {
        const comparison = await compareModelsApi(selectedJobsForComparison.value);
        // Implement comparison view
      } catch (error) {
        }
    };

    // Dataset preparation methods
    const handleFileSelect = (event) => {
      const files = Array.from(event.target.files);
      processFiles(files);
      // Reset file input
      if (event.target) {
        event.target.value = '';
      }
    };

    const handleImageDrop = (event) => {
      event.preventDefault();
      isDragOver.value = false;

      const files = Array.from(event.dataTransfer.files);
      processFiles(files);
    };

    const handleDragEnter = () => {
      isDragOver.value = true;
    };

    const handleDragLeave = () => {
      isDragOver.value = false;
    };

    const processFiles = (files) => {
      for (const [index, file] of files.entries()) {
        const reader = new FileReader();
        reader.onload = (e) => {
          const imageData = {
            id: `img_${Date.now()}_${index}`,
            file: file,
            preview: e.target.result,
            height: null,
            width: null,
            thickness: null,
            weight: null
          };
          uploadedImages.value.push(imageData);
        };
        reader.readAsDataURL(file);
      }
    };

    const removeImage = (index) => {
      uploadedImages.value.splice(index, 1);
    };

    const canSubmitDataset = computed(() => {
      return uploadedImages.value.length > 0 &&
        uploadedImages.value.every(img =>
          img.height &&
          img.width &&
          img.thickness &&
          img.weight
        );
    });

    const submitDataset = async () => {
      if (!canSubmitDataset.value) return;

      isSubmittingDataset.value = true;

      try {
        const formData = new FormData();

        // Add images and their data
        for (const [index, image] of uploadedImages.value.entries()) {
          formData.append('images', image.file);
          formData.append(`data_${index}`, JSON.stringify({
            height: image.height,
            width: image.width,
            thickness: image.thickness,
            weight: image.weight
          }));
        }

        // Submit dataset to API
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 2000));

        // Reset after submission
        uploadedImages.value = [];

        } catch (error) {
        } finally {
        isSubmittingDataset.value = false;
      }
    };

    const startTraining = async () => {
      if (hasActiveTraining.value) {
        alert('Ya hay un entrenamiento en ejecución. Espera a que termine o cancélalo primero.');
        return;
      }

      // Limpiar intervalo anterior si existe
      if (refreshIntervalRef.value) {
        clearInterval(refreshIntervalRef.value);
        refreshIntervalRef.value = null;
      }

      isStartingTraining.value = true;
      lastTrainingResult.value = null;

      try {
        const result = await startMLTraining();
        
        // El backend devuelve job_id directamente o en job.job_id
        const jobId = result.job_id || result.job?.job_id || result.data?.job_id || result.data?.job?.job_id;
        
        lastTrainingResult.value = {
          success: true,
          message: 'Entrenamiento iniciado exitosamente',
          job_id: jobId
        };

        // Actualizar historial después de iniciar
        await refreshTrainingData();

        // Recargar historial periódicamente (solo si el entrenamiento se inició correctamente)
        if (jobId) {
          
          // Limpiar cualquier intervalo anterior
          if (refreshIntervalRef.value) {
            clearInterval(refreshIntervalRef.value);
          }
          
          refreshIntervalRef.value = setInterval(async () => {
            try {
              await refreshTrainingData();
              
              // Verificar si el job actual ya terminó (completed, failed, o cancelled)
              const currentJob = trainingHistory.value.find(job => job.job_id === jobId);
              if (currentJob && (currentJob.status === 'completed' || currentJob.status === 'failed' || currentJob.status === 'cancelled')) {
                // Job terminado, detener polling
                if (refreshIntervalRef.value) {
                  clearInterval(refreshIntervalRef.value);
                  refreshIntervalRef.value = null;
                }
                return;
              }
              
              // Verificar si hay algún entrenamiento activo
              const stillActive = trainingHistory.value.filter(job => 
                (job.status === 'running' || job.status === 'pending') &&
                job.status !== 'completed' && 
                job.status !== 'failed' && 
                job.status !== 'cancelled'
              );
              
              // Si no hay entrenamientos activos, detener polling
              if (stillActive.length === 0 && refreshIntervalRef.value) {
                clearInterval(refreshIntervalRef.value);
                refreshIntervalRef.value = null;
              }
            } catch (error) {
              // No detener polling en caso de error, solo continuar
            }
          }, 5000);
        }

      } catch (error) {
        lastTrainingResult.value = {
          success: false,
          message: error.message || 'Error al iniciar el entrenamiento. Verifica que el worker de Celery esté corriendo.',
          job_id: null
        };
        
        // Limpiar intervalo si hay error
        if (refreshIntervalRef.value) {
          clearInterval(refreshIntervalRef.value);
          refreshIntervalRef.value = null;
        }
      } finally {
        isStartingTraining.value = false;
      }
    };

    // Lifecycle
    onMounted(() => {
      refreshTrainingData();
    });

    onBeforeUnmount(() => {
      if (refreshIntervalRef.value) {
        clearInterval(refreshIntervalRef.value);
        refreshIntervalRef.value = null;
      }
    });

    return {
      // Sidebar & Navbar
      isSidebarCollapsed,
      toggleSidebarCollapse,
      brandName,
      userName,
      userRole,
      navbarTitle,
      navbarSubtitle,
      searchPlaceholder,
      refreshButtonText,
      handleMenuClick,
      handleLogout,
      handleSearch,
      handleRefresh,

      // State
      isRefreshing,
      trainingHistory,
      historyFilters,
      selectedJobsForComparison,
      uploadedImages,
      isDragOver,
      isSubmittingDataset,
      fileInput,
      isStartingTraining,
      lastTrainingResult,
      refreshIntervalRef,

      // Computed
      filteredTrainingHistory,
      activeTrainings,
      completedJobs,
      stats,
      canSubmitDataset,
      hasActiveTraining,

      // Methods
      refreshTrainingData,
      getModelTypeLabel,
      getStatusLabel,
      getStatusBadgeClass,
      formatDate,
      viewJobDetails,
      cancelJob,
      compareModels,
      handleFileSelect,
      handleImageDrop,
      handleDragEnter,
      handleDragLeave,
      removeImage,
      submitDataset,
      startTraining
    };
  }
};
</script>

<style scoped>
/* Transiciones */
.transition-all {
  transition: all 0.2s ease;
}

.transition-colors {
  transition: color 0.2s ease, background-color 0.2s ease, border-color 0.2s ease;
}

/* Focus states */
.focus-visible:focus {
  outline: 2px solid #10b981;
  outline-offset: 2px;
}

/* Loading states */
.loading {
  opacity: 0.6;
  pointer-events: none;
}

/* Custom scrollbar */
.overflow-y-auto::-webkit-scrollbar {
  width: 6px;
}

.overflow-y-auto::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}
</style>