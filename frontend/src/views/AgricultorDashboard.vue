<template>
  <div class="farmer-dashboard-container">
    <!-- Sidebar -->
    <AgricultorSidebar
      :farmer-name="farmerName"
      :farmer-role="'Agricultor'"
      :sidebar-collapsed="sidebarCollapsed"
      :active-section="activeSection"
      :stats="stats"
      @toggle-sidebar="toggleSidebar"
      @set-active-section="setActiveSection"
      @logout="logout"
    />

    <!-- Main Content -->
    <main class="dashboard-main" :class="{ 'main-expanded': !sidebarCollapsed, 'main-collapsed': sidebarCollapsed }">
      <!-- Overview Section -->
      <div v-if="activeSection === 'overview'" class="dashboard-section">
        <div class="section-header">
          <h1>¡Bienvenido a CacaoScan, {{ farmerName }}!</h1>
          <p>Esta es su herramienta para asegurar la calidad de cada grano. Con CacaoScan, podrá analizar su cosecha de forma rápida y precisa, eliminando las dudas del análisis tradicional. Obtenga los datos que necesita para mejorar sus procesos y aumentar el valor de su trabajo. Estamos aquí para ayudarle a que su cacao destaque.</p>
        </div>
        
        <!-- Estadísticas básicas -->
        <div class="stats-grid">
          <div class="stat-card">
            <h3>{{ formattedStats.totalBatches }}</h3>
            <p>Lotes Totales</p>
          </div>
          <div class="stat-card">
            <h3>{{ formattedStats.avgQuality }}%</h3>
            <p>Calidad Promedio</p>
          </div>
          <div class="stat-card">
            <h3>{{ formattedStats.defectRate }}%</h3>
            <p>Tasa de Defectos</p>
          </div>
        </div>
        
        <div class="overview-grid">
          <div class="overview-card">
            <h3>Actividad Reciente</h3>
            <div class="recent-analyses">
              <div v-for="analysis in recentAnalyses" :key="analysis.id" class="analysis-item">
                <span class="analysis-id">Lote #{{ analysis.id }}</span>
                <span class="analysis-quality">{{ analysis.quality }}%</span>
                <span class="analysis-date">{{ analysis.date }}</span>
              </div>
            </div>
          </div>
          
          <div class="overview-card">
            <h3>Acciones Rápidas</h3>
            <div class="quick-actions">
              <button @click="setActiveSection('analysis')" class="action-btn">
                <i class="fas fa-microscope"></i>
                Nuevo Análisis
              </button>
              <button @click="setActiveSection('fincas')" class="action-btn">
                <i class="fas fa-tree"></i>
                Gestionar Fincas
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Analysis Section -->
      <div v-if="activeSection === 'analysis'" class="dashboard-section">
        <!-- Back Button -->
        <div class="mb-6">
          <button 
            @click="goBack"
            class="back-button"
          >
            <i class="fas fa-arrow-left"></i>
            <span>Volver</span>
          </button>
        </div>

        <!-- Header Banner -->
        <div class="analysis-header">
          <h1>Nuevo Análisis de Lote</h1>
          <p>Sube imágenes de granos de cacao y completa la información del lote para iniciar un análisis de calidad detallado y preciso.</p>
        </div>
        
        <!-- Main Content -->
        <div class="bg-white shadow rounded-lg overflow-hidden">
          <div class="p-6 space-y-8">
            <!-- Batch Info Form -->
            <div class="space-y-6">
              <div class="text-center">
                <h2 class="text-2xl font-bold text-gray-900 mb-2">Información del Lote</h2>
              </div>
              
              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <!-- Left Column -->
                <div class="space-y-4">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Finca *</label>
                    <input 
                      v-model="batchData.finca"
                      type="text" 
                      class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
                      placeholder="Nombre de la finca"
                      @input="clearFieldError('finca')"
                    />
                    <p v-if="formErrors.finca && formErrors.finca !== ''" class="mt-1 text-sm text-red-600">{{ formErrors.finca }}</p>
                  </div>
                  
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Agricultor *</label>
                    <input 
                      v-model="batchData.agricultor"
                      type="text" 
                      class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
                      placeholder="Nombre del agricultor"
                      @input="clearFieldError('agricultor')"
                    />
                    <p v-if="formErrors.agricultor && formErrors.agricultor !== ''" class="mt-1 text-sm text-red-600">{{ formErrors.agricultor }}</p>

                  </div>
                  
                  
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Nombre o código del lote *</label>
                    <input 
                      v-model="batchData.nombreLote"
                      type="text" 
                      class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
                      placeholder="Código o nombre del lote"
                      @input="clearFieldError('nombreLote')"
                    />
                    <p v-if="formErrors.nombreLote && formErrors.nombreLote !== ''" class="mt-1 text-sm text-red-600">{{ formErrors.nombreLote }}</p>
                  </div>
                  
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Fecha de recolección *</label>
                    <div class="relative">
                      <input 
                        v-model="batchData.fechaRecoleccion"
                        type="text" 
                        class="w-full px-3 py-2 pr-10 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
                        placeholder="dd/mm/aaaa"
                        @input="clearFieldError('fechaRecoleccion')"
                      />
                      <svg class="absolute right-3 top-2.5 h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                      </svg>
                    </div>
                    <p v-if="formErrors.fechaRecoleccion && formErrors.fechaRecoleccion !== ''" class="mt-1 text-sm text-red-600">{{ formErrors.fechaRecoleccion }}</p>
                  </div>
                  
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Observaciones (opcional)</label>
                    <textarea 
                      v-model="batchData.observaciones"
                      rows="3"
                      class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
                      placeholder="Notas adicionales sobre el lote..."
                    ></textarea>
                  </div>
                </div>
                
                <!-- Right Column -->
                <div class="space-y-4">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Lugar de origen *</label>
                    <input 
                      v-model="batchData.lugarOrigen"
                      type="text" 
                      class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
                      placeholder="Lugar de origen del lote"
                      @input="clearFieldError('lugarOrigen')"
                    />
                    <p v-if="formErrors.lugarOrigen && formErrors.lugarOrigen !== ''" class="mt-1 text-sm text-red-600">{{ formErrors.lugarOrigen }}</p>
                  </div>
                  
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Genética *</label>
                    <select 
                      v-model="batchData.genetica"
                      class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
                      @change="clearFieldError('genetica')"
                    >
                      <option value="">Selecciona la genética</option>
                      <option value="criollo">Criollo</option>
                      <option value="forastero">Forastero</option>
                      <option value="trinitario">Trinitario</option>
                      <option value="nacional">Nacional</option>
                    </select>
                    <p v-if="formErrors.genetica && formErrors.genetica !== ''" class="mt-1 text-sm text-red-600">{{ formErrors.genetica }}</p>
                  </div>
                  
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">Origen</label>
                    <select 
                      v-model="batchData.origen"
                      class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
                    >
                      <option value="">Selecciona un origen</option>
                      <option value="nacional">Nacional</option>
                      <option value="importado">Importado</option>
                      <option value="local">Local</option>
                    </select>
                  </div>
                </div>
              </div>
            </div>

            <!-- Image Capture Section -->
            <div class="space-y-6">
              <div class="text-center">
                <h2 class="text-2xl font-bold text-gray-900 mb-2">Imágenes del Lote</h2>
                <p class="text-gray-600">Captura fotos de alta calidad de los granos de cacao para un análisis preciso</p>
              </div>

              <!-- Tabs -->
              <div class="border-b border-gray-200">
                <nav class="-mb-px flex space-x-8 justify-center">
                  <button
                    v-for="tab in tabs"
                    :key="tab.name"
                    @click="currentTab = tab.name"
                    :class="[
                      currentTab === tab.name
                        ? 'border-green-500 text-green-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300',
                      'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm transition-colors duration-200'
                    ]"
                  >
                    {{ tab.label }}
                  </button>
                </nav>
              </div>

              <!-- Tab Content -->
              <div class="mt-6">
                <!-- File Upload Tab -->
                <div v-if="currentTab === 'upload'" class="space-y-4">
                  <div class="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-green-400 transition-colors duration-200 bg-gray-50">
                    <div class="flex flex-col items-center">
                      <svg class="w-12 h-12 text-gray-400 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                      </svg>
                      <p class="text-lg font-medium text-gray-900 mb-2">Arrastra tus imágenes aquí o haz clic para seleccionarlas</p>
                      <p class="text-sm text-gray-600 mb-4">Formatos soportados: JPG, PNG (máx. 5MB por imagen)</p>
                      <input 
                        type="file" 
                        multiple 
                        accept="image/*"
                        @change="handleFileUpload"
                        class="hidden"
                        ref="fileInput"
                      />
                      <button 
                        @click="$refs.fileInput.click()"
                        class="bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700 transition-colors duration-200"
                      >
                        Seleccionar Archivos
                      </button>
                    </div>
                  </div>
                  
                  <!-- Preview de imágenes subidas -->
                  <div v-if="images.length > 0" class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
                    <div v-for="(img, index) in images" :key="index" class="relative group">
                      <div class="aspect-square rounded-lg overflow-hidden bg-gray-200">
                        <img :src="getImageUrl(img)" alt="Imagen del lote" class="w-full h-full object-cover" />
                      </div>
                      <button 
                        @click="removeImage(index)"
                        class="absolute top-2 right-2 bg-red-500 text-white rounded-full p-1 opacity-0 group-hover:opacity-100 transition-opacity duration-200"
                      >
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                        </svg>
                      </button>
                    </div>
                  </div>
                </div>

                <!-- Camera Capture Tab -->
                <div v-else-if="currentTab === 'camera'" class="space-y-6">
                  <CameraCapture @capture="handleCapturedImage" />

                  <!-- Captured Images Preview -->
                  <div v-if="capturedImages.length > 0" class="bg-gray-50 rounded-lg p-6">
                    <h3 class="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                      <svg class="w-5 h-5 text-green-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                      </svg>
                      Fotos capturadas ({{ capturedImages.length }})
                    </h3>
                    <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
                      <div v-for="(img, index) in capturedImages" :key="index" class="relative group">
                        <div class="aspect-square rounded-lg overflow-hidden bg-gray-200">
                          <img :src="getImageUrl(img)" alt="Imagen capturada" class="w-full h-full object-cover" />
                        </div>
                        <button 
                          @click="removeCapturedImage(index)"
                          class="absolute top-2 right-2 bg-red-500 text-white rounded-full p-1 opacity-0 group-hover:opacity-100 transition-opacity duration-200"
                        >
                          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                          </svg>
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Ready to Analyze Section -->
            <div class="text-center pt-6">
              <h2 class="text-2xl font-bold text-gray-900 mb-2">¿Listo para analizar?</h2>
              <p class="text-gray-600 mb-6">Revisa que toda la información esté completa antes de continuar</p>
              
              <div class="flex justify-center gap-4">
                <button 
                  @click="resetForm"
                  class="px-6 py-3 rounded-lg font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 transition-all duration-200 border border-gray-300"
                >
                  <svg class="w-5 h-5 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
                  </svg>
                  Limpiar Formulario
                </button>
                
                <button 
                  @click="submitAnalysis"
                  :disabled="!isFormValid || isSubmitting"
                  :class="[
                    'px-8 py-3 rounded-lg font-medium text-white transition-all duration-200 bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5',
                    (!isFormValid || isSubmitting) && 'opacity-50 cursor-not-allowed transform-none'
                  ]"
                >
                  <svg v-if="isSubmitting" class="w-5 h-5 inline mr-2 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
                  </svg>
                  
                  <svg v-else class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                  </svg>
                  
                  {{ isSubmitting ? 'Procesando análisis...' : 'Iniciar Análisis de Calidad' }}
                </button>
              </div>
              
              <div v-if="!isFormValid" class="mt-4 text-center">
                <p class="text-sm text-amber-600 flex items-center justify-center">
                  <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
                  </svg>
                  Completa todos los campos requeridos para continuar
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Fincas Section -->
      <div v-if="activeSection === 'fincas'" class="dashboard-section">
        <div class="section-header">
          <h1>Gestión de Fincas</h1>
          <p>Administra y monitorea tus fincas y lotes de cacao</p>
        </div>
        
        <div class="fincas-overview">
          <div class="fincas-stats">
            <div class="stat-card">
              <i class="fas fa-map-marked-alt"></i>
              <div class="stat-content">
                <h3>{{ fincasStats.totalFincas }}</h3>
                <p>Fincas Registradas</p>
              </div>
            </div>
            <div class="stat-card">
              <i class="fas fa-seedling"></i>
              <div class="stat-content">
                <h3>{{ fincasStats.totalLotes }}</h3>
                <p>Lotes Activos</p>
              </div>
            </div>
            <div class="stat-card">
              <i class="fas fa-ruler-combined"></i>
              <div class="stat-content">
                <h3>{{ fincasStats.areaTotal }} ha</h3>
                <p>Área Total</p>
              </div>
            </div>
          </div>
        </div>
        
        <div class="fincas-actions">
          <h3>Acciones de Fincas</h3>
          <div class="actions-grid">
            <div class="action-card">
              <i class="fas fa-plus-circle"></i>
              <h4>Registrar Nueva Finca</h4>
              <p>Agrega una nueva finca a tu portafolio</p>
              <button class="btn btn-primary" @click="registrarNuevaFinca">Registrar Finca</button>
            </div>
            <div class="action-card">
              <i class="fas fa-chart-line"></i>
              <h4>Monitoreo de Lotes</h4>
              <p>Visualiza el estado y rendimiento de tus lotes</p>
              <button class="btn btn-secondary" @click="monitorearLotes">Monitorear</button>
            </div>
          </div>
        </div>
      </div>

      <!-- Registrar Finca Section -->
      <div v-if="activeSection === 'registrar-finca'" class="dashboard-section">
        <div class="section-header">
          <h1>Registrar Nueva Finca</h1>
          <p>Completa la información para registrar una nueva finca en tu portafolio</p>
        </div>
        
        <!-- Formulario de Registro de Finca -->
        <div class="bg-white shadow-lg rounded-xl border border-gray-100">
          <div class="p-8">
            <!-- Mensaje informativo -->
            <div class="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <div class="flex items-center">
                <svg class="w-5 h-5 text-blue-600 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
                <p class="text-sm text-blue-800">
                  Los campos marcados con <span class="text-green-600 font-medium">*</span> son obligatorios para completar el registro.
                </p>
              </div>
            </div>
            
            <!-- Información Básica -->
            <div class="mb-8">
              <h2 class="text-lg font-semibold text-gray-800 mb-6 pb-2 border-b border-gray-200">Información Básica</h2>
              
              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">
                    Nombre de la Finca 
                    <span class="text-green-600 ml-1">*</span>
                  </label>
                  <input 
                    v-model="nuevaFinca.nombre"
                    type="text" 
                    class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent transition-all duration-200"
                    placeholder="Ej: Finca El Paraíso"
                  />
                </div>
                
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">Código de la Finca</label>
                  <input 
                    v-model="nuevaFinca.codigo"
                    type="text" 
                    class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent transition-all duration-200"
                    placeholder="Ej: FIN-001"
                  />
                </div>
                
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">
                    Área Total (hectáreas) 
                    <span class="text-green-600 ml-1">*</span>
                  </label>
                  <input 
                    v-model="nuevaFinca.area"
                    type="number" 
                    step="0.1"
                    min="0"
                    class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent transition-all duration-200"
                    placeholder="0.0"
                  />
                </div>
                
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">Tipo de Suelo</label>
                  <select 
                    v-model="nuevaFinca.tipoSuelo"
                    class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent transition-all duration-200"
                  >
                    <option value="">Selecciona el tipo de suelo</option>
                    <option value="arcilloso">Arcilloso</option>
                    <option value="arenoso">Arenoso</option>
                    <option value="limoso">Limoso</option>
                    <option value="franco">Franco</option>
                    <option value="orgánico">Orgánico</option>
                  </select>
                </div>
              </div>
            </div>

            <!-- Ubicación -->
            <div class="mb-8">
              <h2 class="text-lg font-semibold text-gray-800 mb-6 pb-2 border-b border-gray-200">Ubicación</h2>
              
              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">
                    Departamento 
                    <span class="text-green-600 ml-1">*</span>
                  </label>
                  <input 
                    v-model="nuevaFinca.departamento"
                    type="text" 
                    class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent transition-all duration-200"
                    placeholder="Ej: Santander"
                  />
                </div>
                
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">
                    Municipio 
                    <span class="text-green-600 ml-1">*</span>
                  </label>
                  <input 
                    v-model="nuevaFinca.municipio"
                    type="text" 
                    class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent transition-all duration-200"
                    placeholder="Ej: Bucaramanga"
                  />
                </div>
                
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">Vereda</label>
                  <input 
                    v-model="nuevaFinca.vereda"
                    type="text" 
                    class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent transition-all duration-200"
                    placeholder="Ej: La Esperanza"
                  />
                </div>
                
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">Altitud (msnm)</label>
                  <input 
                    v-model="nuevaFinca.altitud"
                    type="number" 
                    min="0"
                    class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent transition-all duration-200"
                    placeholder="0"
                  />
                </div>
              </div>
            </div>

            <!-- Información Adicional -->
            <div class="mb-8">
              <h2 class="text-lg font-semibold text-gray-800 mb-6 pb-2 border-b border-gray-200">Información Adicional</h2>
              
              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">Año de Establecimiento</label>
                  <input 
                    v-model="nuevaFinca.anoEstablecimiento"
                    type="number" 
                    min="1900"
                    :max="new Date().getFullYear()"
                    class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent transition-all duration-200"
                    placeholder="Ej: 2020"
                  />
                </div>
                
                <div>
                  <label class="block text-sm font-medium text-gray-700 mb-2">Estado de la Finca</label>
                  <select 
                    v-model="nuevaFinca.estado"
                    class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent transition-all duration-200"
                  >
                    <option value="activa">Activa</option>
                    <option value="en-desarrollo">En Desarrollo</option>
                    <option value="temporal">Temporal</option>
                    <option value="inactiva">Inactiva</option>
                  </select>
                </div>
                
                <div class="md:col-span-2">
                  <label class="block text-sm font-medium text-gray-700 mb-2">Descripción</label>
                  <textarea 
                    v-model="nuevaFinca.descripcion"
                    rows="3"
                    class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent transition-all duration-200"
                    placeholder="Describe las características especiales de tu finca..."
                  ></textarea>
                </div>
              </div>
            </div>

            <!-- Botones de Acción -->
            <div class="flex justify-end space-x-4 pt-6 border-t border-gray-200">
              <button 
                @click="cancelarRegistroFinca"
                class="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition-all duration-200 font-medium"
              >
                Cancelar
              </button>
              
              <button 
                @click="guardarFinca"
                :disabled="!isFincaFormValid || isGuardandoFinca"
                :class="[
                  'px-6 py-3 rounded-lg text-white font-medium transition-all duration-200',
                  isFincaFormValid && !isGuardandoFinca
                    ? 'bg-green-600 hover:bg-green-700 shadow-lg hover:shadow-xl'
                    : 'bg-gray-400 cursor-not-allowed'
                ]"
              >
                <svg v-if="isGuardandoFinca" class="w-4 h-4 inline mr-2 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
                </svg>
                {{ isGuardandoFinca ? 'Guardando...' : 'Guardar Finca' }}
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Reports Section -->
      <div v-if="activeSection === 'reports'" class="dashboard-section">
        <div class="section-header">
          <h1>Reportes y Estadísticas</h1>
          <p>Genera reportes detallados de tus análisis</p>
        </div>
        
        <div class="reports-grid">
          <div class="report-card">
            <h3>Reporte de Calidad</h3>
            <p>Análisis detallado de la calidad de tus lotes</p>
            <button 
              class="btn btn-primary" 
              @click="handleGenerateReport('quality')"
              :disabled="loading"
            >
              {{ loading ? 'Generando...' : 'Generar Reporte' }}
            </button>
          </div>
          <div class="report-card">
            <h3>Reporte de Defectos</h3>
            <p>Identificación y clasificación de defectos</p>
            <button 
              class="btn btn-primary" 
              @click="handleGenerateReport('defects')"
              :disabled="loading"
            >
              {{ loading ? 'Generando...' : 'Generar Reporte' }}
            </button>
          </div>
          <div class="report-card">
            <h3>Reporte de Rendimiento</h3>
            <p>Métricas de rendimiento por período</p>
            <button 
              class="btn btn-primary" 
              @click="handleGenerateReport('performance')"
              :disabled="loading"
            >
              {{ loading ? 'Generando...' : 'Generar Reporte' }}
            </button>
          </div>
        </div>
      </div>

      <!-- History Section -->
      <div v-if="activeSection === 'history'" class="dashboard-section">
        <div class="section-header">
          <h1>Historial de Análisis</h1>
          <p>Revisa todos tus análisis de granos de cacao</p>
        </div>
        
        <ImageHistoryCard 
          :initial-images="recentAnalyses"
          :auto-load="true"
          @image-selected="handleImageSelected"
          @refresh-requested="refreshData"
        />
      </div>

      <!-- Settings Section -->
      <div v-if="activeSection === 'settings'" class="dashboard-section">
        <div class="section-header">
          <h1>Configuración</h1>
          <p>Gestiona tu perfil y preferencias</p>
        </div>
        
        <div class="settings-grid">
          <div class="settings-card">
            <h3>Perfil de Usuario</h3>
            <form class="profile-form">
              <div class="form-group">
                <label>Nombre completo</label>
                <input type="text" v-model="userProfile.fullName" placeholder="Tu nombre completo">
              </div>
              <div class="form-group">
                <label>Email</label>
                <input type="email" v-model="userProfile.email" placeholder="tu@email.com">
              </div>
              <div class="form-group">
                <label>Teléfono</label>
                <input type="tel" v-model="userProfile.phone" placeholder="+57 300 123 4567">
              </div>
              <button type="submit" class="btn btn-primary">Guardar Cambios</button>
            </form>
          </div>
          
          <div class="settings-card">
            <h3>Preferencias</h3>
            <div class="preferences">
              <div class="preference-item">
                <label>
                  <input type="checkbox" v-model="userPreferences.notifications">
                  Recibir notificaciones por email
                </label>
              </div>
              <div class="preference-item">
                <label>
                  <input type="checkbox" v-model="userPreferences.autoReports">
                  Generar reportes automáticamente
                </label>
              </div>
              <div class="preference-item">
                <label>
                  <input type="checkbox" v-model="userPreferences.dataSharing">
                  Compartir datos anónimos para investigación
                </label>
              </div>
            </div>
            <button class="btn btn-secondary">Guardar Preferencias</button>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import { useAuthStore } from '@/stores/auth';
