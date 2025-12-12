<template>
  <section class="upload-section">
    <div class="upload-card cursor-pointer" @click="triggerFileInput">
      <div class="upload-icon">
        <i class="fas fa-camera"></i>
      </div>
      <h3>Subir imágenes de granos</h3>
      <p>Arrastra o haz clic para subir fotos de tus granos de cacao</p>
      <input 
        type="file" 
        ref="fileInput" 
        @change="handleFileUpload" 
        multiple 
        accept="image/*"
        style="display: none;"
      >
    </div>
  </section>
</template>

<script>
export default {
  name: 'UploadSection',
  emits: ['file-upload'],
  methods: {
    triggerFileInput() {
      this.$refs.fileInput.click();
    },
    handleFileUpload(event) {
      const files = event.target.files;
      if (files && files.length > 0) {
        this.$emit('file-upload', files);
      }
      // Reset the input to allow selecting the same file again
      event.target.value = '';
    }
  }
};
</script>

<style scoped>
.upload-section {
  margin: 2rem 0;
}

.upload-card {
  background: white;
  border: 2px dashed #bdc3c7;
  border-radius: 10px;
  padding: 2rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s ease;
}

.upload-card:hover {
  border-color: #27ae60;
  background-color: #f8f9fa;
}

.upload-icon {
  font-size: 2.5rem;
  color: #7f8c8d;
  margin-bottom: 1rem;
}

.upload-card h3 {
  margin: 0.5rem 0;
  color: #2c3e50;
}

.upload-card p {
  color: #7f8c8d;
  margin: 0;
}
</style>
