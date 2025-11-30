<template>
  <div class="app" :class="containerClass">
    <!-- Router view principal -->
    <slot>
      <RouterView />
    </slot>
    
    <!-- Global loading overlay -->
    <GlobalLoader v-if="showGlobalLoader" />
    
    <!-- Session expired modal -->
    <SessionExpiredModal 
      v-if="showSessionModal" 
      ref="sessionExpiredModalRef" 
    />
    
    <!-- Additional global components -->
    <slot name="global"></slot>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { RouterView } from 'vue-router'
import GlobalLoader from '@/components/common/GlobalLoader.vue'
import SessionExpiredModal from '@/components/common/SessionExpiredModal.vue'

defineProps({
  containerClass: {
    type: String,
    default: ''
  },
  showGlobalLoader: {
    type: Boolean,
    default: true
  },
  showSessionModal: {
    type: Boolean,
    default: true
  }
})

const sessionExpiredModalRef = ref(null)

// Expose modal globally if needed
onMounted(() => {
  if (sessionExpiredModalRef.value) {
    globalThis.showSessionExpiredModal = () => {
      if (sessionExpiredModalRef.value) {
        sessionExpiredModalRef.value.show()
      }
    }
  }
})
</script>

<style scoped>
/* App-level styles can be added here */
</style>