import { useImageStats } from '@/composables/useImageStats'
import ImageHistoryCard from '@/components/dashboard/ImageHistoryCard.vue'
import AgricultorSidebar from '@/components/common/AgricultorSidebar.vue'

export default {
  name: 'AgricultorDashboard',
  components: {
    AgricultorSidebar,
    ImageHistoryCard
  },
  setup() {
    const authStore = useAuthStore();
    const sidebarCollapsed = ref(localStorage.getItem('sidebarCollapsed') === 'true');
    const activeSection = ref('overview');
    
    // Usar composable para estadísticas reales
    const { 
      stats, 
      loading, 
      error, 
      fetchStats, 
      fetchImages, 
      generateReport,
      totalImages,
      processedImages,
      processingRate,
      averageConfidence,
      averageDimensions,
      regionStats,
      topFincas
    } = useImageStats();
    
    // Usar datos reales del usuario autenticado
    const farmerName = computed(() => authStore.userFullName || 'Usuario');
    
    // Datos de análisis recientes (ahora desde API)
    const recentAnalyses = ref([]);
    const imagesLoading = ref(false);
    
    // Cargar datos reales al montar el componente
    onMounted(async () => {
      await Promise.all([
        fetchStats(),
        loadRecentAnalyses()
      ]);
    });
    
    // Función para cargar análisis recientes
    async function loadRecentAnalyses() {
      imagesLoading.value = true;
      try {
        const data = await fetchImages(1, { page_size: '5' });
        recentAnalyses.value = data.results.map(image => ({
          id: `CAC-${image.id}`,
          status: image.processed ? 'completed' : 'pending',
          statusLabel: image.processed ? 'Completado' : 'Pendiente',
          quality: image.prediction ? Math.round(image.prediction.average_confidence * 100) : 0,
          defects: image.prediction ? Math.round((1 - image.prediction.average_confidence) * 100 * 10) / 10 : 0,
          avgSize: image.prediction ? Math.round((image.prediction.alto_mm + image.prediction.ancho_mm + image.prediction.grosor_mm) / 3 * 10) / 10 : 0,
          date: new Date(image.created_at).toLocaleDateString('es-ES')
        }));
      } catch (err) {
        console.error('Error loading recent analyses:', err);
      } finally {
        imagesLoading.value = false;
      }
    }
    
    // Función para generar reportes
    async function handleGenerateReport(reportType) {
      const filters = {
        date_from: filterDateFrom.value,
        date_to: filterDateTo.value,
        region: filterRegion.value,
        finca: filterFinca.value
      };
      
      const success = await generateReport(reportType, filters);
      if (success) {
        // Mostrar mensaje de éxito
        console.log(`Reporte ${reportType} generado exitosamente`);
      }
    }
    
    // Función para refrescar datos
    async function refreshData() {
      await Promise.all([
        fetchStats(),
        loadRecentAnalyses()
      ]);
    }
    
    // Función para manejar selección de imagen
    function handleImageSelected(image) {
      console.log('Imagen seleccionada:', image);
      // Aquí se puede agregar lógica adicional si es necesario
    }
    
    // Computed para estadísticas formateadas
    const formattedStats = computed(() => ({
      totalBatches: totalImages.value,
      batchesChange: '+0%', // TODO: Calcular cambio porcentual
      avgQuality: Math.round(averageConfidence.value * 100),
      qualityChange: '+0%', // TODO: Calcular cambio porcentual
      defectRate: Math.round((1 - averageConfidence.value) * 100 * 10) / 10,
      defectChange: '+0%' // TODO: Calcular cambio porcentual
    }));
    
    const formattedFincasStats = computed(() => ({
      totalFincas: topFincas.value.length,
      totalLotes: processedImages.value,
      areaTotal: 0, // TODO: Calcular área total
      ultimaActualizacion: 'Hoy'
    }));
    
    // Variables de filtros para reportes
    const filterDateFrom = ref('');
    const filterDateTo = ref('');
    const filterRegion = ref('');
    const filterFinca = ref('');
    
    const isUploading = ref(false);
    const uploadProgress = ref(0);
    const analysisResult = ref(null);
    const batchData = ref({
      finca: '',
      agricultor: '',
      nombreLote: '',
      fechaRecoleccion: '',
      observaciones: '',
      lugarOrigen: '',
      genetica: '',
      origen: ''
    });
    const formErrors = ref({
      hasAttemptedSubmit: false,
      finca: '',
      agricultor: '',
      nombreLote: '',
      fechaRecoleccion: '',
      observaciones: '',
      lugarOrigen: '',
      genetica: '',
      origen: '',
      images: ''
    });
    const images = ref([]);
    const capturedImages = ref([]);
    const currentTab = ref('upload'); // 'upload' or 'camera'
    const isSubmitting = ref(false);
    const tabs = ref([
      { name: 'upload', label: 'Subir Imágenes' },
      { name: 'camera', label: 'Capturar Imagen' }
    ]);

    // Variables para el formulario de finca
    const nuevaFinca = ref({
      nombre: '',
      codigo: '',
      area: '',
      tipoSuelo: '',
      departamento: '',
      municipio: '',
      vereda: '',
      altitud: '',
      anoEstablecimiento: '',
      estado: 'activa',
      descripcion: ''
    });

    const fincaErrors = ref({
      nombre: '',
      area: '',
      departamento: '',
      municipio: ''
    });

    const isGuardandoFinca = ref(false);
    const hasAttemptedSubmit = ref(false);

    const filteredAnalyses = computed(() => {
      let filtered = [...recentAnalyses.value];
      
      if (historyFilter.value.quality !== 'all') {
        const qualityRanges = {
          excellent: analysis => analysis.quality >= 90,
          good: analysis => analysis.quality >= 80 && analysis.quality < 90,
          fair: analysis => analysis.quality >= 70 && analysis.quality < 80,
          poor: analysis => analysis.quality < 70
        };
        filtered = filtered.filter(qualityRanges[historyFilter.value.quality]);
      }
      
      return filtered;
    });

    const isFormValid = computed(() => {
      // Solo validar si se ha intentado enviar el formulario
      if (!formErrors.value.hasAttemptedSubmit) {
        return false;
      }
      
      let isValid = true;
      
      if (!batchData.value.finca) {
        formErrors.value.finca = 'La finca es requerida';
        isValid = false;
      } else {
        formErrors.value.finca = '';
      }
      
      if (!batchData.value.agricultor) {
        formErrors.value.agricultor = 'El agricultor es requerido';
        isValid = false;
      } else {
        formErrors.value.agricultor = '';
      }
      
      if (!batchData.value.nombreLote) {
        formErrors.value.nombreLote = 'El nombre del lote es requerido';
        isValid = false;
      } else {
        formErrors.value.nombreLote = '';
      }
      
      if (!batchData.value.fechaRecoleccion) {
        formErrors.value.fechaRecoleccion = 'La fecha de recolección es requerida';
        isValid = false;
      } else {
        formErrors.value.fechaRecoleccion = '';
      }
      
      if (!batchData.value.lugarOrigen) {
        formErrors.value.lugarOrigen = 'El lugar de origen es requerido';
        isValid = false;
      } else {
        formErrors.value.lugarOrigen = '';
      }
      
      if (!batchData.value.genetica) {
        formErrors.value.genetica = 'La genética es requerida';
        isValid = false;
      } else {
        formErrors.value.genetica = '';
      }
      
      if (currentTab.value === 'upload' && images.value.length === 0) {
        formErrors.value.images = 'Debes subir al menos una imagen';
        isValid = false;
      } else {
        formErrors.value.images = '';
      }
      
      if (currentTab.value === 'camera' && capturedImages.value.length === 0) {
        formErrors.value.images = 'Debes capturar al menos una imagen';
        isValid = false;
      } else {
        formErrors.value.images = '';
      }
      
      return isValid;
    });

    const checkScreenSize = () => {
      if (window.innerWidth <= 768) {
        sidebarCollapsed.value = true;
        localStorage.setItem('sidebarCollapsed', 'true');
      }
    };

    const setActiveSection = (section) => {
      activeSection.value = section;
    };

    const toggleSidebar = () => {
      sidebarCollapsed.value = !sidebarCollapsed.value;
      localStorage.setItem('sidebarCollapsed', sidebarCollapsed.value);
    };

    const registrarNuevaFinca = () => {
      activeSection.value = 'registrar-finca';
    };

    const monitorearLotes = () => {
      alert('Función de monitoreo de lotes en desarrollo');
    };

    const logout = async () => {
      if (confirm('¿Estás seguro de que quieres cerrar sesión?')) {
        try {
          await authStore.logout();
        } catch (error) {
          console.error('Error al cerrar sesión:', error);
          authStore.clearAll();
        }
      }
    };

    const goBack = () => {
      activeSection.value = 'overview';
    };

    const openUploadModal = () => {
      // This will be handled by the UploadSection component
    };

    const getImageUrl = (img) => {
      // If img is already a data URL, return it
      if (typeof img === 'string' && img.startsWith('data:')) {
        return img;
      }
      // If img is a File object, create a data URL
      if (img instanceof File) {
        return URL.createObjectURL(img);
      }
      // If img is an object with a url property
      if (img && img.url) {
        return img.url;
      }
      // Default fallback - return the img as is
      return img;
    };

    const handleFileUpload = (event) => {
      const files = event.target.files;
      if (files && files.length > 0) {
        for (let i = 0; i < files.length; i++) {
          const reader = new FileReader();
          reader.onload = (e) => {
            images.value.push(e.target.result);
          };
          reader.readAsDataURL(files[i]);
        }
      }
    };

    const clearFieldError = (fieldName) => {
      if (formErrors.value[fieldName]) {
        formErrors.value[fieldName] = '';
      }
    };

    const handleCapturedImage = (imageData) => {
      capturedImages.value.push(imageData);
    };

    const removeImage = (index) => {
      images.value.splice(index, 1);
    };

    const removeCapturedImage = (index) => {
      capturedImages.value.splice(index, 1);
    };

    const submitAnalysis = async () => {
      // Activar la validación
      formErrors.value.hasAttemptedSubmit = true;
      
      if (!isFormValid.value) {
        alert('Por favor, completa todos los campos requeridos.');
        return;
      }

      isSubmitting.value = true;
      analysisResult.value = null;
      formErrors.value = {};

      try {
        const formData = new FormData();
        if (currentTab.value === 'upload') {
          for (let i = 0; i < images.value.length; i++) {
            formData.append('images', images.value[i]);
          }
        } else if (currentTab.value === 'camera') {
          for (let i = 0; i < capturedImages.value.length; i++) {
            formData.append('images', capturedImages.value[i]);
          }
        }

        formData.append('batchName', batchData.value.nombreLote);
        formData.append('finca', batchData.value.finca);
        formData.append('agricultor', batchData.value.agricultor);
        formData.append('fechaRecoleccion', batchData.value.fechaRecoleccion);
        formData.append('observaciones', batchData.value.observaciones);
        formData.append('lugarOrigen', batchData.value.lugarOrigen);
        formData.append('genetica', batchData.value.genetica);
        formData.append('origen', batchData.value.origen);

        const response = await fetch('http://localhost:5000/api/analyze', { // Replace with your backend endpoint
          method: 'POST',
          body: formData
        });

        if (!response.ok) {
          const error = await response.json();
          throw new Error(error.message || 'Error al enviar el análisis');
        }

        const result = await response.json();
        analysisResult.value = result;
        images.value = []; // Clear images after submission
        capturedImages.value = []; // Clear captured images after submission
        currentTab.value = 'upload'; // Reset to upload tab
        alert('Análisis enviado con éxito!');
      } catch (error) {
        console.error('Error submitting analysis:', error);
        alert(`Error al enviar el análisis: ${error.message}`);
      } finally {
        isSubmitting.value = false;
      }
    };


    return {
      sidebarCollapsed,
      activeSection,
      farmerName,
      recentAnalyses,
      formattedStats,
      formattedFincasStats,
      loading,
      error,
      imagesLoading,
      checkScreenSize,
      setActiveSection,
      toggleSidebar,
      registrarNuevaFinca,
      monitorearLotes,
      logout,
      goBack,
      handleGenerateReport,
      refreshData,
      loadRecentAnalyses,
      handleImageSelected
    };
  },
  mounted() {
    this.checkScreenSize();
    window.addEventListener('resize', this.checkScreenSize);
  },
  beforeUnmount() {
    window.removeEventListener('resize', this.checkScreenSize);
  }
};
</script>

