<template>
  <div class="mt-8">
    <h3 class="text-lg font-medium text-gray-900 mb-4">Imágenes Analizadas</h3>
    <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
      <div 
        v-for="(image, index) in images" 
        :key="index"
        class="relative group rounded-lg overflow-hidden border border-gray-200 hover:shadow-md transition-shadow"
      >
        <img 
          :src="image.thumbnailUrl" 
          :alt="`Imagen ${index + 1}`"
          class="w-full h-32 object-cover"
        />
        <div class="absolute inset-0 bg-black bg-opacity-50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
          <button 
            @click="$emit('image-click', image)"
            class="text-white p-2 rounded-full bg-black bg-opacity-50 hover:bg-opacity-70"
            aria-label="Ver detalles de la imagen"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v6m0 0v6m0-6h6m-6 0H4" />
            </svg>
          </button>
        </div>
        <div class="absolute bottom-0 left-0 right-0 bg-black bg-opacity-70 text-white text-xs p-2">
          {{ image.defects.length }} defecto{{ image.defects.length !== 1 ? 's' : '' }}
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ImageGallery',
  props: {
    images: {
      type: Array,
      required: true,
      default: () => []
    }
  },
  emits: ['image-click']
}
</script>
