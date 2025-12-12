<template>
  <div 
    class="relative bg-white rounded-xl shadow-md hover:shadow-lg transition-all duration-300 transform hover:-translate-y-1 border border-gray-200 cursor-pointer group"
    @click="$emit('view-details', finca)"
  >
    <div class="p-6">
      <!-- Header de la tarjeta -->
      <div class="flex justify-between items-start mb-4">
        <div class="flex-1">
          <h3 class="text-lg font-bold text-gray-900 mb-1">{{ finca.nombre }}</h3>
          <p class="text-sm text-gray-600 flex items-center gap-1">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path>
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path>
            </svg>
            {{ finca.municipio }}, {{ finca.departamento }}
          </p>
        </div>
        <span
          :class="[
            'px-3 py-1 text-xs font-semibold rounded-full flex items-center gap-1',
            finca.activa ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
          ]"
        >
          <svg v-if="finca.activa" class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
          <svg v-else class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
          {{ finca.activa ? 'Activa' : 'Inactiva' }}
        </span>
      </div>

      <!-- Información de la finca -->
      <div class="space-y-3 mb-4">
        <div class="flex items-center text-sm text-gray-600">
          <svg class="w-4 h-4 mr-2 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path>
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path>
          </svg>
          {{ finca.ubicacion }}
        </div>
        <div class="flex items-center text-sm text-gray-600">
          <svg class="w-4 h-4 mr-2 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z"></path>
          </svg>
          {{ finca.hectareas }} hectáreas
        </div>
      </div>

      <!-- Estadísticas -->
      <div class="grid grid-cols-2 gap-4 mb-4">
        <div class="bg-blue-50 rounded-lg p-3 text-center">
          <div class="text-2xl font-bold text-blue-600">{{ finca.total_lotes || 0 }}</div>
          <div class="text-xs text-gray-600">Lotes</div>
        </div>
        <div class="bg-purple-50 rounded-lg p-3 text-center">
          <div class="text-2xl font-bold text-purple-600">{{ finca.total_analisis || 0 }}</div>
          <div class="text-xs text-gray-600">Análisis</div>
        </div>
      </div>

      <!-- Acciones -->
      <div class="flex gap-2 flex-wrap">
        <!-- Botón Activar para admins (solo si está inactiva) -->
        <button
          v-if="userRole === 'admin' && !finca.activa"
          @click.stop="$emit('confirm-activate', finca)"
          class="flex-1 bg-green-600 hover:bg-green-700 text-white px-3 py-2 rounded-lg text-sm transition-all duration-200 flex items-center justify-center gap-1"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
          </svg>
          Activar
        </button>
        <!-- Botón Editar (solo si está activa o si es admin) -->
        <button
          v-if="finca.activa || userRole === 'admin'"
          @click.stop="$emit('edit', finca)"
          class="flex-1 bg-blue-600 hover:bg-blue-700 text-white px-3 py-2 rounded-lg text-sm transition-all duration-200 flex items-center justify-center gap-1"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path>
          </svg>
          Editar
        </button>
        <!-- Botón Ver Lotes (solo si está activa o si es admin) -->
        <button
          v-if="finca.activa || userRole === 'admin'"
          @click.stop="$emit('view-lotes', finca)"
          class="flex-1 bg-green-600 hover:bg-green-700 text-white px-3 py-2 rounded-lg text-sm transition-all duration-200 flex items-center justify-center gap-1"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 10h16M4 14h16M4 18h16"></path>
          </svg>
          Ver Lotes
        </button>
        <!-- Botón Desactivar (solo si está activa) -->
        <button
          v-if="finca.activa"
          @click.stop="$emit('confirm-delete', finca)"
          class="flex-1 bg-red-600 hover:bg-red-700 text-white px-3 py-2 rounded-lg text-sm transition-all duration-200 flex items-center justify-center gap-1"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636"></path>
          </svg>
          Desactivar
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  finca: {
    type: Object,
    required: true
  },
  userRole: {
    type: String,
    default: 'agricultor'
  }
})

defineEmits(['edit', 'view-lotes', 'confirm-delete', 'confirm-activate', 'view-details'])
</script>

<style scoped>
/* Estilos adicionales si son necesarios */
</style>