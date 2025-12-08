<template>
  <div class="camera-capture">
    <!-- Camera Container with Professional Styling -->
    <div class="camera-container">
      <!-- Camera Preview with Enhanced Styling -->
      <div class="camera-preview-container">
        <div class="camera-preview" :class="{ 'border-red-500': hasError, 'border-green-500': isCameraReady }">
          <!-- Loading State -->
          <div v-if="isLoading" class="camera-loading">
            <div class="loading-spinner">
              <svg class="animate-spin" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            </div>
            <p class="loading-text">Inicializando cámara...</p>
          </div>

          <!-- Camera Feed -->
          <video
            v-show="!photoTaken && !isLoading"
            ref="video"
            class="camera-feed"
            autoplay
            playsinline
          ></video>

          <!-- Captured Photo Preview -->
          <canvas
            v-show="photoTaken"
            ref="canvas"
            class="camera-feed"
          ></canvas>

          <!-- Camera Overlay with Composition Guides -->
          <div v-if="!photoTaken && !isLoading" class="camera-overlay">
            <div class="composition-frame">
              <div class="corner-guide top-left"></div>
              <div class="corner-guide top-right"></div>
              <div class="corner-guide bottom-left"></div>
              <div class="corner-guide bottom-right"></div>
            </div>
            <div class="center-indicator">
              <div class="center-dot"></div>
            </div>
          </div>

          <!-- Camera Status Indicator -->
          <div class="camera-status">
            <div v-if="isCameraReady" class="status-indicator ready">
              <svg class="status-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
              </svg>
              <span>Cámara lista</span>
            </div>
            <div v-else-if="hasError" class="status-indicator error">
              <svg class="status-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
              </svg>
              <span>Error de cámara</span>
            </div>
          </div>
        </div>

        <!-- Camera Info Bar -->
        <div class="camera-info">
          <div class="info-item">
            <svg class="info-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"></path>
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z"></path>
            </svg>
            <span>Resolución HD</span>
          </div>
          <div class="info-item">
            <svg class="info-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z"></path>
            </svg>
            <span>Auto-enfoque</span>
          </div>
        </div>
      </div>

      <!-- Enhanced Camera Controls -->
      <div class="camera-controls">
        <!-- Capture Button -->
        <button
          v-if="!photoTaken"
          @click="capturePhoto"
          type="button"
          class="capture-button"
          :disabled="isLoading || !isCameraReady"
          :class="{ 'disabled': isLoading || !isCameraReady }"
        >
          <div class="capture-button-inner">
            <svg class="capture-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"></path>
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z"></path>
            </svg>
          </div>
        </button>

        <!-- Photo Actions -->
        <div v-if="photoTaken" class="photo-actions">
          <button
            @click="retakePhoto"
            type="button"
            class="action-button retake"
          >
            <svg class="action-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
            </svg>
            <span>Retomar</span>
          </button>

          <button
            @click="savePhoto"
            type="button"
            class="action-button save"
          >
            <svg class="action-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
            </svg>
            <span>Usar foto</span>
          </button>
        </div>
      </div>

      <!-- Error Display -->
      <div v-if="error" class="error-display">
        <div class="error-content">
          <svg class="error-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"></path>
          </svg>
          <div class="error-text">
            <h4 class="error-title">Error de cámara</h4>
            <p class="error-message">{{ error }}</p>
          </div>
          <button @click="retryCamera" type="button" class="retry-button">
            <svg class="retry-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
            </svg>
            Reintentar
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
// 1. Vue core
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'

// Emits
const emit = defineEmits(['capture'])

// State
const video = ref(null)
const canvas = ref(null)
const stream = ref(null)
const photoTaken = ref(false)
const isLoading = ref(true)
const isCameraReady = ref(false)
const hasError = ref(false)
const error = ref('')

