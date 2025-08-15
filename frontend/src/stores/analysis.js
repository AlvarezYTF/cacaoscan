import { defineStore } from 'pinia';

export const useAnalysisStore = defineStore('analysis', {
  state: () => ({
    batch: {
      name: '',
      collectionDate: '',
      origin: '',
      notes: '',
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
      };
      this.images = [];
      this.uploadProgress = 0;
      this.uploadError = null;
    },

    async submitBatch() {
      if (!this.isValid || this.isUploading) return false;

      this.isUploading = true;
      this.uploadError = null;

      try {
        const formData = new FormData();

        // Add batch data
        Object.entries(this.batch).forEach(([key, value]) => {
          if (value) formData.append(key, value);
        });

        // Add images
        this.images.forEach((file) => {
          formData.append('images', file);
        });

        // TODO: Replace with actual API endpoint
        const response = await fetch('/api/analysis', {
          method: 'POST',
          body: formData,
          onUploadProgress: (progressEvent) => {
            this.uploadProgress = Math.round(
              (progressEvent.loaded * 100) / progressEvent.total
            );
          },
        });

        if (!response.ok) {
          throw new Error('Error al enviar el análisis');
        }

        const result = await response.json();
        return result;

      } catch (error) {
        this.uploadError = error.message || 'Error desconocido al procesar la solicitud';
        throw error;
      } finally {
        this.isUploading = false;
      }
    },
  },
});
