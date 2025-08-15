<template>
  <div v-if="show" class="fixed inset-0 z-50 overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
    <div class="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
      <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" aria-hidden="true" @click="$emit('close')"></div>
      <span class="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>
      <div class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-4xl sm:w-full">
        <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
          <div class="sm:flex sm:items-start w-full">
            <div class="mt-3 text-center sm:mt-0 sm:ml-4 sm:text-left w-full">
              <div class="flex justify-between items-center">
                <h3 class="text-lg leading-6 font-medium text-gray-900" id="modal-title">
                  Imagen Analizada
                </h3>
                <button 
                  type="button" 
                  class="bg-white rounded-md text-gray-400 hover:text-gray-500 focus:outline-none"
                  @click="$emit('close')"
                  aria-label="Cerrar modal"
                >
                  <span class="sr-only">Cerrar</span>
                  <svg class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              <div class="mt-4 relative">
                <img :src="image.fullSizeUrl" class="w-full max-h-[70vh] object-contain" :alt="'Imagen analizada'" />
                <!-- Defect markers would go here -->
              </div>
              <div class="mt-4">
                <h4 class="font-medium text-gray-900">Defectos Detectados ({{ image.defects.length }})</h4>
                <ul class="mt-2 space-y-2">
                  <li v-for="(defect, index) in image.defects" :key="index" class="text-sm text-gray-600">
                    • {{ defect.type }} ({{ defect.confidence }}% de confianza)
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>
        <div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
          <button 
            type="button" 
            class="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm"
            @click="$emit('close')"
          >
            Cerrar
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ImageModal',
  props: {
    show: {
      type: Boolean,
      default: false
    },
    image: {
      type: Object,
      default: () => ({
        fullSizeUrl: '',
        defects: []
      })
    }
  },
  emits: ['close']
}
</script>
