<template>
  <BaseStatsCard
    :title="title"
    :value="value"
    :icon="icon"
    :trend="trendData"
    :color="variant"
    :format="format"
    :loading="loading"
  />
</template>

<script setup>
import { computed } from 'vue'
import BaseStatsCard from '@/components/common/BaseStatsCard.vue'

const props = defineProps({
  title: {
    type: String,
    required: true
  },
  value: {
    type: [String, Number],
    required: true
  },
  change: {
    type: Number,
    default: null
  },
  icon: {
    type: [String, Object],
    required: true
  },
  variant: {
    type: String,
    default: 'default',
    validator: (value) => ['default', 'success', 'warning', 'danger', 'info'].includes(value)
  },
  format: {
    type: String,
    default: 'number',
    validator: (value) => ['number', 'currency', 'percentage'].includes(value)
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const trendData = computed(() => {
  if (props.change === null || props.change === undefined) {
    return null
  }
  return {
    value: props.change,
    label: `${Math.abs(props.change)}% desde el mes pasado`
  }
})
</script>
