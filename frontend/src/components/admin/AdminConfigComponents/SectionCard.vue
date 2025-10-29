<template>
  <div class="bg-white rounded-xl border border-gray-200 shadow-sm p-6 mb-6">
    <div class="flex items-center mb-4">
      <div class="bg-green-100 p-2 rounded-lg mr-3">
        <component :is="icon" v-if="icon" class="w-5 h-5 text-green-600" />
      </div>
      <div>
        <h3 class="text-lg font-semibold text-gray-900">
          {{ title }}
        </h3>
        <p v-if="description" class="text-sm text-gray-600 mt-1">{{ description }}</p>
      </div>
    </div>
    
    <slot />
  </div>
</template>

<script>
export default {
  name: 'SectionCard',
  props: {
    title: {
      type: String,
      required: true
    },
    description: {
      type: String,
      default: ''
    },
    icon: {
      type: Object,
      default: null
    }
  }
}
</script>