<style>
.farmer-dashboard-container {
  display: flex;
  min-height: 100vh;
  background-color: #f8f9fa;
}

/* Estadísticas básicas */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: white;
  border-radius: 10px;
  padding: 1.5rem;
  text-align: center;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  transition: transform 0.2s ease;
}

.stat-card:hover {
  transform: translateY(-3px);
}

.stat-card h3 {
  font-size: 2rem;
  color: #27ae60;
  margin: 0 0 0.5rem 0;
}

.stat-card p {
  color: #7f8c8d;
  margin: 0;
}

/* Análisis recientes */
.recent-analyses {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.analysis-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  background: #f8f9fa;
  border-radius: 8px;
  border-left: 4px solid #27ae60;
}

.analysis-id {
  font-weight: 600;
  color: #2c3e50;
}

.analysis-quality {
  color: #27ae60;
  font-weight: 600;
}

.analysis-date {
  color: #7f8c8d;
  font-size: 0.9rem;
}

/* Acciones rápidas */
.quick-actions {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem;
  background: white;
  border: 2px solid #27ae60;
  border-radius: 8px;
  color: #27ae60;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.action-btn:hover {
  background: #27ae60;
  color: white;
  transform: translateY(-2px);
}

.action-btn i {
  font-size: 1.2rem;
}