// Functions
const startCamera = async () => {
  try {
    isLoading.value = true
    error.value = ''
    hasError.value = false
    
    if (stream.value) {
      stopCamera()
    }

    stream.value = await navigator.mediaDevices.getUserMedia({
      video: {
        width: { ideal: 1280 },
        height: { ideal: 720 },
        facingMode: 'environment'
      },
      audio: false
    })

    if (video.value) {
      video.value.srcObject = stream.value
      await new Promise((resolve) => {
        if (video.value) {
          video.value.onloadedmetadata = () => {
            video.value?.play()
            resolve()
          }
        }
      })
      isCameraReady.value = true
    }
  } catch (err) {
    error.value = 'No se pudo acceder a la cámara. Asegúrate de otorgar los permisos necesarios.'
    hasError.value = true
  } finally {
    isLoading.value = false
  }
}

const stopCamera = () => {
  if (stream.value) {
    const tracks = stream.value.getTracks()
    for (const track of tracks) {
      track.stop()
    }
    stream.value = null
  }
  isCameraReady.value = false
}

const capturePhoto = () => {
  if (!video.value || !canvas.value) return

  const context = canvas.value.getContext('2d')
  canvas.value.width = video.value.videoWidth
  canvas.value.height = video.value.videoHeight
  
  context.drawImage(video.value, 0, 0, canvas.value.width, canvas.value.height)
  
  // Emitir la foto inmediatamente después de capturarla
  canvas.value.toBlob((blob) => {
    if (blob) {
      const file = new File([blob], `cocoa-${Date.now()}.jpg`, { type: 'image/jpeg' })
      emit('capture', file)
      
      // Auto-resetear después de un breve delay para tomar otra foto
      setTimeout(async () => {
        photoTaken.value = false
        await startCamera()
      }, 1500) // 1.5 segundos para que el usuario vea la foto
    }
  }, 'image/jpeg', 0.9)
  
  stopCamera()
  photoTaken.value = true
}

const retakePhoto = async () => {
  photoTaken.value = false
  await startCamera()
}

const savePhoto = async () => {
  // La foto ya fue emitida en capturePhoto, solo resetear para tomar otra
  if (!canvas.value) return
  
  photoTaken.value = false
  await startCamera()
}

const retryCamera = async () => {
  await startCamera()
}

// Lifecycle
onMounted(async () => {
  await startCamera()
})

onBeforeUnmount(() => {
  stopCamera()
})
</script>

<style scoped>
/* Estilos personalizados necesarios para el diseño de la cámara */
.camera-capture {
  width: 100%;
}

.camera-container {
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
  border-radius: 1rem;
  padding: 1.5rem;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  border: 1px solid #e2e8f0;
}

.camera-preview-container {
  position: relative;
  margin-bottom: 1.5rem;
}

.camera-preview {
  width: 100%;
  height: 400px;
  background: linear-gradient(45deg, #1a202c 0%, #2d3748 100%);
  border-radius: 1rem;
  overflow: hidden;
  position: relative;
  border: 3px solid #e2e8f0;
  transition: all 0.3s ease;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
}

.camera-preview.border-green-500 {
  border-color: #10b981;
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.1);
}

.camera-preview.border-red-500 {
  border-color: #ef4444;
  box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1);
}

.camera-feed {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.camera-loading {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
  color: white;
}

.loading-spinner {
  width: 3rem;
  height: 3rem;
  margin: 0 auto 1rem;
}

.loading-spinner svg {
  width: 100%;
  height: 100%;
  color: #10b981;
}

.loading-text {
  font-size: 0.875rem;
  font-weight: 500;
  opacity: 0.9;
}

.camera-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
}

.composition-frame {
  position: absolute;
  top: 10%;
  left: 10%;
  right: 10%;
  bottom: 10%;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 0.5rem;
}

.corner-guide {
  position: absolute;
  width: 20px;
  height: 20px;
  border: 2px solid rgba(255, 255, 255, 0.6);
}

.top-left {
  top: -2px;
  left: -2px;
  border-right: none;
  border-bottom: none;
  border-top-left-radius: 0.5rem;
}

