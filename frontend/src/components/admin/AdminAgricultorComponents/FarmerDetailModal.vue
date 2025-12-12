<template>
  <BaseModal
    :show="isOpen"
    :title="farmer ? farmer.name : 'Detalles del Cacaocultor'"
    :subtitle="farmer ? farmer.email : ''"
    max-width="4xl"
    overlay-class="bg-black/30 backdrop-blur-sm"
    @close="closeModal"
    @update:show="(value) => { if (!value) closeModal() }"
  >
    <template #header>
      <div v-if="farmer" class="flex items-center">
        <div class="bg-green-100 p-3 rounded-lg mr-4 shadow-sm">
          <div class="w-12 h-12 rounded-full bg-gradient-to-br from-green-500 to-green-600 flex items-center justify-center text-white font-bold text-base border-2 border-green-100 shadow-md">
            {{ farmer.initials }}
          </div>
        </div>
        <div>
          <h3 class="text-2xl font-bold text-gray-900">{{ farmer.name }}</h3>
          <p class="text-sm text-gray-600 mt-1 flex items-center gap-2">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path>
            </svg>
            {{ farmer.email }}
          </p>
        </div>
      </div>
    </template>

    <!-- Loading state -->
    <div v-if="loading" class="flex items-center justify-center p-12">
      <svg class="animate-spin h-8 w-8 text-green-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
    </div>

    <!-- Content -->
    <template v-else-if="farmer">

          <!-- Modal body -->
          <div class="p-6">
            <!-- Datos Personales -->
            <div v-if="persona" class="mb-6">
              <div class="bg-gradient-to-r from-green-50 to-green-50 px-4 py-3 border-b border-gray-200 rounded-t-lg">
                <div class="flex items-center">
                  <div class="bg-green-100 p-2 rounded-lg mr-3">
                    <svg class="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5.121 17.804A13.937 13.937 0 0112 15c2.5 0 4.847.655 6.879 1.804M15 11a3 3 0 10-6 0 3 3 0 006 0z" />
                    </svg>
                  </div>
                  <div>
                    <h4 class="text-lg font-bold text-gray-900">Datos Personales</h4>
                    <p class="text-sm text-gray-600">Información registrada del cacaocultor</p>
                  </div>
                </div>
              </div>
              <div class="bg-white border border-gray-200 rounded-b-lg p-4">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <p class="text-xs text-gray-500">Documento</p>
                    <p class="text-sm font-semibold text-gray-900">
                      {{ persona.tipo_documento_info?.codigo || persona.tipo_documento || '-' }}
                      {{ persona.numero_documento || '' }}
                    </p>
                  </div>
                  <div>
                    <p class="text-xs text-gray-500">Nombre completo</p>
                    <p class="text-sm font-semibold text-gray-900">
                      {{ persona.primer_nombre }} {{ persona.segundo_nombre }} {{ persona.primer_apellido }} {{ persona.segundo_apellido }}
                    </p>
                  </div>
                  <div>
                    <p class="text-xs text-gray-500">Teléfono</p>
                    <p class="text-sm font-semibold text-gray-900">{{ persona.telefono || '-' }}</p>
                  </div>
                  <div>
                    <p class="text-xs text-gray-500">Género</p>
                    <p class="text-sm font-semibold text-gray-900">{{ persona.genero_info?.nombre || '-' }}</p>
                  </div>
                  <div class="md:col-span-2">
                    <p class="text-xs text-gray-500">Dirección</p>
                    <p class="text-sm font-semibold text-gray-900">
                      {{ persona.direccion || '-' }}
                    </p>
                  </div>
                  <div>
                    <p class="text-xs text-gray-500">Departamento</p>
                    <p class="text-sm font-semibold text-gray-900">{{ persona.departamento_info?.nombre || '-' }}</p>
                  </div>
                  <div>
                    <p class="text-xs text-gray-500">Municipio</p>
                    <p class="text-sm font-semibold text-gray-900">{{ persona.municipio_info?.nombre || '-' }}</p>
                  </div>
                  <div>
                    <p class="text-xs text-gray-500">Fecha de nacimiento</p>
                    <p class="text-sm font-semibold text-gray-900">{{ persona.fecha_nacimiento || '-' }}</p>
                  </div>
                </div>
              </div>
            </div>
            <!-- Stats cards -->
            <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
              <div class="bg-white rounded-lg p-6 border border-gray-200 shadow-md hover:shadow-lg transition-all duration-300 transform hover:-translate-y-1">
                <div class="flex items-center justify-between">
                  <div class="flex-1">
                    <p class="text-xs font-semibold text-gray-600 uppercase tracking-wider mb-1">Total Fincas</p>
                    <p class="text-2xl font-bold text-gray-900">{{ fincasList.length }}</p>
                  </div>
                  <div class="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                    <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"></path>
                    </svg>
                  </div>
                </div>
              </div>
              
              <div class="bg-white rounded-lg p-6 border border-gray-200 shadow-md hover:shadow-lg transition-all duration-300 transform hover:-translate-y-1">
                <div class="flex items-center justify-between">
                  <div class="flex-1">
                    <p class="text-xs font-semibold text-gray-600 uppercase tracking-wider mb-1">Área Total</p>
                    <p class="text-2xl font-bold text-gray-900">{{ totalArea }} ha</p>
                  </div>
                  <div class="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                    <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 21v-4m0 0V5a2 2 0 012-2h6.5l1 1H21l-3 6 3 6h-8.5l-1-1H5a2 2 0 00-2 2zm9-13.5V9"></path>
                    </svg>
                  </div>
                </div>
              </div>
              
              <div class="bg-white rounded-lg p-6 border border-gray-200 shadow-md hover:shadow-lg transition-all duration-300 transform hover:-translate-y-1">
                <div class="flex items-center justify-between">
                  <div class="flex-1">
                    <p class="text-xs font-semibold text-gray-600 uppercase tracking-wider mb-1">Estado</p>
                    <span :class="getStatusClasses(farmer.status)" class="px-3 py-1.5 inline-flex text-xs leading-4 font-semibold rounded-full">
                      {{ farmer.status }}
                    </span>
                  </div>
                  <div class="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
                    <svg class="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                    </svg>
                  </div>
                </div>
              </div>
              
              <div class="bg-white rounded-lg p-6 border border-gray-200 shadow-md hover:shadow-lg transition-all duration-300 transform hover:-translate-y-1">
                <div class="flex items-center justify-between">
                  <div class="flex-1">
                    <p class="text-xs font-semibold text-gray-600 uppercase tracking-wider mb-1">Análisis</p>
                    <p class="text-2xl font-bold text-gray-900">{{ totalAnalisis }}</p>
                  </div>
                  <div class="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center">
                    <svg class="w-6 h-6 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
                    </svg>
                  </div>
                </div>
              </div>
            </div>

            <!-- Fincas Section -->
            <div v-if="fincasList.length > 0" class="mb-6">
              <div class="bg-gradient-to-r from-green-50 to-green-50 px-4 py-3 border-b border-gray-200 rounded-t-lg">
                <div class="flex items-center">
                  <div class="bg-green-100 p-2 rounded-lg mr-3">
                    <svg class="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"></path>
                    </svg>
                  </div>
                  <div>
                    <h4 class="text-lg font-bold text-gray-900">Fincas</h4>
                    <p class="text-sm text-gray-600">Fincas asociadas al cacaocultor</p>
                  </div>
                </div>
              </div>
              
              <div class="bg-white border border-gray-200 rounded-b-lg overflow-hidden">
                <div class="divide-y divide-gray-200">
                  <div 
                    v-for="(finca, index) in fincasList" 
                    :key="index"
                    class="p-4 hover:bg-green-50 transition-all duration-200 border-l-4 border-transparent hover:border-green-500 cursor-pointer group"
                    @click="handleFincaClick(finca)"
                  >
                    <div class="flex items-start justify-between">
                      <div class="flex-1">
                        <div class="flex items-center gap-3 mb-2">
                          <div class="w-10 h-10 rounded-lg bg-gradient-to-br from-green-100 to-green-200 flex items-center justify-center group-hover:from-green-500 group-hover:to-green-600 transition-all duration-200">
                            <svg class="w-5 h-5 text-green-700 group-hover:text-white transition-colors duration-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"></path>
                            </svg>
                          </div>
                          <h5 class="text-base font-bold text-gray-900 group-hover:text-green-700 transition-colors duration-200">{{ finca.nombre }}</h5>
                        </div>
                        <p class="text-sm text-gray-600 mb-2 flex items-center gap-2">
                          <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path>
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path>
                          </svg>
                          {{ finca.municipio }}, {{ finca.departamento }}
                        </p>
                        <div class="flex items-center gap-4 text-sm">
                          <span class="flex items-center gap-2 text-gray-600 bg-gray-50 px-3 py-1.5 rounded-lg">
                            <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 21v-4m0 0V5a2 2 0 012-2h6.5l1 1H21l-3 6 3 6h-8.5l-1-1H5a2 2 0 00-2 2zm9-13.5V9"></path>
                            </svg>
                            {{ finca.hectareas }} hectáreas
                          </span>
                          <span :class="finca.activa ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'" class="px-3 py-1.5 rounded-lg font-semibold flex items-center gap-1.5">
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" v-if="finca.activa">
                              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                            </svg>
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" v-else>
                              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                            </svg>
                            {{ finca.activa ? 'Activa' : 'Inactiva' }}
                          </span>
                        </div>
                        
                        <!-- Coordenadas GPS -->
                        <div v-if="finca.coordenadas_lat && finca.coordenadas_lng" class="mt-2 flex items-center gap-2 text-xs">
                          <svg class="w-3 h-3 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                          </svg>
                          <a
                            :href="getGoogleMapsUrl(finca.coordenadas_lat, finca.coordenadas_lng)"
                            target="_blank"
                            rel="noopener noreferrer"
                            class="text-blue-600 hover:text-blue-800 hover:underline flex items-center gap-1 transition-colors duration-200"
                            @click.stop
                          >
                            <span>📍 GPS: {{ finca.coordenadas_lat }}, {{ finca.coordenadas_lng }}</span>
                            <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path>
                            </svg>
                          </a>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Message if no farms -->
            <div v-else class="bg-gray-50 border border-gray-200 rounded-lg p-8 text-center mb-6">
              <svg class="w-16 h-16 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"></path>
              </svg>
              <h4 class="text-lg font-bold text-gray-900 mb-2">Sin fincas registradas</h4>
              <p class="text-gray-600">Este cacaocultor no tiene fincas asociadas aún</p>
            </div>

            <!-- Información de Usuario -->
            <div v-if="userDetails" class="mb-6">
              <div class="bg-gradient-to-r from-blue-50 to-blue-50 px-4 py-3 border-b border-gray-200 rounded-t-lg">
                <div class="flex items-center">
                  <div class="bg-blue-100 p-2 rounded-lg mr-3">
                    <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
                    </svg>
                  </div>
                  <div>
                    <h4 class="text-lg font-bold text-gray-900">Información de Usuario</h4>
                    <p class="text-sm text-gray-600">Datos de la cuenta del cacaocultor</p>
                  </div>
                </div>
              </div>
              <div class="bg-white border border-gray-200 rounded-b-lg p-4">
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <p class="text-xs text-gray-500">ID de Usuario</p>
                    <p class="text-sm font-semibold text-gray-900">#{{ userDetails.id || farmer.id }}</p>
                  </div>
                  <div>
                    <p class="text-xs text-gray-500">Username</p>
                    <p class="text-sm font-semibold text-gray-900">{{ userDetails.username || '-' }}</p>
                  </div>
                  <div>
                    <p class="text-xs text-gray-500">Email</p>
                    <p class="text-sm font-semibold text-gray-900">{{ userDetails.email || farmer.email || '-' }}</p>
                  </div>
                  <div>
                    <p class="text-xs text-gray-500">Rol</p>
                    <p class="text-sm font-semibold text-gray-900">
                      <span class="px-2 py-1 rounded-full text-xs" :class="{
                        'bg-purple-100 text-purple-800': userDetails.role === 'admin',
                        'bg-blue-100 text-blue-800': userDetails.role === 'analyst',
                        'bg-green-100 text-green-800': userDetails.role === 'farmer'
                      }">
                        {{ userDetails.role === 'admin' ? 'Administrador' : userDetails.role === 'analyst' ? 'Analista' : 'Cacaocultor' }}
                      </span>
                    </p>
                  </div>
                  <div>
                    <p class="text-xs text-gray-500">Email Verificado</p>
                    <p class="text-sm font-semibold text-gray-900">
                      <span :class="userDetails.is_verified ? 'text-green-600' : 'text-red-600'" class="flex items-center gap-1">
                        <svg v-if="userDetails.is_verified" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
                        </svg>
                        <svg v-else class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                        </svg>
                        {{ userDetails.is_verified ? 'Verificado' : 'No verificado' }}
                      </span>
                    </p>
                  </div>
                  <div>
                    <p class="text-xs text-gray-500">Fecha de Registro</p>
                    <p class="text-sm font-semibold text-gray-900">{{ formatDate(userDetails.date_joined) }}</p>
                  </div>
                  <div v-if="userStats?.last_login">
                    <p class="text-xs text-gray-500">Último Acceso</p>
                    <p class="text-sm font-semibold text-gray-900">{{ formatDateTime(userStats.last_login) }}</p>
                  </div>
                  <div v-if="userStats?.days_since_registration !== undefined">
                    <p class="text-xs text-gray-500">Días desde Registro</p>
                    <p class="text-sm font-semibold text-gray-900">{{ userStats.days_since_registration }} días</p>
                  </div>
                  <div v-if="userStats?.groups && userStats.groups.length > 0" class="md:col-span-2">
                    <p class="text-xs text-gray-500">Grupos</p>
                    <div class="flex flex-wrap gap-2 mt-1">
                      <span v-for="group in userStats.groups" :key="group" class="px-2 py-1 bg-gray-100 text-gray-700 rounded-md text-xs">
                        {{ group }}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Estadísticas de Usuario -->
            <div v-if="userStats" class="mb-6">
              <div class="bg-gradient-to-r from-purple-50 to-purple-50 px-4 py-3 border-b border-gray-200 rounded-t-lg">
                <div class="flex items-center">
                  <div class="bg-purple-100 p-2 rounded-lg mr-3">
                    <svg class="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
                    </svg>
                  </div>
                  <div>
                    <h4 class="text-lg font-bold text-gray-900">Estadísticas de Actividad</h4>
                    <p class="text-sm text-gray-600">Métricas de uso del sistema</p>
                  </div>
                </div>
              </div>
              <div class="bg-white border border-gray-200 rounded-b-lg p-4">
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div class="bg-purple-50 rounded-lg p-4 border border-purple-100">
                    <p class="text-xs font-semibold text-gray-600 uppercase tracking-wider mb-2">Total Imágenes</p>
                    <p class="text-2xl font-bold text-gray-900">{{ userStats.total_images || 0 }}</p>
                  </div>
                  <div class="bg-green-50 rounded-lg p-4 border border-green-100">
                    <p class="text-xs font-semibold text-gray-600 uppercase tracking-wider mb-2">Imágenes Procesadas</p>
                    <p class="text-2xl font-bold text-gray-900">{{ userStats.processed_images || 0 }}</p>
                  </div>
                  <div class="bg-blue-50 rounded-lg p-4 border border-blue-100">
                    <p class="text-xs font-semibold text-gray-600 uppercase tracking-wider mb-2">Tiene Perfil</p>
                    <p class="text-base font-bold text-gray-900">
                      <span :class="userStats.has_profile ? 'text-green-600' : 'text-gray-400'">
                        {{ userStats.has_profile ? 'Sí' : 'No' }}
                      </span>
                    </p>
                  </div>
                </div>
              </div>
            </div>

            <!-- Additional Info -->
            <div class="bg-white rounded-lg p-6 border border-gray-200 shadow-md">
              <h4 class="text-lg font-bold text-gray-900 mb-6 flex items-center gap-2">
                <svg class="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
                Información Adicional
              </h4>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div class="bg-green-50 rounded-lg p-4 border border-green-100">
                  <p class="text-xs font-semibold text-gray-600 uppercase tracking-wider mb-2">Departamento</p>
                  <p class="text-base font-bold text-gray-900 flex items-center gap-2">
                    <svg class="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                    </svg>
                    {{ persona?.departamento_info?.nombre || 'No especificado' }}
                  </p>
                </div>
                <div class="bg-blue-50 rounded-lg p-4 border border-blue-100">
                  <p class="text-xs font-semibold text-gray-600 uppercase tracking-wider mb-2">ID de Usuario</p>
                  <p class="text-base font-bold text-gray-900 flex items-center gap-2">
                    <svg class="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V8a2 2 0 00-2-2h-5m-4 0V5a2 2 0 114 0v1m-4 0a2 2 0 104 0m-5 8a2 2 0 100-4 2 2 0 000 4zm0 0c1.306 0 2.417.835 2.83 2M9 14a3.001 3.001 0 00-2.83 2M15 11h3m-3 4h2"></path>
                    </svg>
                    #{{ farmer.id }}
                  </p>
                </div>
              </div>
            </div>
          </div>

    </template>

    <template #footer>
      <div class="flex items-center justify-end">
        <button 
          type="button"
          @click="closeModal"
          class="px-6 py-3 text-sm font-semibold text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 transition-all duration-200"
        >
          Cerrar
        </button>
      </div>
    </template>
  </BaseModal>

  <!-- Modal de detalles de finca -->
  <Teleport to="body">
    <FincaDetailModal
      v-if="showFincaModal"
      :show="showFincaModal"
      :finca="selectedFinca"
      :user-role="userRole"
      :hide-actions="true"
      @close="closeFincaModal"
      @edit="handleFincaEdit"
      @view-lotes="handleFincaViewLotes"
    />
  </Teleport>
