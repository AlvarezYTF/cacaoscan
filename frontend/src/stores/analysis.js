import { defineStore } from 'pinia';
import api from '@/services/api';

export const useAnalysisStore = defineStore('analysis', {
  state: () => ({
    batch: {
      name: '',
      collectionDate: '',
      origin: '',
      notes: '',
      farm: '',
      originPlace: '',
      genetics: '',
      farmer: '',
    },
    images: [],
    uploadProgress: 0,
    isUploading: false,
    uploadError: null,
  }),

  getters: {
    hasImages: (state) => state.images.length > 0,
    isValid: (state) => {
      return (
        state.batch.name.trim() !== '' &&
        state.batch.collectionDate &&
        state.batch.farm &&
        state.batch.genetics &&
        state.images.length > 0
      );
    },
  },

  actions: {
    setBatchData(data) {
      this.batch = { ...this.batch, ...data };
    },

    addImages(newImages) {
      const validImages = Array.from(newImages).filter(file =>
        file.type.startsWith('image/')
      );

      this.images = [...this.images, ...validImages];
      return validImages.length;
    },

    removeImage(index) {
      this.images.splice(index, 1);
    },

    clearBatch() {
      this.batch = {
        name: '',
        collectionDate: '',
        origin: '',
        notes: '',
        farm: '',
        originPlace: '',
        genetics: '',
        farmer: '',
      };
      this.images = [];
      this.uploadProgress = 0;
      this.uploadError = null;
    },

    async submitBatch() {
      if (!this.isValid || this.isUploading) return false;

      this.isUploading = true;
      this.uploadError = null;
      this.uploadProgress = 0;

      try {
        const formData = new FormData();

        // Add batch data
        for (const [key, value] of Object.entries(this.batch)) {
          if (value) {
            formData.append(key, value);
          }
        }

        // Add images
        for (const file of this.images) {
          formData.append('images', file);
        }

        // Upload with progress tracking
        // Timeout aumentado a 120 segundos para análisis batch con múltiples imágenes
        const response = await api.post('/analysis/batch/', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
          timeout: 120000, // 120 segundos (2 minutos) para procesamiento de múltiples imágenes
          onUploadProgress: (progressEvent) => {
            if (progressEvent.total) {
              this.uploadProgress = Math.round(
                (progressEvent.loaded * 100) / progressEvent.total
              );
            }
          },
        });

        // El endpoint /api/v1/images/batch/upload/ procesa automáticamente las imágenes
        // incluyendo mediciones, por lo que no es necesario llamar a /scan/measure/ por separado.
        // Esto evita procesamiento duplicado y mejora el rendimiento del sistema.

        return response.data;

      } catch (error) {
        const errorMessage = error.response?.data?.error || 
                            error.message || 
                            'Error desconocido al procesar la solicitud';
        this.uploadError = errorMessage;
        throw new Error(errorMessage);
      } finally {
        this.isUploading = false;
      }
    },
  },
});
