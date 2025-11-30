<template>
  <div 
    class="mt-8 pt-6 border-t border-gray-200 flex justify-end space-x-3"
    :class="containerClass"
  >
    <slot>
      <!-- Default actions if no slot provided -->
      <button
        v-if="showDownloadPdf"
        type="button"
        class="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
        @click="handleDownloadPdf"
      >
        <svg class="-ml-1 mr-2 h-5 w-5 text-gray-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
        </svg>
        {{ downloadLabel || 'Descargar PDF' }}
      </button>
      
      <button
        v-if="showNewAnalysis"
        type="button"
        class="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
        @click="handleNewAnalysis"
      >
        <svg class="-ml-1 mr-2 h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
        {{ newAnalysisLabel || 'Nuevo Análisis' }}
      </button>
    </slot>
  </div>
</template>

<script setup>
defineProps({
  showDownloadPdf: {
    type: Boolean,
    default: true
  },
  showNewAnalysis: {
    type: Boolean,
    default: true
  },
  downloadLabel: {
    type: String,
    default: ''
  },
  newAnalysisLabel: {
    type: String,
    default: ''
  },
  containerClass: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['download-pdf', 'new-analysis'])

const handleDownloadPdf = () => {
  emit('download-pdf')
}

const handleNewAnalysis = () => {
  emit('new-analysis')
}
</script>

<style scoped>
/* Styles handled by Tailwind classes */
</style>

