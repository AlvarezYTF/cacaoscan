<template>
  <div class="bg-white rounded-xl shadow-lg border border-gray-200 p-8">
    <div class="flex items-center justify-between flex-wrap gap-4">
      <div class="flex items-center">
        <div class="bg-green-100 p-3 rounded-lg mr-4">
          <svg class="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"></path>
          </svg>
        </div>
        <div>
          <h1 class="text-3xl font-bold text-gray-900">Gestión de Lotes</h1>
          <p class="text-gray-600 mt-1" v-if="fincaNombre">Lotes de la finca: {{ fincaNombre }}</p>
          <p class="text-gray-600 mt-1" v-else>Administra los lotes de cacao</p>
        </div>
      </div>
      <!-- Acciones intuitivas -->
      <div class="flex items-center space-x-3">
        <button
          v-if="canCreate"
          @click="handleCreate"
          class="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-all duration-200 flex items-center gap-2"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
          </svg>
          Nuevo Lote
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  fincaNombre: {
    type: String,
    default: ''
  },
  canCreate: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['create'])

const handleCreate = () => {
  emit('create')
}
</script>

<style scoped>
/* Estilos adicionales si son necesarios */
</style>

