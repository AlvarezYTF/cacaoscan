<template>
  <div 
    class="bg-white rounded-xl shadow-lg border border-gray-200"
    :class="containerClass"
  >
    <div class="flex items-center gap-4 p-6">
      <div class="flex-1 relative">
        <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
          <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
          </svg>
        </div>
        <input 
          type="text" 
          :value="modelValue"
          @input="handleInput"
          :placeholder="placeholder"
          :disabled="disabled"
          class="w-full pl-12 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500 transition-all duration-200"
          :class="inputClass"
          :data-cy="searchCy || 'search-input'"
        />
        <button
          v-if="showClearButton && modelValue"
          @click="handleClear"
          type="button"
          class="absolute inset-y-0 right-0 pr-4 flex items-center text-gray-400 hover:text-gray-600"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
          </svg>
        </button>
      </div>
      <div v-if="$slots.actions" class="flex-shrink-0">
        <slot name="actions"></slot>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  placeholder: {
    type: String,
    default: 'Buscar...'
  },
  disabled: {
    type: Boolean,
    default: false
  },
  showClearButton: {
    type: Boolean,
    default: true
  },
  containerClass: {
    type: String,
    default: ''
  },
  inputClass: {
    type: String,
    default: 'bg-gray-50'
  },
  searchCy: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['update:modelValue', 'clear', 'input'])

const handleInput = (event) => {
  const value = event.target.value
  emit('update:modelValue', value)
  emit('input', value)
}

const handleClear = () => {
  emit('update:modelValue', '')
  emit('clear')
}
</script>

<style scoped>
/* Styles handled by Tailwind classes */
</style>

