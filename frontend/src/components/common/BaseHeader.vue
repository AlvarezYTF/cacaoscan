<template>
  <header 
    class="bg-white shadow-sm border-b border-gray-200"
    :class="headerClass"
  >
    <div class="px-4 sm:px-6 lg:px-8 py-4 sm:py-6">
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <!-- Left section: Branding/Title -->
        <div class="flex items-center flex-1 min-w-0">
          <slot name="brand">
            <div v-if="icon || iconSlot" class="flex-shrink-0 mr-3">
              <slot name="icon">
                <component v-if="icon" :is="icon" class="w-6 h-6 text-green-600" />
              </slot>
            </div>
            <div class="min-w-0 flex-1">
              <h1 v-if="title" class="text-xl sm:text-2xl lg:text-3xl font-bold text-gray-900 truncate">
                {{ title }}
              </h1>
              <p v-if="subtitle" class="mt-1 text-sm text-gray-600 truncate">
                {{ subtitle }}
              </p>
              <slot name="subtitle"></slot>
            </div>
          </slot>
        </div>

        <!-- Right section: Actions -->
        <div v-if="$slots.actions || showActions" class="flex items-center gap-3 flex-shrink-0">
          <slot name="actions"></slot>
        </div>
      </div>
    </div>
  </header>
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
  icon: {
    type: [Object, String],
    default: null
  },
  headerClass: {
    type: String,
    default: ''
  },
  showActions: {
    type: Boolean,
    default: false
  }
})

const iconSlot = computed(() => {
  return !!props.icon
})
</script>

<style scoped>
/* Styles handled by Tailwind classes */
</style>

