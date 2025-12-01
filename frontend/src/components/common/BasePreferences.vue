<template>
  <div :class="['base-preferences', containerClass]">
    <!-- Header -->
    <div v-if="showHeader" class="flex items-center gap-3 mb-6">
      <div class="p-2 bg-green-100 rounded-xl">
        <slot name="header-icon">
          <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
        </slot>
      </div>
      <h3 class="text-2xl font-bold text-gray-900">{{ title }}</h3>
    </div>

    <!-- Content -->
    <div class="space-y-5">
      <slot name="content" :value="modelValue" :update="updateValue">
        <!-- Default content can be provided via props or slots -->
      </slot>
    </div>

    <!-- Footer Actions -->
    <div v-if="showActions || $slots.actions" class="mt-6 flex gap-3">
      <slot name="actions">
        <button
          v-if="showSaveButton"
          @click="handleSave"
          class="bg-green-600 hover:bg-green-700 text-white px-6 py-3 rounded-xl transition-all duration-200 flex items-center gap-2"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
          </svg>
          {{ saveButtonText }}
        </button>
        <button
          v-if="showResetButton"
          @click="handleReset"
          class="bg-gray-500 hover:bg-gray-600 text-white px-6 py-3 rounded-xl transition-all duration-200"
        >
          {{ resetButtonText }}
        </button>
      </slot>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  modelValue: {
    type: Object,
    required: true,
    default: () => ({})
  },
  title: {
    type: String,
    required: true
  },
  showHeader: {
    type: Boolean,
    default: true
  },
  showActions: {
    type: Boolean,
    default: true
  },
  showSaveButton: {
    type: Boolean,
    default: true
  },
  showResetButton: {
    type: Boolean,
    default: false
  },
  saveButtonText: {
    type: String,
    default: 'Guardar'
  },
  resetButtonText: {
    type: String,
    default: 'Restablecer'
  },
  containerClass: {
    type: String,
    default: 'bg-white rounded-2xl border-2 border-gray-200 p-8 shadow-lg'
  }
})

const emit = defineEmits(['update:modelValue', 'save', 'reset'])

const updateValue = (key, value) => {
  const updated = { ...props.modelValue, [key]: value }
  emit('update:modelValue', updated)
}

const handleSave = () => {
  emit('save', props.modelValue)
}

const handleReset = () => {
  emit('reset')
}
</script>

<style scoped>
.base-preferences {
  @apply w-full;
}
</style>