/* Botón de volver */
.back-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  background: #f8f9fa;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  color: #6c757d;
  cursor: pointer;
  transition: all 0.2s ease;
}

.back-button:hover {
  background: #e9ecef;
  color: #495057;
}

/* Header de análisis */
.analysis-header {
  text-align: center;
  margin-bottom: 2rem;
}

.analysis-header h1 {
  color: #2c3e50;
  margin-bottom: 1rem;
  font-size: 2rem;
}

.analysis-header p {
  color: #7f8c8d;
  font-size: 1.1rem;
  max-width: 600px;
  margin: 0 auto;
}

/* Sidebar Styles */
.dashboard-sidebar {
  width: 280px; 
  background: linear-gradient(135deg, #27ae60 0%, #2ecc71 100%); 
  color: white;
  transition: all 0.3s ease; 
  box-shadow: 2px 0 10px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column; 
}
.sidebar-collapsed {
  width: 70px;
}

.sidebar-collapsed .sidebar-header {
  padding: 1rem 0.5rem;
  justify-content: center;
}

.sidebar-collapsed .farmer-info {
  justify-content: center;
  padding: 0.5rem;
}

.sidebar-collapsed .farmer-info:hover {
  background: rgba(255, 255, 255, 0.1);
  transform: scale(1.1);
}

.sidebar-collapsed .farmer-avatar {
  animation: subtle-pulse 2s infinite;
}

@keyframes subtle-pulse {
  0%, 100% {
    box-shadow: 0 0 0 0 rgba(255, 255, 255, 0.4);
  }
  50% {
    box-shadow: 0 0 0 8px rgba(255, 255, 255, 0.1);
  }
}

.sidebar-collapsed .farmer-avatar {
  width: 40px;
  height: 40px;
  font-size: 1.2rem;
}

.sidebar-collapsed .nav-link {
  padding: 1rem;
  justify-content: center;
  margin-right: 0;
}

.sidebar-collapsed .nav-link i {
  margin: 0;
}

.sidebar-collapsed .nav-link:hover {
  background: rgba(255, 255, 255, 0.1);
  transform: none;
}

.sidebar-collapsed .nav-item.active .nav-link {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  margin: 0.5rem;
}

.sidebar-header {
  padding: 1.5rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.farmer-info {
  display: flex;
  align-items: center;
  gap: 1rem;
  transition: all 0.2s ease;
  border-radius: 8px;
  padding: 0.5rem;
}

.farmer-info:hover {
  background: rgba(255, 255, 255, 0.1);
  transform: scale(1.05);
}

.farmer-avatar {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  transition: all 0.2s ease;
  position: relative;
}

.farmer-avatar::after {
  content: '';
  position: absolute;
  bottom: -2px;
  right: -2px;
  width: 12px;
  height: 12px;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.6rem;
  color: #27ae60;
  opacity: 0;
  transition: opacity 0.2s ease;
}

.farmer-info:hover .farmer-avatar::after {
  opacity: 1;
}

.farmer-info:active {
  transform: scale(0.95);
}

/* Indicador de estado del sidebar */
.sidebar-header::before {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  width: 4px;
  height: 100%;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 2px 0 0 2px;
  transition: all 0.3s ease;
}

.sidebar-collapsed .sidebar-header::before {
  background: rgba(255, 255, 255, 0.6);
  width: 6px;
}

.farmer-details h3 {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 600;
}

.farmer-role {
  font-size: 0.9rem;
  opacity: 0.8;
}

.sidebar-toggle {
  background: none;
  border: none;
  color: white;
  font-size: 1.2rem;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 4px;
  transition: background-color 0.2s ease;
}

.sidebar-toggle:hover {
  background: rgba(255, 255, 255, 0.1);
}

.sidebar-nav {
  flex: 1;
  padding: 1rem 0;
}

.nav-menu {
  list-style: none;
  padding: 0;
  margin: 0;
}

.nav-item {
  margin: 0.5rem 0;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem 1.5rem;
  color: white;
  text-decoration: none;
  transition: all 0.2s ease;
  border-radius: 0 25px 25px 0;
  margin-right: 1rem;
}

.nav-link:hover {
  background: rgba(255, 255, 255, 0.1);
  transform: translateX(5px);
}

.nav-item.active .nav-link {
  background: rgba(255, 255, 255, 0.2);
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.nav-link i {
  font-size: 1.2rem;
  width: 20px;
  text-align: center;
}

.sidebar-footer {
  padding: 1.5rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.quick-stats {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stat-label {
  font-size: 0.9rem;
  opacity: 0.8;
}

.stat-value {
  font-weight: 600;
  font-size: 1.1rem;
}

/* Logout Section Styles */
.logout-section {
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  animation: fadeInUp 0.3s ease;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.logout-btn {
  width: 100%;
  background: rgba(231, 76, 60, 0.8);
  color: white;
  border: none;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  font-size: 0.95rem;
  transition: all 0.2s ease;
}

.logout-btn:hover {
  background: rgba(231, 76, 60, 1);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(231, 76, 60, 0.3);
}

.logout-btn:active {
  transform: translateY(0);
}

.logout-btn i {
  font-size: 1rem;
}

/* Collapsed sidebar logout button */
.sidebar-footer-collapsed {
  padding: 1rem 0.5rem;
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  display: flex;
  justify-content: center;
}

.logout-btn-collapsed {
  width: 40px;
  height: 40px;
  background: rgba(231, 76, 60, 0.8);
  color: white;
  border: none;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.logout-btn-collapsed:hover {
  background: rgba(231, 76, 60, 1);
  transform: scale(1.1);
  box-shadow: 0 4px 12px rgba(231, 76, 60, 0.3);
}

.logout-btn-collapsed:active {
  transform: scale(0.95);
}

/* Indicador de logout en sidebar colapsado */
.sidebar-collapsed .logout-btn-collapsed {
  position: relative;
}

.sidebar-collapsed .logout-btn-collapsed::after {
  content: '';
  position: absolute;
  top: -2px;
  right: -2px;
  width: 8px;
  height: 8px;
  background: rgba(255, 255, 255, 0.9);
  border-radius: 50%;
  opacity: 0;
  transition: opacity 0.2s ease;
}

.sidebar-collapsed .logout-btn-collapsed:hover::after {
  opacity: 1;
}

/* Main Content Styles */
.dashboard-main {
  flex: 1;
  padding: 1rem 1.5rem;
  transition: padding-left 0.3s ease;
  width: 100%;
  max-width: 1400px; /* Ancho máximo para el contenido */
  margin: 0 auto;      /* Centra el contenedor en el espacio disponible */
  box-sizing: border-box;
  overflow-x: hidden;
}

/* Contenido principal cuando está expandido */
.main-expanded {
  padding-left: 280px;
  /* Centra el contenido en toda la pantalla disponible */
  display: flex;
  flex-direction: column;
  align-items: center;
}

/* Ajusta el ancho del contenido cuando está expandido */
.main-expanded .dashboard-section {
  width: 100%;
  max-width: 1000px;
  margin: 0 auto;
}

/* Contenido principal cuando está colapsado */
.main-collapsed {
  padding-left: 70px;
  /* Centra el contenido en toda la pantalla disponible */
  display: flex;
  flex-direction: column;
  align-items: center;
}

/* Ajusta el ancho del contenido cuando está colapsado */
.main-collapsed .dashboard-section {
  width: 100%;
  max-width: 800px;
  margin: 0 auto;
  text-align: center;
}

/* Centra el contenido de texto cuando el sidebar está colapsado */
.main-collapsed .section-header {
  max-width: 800px;
  margin: 0 auto 1.5rem auto;
}

/* Centra el contenido de texto cuando el sidebar está expandido */
.main-expanded .section-header {
  max-width: 1000px;
  margin: 0 auto 1.5rem auto;
}

/* Ajustes responsivos */
@media (max-width: 1024px) {
  .dashboard-main {
    padding: 1.5rem;
  }
  
  .main-expanded {
    padding-left: 200px;
  }
}

@media (max-width: 768px) {
  .dashboard-main {
    padding-left: 70px !important;
    padding: 1rem;
  }
  
  .main-expanded,
  .main-collapsed {
    padding-left: 70px !important;
  }
  
  .section-header h1 {
    font-size: 1.75rem;
  }
}

@media (max-width: 480px) {
  .dashboard-main {
    padding-left: 60px !important;
    padding: 0.75rem;
  }
  
  .main-expanded,
  .main-collapsed {
    padding-left: 60px !important;
  }
  
  .section-header h1 {
    font-size: 1.5rem;
  }
}

.dashboard-section {
  max-width: 1000px;
  margin: 0 auto;
  width: 100%;
}

/* Ajusta el ancho máximo según el estado del sidebar */
.main-expanded .dashboard-section {
  max-width: 1000px;
}

.main-collapsed .dashboard-section {
  max-width: 800px;
}

.section-header {
  margin-bottom: 1.5rem;
  text-align: center;
}

.section-header h1 {
  color: #2c3e50;
  margin-bottom: 0.5rem;
  font-size: 2.25rem;
}

.section-header p {
  color: #7f8c8d;
  font-size: 1rem;
  margin-bottom: 0;
}

/* Overview Grid */
.overview-grid {
  display: grid;
  grid-template-columns: 0fr 5fr; /* Proporción 3:2 */
  gap: 1.5rem;
  margin: 0.5rem 0;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
}

/* Ajusta el grid para diferentes estados del sidebar */
.main-expanded .overview-grid {
  grid-template-columns: 0fr 5fr; /* Mantiene la proporción original */
  max-width: 1000px;
}

.main-collapsed .overview-grid {
  grid-template-columns: 1fr 1fr; /* Cambia a 2 columnas iguales */
  gap: 1rem;
  max-width: 800px;
}



/* Centra las tarjetas de estadísticas cuando el sidebar está colapsado */
.main-collapsed .fincas-stats {
  max-width: 800px;
  margin: 0 auto 1.5rem auto;
}

.main-collapsed .fincas-actions {
  max-width: 800px;
  margin: 0 auto 1.5rem auto;
}

.main-collapsed .fincas-grid {
  max-width: 800px;
  margin: 0 auto;
}

/* Centra las tarjetas de estadísticas cuando el sidebar está expandido */
.main-expanded .fincas-stats {
  max-width: 1000px;
  margin: 0 auto 1.5rem auto;
}

.main-expanded .fincas-actions {
  max-width: 1000px;
  margin: 0 auto 1.5rem auto;
}

.main-expanded .fincas-grid {
  max-width: 1000px;
  margin: 0 auto;
}

/* Estilo base para ambas tarjetas */
.overview-card {
  background: white;
  border-radius: 12px;
  padding: 1.25rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  transition: transform 0.2s, box-shadow 0.2s;
  height: 100%;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
}

/* Centra las tarjetas de estadísticas principales */
.main-expanded .overview-grid:first-child {
  max-width: 1000px;
  margin: 0 auto;
}

.main-collapsed .overview-grid:first-child {
  max-width: 800px;
  margin: 0 auto;
}

.overview-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.overview-card h3 {
  color: #2c3e50;
  margin: 0 0 1rem 0;
  font-size: 1.25rem;
  font-weight: 600;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #eee;
}

/* Ajustes responsivos */
@media (max-width: 1200px) {
  .overview-grid {
    gap: 1rem;
  }
  
  .overview-card {
    padding: 1rem;
  }
}

@media (max-width: 992px) {
  .overview-grid {
    grid-template-columns: 1fr;
    gap: 0.75rem;
  }
  
  .overview-card {
    padding: 1rem;
  }
}

@media (max-width: 768px) {
  .overview-card {
    padding: 0.75rem;
  }
  
  .overview-card h3 {
    font-size: 1.1rem;
    margin-bottom: 0.75rem;
  }
}

/* Ajustes específicos para la tarjeta de actividad reciente */
.overview-card:first-child {
  min-height: 400px; /* Altura mínima para mejor visualización */
}

/* Ajustes específicos para la tarjeta de acciones rápidas */
.overview-card:last-child {
  background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
}

/* Analysis Tools */
.analysis-tools {
  margin-top: 2rem;
}

.analysis-tools h3 {
  color: #2c3e50;
  margin-bottom: 1.5rem;
  font-size: 1.5rem;
}

.tools-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}

.tool-card {
  background: white;
  border-radius: 10px;
  padding: 2rem;
  text-align: center;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  transition: transform 0.2s ease;
}

.tool-card:hover {
  transform: translateY(-5px);
}

.tool-card i {
  font-size: 3rem;
  color: #27ae60;
  margin-bottom: 1rem;
}

.tool-card h4 {
  color: #2c3e50;
  margin-bottom: 1rem;
  font-size: 1.3rem;
}

.tool-card p {
  color: #7f8c8d;
  margin-bottom: 1.5rem;
  line-height: 1.5;
}

/* Reports Grid */
.reports-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}

.report-card {
  background: white;
  border-radius: 10px;
  padding: 2rem;
  text-align: center;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  transition: transform 0.2s ease;
}

.report-card:hover {
  transform: translateY(-5px);
}

.report-card h3 {
  color: #2c3e50;
  margin-bottom: 1rem;
  font-size: 1.3rem;
}

.report-card p {
  color: #7f8c8d;
  margin-bottom: 1.5rem;
  line-height: 1.5;
}

/* History Filters */
.history-filters {
  background: white;
  border-radius: 10px;
  padding: 1.5rem;
  margin-bottom: 2rem;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  display: flex;
  gap: 2rem;
  flex-wrap: wrap;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.filter-group label {
  font-weight: 600;
  color: #2c3e50;
}

.filter-group select {
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

/* Settings Grid */
.settings-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 2rem;
}

.settings-card {
  background: white;
  border-radius: 10px;
  padding: 2rem;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.settings-card h3 {
  color: #2c3e50;
  margin-bottom: 1.5rem;
  font-size: 1.3rem;
}

.profile-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-weight: 600;
  color: #2c3e50;
}

.form-group input {
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

.preferences {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.preference-item label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  color: #2c3e50;
}

.preference-item input[type="checkbox"] {
  width: auto;
}

/* Button Styles */
.btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.2s ease;
  text-decoration: none;
  justify-content: center;
}

.btn-primary {
  background-color: #27ae60;
  color: white;
}

.btn-primary:hover {
  background-color: #219653;
  transform: translateY(-2px);
}

.btn-secondary {
  background-color: #f1f2f6;
  color: #2c3e50;
}

.btn-secondary:hover {
  background-color: #dfe4ea;
  transform: translateY(-2px);
}

/* Responsive Design */
@media (max-width: 1600px) {
  .dashboard-main {
    padding: 1rem 1.25rem;
    max-width: 1200px;
  }
}

@media (max-width: 1366px) {
  .dashboard-main {
    max-width: 1100px;
  }
}

@media (max-width: 1200px) {
  .dashboard-main {
    max-width: 100%;
    padding: 1rem 1.5rem;
  }
}

@media (max-width: 768px) {
  .farmer-dashboard-container {
    flex-direction: row; /* Asegura que el menú y contenido estén en fila */
  }

  .dashboard-sidebar {
    position: fixed; /* Fija el menú en la pantalla */
    left: 0;
    top: 0;
    height: 100%;
    width: 70px !important; /* Ancho fijo de íconos */
    z-index: 1000;
  }

  /* Oculta los textos para forzar el modo colapsado */
  .sidebar-header .farmer-details,
  .sidebar-nav .nav-link span,
  .sidebar-footer {
    display: none;
  }

  .sidebar-footer-collapsed {
    display: flex !important; /* Muestra el botón de logout colapsado */
  }

  .dashboard-main {
    margin-left: 70px !important; /* Fuerza el espacio mínimo para el menú colapsado */
    padding: 0.75rem;
  }

  .main-expanded,
  .main-collapsed {
    margin-left: 70px !important; /* Mantiene el espacio mínimo en móvil */
  }

  /* Oculta botones innecesarios en esta vista */
  .desktop-collapse-button,
  .mobile-menu-button {
    display: none;
  }

  .section-header h1 {
    font-size: 2rem;
  }

  .history-filters {
    flex-direction: column;
  }

  .settings-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 480px) {
  .overview-grid,
  .tools-grid,
  .reports-grid,
  .settings-grid {
    grid-template-columns: 1fr;
  }
  
  .tool-card,
  .report-card,
  .settings-card {
    padding: 1.5rem;
  }
}

/* Estilos para el módulo de Fincas */
.fincas-overview {
  margin-bottom: 1.5rem;
}

.fincas-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.stat-card {
  background: white;
  border-radius: 10px;
  padding: 1.25rem;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  display: flex;
  align-items: center;
  gap: 1rem;
  transition: transform 0.2s ease;
}

.stat-card:hover {
  transform: translateY(-3px);
}

.stat-card i {
  font-size: 2rem;
  color: #27ae60;
  width: 40px;
  text-align: center;
}

.stat-content h3 {
  margin: 0;
  color: #2c3e50;
  font-size: 1.8rem;
  font-weight: 600;
}

.stat-content p {
  margin: 0;
  color: #7f8c8d;
  font-size: 0.9rem;
}

.fincas-actions {
  margin-bottom: 1.5rem;
}

.fincas-actions h3 {
  color: #2c3e50;
  margin-bottom: 1rem;
  font-size: 1.5rem;
}

.actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
}

.action-card {
  background: white;
  border-radius: 10px;
  padding: 1.5rem;
  text-align: center;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  transition: transform 0.2s ease;
}

.action-card:hover {
  transform: translateY(-5px);
}

.action-card i {
  font-size: 3rem;
  color: #27ae60;
  margin-bottom: 1rem;
}

.action-card h4 {
  color: #2c3e50;
  margin-bottom: 0.75rem;
  font-size: 1.3rem;
}

.action-card p {
  color: #7f8c8d;
  margin-bottom: 1.25rem;
  line-height: 1.5;
}

.fincas-list {
  margin-bottom: 1.5rem;
}

.fincas-list h3 {
  color: #2c3e50;
  margin-bottom: 1rem;
  font-size: 1.5rem;
}

.fincas-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1rem;
}

.finca-card {
  background: white;
  border-radius: 10px;
  padding: 1.25rem;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  transition: transform 0.2s ease;
}

.finca-card:hover {
  transform: translateY(-3px);
}

.finca-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid #ecf0f1;
}

.finca-header h4 {
  margin: 0;
  color: #2c3e50;
  font-size: 1.2rem;
}

.finca-status {
  padding: 0.25rem 0.75rem;
  border-radius: 15px;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
}

.finca-status.active {
  background: rgba(39, 174, 96, 0.1);
  color: #27ae60;
}

.finca-status.inactive {
  background: rgba(231, 76, 60, 0.1);
  color: #e74c3c;
}

.finca-details {
  margin-bottom: 1.25rem;
}

.finca-details p {
  margin: 0.5rem 0;
  color: #7f8c8d;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.finca-details i {
  width: 16px;
  color: #27ae60;
}

.finca-actions {
  display: flex;
  gap: 0.5rem;
}

.btn-sm {
  padding: 0.5rem 1rem;
  font-size: 0.9rem;
}

/* Responsive para fincas */
@media (max-width: 768px) {
  .fincas-stats {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .actions-grid {
    grid-template-columns: 1fr;
  }
  
  .fincas-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 480px) {
  .fincas-stats {
    grid-template-columns: 1fr;
  }
  
  .stat-card {
    padding: 1rem;
  }
  
  .action-card {
    padding: 1.5rem;
  }
  
  .finca-card {
    padding: 1rem;
  }
}

/* Estilos para la nueva vista de análisis */
.analysis-section {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.analysis-form {
  padding: 2rem;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-label {
  font-weight: 600;
  color: #374151;
  margin-bottom: 0.5rem;
  font-size: 0.875rem;
}

.form-input {
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  transition: all 0.2s;
}

.form-input:focus {
  outline: none;
  border-color: #10b981;
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1);
}

.form-textarea {
  resize: vertical;
  min-height: 80px;
}

.tabs-container {
  border-bottom: 1px solid #e5e7eb;
  margin-bottom: 1.5rem;
}

.tabs-nav {
  display: flex;
  justify-content: center;
  gap: 2rem;
}

.tab-button {
  padding: 1rem 0.25rem;
  border-bottom: 2px solid transparent;
  font-weight: 500;
  font-size: 0.875rem;
  color: #6b7280;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.tab-button:hover {
  color: #374151;
  border-color: #d1d5db;
}

.tab-button.active {
  color: #10b981;
  border-color: #10b981;
}

.upload-area {
  border: 2px dashed #d1d5db;
  border-radius: 0.5rem;
  padding: 2rem;
  text-align: center;
  transition: all 0.2s;
  cursor: pointer;
}

.upload-area:hover {
  border-color: #10b981;
  background-color: #f0fdf4;
}

.upload-icon {
  width: 3rem;
  height: 3rem;
  color: #9ca3af;
  margin-bottom: 1rem;
}

.upload-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: #111827;
  margin-bottom: 0.5rem;
}

.upload-description {
  color: #6b7280;
  margin-bottom: 1rem;
}

.upload-button {
  background-color: #10b981;
  color: white;
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  font-weight: 500;
  transition: all 0.2s;
}

.upload-button:hover {
  background-color: #059669;
  transform: translateY(-1px);
}

.image-preview-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 1rem;
  margin-top: 1rem;
}

.image-preview-item {
  position: relative;
  aspect-ratio: 1;
  border-radius: 0.5rem;
  overflow: hidden;
  background-color: #f3f4f6;
}

.image-preview-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.remove-image-btn {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  background-color: #ef4444;
  color: white;
  border-radius: 50%;
  width: 1.5rem;
  height: 1.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.2s;
  cursor: pointer;
}

.image-preview-item:hover .remove-image-btn {
  opacity: 1;
}

.camera-section {
  text-align: center;
  padding: 2rem;
}

.capture-button {
  background-color: #10b981;
  color: white;
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  font-weight: 500;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.2s;
}

.capture-button:hover {
  background-color: #059669;
  transform: translateY(-1px);
}

.submit-section {
  text-align: center;
  padding-top: 1.5rem;
}

.submit-button {
  padding: 1rem 2rem;
  border-radius: 0.5rem;
  font-weight: 600;
  font-size: 1rem;
  transition: all 0.2s;
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
}

.submit-button:enabled {
  background-color: #10b981;
  color: white;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.submit-button:enabled:hover {
  background-color: #059669;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.submit-button:disabled {
  background-color: #9ca3af;
  cursor: not-allowed;
  transform: none;
}

.progress-indicator {
  background-color: #eff6ff;
  border-left: 4px solid #3b82f6;
  padding: 1rem;
  margin-bottom: 1.5rem;
}

.progress-bar {
  width: 100%;
  background-color: #dbeafe;
  border-radius: 0.5rem;
  height: 0.5rem;
  margin-top: 0.5rem;
}

.progress-fill {
  background-color: #3b82f6;
  height: 100%;
  border-radius: 0.5rem;
  transition: width 0.3s ease;
}

.success-alert {
  background-color: #f0fdf4;
  border-left: 4px solid #22c55e;
  padding: 1rem;
  margin-bottom: 1.5rem;
}

.warning-message {
  color: #d97706;
  font-size: 0.875rem;
  margin-top: 1rem;
  text-align: center;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .analysis-form {
    padding: 1rem;
  }
  
  .form-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
  
  .tabs-nav {
    gap: 1rem;
  }
  
  .upload-area {
    padding: 1.5rem;
  }
  
  .image-preview-grid {
    grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
  }
}

@media (max-width: 640px) {
  .analysis-form {
    padding: 0.75rem;
  }
  
  .upload-area {
    padding: 1rem;
  }
  
  .upload-title {
    font-size: 1rem;
  }
  
  .submit-button {
    padding: 0.75rem 1.5rem;
    font-size: 0.875rem;
  }
}
</style>
