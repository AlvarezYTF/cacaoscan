<template>
  <BaseStatsCard
    :label="title"
    :value="value"
    :icon="icon"
    :color="color || 'blue'"
    :trend="percentage !== null && percentage !== undefined ? percentage : null"
    trend-label="desde el mes pasado"
  />
</template>

<script setup>
import BaseStatsCard from '@/components/common/BaseStatsCard.vue'

defineProps({
  title: {
    type: String,
    required: true
  },
  value: {
    type: [String, Number],
    required: true
  },
  icon: {
    type: String,
    default: '📊'
  },
  color: {
    type: String,
    default: ''
  },
  percentage: {
    type: Number,
    default: null
  }
})
</script>
  