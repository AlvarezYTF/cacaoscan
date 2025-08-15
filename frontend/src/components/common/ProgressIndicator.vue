<template>
  <div v-if="show" class="space-y-2">
    <div class="flex justify-between text-sm text-gray-600">
      <span>{{ label || 'Procesando...' }}</span>
      <span>{{ progress }}%</span>
    </div>
    <div class="w-full bg-gray-200 rounded-full h-2.5">
      <div
        class="bg-green-600 h-2.5 rounded-full transition-all duration-300"
        :style="{ width: `${progress}%` }"
      ></div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ProgressIndicator',
  props: {
    progress: {
      type: Number,
      required: true,
      validator: value => value >= 0 && value <= 100
    },
    label: {
      type: String,
      default: ''
    },
    show: {
      type: Boolean,
      default: true
    }
  }
}
</script>