</template>

<script>
import { ref, computed, watch } from 'vue';
import { getFincas } from '@/services/fincasApi';
import authApi from '@/services/authApi';
import BaseModal from '@/components/common/BaseModal.vue';
import FincaDetailModal from '@/components/common/FincasViewComponents/FincaDetailModal.vue';
import { useAuthStore } from '@/stores/auth';

export default {
  name: 'FarmerDetailModal',
  props: {
    farmer: {
      type: Object,
      default: () => ({
        id: null,
        name: '',
        email: '',
        initials: '',
        status: 'Inactivo',
        fincas: []
      })
    }
  },
  emits: ['close'],
  components: {
    BaseModal,
    FincaDetailModal
  },
  setup(props, { emit }) {
    const authStore = useAuthStore();
    const isOpen = ref(false);
    const loading = ref(false);
    const fincasList = ref([]); // Estado local para las fincas
    const persona = ref(null);
    const userDetails = ref(null);
    const userStats = ref(null);
    const showFincaModal = ref(false);
    const selectedFinca = ref(null);
    
    const userRole = computed(() => {
      const role = authStore.userRole || 'admin';
      if (role === 'farmer') return 'agricultor';
      return role;
    });

    const totalArea = computed(() => {
      if (fincasList.value.length === 0) {
        return '0.0';
      }
      
      const total = fincasList.value.reduce((sum, finca) => {
        return sum + Number.parseFloat(finca.hectareas || 0);
      }, 0);
      
      return total.toFixed(1);
    });

    const totalAnalisis = computed(() => {
      if (userStats.value?.total_images) {
        return userStats.value.total_images;
      }
      return 0;
    });

    const formatDate = (dateString) => {
      if (!dateString) return '-';
      try {
        const date = new Date(dateString);
        return date.toLocaleDateString('es-ES', { 
          year: 'numeric', 
          month: 'long', 
          day: 'numeric' 
        });
      } catch (error) {
        return dateString;
      }
    };

    const formatDateTime = (dateString) => {
      if (!dateString) return '-';
      try {
        const date = new Date(dateString);
        return date.toLocaleString('es-ES', { 
          year: 'numeric', 
          month: 'long', 
          day: 'numeric',
          hour: '2-digit',
          minute: '2-digit'
        });
      } catch (error) {
        return dateString;
      }
    };

    const getGoogleMapsUrl = (lat, lng) => {
      if (!lat || !lng) return '#';
      return `https://www.google.com/maps?q=${lat},${lng}`;
    };

    const getStatusClasses = (status) => {
      switch (status) {
        case 'Activo':
          return 'bg-green-100 text-green-800';
        case 'Inactivo':
          return 'bg-red-100 text-red-800';
        default:
          return 'bg-gray-100 text-gray-800';
      }
    };

    const closeModal = () => {
      isOpen.value = false;
      emit('close');
    };

    const openModal = () => {
      isOpen.value = true;
    };

    // Cargar detalles completos de usuario (incluye persona)
    const loadFarmerDetails = async (userId) => {
      try {
        loading.value = true;
        const data = await authApi.getUser(userId);
        console.log('Datos recibidos del API:', data);
        userDetails.value = data || null;
        persona.value = data?.persona || null;
        userStats.value = data?.stats || null;
        console.log('Persona asignada:', persona.value);
        console.log('UserStats asignado:', userStats.value);
      } catch (error) {
        console.error('Error cargando detalles del usuario:', error);
        userDetails.value = null;
        persona.value = null;
        userStats.value = null;
      } finally {
        loading.value = false;
      }
    };

    // Watch for farmer changes and load data
    // Función para cargar las fincas del agricultor
    const loadFarmersFincas = async (agricultorId) => {
      try {
        const response = await getFincas({ agricultor: agricultorId });
        fincasList.value = response.results || [];
      } catch (error) {
        fincasList.value = [];
      }
    };

    const handleFincaClick = (finca) => {
      console.log('Finca clickeada:', finca);
      selectedFinca.value = finca;
      showFincaModal.value = true;
      console.log('showFincaModal:', showFincaModal.value);
      console.log('selectedFinca:', selectedFinca.value);
    };

    const closeFincaModal = () => {
      showFincaModal.value = false;
      setTimeout(() => {
        selectedFinca.value = null;
      }, 300);
    };

    const handleFincaEdit = (finca) => {
      // Emitir evento para editar finca o navegar
      closeFincaModal();
      // Aquí puedes agregar lógica adicional si necesitas editar desde el modal de agricultor
    };

    const handleFincaViewLotes = (finca) => {
      // Emitir evento para ver lotes o navegar
      closeFincaModal();
      // Aquí puedes agregar lógica adicional si necesitas ver lotes desde el modal de agricultor
    };

    watch(() => props.farmer, async (newFarmer, oldFarmer) => {
      if (newFarmer && newFarmer.id) {
        // Open modal when farmer is set
        if (newFarmer.id !== oldFarmer?.id) {
          isOpen.value = true;
        }
        // Load farmer data
        await loadFarmersFincas(newFarmer.id);
        await loadFarmerDetails(newFarmer.id);
        // Pendiente: Cargar estadísticas detalladas de análisis del agricultor
        // cuando esté disponible el endpoint: GET /api/v1/agricultores/{id}/analisis/detailed/
      } else if (!newFarmer) {
        // Close modal when farmer is cleared
        isOpen.value = false;
      }
    }, { immediate: true });

    return {
      isOpen,
      loading,
      totalArea,
      totalAnalisis,
      getStatusClasses,
      closeModal,
      openModal,
      fincasList,
      persona,
      userDetails,
      userStats,
      loadFarmersFincas,
      loadFarmerDetails,
      showFincaModal,
      selectedFinca,
      userRole,
      handleFincaClick,
      closeFincaModal,
      handleFincaEdit,
      handleFincaViewLotes,
      formatDate,
      formatDateTime,
      getGoogleMapsUrl
    };
  }
};
</script>

