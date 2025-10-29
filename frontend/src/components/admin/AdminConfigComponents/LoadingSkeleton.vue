<template>
  <div class="animate-pulse">
    <div class="space-y-4">
      <div v-if="showTitle" class="h-4 bg-gray-200 rounded w-1/4"></div>
      <div class="space-y-2">
        <div v-for="n in lines" :key="n" class="h-4 bg-gray-200 rounded" :class="widthClasses[n % widthClasses.length]"></div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'LoadingSkeleton',
  props: {
    lines: {
      type: Number,
      default: 3
    },
    showTitle: {
      type: Boolean,
      default: true
    }
  },
  setup() {
    const widthClasses = ['w-full', 'w-5/6', 'w-4/6', 'w-3/4']
    return { widthClasses }
  }
}
</script>

<style scoped>
@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
</style>

