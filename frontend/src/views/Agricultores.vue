<template>
    <div class="min-h-screen bg-gray-50 flex pb-8">
      <!-- Sidebar -->
      <aside class="w-16 md:w-64 bg-gradient-to-b from-green-800 to-green-600 text-white fixed inset-y-0 left-0 z-10 flex flex-col shadow-lg">
        <!-- Logo/Brand -->
        <div class="p-4 flex items-center justify-center md:justify-start">
          <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
          </svg>
          <h1 class="text-xl font-bold text-white tracking-tight ml-3 hidden md:block">Panel Admin</h1>
        </div>
        
        <!-- Navigation -->
        <nav class="mt-8 flex-1">
          <div class="px-2 space-y-1">
            <router-link :to="{name: 'admin-dashboard'}" class="group flex items-center px-2 py-3 text-sm font-medium rounded-md hover:bg-green-700 transition-colors" :class="{'bg-green-700': $route.name === 'admin-dashboard'}">
              <svg class="w-6 h-6 mr-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"></path>
              </svg>
              <span class="hidden md:block">Inicio</span>
            </router-link>
            
            <router-link :to="{name: 'agricultores'}" class="group flex items-center px-2 py-3 text-sm font-medium rounded-md hover:bg-green-700 transition-colors" :class="{'bg-green-700': $route.name === 'agricultores'}">
              <svg class="w-6 h-6 mr-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path>
              </svg>
              <span class="hidden md:block">Agricultores</span>
            </router-link>
            
            <router-link :to="{name: 'analisis'}" class="group flex items-center px-2 py-3 text-sm font-medium rounded-md hover:bg-green-700 transition-colors" :class="{'bg-green-700': $route.name === 'analisis'}">
              <svg class="w-6 h-6 mr-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01"></path>
              </svg>
              <span class="hidden md:block">Análisis</span>
            </router-link>
            
            <router-link :to="{name: 'reportes'}" class="group flex items-center px-2 py-3 text-sm font-medium rounded-md hover:bg-green-700 transition-colors" :class="{'bg-green-700': $route.name === 'reportes'}">
              <svg class="w-6 h-6 mr-3 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
              </svg>
              <span class="hidden md:block">Reportes</span>
            </router-link>
          </div>
        </nav>
        
        <!-- User Profile -->
        <div class="p-4 border-t border-green-700">
          <div class="flex items-center">
            <div class="h-8 w-8 rounded-full bg-white flex items-center justify-center text-green-800 font-bold">
              AD
            </div>
            <div class="ml-3 hidden md:block">
              <p class="text-sm font-medium text-white">Admin</p>
              <p class="text-xs text-green-200">Ver perfil</p>
            </div>
          </div>
        </div>
      </aside>
  
      <!-- Main Content -->
      <main class="flex-1 ml-16 md:ml-64">
        <!-- Header -->
        <header class="bg-white shadow-sm mb-4 md:mb-6">
          <div class="px-3 sm:px-4 lg:px-8 py-4 md:py-6">
            <div class="flex items-center">
              <svg class="h-6 w-6 md:h-8 md:w-8 mr-2 md:mr-3 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path>
              </svg>
              <div>
                <h1 class="text-lg md:text-2xl font-bold text-gray-800">Agricultores</h1>
                <p class="text-xs md:text-sm text-gray-600">Gestión de agricultores y fincas</p>
              </div>
            </div>
          </div>
        </header>
  
      <!-- Contenido principal -->
      <div class="max-w-7xl mx-auto px-3 sm:px-4 lg:px-8 py-4 md:py-8">
        <!-- Barra de acciones -->
        <div class="mb-4 md:mb-6">
          <div class="flex flex-col sm:flex-row sm:justify-between sm:items-center space-y-3 sm:space-y-0">
            <div>
              <h2 class="text-lg md:text-xl font-semibold text-gray-800">Listado de Agricultores</h2>
              <p class="text-xs md:text-sm text-gray-500">Gestiona los agricultores registrados en el sistema</p>
            </div>
            <div class="flex flex-col sm:flex-row items-stretch sm:items-center space-y-2 sm:space-y-0 sm:space-x-3">
              <div class="relative">
                <input type="text" placeholder="Buscar agricultor..." class="w-full sm:w-64 pl-9 pr-4 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500" />
                <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <svg class="h-4 w-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
                  </svg>
                </div>
              </div>
              <button class="bg-green-600 text-white hover:bg-green-700 px-4 py-2 rounded-md text-sm font-medium flex items-center justify-center transition-colors duration-150">
                <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
                </svg>
                <span class="hidden sm:inline">Nuevo Agricultor</span>
                <span class="sm:hidden">+ Nuevo</span>
              </button>
            </div>
          </div>
        </div>
  
        <!-- Filtros -->
        <div class="mb-4 md:mb-6 bg-white p-3 md:p-4 rounded-lg shadow-sm border border-gray-200">
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 md:gap-4">
            <div>
              <label for="region" class="block text-xs md:text-sm font-medium text-gray-700 mb-1">Región</label>
              <select id="region" class="block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500 text-xs md:text-sm">
                <option value="">Todas las regiones</option>
                <option>Antioquia</option>
                <option>Santander</option>
                <option>Nariño</option>
                <option>Huila</option>
              </select>
            </div>
            
            <div>
              <label for="status" class="block text-xs md:text-sm font-medium text-gray-700 mb-1">Estado</label>
              <select id="status" class="block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500 text-xs md:text-sm">
                <option value="">Todos los estados</option>
                <option>Activo</option>
                <option>En Revisión</option>
                <option>Inactivo</option>
              </select>
            </div>
            
            <div class="sm:col-span-2 lg:col-span-1 flex items-end">
              <button class="w-full bg-white border border-gray-300 text-gray-700 px-4 py-2 rounded-md text-xs md:text-sm font-medium hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500">
                Aplicar Filtros
              </button>
            </div>
          </div>
        </div>
  
        <!-- Tabla de agricultores -->
        <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden hover:shadow-md transition-shadow duration-300">
          <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
              <thead class="bg-gray-50">
                <tr>
                  <th scope="col" class="px-3 md:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Agricultor</th>
                  <th scope="col" class="px-3 md:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Finca</th>
                  <th scope="col" class="px-3 md:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Región</th>
                  <th scope="col" class="px-3 md:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Estado</th>
                  <th scope="col" class="px-3 md:px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Acciones</th>
                </tr>
              </thead>
              <tbody class="bg-white divide-y divide-gray-200">
                <!-- Fila 1 -->
                <tr class="hover:bg-gray-50 transition-colors duration-150">
                  <td class="px-3 md:px-6 py-3 md:py-4 whitespace-nowrap">
                    <div class="flex items-center">
                      <div class="h-8 w-8 md:h-10 md:w-10 rounded-full bg-green-100 flex items-center justify-center text-green-600 font-medium text-sm md:text-base">CH</div>
                      <div class="ml-2 md:ml-4">
                        <div class="text-xs md:text-sm font-medium text-gray-900">Camilo Hernandez</div>
                        <div class="text-xs md:text-sm text-gray-500">camilo@example.com</div>
                      </div>
                    </div>
                  </td>
                  <td class="px-3 md:px-6 py-3 md:py-4 whitespace-nowrap">
                    <div class="text-xs md:text-sm text-gray-900">Finca El Paraíso</div>
                    <div class="text-xs md:text-sm text-gray-500">12 hectáreas</div>
                  </td>
                  <td class="px-3 md:px-6 py-3 md:py-4 whitespace-nowrap">
                    <div class="text-xs md:text-sm text-gray-900">Santander</div>
                  </td>
                  <td class="px-3 md:px-6 py-3 md:py-4 whitespace-nowrap">
                    <span class="px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">Activo</span>
                  </td>
                  <td class="px-3 md:px-6 py-3 md:py-4 whitespace-nowrap text-right text-xs md:text-sm font-medium">
                    <div class="flex flex-col sm:flex-row sm:space-x-2 space-y-1 sm:space-y-0">
                      <a href="#" class="text-green-600 hover:text-green-900">Ver</a>
                      <a href="#" class="text-blue-600 hover:text-blue-900">Editar</a>
                      <a href="#" class="text-red-600 hover:text-red-900">Eliminar</a>
                    </div>
                  </td>
                </tr>
                <!-- Fila 2 -->
                <tr class="hover:bg-gray-50 transition-colors duration-150">
                  <td class="px-3 md:px-6 py-3 md:py-4 whitespace-nowrap">
                    <div class="flex items-center">
                      <div class="h-8 w-8 md:h-10 md:w-10 rounded-full bg-blue-100 flex items-center justify-center text-blue-600 font-medium text-sm md:text-base">JA</div>
                      <div class="ml-2 md:ml-4">
                        <div class="text-xs md:text-sm font-medium text-gray-900">Jeferson Alvarez</div>
                        <div class="text-xs md:text-sm text-gray-500">jeferson@example.com</div>
                      </div>
                    </div>
                  </td>
                  <td class="px-3 md:px-6 py-3 md:py-4 whitespace-nowrap">
                    <div class="text-xs md:text-sm text-gray-900">Finca Los Laureles</div>
                    <div class="text-xs md:text-sm text-gray-500">8 hectáreas</div>
                  </td>
                  <td class="px-3 md:px-6 py-3 md:py-4 whitespace-nowrap">
                    <div class="text-xs md:text-sm text-gray-900">Antioquia</div>
                  </td>
                  <td class="px-3 md:px-6 py-3 md:py-4 whitespace-nowrap">
                    <span class="px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">Activo</span>
                  </td>
                  <td class="px-3 md:px-6 py-3 md:py-4 whitespace-nowrap text-right text-xs md:text-sm font-medium">
                    <div class="flex flex-col sm:flex-row sm:space-x-2 space-y-1 sm:space-y-0">
                      <a href="#" class="text-green-600 hover:text-green-900">Ver</a>
                      <a href="#" class="text-blue-600 hover:text-blue-900">Editar</a>
                      <a href="#" class="text-red-600 hover:text-red-900">Eliminar</a>
                    </div>
                  </td>
                </tr>
                <!-- Fila 3 -->
                <tr class="hover:bg-gray-50 transition-colors duration-150">
                  <td class="px-3 md:px-6 py-3 md:py-4 whitespace-nowrap">
                    <div class="flex items-center">
                      <div class="h-8 w-8 md:h-10 md:w-10 rounded-full bg-yellow-100 flex items-center justify-center text-yellow-600 font-medium text-sm md:text-base">CC</div>
                      <div class="ml-2 md:ml-4">
                        <div class="text-xs md:text-sm font-medium text-gray-900">Cristian Camacho</div>
                        <div class="text-xs md:text-sm text-gray-500">cristian@example.com</div>
                      </div>
                    </div>
                  </td>
                  <td class="px-3 md:px-6 py-3 md:py-4 whitespace-nowrap">
                    <div class="text-xs md:text-sm text-gray-900">Finca El Mirador</div>
                    <div class="text-xs md:text-sm text-gray-500">15 hectáreas</div>
                  </td>
                  <td class="px-3 md:px-6 py-3 md:py-4 whitespace-nowrap">
                    <div class="text-xs md:text-sm text-gray-900">Huila</div>
                  </td>
                  <td class="px-3 md:px-6 py-3 md:py-4 whitespace-nowrap">
                    <span class="px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full bg-yellow-100 text-yellow-800">En revisión</span>
                  </td>
                  <td class="px-3 md:px-6 py-3 md:py-4 whitespace-nowrap text-right text-xs md:text-sm font-medium">
                    <div class="flex flex-col sm:flex-row sm:space-x-2 space-y-1 sm:space-y-0">
                      <a href="#" class="text-green-600 hover:text-green-900">Ver</a>
                      <a href="#" class="text-blue-600 hover:text-blue-900">Editar</a>
                      <a href="#" class="text-red-600 hover:text-red-900">Eliminar</a>
                    </div>
                  </td>
                </tr>
                <!-- Fila 4 -->
                <tr class="hover:bg-gray-50 transition-colors duration-150">
                  <td class="px-3 md:px-6 py-3 md:py-4 whitespace-nowrap">
                    <div class="flex items-center">
                      <div class="h-8 w-8 md:h-10 md:w-10 rounded-full bg-red-100 flex items-center justify-center text-red-600 font-medium text-sm md:text-base">JP</div>
                      <div class="ml-2 md:ml-4">
                        <div class="text-xs md:text-sm font-medium text-gray-900">Juan Pablo Pérez</div>
                        <div class="text-xs md:text-sm text-gray-500">juanpablo@example.com</div>
                      </div>
                    </div>
                  </td>
                  <td class="px-3 md:px-6 py-3 md:py-4 whitespace-nowrap">
                    <div class="text-xs md:text-sm text-gray-900">Finca La Esperanza</div>
                    <div class="text-xs md:text-sm text-gray-500">10 hectáreas</div>
                  </td>
                  <td class="px-3 md:px-6 py-3 md:py-4 whitespace-nowrap">
                    <div class="text-xs md:text-sm text-gray-900">Nariño</div>
                  </td>
                  <td class="px-3 md:px-6 py-3 md:py-4 whitespace-nowrap">
                    <span class="px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full bg-red-100 text-red-800">Inactivo</span>
                  </td>
                  <td class="px-3 md:px-6 py-3 md:py-4 whitespace-nowrap text-right text-xs md:text-sm font-medium">
                    <div class="flex flex-col sm:flex-row sm:space-x-2 space-y-1 sm:space-y-0">
                      <a href="#" class="text-green-600 hover:text-green-900">Ver</a>
                      <a href="#" class="text-blue-600 hover:text-blue-900">Editar</a>
                      <a href="#" class="text-red-600 hover:text-red-900">Eliminar</a>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <!-- Paginación -->
          <div class="bg-gray-50 px-3 md:px-6 py-3 md:py-4 border-t border-gray-100">
            <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-3 sm:space-y-0">
              <div class="flex justify-center sm:justify-start">
                <p class="text-xs md:text-sm text-gray-700">
                  Mostrando <span class="font-medium">1</span> a <span class="font-medium">4</span> de <span class="font-medium">12</span> resultados
                </p>
              </div>
              <div class="flex justify-center sm:justify-end">
                <nav class="relative z-0 inline-flex rounded-md shadow-sm -space-x-px" aria-label="Pagination">
                  <button class="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-xs md:text-sm font-medium text-gray-500 hover:bg-gray-50">
                    <span class="sr-only">Anterior</span>
                    <svg class="h-4 w-4 md:h-5 md:w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                      <path fill-rule="evenodd" d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clip-rule="evenodd" />
                    </svg>
                  </button>
                  <button class="relative inline-flex items-center px-3 md:px-4 py-2 border border-gray-300 bg-white text-xs md:text-sm font-medium text-gray-700 hover:bg-gray-50">
                    1
                  </button>
                  <button class="relative inline-flex items-center px-3 md:px-4 py-2 border border-gray-300 bg-white text-xs md:text-sm font-medium text-gray-700 hover:bg-gray-50">
                    2
                  </button>
                  <button class="relative inline-flex items-center px-3 md:px-4 py-2 border border-gray-300 bg-white text-xs md:text-sm font-medium text-gray-700 hover:bg-gray-50">
                    3
                  </button>
                  <button class="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-xs md:text-sm font-medium text-gray-500 hover:bg-gray-50">
                    <span class="sr-only">Siguiente</span>
                    <svg class="h-4 w-4 md:h-5 md:w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                      <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
                    </svg>
                  </button>
                </nav>
              </div>
            </div>
          </div>
        </div>
      </div>
      </main>
    </div>
  </template>
  
  <script>
  export default {
  name: 'AgricultoresView',
  setup() {
    // Aquí iría la lógica del componente
    return {};
  }
};
  </script>