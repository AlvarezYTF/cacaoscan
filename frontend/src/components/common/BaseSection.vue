<template>
  <section :class="sectionClass" :id="id">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 sm:py-16 lg:py-20">
      <!-- Section header -->
      <div v-if="title || subtitle || $slots.header" class="text-center mb-12">
        <slot name="header">
          <h2 v-if="title" class="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">{{ title }}</h2>
          <p v-if="subtitle" class="text-lg text-gray-600 max-w-3xl mx-auto">{{ subtitle }}</p>
        </slot>
      </div>

      <!-- Section content -->
      <div :class="contentClass">
        <slot />
      </div>
    </div>
  </section>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  title: {
    type: String,
    default: ''
  },
  subtitle: {
    type: String,
    default: ''
  },
  variant: {
    type: String,
    default: 'default',
    validator: (value) => ['default', 'hero', 'features', 'about', 'dark', 'light'].includes(value)
  },
  id: {
    type: String,
    default: null
  },
  fullWidth: {
    type: Boolean,
    default: false
  }
})

const sectionClass = computed(() => {
  const baseClasses = 'w-full'
  
  const variantClasses = {
    default: 'bg-white',
    hero: 'bg-gradient-to-br from-green-50 to-blue-50',
    features: 'bg-gray-50',
    about: 'bg-white',
    dark: 'bg-gray-900 text-white',
    light: 'bg-white'
  }

  return `${baseClasses} ${variantClasses[props.variant]}`
})

const contentClass = computed(() => {
  return props.fullWidth ? 'w-full' : ''
})
</script>

<style scoped>
/* Additional styles if needed */
</style>

