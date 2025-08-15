<template>
  <div class="space-y-4">
    <!-- Drop Zone -->
    <div 
      @dragover.prevent="isDragging = true"
      @dragleave="isDragging = false"
      @drop.prevent="handleDrop"
      @click="$refs.fileInput.click()"
      class="border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors"
      :class="{
        'border-green-500 bg-green-50': isDragging,
        'border-gray-300 hover:border-green-400': !isDragging,
      }"
    >
      <div class="flex flex-col items-center justify-center space-y-2">
        <svg 
          class="w-12 h-12 text-gray-400" 
          fill="none" 
          stroke="currentColor" 
          viewBox="0 0 24 24"
        >
          <path 
            stroke-linecap="round" 
            stroke-linejoin="round" 
            stroke-width="1.5" 
            d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
          />
        </svg>
        <p class="text-lg font-medium text-gray-700">
          Arrastra tus imágenes aquí o haz clic para seleccionarlas
        </p>
        <p class="text-sm text-gray-500">
          Formatos soportados: JPG, PNG (máx. 5MB por imagen)
        </p>
      </div>
      <input
        ref="fileInput"
        type="file"
        class="hidden"
        multiple
        accept="image/*"
        @change="handleFileSelect"
      />
    </div>

    <!-- Image Previews -->
    <div v-if="images.length > 0" class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
      <div 
        v-for="(image, index) in images" 
        :key="index"
        class="relative group rounded-lg overflow-hidden border border-gray-200"
      >
        <img 
          :src="getImageUrl(image)" 
          :alt="`Imagen ${index + 1}`"
          class="w-full h-32 object-cover"
        />
        <button
          @click.stop="removeImage(index)"
          class="absolute top-2 right-2 bg-red-500 text-white rounded-full p-1 opacity-0 group-hover:opacity-100 transition-opacity"
          aria-label="Eliminar imagen"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </div>

    <!-- Error Message -->
    <div v-if="error" class="text-red-500 text-sm mt-2">
      {{ error }}
    </div>
  </div>
</template>

<script>
import { ref, toRefs } from 'vue';

export default {
  name: 'ImageUploader',
  props: {
    modelValue: {
      type: Array,
      default: () => []
    },
    maxFiles: {
      type: Number,
      default: 10
    },
    maxFileSize: {
      type: Number, // in MB
      default: 5
    }
  },
  emits: ['update:modelValue'],
  setup(props, { emit }) {
    const { modelValue } = toRefs(props);
    const isDragging = ref(false);
    const fileInput = ref(null);
    const error = ref('');

    const images = ref([...modelValue.value]);

    const getImageUrl = (file) => {
      return URL.createObjectURL(file);
    };

    const validateFile = (file) => {
      const validTypes = ['image/jpeg', 'image/png', 'image/jpg'];
      const maxSize = props.maxFileSize * 1024 * 1024; // Convert MB to bytes

      if (!validTypes.includes(file.type)) {
        return 'Tipo de archivo no soportado. Por favor, sube solo imágenes JPG o PNG.';
      }

      if (file.size > maxSize) {
        return `El archivo ${file.name} es demasiado grande. Tamaño máximo: ${props.maxFileSize}MB.`;
      }

      return '';
    };

    const handleFileSelect = (event) => {
      error.value = '';
      const files = Array.from(event.target.files);
      processFiles(files);
      // Reset file input to allow selecting the same file again
      if (fileInput.value) {
        fileInput.value.value = '';
      }
    };

    const handleDrop = (event) => {
      isDragging.value = false;
      error.value = '';
      const files = Array.from(event.dataTransfer.files);
      processFiles(files);
    };

    const processFiles = (files) => {
      if (files.length === 0) return;

      // Check if adding these files would exceed maxFiles
      if (images.value.length + files.length > props.maxFiles) {
        error.value = `Solo puedes subir un máximo de ${props.maxFiles} imágenes.`;
        return;
      }

      let hasError = false;
      const validFiles = [];

      files.forEach(file => {
        const validationError = validateFile(file);
        if (validationError) {
          error.value = validationError;
          hasError = true;
          return;
        }
        validFiles.push(file);
      });

      if (hasError && validFiles.length === 0) return;

      // Add valid files to the images array
      images.value = [...images.value, ...validFiles];
      emit('update:modelValue', images.value);
    };

    const removeImage = (index) => {
      images.value.splice(index, 1);
      emit('update:modelValue', images.value);
    };

    return {
      isDragging,
      fileInput,
      error,
      images,
      getImageUrl,
      handleFileSelect,
      handleDrop,
      removeImage
    };
  }
};
</script>
