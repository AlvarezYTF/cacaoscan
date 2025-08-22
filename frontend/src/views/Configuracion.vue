<template>
  <div class="bg-gray-50 min-h-screen">
    <div class="flex h-screen">
      <!-- Sidebar -->
      <AdminSidebar 
        :user-initials="userInitials"
        :user-name="userName"
        :user-role="userRole"
        :sidebar-collapsed="sidebarCollapsed"
        @toggle-sidebar="toggleSidebar"
      />
      
      <!-- Contenido principal -->
      <div class="flex-1 flex flex-col min-w-0 overflow-hidden" :class="{ 'main-expanded': sidebarCollapsed }">
        <!-- Header de la página -->
        <div class="bg-white border-b border-gray-200 px-4 py-6 sm:px-6 lg:px-8">
          <div class="max-w-7xl mx-auto">
            <h1 class="text-2xl font-bold text-gray-900">Configuración del Sistema</h1>
            <p class="mt-2 text-sm text-gray-600">Gestiona la configuración general de la aplicación</p>
          </div>
        </div>
        
        <!-- Contenido principal -->
        <main class="flex-1 p-4 md:p-6 lg:p-8 pb-0 overflow-y-auto">
          <div class="max-w-7xl mx-auto">
            <!-- Pestañas de configuración -->
            <div class="bg-white rounded-lg shadow-sm border border-gray-200 mb-6">
              <div class="border-b border-gray-200">
                <nav class="-mb-px flex space-x-8 px-6" aria-label="Tabs">
                  <button
                    v-for="tab in tabs"
                    :key="tab.id"
                    @click="activeTab = tab.id"
                    :class="[
                      activeTab === tab.id
                        ? 'border-green-500 text-green-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300',
                      'whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm'
                    ]"
                  >
                    {{ tab.name }}
                  </button>
                </nav>
              </div>
              
              <!-- Contenido de las pestañas -->
              <div class="p-6">
                <!-- Usuarios y Roles -->
                <div v-if="activeTab === 'users'" class="space-y-6">
                  <div class="flex justify-between items-center">
                    <h3 class="text-lg font-medium text-gray-900">Gestión de Usuarios y Roles</h3>
                    <button
                      @click="showUserModal = true"
                      class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
                    >
                      <svg class="h-4 w-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
                      </svg>
                      Nuevo Usuario
                    </button>
                  </div>
                  
                  <!-- Tabla de usuarios -->
                  <div class="overflow-x-auto">
                    <table class="min-w-full divide-y divide-gray-200">
                      <thead class="bg-gray-50">
                        <tr>
                          <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Usuario</th>
                          <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Email</th>
                          <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Rol</th>
                          <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Estado</th>
                          <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Acciones</th>
                        </tr>
                      </thead>
                      <tbody class="bg-white divide-y divide-gray-200">
                        <tr v-for="user in users" :key="user.id">
                          <td class="px-6 py-4 whitespace-nowrap">
                            <div class="flex items-center">
                              <div class="h-10 w-10 rounded-full bg-green-100 flex items-center justify-center">
                                <span class="text-sm font-medium text-green-800">{{ user.initials }}</span>
                              </div>
                              <div class="ml-4">
                                <div class="text-sm font-medium text-gray-900">{{ user.name }}</div>
                              </div>
                            </div>
                          </td>
                          <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ user.email }}</td>
                          <td class="px-6 py-4 whitespace-nowrap">
                            <span :class="getRoleBadgeClass(user.role)" class="inline-flex px-2 py-1 text-xs font-semibold rounded-full">
                              {{ getRoleDisplay(user.role) }}
                            </span>
                          </td>
                          <td class="px-6 py-4 whitespace-nowrap">
                            <span :class="user.isActive ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'" class="inline-flex px-2 py-1 text-xs font-semibold rounded-full">
                              {{ user.isActive ? 'Activo' : 'Inactivo' }}
                            </span>
                          </td>
                          <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                            <button @click="editUser(user)" class="text-green-600 hover:text-green-900 mr-3">Editar</button>
                            <button @click="deleteUser(user.id)" class="text-red-600 hover:text-red-900">Eliminar</button>
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>

                <!-- Parámetros de Calidad -->
                <div v-if="activeTab === 'quality'" class="space-y-6">
                  <h3 class="text-lg font-medium text-gray-900">Parámetros de Calidad</h3>
                  
                  <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div class="space-y-4">
                      <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">Humedad Máxima (%)</label>
                        <div class="flex items-center space-x-4">
                          <input
                            type="range"
                            v-model="qualityParams.humidity"
                            min="0"
                            max="20"
                            step="0.1"
                            class="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
                          />
                          <span class="text-sm font-medium text-gray-900 w-16">{{ qualityParams.humidity }}%</span>
                        </div>
                      </div>
                      
                      <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">Defectos Máximos (%)</label>
                        <div class="flex items-center space-x-4">
                          <input
                            type="range"
                            v-model="qualityParams.defects"
                            min="0"
                            max="15"
                            step="0.5"
                            class="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
                          />
                          <span class="text-sm font-medium text-gray-900 w-16">{{ qualityParams.defects }}%</span>
                        </div>
                      </div>
                    </div>
                    
                    <div class="space-y-4">
                      <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">Coloración Mínima (escala 1-10)</label>
                        <div class="flex items-center space-x-4">
                          <input
                            type="range"
                            v-model="qualityParams.coloration"
                            min="1"
                            max="10"
                            step="0.5"
                            class="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
                          />
                          <span class="text-sm font-medium text-gray-900 w-16">{{ qualityParams.coloration }}</span>
                        </div>
                      </div>
                      
                      <div>
                        <label class="block text-sm font-medium text-gray-700 mb-2">Tamaño Mínimo (mm)</label>
                        <div class="flex items-center space-x-4">
                          <input
                            type="range"
                            v-model="qualityParams.size"
                            min="15"
                            max="25"
                            step="0.5"
                            class="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
                          />
                          <span class="text-sm font-medium text-gray-900 w-16">{{ qualityParams.size }}mm</span>
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  <div class="flex justify-end">
                    <button
                      @click="saveQualityParams"
                      class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
                    >
                      Guardar Parámetros
                    </button>
                  </div>
                </div>

                <!-- Procesos de Análisis -->
                <div v-if="activeTab === 'analysis'" class="space-y-6">
                  <div class="flex justify-between items-center">
                    <h3 class="text-lg font-medium text-gray-900">Procesos de Análisis</h3>
                    <button
                      @click="showAnalysisModal = true"
                      class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
                    >
                      <svg class="h-4 w-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
                      </svg>
                      Nuevo Proceso
                    </button>
                  </div>
                  
                  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    <div
                      v-for="process in analysisProcesses"
                      :key="process.id"
                      class="bg-gray-50 rounded-lg p-4 border border-gray-200"
                    >
                      <div class="flex justify-between items-start mb-2">
                        <h4 class="text-sm font-medium text-gray-900">{{ process.name }}</h4>
                        <span :class="getStatusBadgeClass(process.status)" class="inline-flex px-2 py-1 text-xs font-semibold rounded-full">
                          {{ process.status }}
                        </span>
                      </div>
                      <p class="text-sm text-gray-600 mb-3">{{ process.description }}</p>
                      <div class="flex space-x-2">
                        <button @click="editProcess(process)" class="text-sm text-green-600 hover:text-green-900">Editar</button>
                        <button @click="deleteProcess(process.id)" class="text-sm text-red-600 hover:text-red-900">Eliminar</button>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Configuración de Plataforma -->
                <div v-if="activeTab === 'platform'" class="space-y-6">
                  <h3 class="text-lg font-medium text-gray-900">Configuración de Plataforma</h3>
                  
                  <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div class="space-y-4">
                      <div>
                        <label class="block text-sm font-medium text-gray-700">Idioma</label>
                        <select v-model="platformConfig.language" class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm rounded-md">
                          <option value="es">Español</option>
                          <option value="en">English</option>
                          <option value="pt">Português</option>
                        </select>
                      </div>
                      
                      <div>
                        <label class="block text-sm font-medium text-gray-700">Unidades de Medida</label>
                        <select v-model="platformConfig.units" class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm rounded-md">
                          <option value="metric">Métrico</option>
                          <option value="imperial">Imperial</option>
                        </select>
                      </div>
                      
                      <div>
                        <label class="block text-sm font-medium text-gray-700">Formato de Reportes</label>
                        <select v-model="platformConfig.reportFormat" class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-green-500 focus:border-green-500 sm:text-sm rounded-md">
                          <option value="pdf">PDF</option>
                          <option value="excel">Excel</option>
                          <option value="csv">CSV</option>
                        </select>
                      </div>
                    </div>
                    
                    <div class="space-y-4">
                      <div>
                        <label class="block text-sm font-medium text-gray-700">URL API Externa</label>
                        <input
                          type="url"
                          v-model="platformConfig.externalApiUrl"
                          placeholder="https://api.example.com"
                          class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 sm:text-sm"
                        />
                      </div>
                      
                      <div>
                        <label class="block text-sm font-medium text-gray-700">Clave API</label>
                        <input
                          type="password"
                          v-model="platformConfig.apiKey"
                          placeholder="Ingresa tu clave API"
                          class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 sm:text-sm"
                        />
                      </div>
                      
                      <div class="space-y-3">
                        <div class="flex items-center">
                          <input
                            type="checkbox"
                            id="twoFactor"
                            v-model="platformConfig.twoFactorAuth"
                            class="h-4 w-4 text-green-600 focus:ring-green-500 border-gray-300 rounded"
                          />
                          <label for="twoFactor" class="ml-2 block text-sm text-gray-900">
                            Autenticación de dos factores
                          </label>
                        </div>
                        
                        <div class="flex items-center">
                          <input
                            type="checkbox"
                            id="auditLog"
                            v-model="platformConfig.auditLog"
                            class="h-4 w-4 text-green-600 focus:ring-green-500 border-gray-300 rounded"
                          />
                          <label for="auditLog" class="ml-2 block text-sm text-gray-900">
                            Registro de auditoría
                          </label>
                        </div>
                      </div>
                    </div>
                  </div>
                  
                  <div class="flex justify-end">
                    <button
                      @click="savePlatformConfig"
                      class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
                    >
                      Guardar Configuración
                    </button>
                  </div>
                </div>

                <!-- Datos de Referencia -->
                <div v-if="activeTab === 'reference'" class="space-y-6">
                  <div class="flex justify-between items-center">
                    <h3 class="text-lg font-medium text-gray-900">Datos de Referencia</h3>
                    <button
                      @click="showVarietyModal = true"
                      class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
                    >
                      <svg class="h-4 w-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
                      </svg>
                      Nueva Variedad
                    </button>
                  </div>
                  
                  <!-- Variedades de Cacao -->
                  <div class="bg-white rounded-lg border border-gray-200">
                    <div class="px-4 py-5 sm:p-6">
                      <h4 class="text-md font-medium text-gray-900 mb-4">Variedades de Cacao</h4>
                      <div class="overflow-x-auto">
                        <table class="min-w-full divide-y divide-gray-200">
                          <thead class="bg-gray-50">
                            <tr>
                              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Variedad</th>
                              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Origen</th>
                              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Características</th>
                              <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Acciones</th>
                            </tr>
                          </thead>
                          <tbody class="bg-white divide-y divide-gray-200">
                            <tr v-for="variety in cacaoVarieties" :key="variety.id">
                              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{{ variety.name }}</td>
                              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{{ variety.origin }}</td>
                              <td class="px-6 py-4 text-sm text-gray-500">{{ variety.characteristics }}</td>
                              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium">
                                <button @click="editVariety(variety)" class="text-green-600 hover:text-green-900 mr-3">Editar</button>
                                <button @click="deleteVariety(variety.id)" class="text-red-600 hover:text-red-900">Eliminar</button>
                              </td>
                            </tr>
                          </tbody>
                        </table>
                      </div>
                    </div>
                  </div>
                  
                  <!-- Normas y Certificaciones -->
                  <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div class="bg-white rounded-lg border border-gray-200 p-6">
                      <h4 class="text-md font-medium text-gray-900 mb-4">Normas Aplicables</h4>
                      <div class="space-y-3">
                        <div v-for="norm in norms" :key="norm.id" class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                          <div>
                            <div class="text-sm font-medium text-gray-900">{{ norm.code }}</div>
                            <div class="text-sm text-gray-500">{{ norm.description }}</div>
                          </div>
                          <button @click="deleteNorm(norm.id)" class="text-red-600 hover:text-red-900 text-sm">Eliminar</button>
                        </div>
                        <button
                          @click="showNormModal = true"
                          class="w-full text-center py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
                        >
                          Agregar Norma
                        </button>
                      </div>
                    </div>
                    
                    <div class="bg-white rounded-lg border border-gray-200 p-6">
                      <h4 class="text-md font-medium text-gray-900 mb-4">Parámetros de Exportación</h4>
                      <div class="space-y-4">
                        <div>
                          <label class="block text-sm font-medium text-gray-700">Certificación Orgánica</label>
                          <select v-model="exportParams.organicCert" class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 sm:text-sm">
                            <option value="none">No requerida</option>
                            <option value="usda">USDA Organic</option>
                            <option value="eu">EU Organic</option>
                            <option value="local">Certificación Local</option>
                          </select>
                        </div>
                        
                        <div>
                          <label class="block text-sm font-medium text-gray-700">Trazabilidad</label>
                          <div class="flex items-center">
                            <input
                              type="checkbox"
                              id="traceability"
                              v-model="exportParams.traceability"
                              class="h-4 w-4 text-green-600 focus:ring-green-500 border-gray-300 rounded"
                            />
                            <label for="traceability" class="ml-2 block text-sm text-gray-900">
                              Requerir trazabilidad completa
                            </label>
                          </div>
                        </div>
                        
                        <div>
                          <label class="block text-sm font-medium text-gray-700">Documentación Adicional</label>
                          <textarea
                            v-model="exportParams.additionalDocs"
                            rows="3"
                            placeholder="Especifica documentos adicionales requeridos..."
                            class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 sm:text-sm"
                          ></textarea>
                        </div>
                        
                        <button
                          @click="saveExportParams"
                          class="w-full inline-flex justify-center items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
                        >
                          Guardar Parámetros
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>

    <!-- Modales -->
    <!-- Modal de Usuario -->
    <div v-if="showUserModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div class="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
        <div class="mt-3">
          <h3 class="text-lg font-medium text-gray-900 mb-4">{{ editingUser ? 'Editar Usuario' : 'Nuevo Usuario' }}</h3>
          <form @submit.prevent="saveUser" class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700">Nombre</label>
              <input
                v-model="userForm.name"
                type="text"
                required
                class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 sm:text-sm"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700">Email</label>
              <input
                v-model="userForm.email"
                type="email"
                required
                class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 sm:text-sm"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700">Rol</label>
              <select v-model="userForm.role" required class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 sm:text-sm">
                <option value="admin">Administrador</option>
                <option value="analyst">Analista</option>
                <option value="farmer">Agricultor</option>
                <option value="viewer">Visualizador</option>
              </select>
            </div>
            <div class="flex justify-end space-x-3">
              <button
                type="button"
                @click="showUserModal = false"
                class="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
              >
                Cancelar
              </button>
              <button
                type="submit"
                class="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
              >
                {{ editingUser ? 'Actualizar' : 'Crear' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Modal de Proceso de Análisis -->
    <div v-if="showAnalysisModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div class="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
        <div class="mt-3">
          <h3 class="text-lg font-medium text-gray-900 mb-4">{{ editingProcess ? 'Editar Proceso' : 'Nuevo Proceso' }}</h3>
          <form @submit.prevent="saveProcess" class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700">Nombre</label>
              <input
                v-model="processForm.name"
                type="text"
                required
                class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 sm:text-sm"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700">Descripción</label>
              <textarea
                v-model="processForm.description"
                rows="3"
                required
                class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 sm:text-sm"
              ></textarea>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700">Estado</label>
              <select v-model="processForm.status" required class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 sm:text-sm">
                <option value="Activo">Activo</option>
                <option value="Inactivo">Inactivo</option>
                <option value="En Desarrollo">En Desarrollo</option>
              </select>
            </div>
            <div class="flex justify-end space-x-3">
              <button
                type="button"
                @click="showAnalysisModal = false"
                class="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
              >
                Cancelar
              </button>
              <button
                type="submit"
                class="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
              >
                {{ editingProcess ? 'Actualizar' : 'Crear' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Modal de Variedad -->
    <div v-if="showVarietyModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div class="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
        <div class="mt-3">
          <h3 class="text-lg font-medium text-gray-900 mb-4">{{ editingVariety ? 'Editar Variedad' : 'Nueva Variedad' }}</h3>
          <form @submit.prevent="saveVariety" class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700">Nombre</label>
              <input
                v-model="varietyForm.name"
                type="text"
                required
                class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 sm:text-sm"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700">Origen</label>
              <input
                v-model="varietyForm.origin"
                type="text"
                required
                class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 sm:text-sm"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700">Características</label>
              <textarea
                v-model="varietyForm.characteristics"
                rows="3"
                required
                class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 sm:text-sm"
              ></textarea>
            </div>
            <div class="flex justify-end space-x-3">
              <button
                type="button"
                @click="showVarietyModal = false"
                class="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
              >
                Cancelar
              </button>
              <button
                type="submit"
                class="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
              >
                {{ editingVariety ? 'Actualizar' : 'Crear' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Modal de Norma -->
    <div v-if="showNormModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div class="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
        <div class="mt-3">
          <h3 class="text-lg font-medium text-gray-900 mb-4">Nueva Norma</h3>
          <form @submit.prevent="saveNorm" class="space-y-4">
            <div>
              <label class="block text-sm font-medium text-gray-700">Código</label>
              <input
                v-model="normForm.code"
                type="text"
                required
                placeholder="ISO 9001, NTC 1234..."
                class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 sm:text-sm"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700">Descripción</label>
              <textarea
                v-model="normForm.description"
                rows="3"
                required
                placeholder="Descripción de la norma..."
                class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-green-500 focus:border-green-500 sm:text-sm"
              ></textarea>
            </div>
            <div class="flex justify-end space-x-3">
              <button
                type="button"
                @click="showNormModal = false"
                class="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
              >
                Cancelar
              </button>
              <button
                type="submit"
                class="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
              >
                Crear
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';
import AdminSidebar from '@/components/common/AdminSidebar.vue';

export default {
  name: 'Configuracion',
  components: {
    AdminSidebar
  },
  setup() {
    // Estado reactivo
    const loading = ref(false);
    const sidebarCollapsed = ref(localStorage.getItem('sidebarCollapsed') === 'true');
    
    // Datos de usuario
    const userInitials = ref('AD');
    const userName = ref('Admin');
    const userRole = ref('Administrador');
    
    // Pestañas activas
    const tabs = [
      { id: 'users', name: 'Usuarios y Roles' },
      { id: 'quality', name: 'Parámetros de Calidad' },
      { id: 'analysis', name: 'Procesos de Análisis' },
      { id: 'platform', name: 'Configuración de Plataforma' },
      { id: 'reference', name: 'Datos de Referencia' }
    ];
    const activeTab = ref('users');
    
    // Estados de modales
    const showUserModal = ref(false);
    const showAnalysisModal = ref(false);
    const showVarietyModal = ref(false);
    const showNormModal = ref(false);
    
    // Estados de edición
    const editingUser = ref(null);
    const editingProcess = ref(null);
    const editingVariety = ref(null);
    
    // Datos de usuarios
    const users = ref([
      {
        id: 1,
        name: 'Juan Doe',
        email: 'juan@cacaoscan.com',
        role: 'admin',
        initials: 'JD',
        isActive: true
      },
      {
        id: 2,
        name: 'María García',
        email: 'maria@cacaoscan.com',
        role: 'analyst',
        initials: 'MG',
        isActive: true
      },
      {
        id: 3,
        name: 'Carlos López',
        email: 'carlos@cacaoscan.com',
        role: 'farmer',
        initials: 'CL',
        isActive: false
      }
    ]);
    
    // Formulario de usuario
    const userForm = ref({
      name: '',
      email: '',
      role: 'farmer'
    });
    
    // Parámetros de calidad
    const qualityParams = ref({
      humidity: 8.5,
      defects: 5.0,
      coloration: 7.5,
      size: 18.0
    });
    
    // Procesos de análisis
    const analysisProcesses = ref([
      {
        id: 1,
        name: 'Análisis Físico',
        description: 'Evaluación de características físicas del grano de cacao',
        status: 'Activo'
      },
      {
        id: 2,
        name: 'Análisis Químico',
        description: 'Determinación de composición química y parámetros de calidad',
        status: 'Activo'
      },
      {
        id: 3,
        name: 'Análisis Sensorial',
        description: 'Evaluación organoléptica por catadores expertos',
        status: 'En Desarrollo'
      }
    ]);
    
    // Formulario de proceso
    const processForm = ref({
      name: '',
      description: '',
      status: 'Activo'
    });
    
    // Configuración de plataforma
    const platformConfig = ref({
      language: 'es',
      units: 'metric',
      reportFormat: 'pdf',
      externalApiUrl: '',
      apiKey: '',
      twoFactorAuth: true,
      auditLog: true
    });
    
    // Variedades de cacao
    const cacaoVarieties = ref([
      {
        id: 1,
        name: 'Criollo',
        origin: 'Venezuela',
        characteristics: 'Granos finos, sabor suave y aromático'
      },
      {
        id: 2,
        name: 'Forastero',
        origin: 'Brasil',
        characteristics: 'Granos gruesos, sabor fuerte y amargo'
      },
      {
        id: 3,
        name: 'Trinitario',
        origin: 'Trinidad',
        characteristics: 'Híbrido, balance entre sabor y resistencia'
      }
    ]);
    
    // Formulario de variedad
    const varietyForm = ref({
      name: '',
      origin: '',
      characteristics: ''
    });
    
    // Normas aplicables
    const norms = ref([
      {
        id: 1,
        code: 'ISO 9001',
        description: 'Sistema de Gestión de Calidad'
      },
      {
        id: 2,
        code: 'NTC 1252',
        description: 'Cacao en grano - Especificaciones'
      }
    ]);
    
    // Formulario de norma
    const normForm = ref({
      code: '',
      description: ''
    });
    
    // Parámetros de exportación
    const exportParams = ref({
      organicCert: 'none',
      traceability: false,
      additionalDocs: ''
    });
    
    // Métodos
    const toggleSidebar = () => {
      sidebarCollapsed.value = !sidebarCollapsed.value;
      localStorage.setItem('sidebarCollapsed', sidebarCollapsed.value);
    };
    
    // Métodos de usuarios
    const editUser = (user) => {
      editingUser.value = user;
      userForm.value = { ...user };
      showUserModal.value = true;
    };
    
    const saveUser = () => {
      if (editingUser.value) {
        // Actualizar usuario existente
        const index = users.value.findIndex(u => u.id === editingUser.value.id);
        if (index !== -1) {
          users.value[index] = { ...editingUser.value, ...userForm.value };
        }
      } else {
        // Crear nuevo usuario
        const newUser = {
          id: Date.now(),
          ...userForm.value,
          initials: userForm.value.name.split(' ').map(n => n[0]).join('').toUpperCase(),
          isActive: true
        };
        users.value.push(newUser);
      }
      
      // Limpiar formulario y cerrar modal
      userForm.value = { name: '', email: '', role: 'farmer' };
      editingUser.value = null;
      showUserModal.value = false;
      
      // Mostrar mensaje de éxito
      alert(editingUser.value ? 'Usuario actualizado exitosamente' : 'Usuario creado exitosamente');
    };
    
    const deleteUser = (userId) => {
      if (confirm('¿Estás seguro de que quieres eliminar este usuario?')) {
        users.value = users.value.filter(u => u.id !== userId);
        alert('Usuario eliminado exitosamente');
      }
    };
    
    // Métodos de parámetros de calidad
    const saveQualityParams = () => {
      // Aquí se implementaría la lógica para guardar en el backend
      console.log('Parámetros de calidad guardados:', qualityParams.value);
      alert('Parámetros de calidad guardados exitosamente');
    };
    
    // Métodos de procesos de análisis
    const editProcess = (process) => {
      editingProcess.value = process;
      processForm.value = { ...process };
      showAnalysisModal.value = true;
    };
    
    const saveProcess = () => {
      if (editingProcess.value) {
        // Actualizar proceso existente
        const index = analysisProcesses.value.findIndex(p => p.id === editingProcess.value.id);
        if (index !== -1) {
          analysisProcesses.value[index] = { ...editingProcess.value, ...processForm.value };
        }
      } else {
        // Crear nuevo proceso
        const newProcess = {
          id: Date.now(),
          ...processForm.value
        };
        analysisProcesses.value.push(newProcess);
      }
      
      // Limpiar formulario y cerrar modal
      processForm.value = { name: '', description: '', status: 'Activo' };
      editingProcess.value = null;
      showAnalysisModal.value = false;
      
      alert(editingProcess.value ? 'Proceso actualizado exitosamente' : 'Proceso creado exitosamente');
    };
    
    const deleteProcess = (processId) => {
      if (confirm('¿Estás seguro de que quieres eliminar este proceso?')) {
        analysisProcesses.value = analysisProcesses.value.filter(p => p.id !== processId);
        alert('Proceso eliminado exitosamente');
      }
    };
    
    // Métodos de configuración de plataforma
    const savePlatformConfig = () => {
      console.log('Configuración de plataforma guardada:', platformConfig.value);
      alert('Configuración de plataforma guardada exitosamente');
    };
    
    // Métodos de variedades
    const editVariety = (variety) => {
      editingVariety.value = variety;
      varietyForm.value = { ...variety };
      showVarietyModal.value = true;
    };
    
    const saveVariety = () => {
      if (editingVariety.value) {
        // Actualizar variedad existente
        const index = cacaoVarieties.value.findIndex(v => v.id === editingVariety.value.id);
        if (index !== -1) {
          cacaoVarieties.value[index] = { ...editingVariety.value, ...varietyForm.value };
        }
      } else {
        // Crear nueva variedad
        const newVariety = {
          id: Date.now(),
          ...varietyForm.value
        };
        cacaoVarieties.value.push(newVariety);
      }
      
      // Limpiar formulario y cerrar modal
      varietyForm.value = { name: '', origin: '', characteristics: '' };
      editingVariety.value = null;
      showVarietyModal.value = false;
      
      alert(editingVariety.value ? 'Variedad actualizada exitosamente' : 'Variedad creada exitosamente');
    };
    
    const deleteVariety = (varietyId) => {
      if (confirm('¿Estás seguro de que quieres eliminar esta variedad?')) {
        cacaoVarieties.value = cacaoVarieties.value.filter(v => v.id !== varietyId);
        alert('Variedad eliminada exitosamente');
      }
    };
    
    // Métodos de normas
    const saveNorm = () => {
      const newNorm = {
        id: Date.now(),
        ...normForm.value
      };
      norms.value.push(newNorm);
      
      // Limpiar formulario y cerrar modal
      normForm.value = { code: '', description: '' };
      showNormModal.value = false;
      
      alert('Norma creada exitosamente');
    };
    
    const deleteNorm = (normId) => {
      if (confirm('¿Estás seguro de que quieres eliminar esta norma?')) {
        norms.value = norms.value.filter(n => n.id !== normId);
        alert('Norma eliminada exitosamente');
      }
    };
    
    // Métodos de parámetros de exportación
    const saveExportParams = () => {
      console.log('Parámetros de exportación guardados:', exportParams.value);
      alert('Parámetros de exportación guardados exitosamente');
    };
    
    // Métodos de utilidad
    const getRoleBadgeClass = (role) => {
      const classes = {
        admin: 'bg-red-100 text-red-800',
        analyst: 'bg-blue-100 text-blue-800',
        farmer: 'bg-green-100 text-green-800',
        viewer: 'bg-gray-100 text-gray-800'
      };
      return classes[role] || classes.viewer;
    };
    
    const getRoleDisplay = (role) => {
      const displays = {
        admin: 'Administrador',
        analyst: 'Analista',
        farmer: 'Agricultor',
        viewer: 'Visualizador'
      };
      return displays[role] || role;
    };
    
    const getStatusBadgeClass = (status) => {
      const classes = {
        'Activo': 'bg-green-100 text-green-800',
        'Inactivo': 'bg-red-100 text-red-800',
        'En Desarrollo': 'bg-yellow-100 text-yellow-800'
      };
      return classes[status] || classes['Inactivo'];
    };
    
    // Lifecycle
    onMounted(() => {
      console.log('Vista Configuración montada');
      checkScreenSize();
      window.addEventListener('resize', checkScreenSize);
    });
    
    const checkScreenSize = () => {
      if (window.innerWidth <= 768) {
        sidebarCollapsed.value = true;
        localStorage.setItem('sidebarCollapsed', 'true');
      }
    };
    
    return {
      // Estado
      loading,
      sidebarCollapsed,
      userInitials,
      userName,
      userRole,
      
      // Pestañas
      tabs,
      activeTab,
      
      // Modales
      showUserModal,
      showAnalysisModal,
      showVarietyModal,
      showNormModal,
      
      // Estados de edición
      editingUser,
      editingProcess,
      editingVariety,
      
      // Datos
      users,
      userForm,
      qualityParams,
      analysisProcesses,
      processForm,
      platformConfig,
      cacaoVarieties,
      varietyForm,
      norms,
      normForm,
      exportParams,
      
      // Métodos
      toggleSidebar,
      editUser,
      saveUser,
      deleteUser,
      saveQualityParams,
      editProcess,
      saveProcess,
      deleteProcess,
      savePlatformConfig,
      editVariety,
      saveVariety,
      deleteVariety,
      saveNorm,
      deleteNorm,
      saveExportParams,
      getRoleBadgeClass,
      getRoleDisplay,
      getStatusBadgeClass
    };
  }
};
</script>

<style scoped>
/* Estilos específicos para la vista de configuración */
.min-h-screen {
  min-height: 100vh;
}

.h-screen {
  height: 100vh;
}

/* Asegurar que el contenido principal no se desborde */
.min-w-0 {
  min-width: 0;
}

/* Eliminar espacio blanco excesivo */
.flex-1 {
  flex: 1 1 0%;
}

/* Asegurar que el contenido principal ocupe toda la altura disponible */
main {
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 0;
}

/* Controlar el overflow */
.overflow-hidden {
  overflow: hidden;
}

.overflow-y-auto {
  overflow-y: auto;
  -webkit-overflow-scrolling: touch;
}

/* Asegurar que el contenido se ajuste correctamente */
.flex.flex-col {
  display: flex;
  flex-direction: column;
}

/* Asegurar que el contenido se ajuste al viewport */
.min-h-0 {
  min-height: 0;
}

/* Layout específico para la vista de configuración */
.bg-gray-50 {
  background-color: #f9fafb;
}

/* Asegurar que el sidebar y contenido principal se alineen correctamente */
.flex.h-screen {
  height: 100vh;
  max-height: 100vh;
}

/* Estilos para cuando el sidebar está colapsado */
.main-expanded {
  margin-left: 0;
  transition: margin-left 0.3s ease;
}

/* Transición suave para el contenido principal */
.flex-1.flex.flex-col {
  transition: margin-left 0.3s ease;
}

/* Estilos para las pestañas */
.tabs {
  border-bottom: 1px solid #e5e7eb;
}

.tab {
  padding: 0.75rem 1rem;
  border-bottom: 2px solid transparent;
  color: #6b7280;
  font-weight: 500;
  transition: all 0.2s ease;
}

.tab:hover {
  color: #374151;
  border-bottom-color: #d1d5db;
}

.tab.active {
  color: #059669;
  border-bottom-color: #059669;
}

/* Estilos para los sliders */
.slider {
  -webkit-appearance: none;
  appearance: none;
  height: 8px;
  border-radius: 4px;
  background: #d1d5db;
  outline: none;
  opacity: 0.7;
  transition: opacity 0.2s;
}

.slider:hover {
  opacity: 1;
}

.slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #059669;
  cursor: pointer;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.slider::-moz-range-thumb {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #059669;
  cursor: pointer;
  border: none;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

/* Estilos para las tablas */
.table-container {
  overflow-x: auto;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
}

.table {
  width: 100%;
  border-collapse: collapse;
}

.table th {
  background-color: #f9fafb;
  padding: 12px 16px;
  text-align: left;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #6b7280;
  border-bottom: 1px solid #e5e7eb;
}

.table td {
  padding: 12px 16px;
  border-bottom: 1px solid #f3f4f6;
}

.table tbody tr:hover {
  background-color: #f9fafb;
}

/* Estilos para los badges */
.badge {
  display: inline-flex;
  align-items: center;
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: capitalize;
}

.badge-admin {
  background-color: #fef2f2;
  color: #dc2626;
}

.badge-analyst {
  background-color: #eff6ff;
  color: #2563eb;
}

.badge-farmer {
  background-color: #f0fdf4;
  color: #16a34a;
}

.badge-viewer {
  background-color: #f9fafb;
  color: #6b7280;
}

/* Estilos para los modales */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 50;
}

.modal {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  max-width: 500px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  padding: 1.5rem 1.5rem 0;
}

.modal-body {
  padding: 1.5rem;
}

.modal-footer {
  padding: 0 1.5rem 1.5rem;
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
}

/* Estilos para los formularios */
.form-group {
  margin-bottom: 1rem;
}

.form-label {
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  color: #374151;
  margin-bottom: 0.5rem;
}

.form-input {
  width: 100%;
  padding: 0.5rem 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.875rem;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.form-input:focus {
  outline: none;
  border-color: #059669;
  box-shadow: 0 0 0 3px rgba(5, 150, 105, 0.1);
}

.form-select {
  width: 100%;
  padding: 0.5rem 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.875rem;
  background-color: white;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.form-select:focus {
  outline: none;
  border-color: #059669;
  box-shadow: 0 0 0 3px rgba(5, 150, 105, 0.1);
}

.form-textarea {
  width: 100%;
  padding: 0.5rem 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 0.875rem;
  resize: vertical;
  min-height: 80px;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.form-textarea:focus {
  outline: none;
  border-color: #059669;
  box-shadow: 0 0 0 3px rgba(5, 150, 105, 0.1);
}

/* Estilos para los botones */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 500;
  text-decoration: none;
  transition: all 0.2s ease;
  cursor: pointer;
  border: none;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary {
  background-color: #059669;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background-color: #047857;
  transform: translateY(-1px);
}

.btn-secondary {
  background-color: #6b7280;
  color: white;
}

.btn-secondary:hover:not(:disabled) {
  background-color: #4b5563;
  transform: translateY(-1px);
}

.btn-danger {
  background-color: #dc2626;
  color: white;
}

.btn-danger:hover:not(:disabled) {
  background-color: #b91c1c;
  transform: translateY(-1px);
}

.btn-outline {
  background-color: transparent;
  color: #374151;
  border: 1px solid #d1d5db;
}

.btn-outline:hover:not(:disabled) {
  background-color: #f9fafb;
  border-color: #9ca3af;
}

/* Estilos para las tarjetas */
.card {
  background-color: white;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
  transition: box-shadow 0.2s ease;
}

.card:hover {
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}

.card-header {
  padding: 1.5rem;
  border-bottom: 1px solid #f3f4f6;
}

.card-body {
  padding: 1.5rem;
}

.card-footer {
  padding: 1.5rem;
  border-top: 1px solid #f3f4f6;
  background-color: #f9fafb;
}

/* Estilos para los grids */
.grid {
  display: grid;
}

.grid-cols-1 {
  grid-template-columns: repeat(1, minmax(0, 1fr));
}

.grid-cols-2 {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.grid-cols-3 {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.gap-4 {
  gap: 1rem;
}

.gap-6 {
  gap: 1.5rem;
}

/* Estilos para el espaciado */
.space-y-4 > * + * {
  margin-top: 1rem;
}

.space-y-6 > * + * {
  margin-top: 1.5rem;
}

/* Estilos para el responsive */
@media (max-width: 768px) {
  .grid-cols-2 {
    grid-template-columns: repeat(1, minmax(0, 1fr));
  }
  
  .grid-cols-3 {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
  
  .tabs {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .tab {
    border-bottom: none;
    border-left: 2px solid transparent;
    padding: 0.75rem 1rem;
  }
  
  .tab.active {
    border-left-color: #059669;
    border-bottom-color: transparent;
  }
}

@media (max-width: 640px) {
  .grid-cols-3 {
    grid-template-columns: repeat(1, minmax(0, 1fr));
  }
  
  .modal {
    width: 95%;
    margin: 1rem;
  }
  
  .btn {
    width: 100%;
    justify-content: center;
  }
  
  .space-x-3 > * + * {
    margin-left: 0;
    margin-top: 0.5rem;
  }
  
  .space-x-4 > * + * {
    margin-left: 0;
    margin-top: 0.5rem;
  }
}

/* Estilos para las animaciones */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.fade-in {
  animation: fadeIn 0.3s ease-out;
}

/* Estilos para los estados de carga */
.loading {
  opacity: 0.6;
  pointer-events: none;
}

.loading::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 20px;
  height: 20px;
  margin: -10px 0 0 -10px;
  border: 2px solid #f3f4f6;
  border-top: 2px solid #059669;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* Estilos para los tooltips */
.tooltip {
  position: relative;
}

.tooltip::before {
  content: attr(data-tooltip);
  position: absolute;
  bottom: 100%;
  left: 50%;
  transform: translateX(-50%);
  padding: 0.5rem;
  background-color: #1f2937;
  color: white;
  font-size: 0.75rem;
  border-radius: 4px;
  white-space: nowrap;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.2s ease;
  z-index: 10;
}

.tooltip:hover::before {
  opacity: 1;
}

/* Estilos para los checkboxes personalizados */
.checkbox-custom {
  position: relative;
  display: inline-block;
  width: 20px;
  height: 20px;
}

.checkbox-custom input {
  opacity: 0;
  width: 0;
  height: 0;
}

.checkbox-custom .checkmark {
  position: absolute;
  top: 0;
  left: 0;
  width: 20px;
  height: 20px;
  background-color: white;
  border: 2px solid #d1d5db;
  border-radius: 4px;
  transition: all 0.2s ease;
}

.checkbox-custom input:checked ~ .checkmark {
  background-color: #059669;
  border-color: #059669;
}

.checkbox-custom .checkmark::after {
  content: '';
  position: absolute;
  left: 6px;
  top: 2px;
  width: 5px;
  height: 10px;
  border: solid white;
  border-width: 0 2px 2px 0;
  transform: rotate(45deg);
  opacity: 0;
  transition: opacity 0.2s ease;
}

.checkbox-custom input:checked ~ .checkmark::after {
  opacity: 1;
}

/* Estilos para los mensajes de éxito/error */
.message {
  padding: 0.75rem 1rem;
  border-radius: 6px;
  margin-bottom: 1rem;
  font-size: 0.875rem;
}

.message-success {
  background-color: #f0fdf4;
  color: #166534;
  border: 1px solid #bbf7d0;
}

.message-error {
  background-color: #fef2f2;
  color: #991b1b;
  border: 1px solid #fecaca;
}

.message-warning {
  background-color: #fffbeb;
  color: #92400e;
  border: 1px solid #fed7aa;
}

.message-info {
  background-color: #eff6ff;
  color: #1e40af;
  border: 1px solid #bfdbfe;
}

/* Estilos para el scroll personalizado */
.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}

.custom-scrollbar::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* Estilos para el focus visible */
.focus-visible:focus {
  outline: 2px solid #059669;
  outline-offset: 2px;
}

/* Estilos para las transiciones */
.transition-all {
  transition-property: all;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 150ms;
}

.transition-colors {
  transition-property: color, background-color, border-color, text-decoration-color, fill, stroke;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 150ms;
}

.transition-transform {
  transition-property: transform;
  transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
  transition-duration: 150ms;
}

/* Estilos para el hover */
.hover\:bg-gray-50:hover {
  background-color: #f9fafb;
}

.hover\:bg-green-700:hover {
  background-color: #047857;
}

.hover\:bg-gray-700:hover {
  background-color: #4b5563;
}





/* Estilos para el responsive utilities */
@media (min-width: 640px) {
  .sm\\:grid-cols-2 {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
  
  .sm\\:flex-row {
    flex-direction: row;
  }
  
  .sm\\:items-center {
    align-items: center;
  }
  
  .sm\\:justify-between {
    justify-content: space-between;
  }
}

@media (min-width: 768px) {
  .md\\:grid-cols-2 {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
  
  .md\\:grid-cols-3 {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

@media (min-width: 1024px) {
  .lg\\:grid-cols-3 {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

/* Estilos para el print */
@media print {
  .no-print {
    display: none !important;
  }
  
  .print-break {
    page-break-before: always;
  }
  
  .print-break-inside {
    page-break-inside: avoid;
  }
}
</style>
