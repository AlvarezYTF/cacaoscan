<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <div class="bg-white shadow-sm border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div class="flex items-center justify-between">
          <div class="flex items-center space-x-4">
            <button
              v-if="showBackButton"
              @click="handleBack"
              class="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
            >
              <svg class="h-5 w-5 mr-2" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M9.707 16.707a1 1 0 01-1.414 0l-6-6a1 1 0 010-1.414l6-6a1 1 0 011.414 1.414L5.414 9H17a1 1 0 110 2H5.414l4.293 4.293a1 1 0 010 1.414z" clip-rule="evenodd" />
              </svg>
              Volver
            </button>
            <h1 v-if="title" class="text-2xl font-bold text-gray-900">{{ title }}</h1>
            <slot name="header" />
          </div>
        </div>
      </div>
    </div>

    <!-- Content -->
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div class="bg-white shadow rounded-lg p-6">
        <slot />
      </div>
    </div>

    <!-- Footer -->
    <div v-if="$slots.footer" class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
      <slot name="footer" />
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const props = defineProps({
  title: {
    type: String,
    default: ''
  },
  showBackButton: {
    type: Boolean,
    default: false
  },
  backRoute: {
    type: String,
    default: null
  }
})

const router = useRouter()

const handleBack = () => {
  if (props.backRoute) {
    router.push(props.backRoute)
  } else {
    router.back()
  }
}
</script>

<style scoped>
/* Additional styles if needed */
</style>

