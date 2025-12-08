<template>
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

defineEmits(['edit', 'view-lotes', 'confirm-delete', 'confirm-activate'])
</script>

