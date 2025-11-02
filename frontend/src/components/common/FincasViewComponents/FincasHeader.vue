<template>
  <div class="bg-white rounded-xl shadow-lg border border-gray-200 p-8">
    <div class="flex items-center justify-between flex-wrap gap-4">
      <div class="flex items-center">
        <div class="bg-green-100 p-3 rounded-lg mr-4">
          <svg class="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2H5a2 2 0 00-2-2z"></path>
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 5a2 2 0 012-2h4a2 2 0 012 2v2H8V5z"></path>
          </svg>
        </div>
        <div>
          <h1 class="text-3xl font-bold text-gray-900">Gestión de Fincas</h1>
          <p class="text-gray-600 mt-1">Administra las fincas de cacao registradas</p>
        </div>
      </div>
      <!-- Acciones intuitivas -->
      <div class="flex items-center space-x-3">
        <button
          @click="handleCreate"
          class="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-all duration-200 flex items-center gap-2"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
          </svg>
          Nueva Finca
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
const emit = defineEmits(['create'])

const handleCreate = () => {
  console.debug('[Fincas] Click Nueva Finca')
  emit('create')
}
</script>

<style scoped>
/* Estilos adicionales si son necesarios */
</style>