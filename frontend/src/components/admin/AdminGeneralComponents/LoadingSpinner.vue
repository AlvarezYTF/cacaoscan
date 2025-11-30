<template>
  <BaseSpinner
    :size="size"
    :color="color"
    :stroke-width="strokeWidth"
    :container-class="className"
  />
</template>

<script setup>
import BaseSpinner from '@/components/common/BaseSpinner.vue'

defineProps({
  size: {
    type: String,
    default: 'md',
    validator: (value) => ['xs', 'sm', 'md', 'lg', 'xl'].includes(value)
  },
  color: {
    type: String,
    default: 'white',
    validator: (value) => ['white', 'gray', 'blue', 'green', 'red', 'yellow', 'purple'].includes(value)
  },
  strokeWidth: {
    type: String,
    default: '4'
  },
  className: {
    type: String,
    default: ''
  }
})
</script>