.top-right {
  top: -2px;
  right: -2px;
  border-left: none;
  border-bottom: none;
  border-top-right-radius: 0.5rem;
}

.bottom-left {
  bottom: -2px;
  left: -2px;
  border-right: none;
  border-top: none;
  border-bottom-left-radius: 0.5rem;
}

.bottom-right {
  bottom: -2px;
  right: -2px;
  border-left: none;
  border-top: none;
  border-bottom-right-radius: 0.5rem;
}

.center-indicator {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

.center-dot {
  width: 8px;
  height: 8px;
  background: rgba(255, 255, 255, 0.8);
  border-radius: 50%;
}

.camera-status {
  position: absolute;
  top: 1rem;
  right: 1rem;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  border-radius: 2rem;
  font-size: 0.75rem;
  font-weight: 500;
  backdrop-filter: blur(10px);
}

.status-indicator.ready {
  background: #065f46;
  color: #ffffff;
}

.status-indicator.error {
  background: #b91c1c;
  color: #ffffff;
}

.status-icon {
  width: 1rem;
  height: 1rem;
}

.camera-info {
  display: flex;
  justify-content: center;
  gap: 2rem;
  margin-top: 1rem;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #64748b;
  font-size: 0.875rem;
  font-weight: 500;
}

.info-icon {
  width: 1.25rem;
  height: 1.25rem;
}

.camera-controls {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
}

.capture-button {
  width: 5rem;
  height: 5rem;
  border-radius: 50%;
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  border: 4px solid white;
  box-shadow: 0 10px 25px -5px rgba(239, 68, 68, 0.4);
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
}

.capture-button:hover:not(.disabled) {
  transform: scale(1.05);
  box-shadow: 0 15px 30px -5px rgba(239, 68, 68, 0.5);
}

.capture-button:active:not(.disabled) {
  transform: scale(0.95);
}

.capture-button.disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.capture-button-inner {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
}

.capture-icon {
  width: 2rem;
  height: 2rem;
  color: white;
}

.photo-actions {
  display: flex;
  gap: 1rem;
}

.action-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border-radius: 0.75rem;
  font-weight: 500;
  transition: all 0.3s ease;
  border: none;
  cursor: pointer;
}

.action-button.retake {
  background: #f1f5f9;
  color: #475569;
  border: 1px solid #e2e8f0;
}

.action-button.retake:hover {
  background: #e2e8f0;
  transform: translateY(-1px);
}

.action-button.save {
  background: linear-gradient(135deg, #047857 0%, #065f46 100%);
  color: #ffffff;
  box-shadow: 0 4px 14px 0 rgba(16, 185, 129, 0.4);
}

.action-button.save:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 20px 0 rgba(16, 185, 129, 0.5);
}

.action-icon {
  width: 1.25rem;
  height: 1.25rem;
}

.error-display {
  margin-top: 1.5rem;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 0.75rem;
  padding: 1.5rem;
}

.error-content {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.error-icon {
  width: 2rem;
  height: 2rem;
  color: #dc2626;
  flex-shrink: 0;
}

.error-text {
  flex: 1;
}

.error-title {
  font-weight: 600;
  color: #991b1b;
  margin: 0 0 0.25rem 0;
}

.error-message {
  color: #7f1d1d;
  margin: 0;
  font-size: 0.875rem;
}

.retry-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: #dc2626;
  color: white;
  border: none;
  border-radius: 0.5rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

.retry-button:hover {
  background: #b91c1c;
  transform: translateY(-1px);
}

.retry-icon {
  width: 1rem;
  height: 1rem;
}

@media (max-width: 640px) {
  .camera-preview {
    height: 300px;
  }
  
  .capture-button {
    width: 4rem;
    height: 4rem;
  }
  
  .camera-info {
    flex-direction: column;
    gap: 1rem;
  }
  
  .photo-actions {
    flex-direction: column;
    width: 100%;
  }
  
  .action-button {
    justify-content: center;
  }
}
</style>
