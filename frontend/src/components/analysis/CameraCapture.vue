<template>
  <div class="camera-capture">
    <div class="camera-preview" :class="{ 'border-2 border-red-500': hasError }">
      <video
        v-show="!photoTaken"
        ref="video"
        class="w-full h-full object-cover"
        autoplay
        playsinline
      ></video>
      <canvas
        v-show="photoTaken"
        ref="canvas"
        class="w-full h-full object-cover"
      ></canvas>
    </div>

    <div class="camera-controls mt-4 flex justify-center space-x-4">
      <button
        v-if="!photoTaken"
        @click="capturePhoto"
        class="p-3 bg-red-600 rounded-full text-white hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2"
        :disabled="isLoading || !isCameraReady"
      >
        <svg
          class="w-8 h-8"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
          xmlns="http://www.w3.org/2000/svg"
        >
          <circle cx="12" cy="12" r="10"></circle>
        </svg>
      </button>

      <button
        v-if="photoTaken"
        @click="retakePhoto"
        class="p-2 bg-gray-200 rounded-md text-gray-700 hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
      >
        Volver a tomar
      </button>

      <button
        v-if="photoTaken"
        @click="savePhoto"
        class="p-2 bg-green-600 rounded-md text-white hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2"
      >
        Usar foto
      </button>
    </div>

    <div v-if="error" class="mt-2 text-sm text-red-600">
      {{ error }}
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onBeforeUnmount } from 'vue';

export default {
  name: 'CameraCapture',
  emits: ['capture'],
  setup(props, { emit }) {
    const video = ref(null);
    const canvas = ref(null);
    const stream = ref(null);
    const photoTaken = ref(false);
    const isLoading = ref(true);
    const isCameraReady = ref(false);
    const hasError = ref(false);
    const error = ref('');

    const startCamera = async () => {
      try {
        isLoading.value = true;
        error.value = '';
        hasError.value = false;
        
        // Stop any existing stream
        if (stream.value) {
          stopCamera();
        }

        // Request camera access
        stream.value = await navigator.mediaDevices.getUserMedia({
          video: {
            width: { ideal: 1280 },
            height: { ideal: 720 },
            facingMode: 'environment' // Use the back camera by default
          },
          audio: false
        });

        // Set video source
        if (video.value) {
          video.value.srcObject = stream.value;
          await new Promise((resolve) => {
            video.value.onloadedmetadata = () => {
              video.value.play();
              resolve();
            };
          });
          isCameraReady.value = true;
        }
      } catch (err) {
        console.error('Error accessing camera:', err);
        error.value = 'No se pudo acceder a la cámara. Asegúrate de otorgar los permisos necesarios.';
        hasError.value = true;
      } finally {
        isLoading.value = false;
      }
    };

    const stopCamera = () => {
      if (stream.value) {
        const tracks = stream.value.getTracks();
        tracks.forEach(track => track.stop());
        stream.value = null;
      }
      isCameraReady.value = false;
    };

    const capturePhoto = () => {
      if (!video.value || !canvas.value) return;

      const context = canvas.value.getContext('2d');
      canvas.value.width = video.value.videoWidth;
      canvas.value.height = video.value.videoHeight;
      
      // Draw the current frame from the video on the canvas
      context.drawImage(video.value, 0, 0, canvas.value.width, canvas.value.height);
      
      // Stop the camera preview
      stopCamera();
      photoTaken.value = true;
    };

    const retakePhoto = async () => {
      photoTaken.value = false;
      await startCamera();
    };

    const savePhoto = () => {
      if (!canvas.value) return;
      
      // Convert canvas to blob and emit the captured photo
      canvas.value.toBlob((blob) => {
        const file = new File([blob], `cocoa-${Date.now()}.jpg`, { type: 'image/jpeg' });
        emit('capture', file);
      }, 'image/jpeg', 0.9);
    };

    // Lifecycle hooks
    onMounted(async () => {
      await startCamera();
    });

    onBeforeUnmount(() => {
      stopCamera();
    });

    return {
      video,
      canvas,
      photoTaken,
      isLoading,
      isCameraReady,
      hasError,
      error,
      capturePhoto,
      retakePhoto,
      savePhoto
    };
  }
};
</script>

<style scoped>
.camera-preview {
  width: 100%;
  height: 300px;
  background-color: #000;
  border-radius: 0.5rem;
  overflow: hidden;
  position: relative;
}

.camera-preview video,
.camera-preview canvas {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
</style>
