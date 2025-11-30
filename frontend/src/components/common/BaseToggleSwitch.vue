<template>
  <div class="base-toggle-switch" :class="containerClass">
    <div class="flex items-center justify-between">
      <div class="flex-1">
        <label v-if="label" :for="fieldId" class="block text-sm font-medium text-gray-700">
          {{ label }}
          <span v-if="required" class="text-red-500">*</span>
        </label>
        <p v-if="description" class="text-sm text-gray-500 mt-1">{{ description }}</p>
      </div>
      <button
        :id="fieldId"
        ref="toggleButton"
        type="button"
        role="switch"
        :aria-checked="modelValue ? 'true' : 'false'"
        :aria-label="ariaLabel"
        :class="[
          'relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 transition-colors duration-200 ease-in-out',
          'focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2',
          modelValue ? activeClasses : inactiveClasses,
          disabled ? 'opacity-50 cursor-not-allowed' : ''
        ]"
        :disabled="disabled"
        @click="handleToggle"
      >
        <span
          :class="[
            'pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out',
            modelValue ? 'translate-x-5' : 'translate-x-0'
          ]"
        />
      </button>
    </div>
    <p v-if="error" class="mt-1 text-sm text-red-600">{{ error }}</p>
    <p v-if="helperText && !error" class="mt-1 text-sm text-gray-500">{{ helperText }}</p>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  label: {
    type: String,
    default: ''
  },
  description: {
    type: String,
    default: ''
  },
  required: {
    type: Boolean,
    default: false
  },
  disabled: {
    type: Boolean,
    default: false
  },
  error: {
    type: String,
    default: ''
  },
  helperText: {
    type: String,
    default: ''
  },
  size: {
    type: String,
    default: 'md',
    validator: (value) => ['sm', 'md', 'lg'].includes(value)
  },
  color: {
    type: String,
    default: 'green',
    validator: (value) => ['green', 'blue', 'purple', 'red'].includes(value)
  },
  containerClass: {
    type: String,
    default: 'mb-4'
  }
})

const emit = defineEmits(['update:modelValue', 'change'])

// Generate unique field ID
const generateSecureId = () => {
  if (typeof crypto !== 'undefined' && crypto.randomUUID) {
    return crypto.randomUUID()
  }
  if (typeof crypto !== 'undefined' && crypto.getRandomValues) {
    const randomArray = new Uint32Array(1)
    crypto.getRandomValues(randomArray)
    return randomArray[0].toString(36)
  }
  return Date.now().toString(36)
}

const fieldId = `toggle-${generateSecureId()}`
const toggleButton = ref(null)

const ariaLabel = computed(() => {
  return props.label || 'Toggle switch'
})

const activeClasses = computed(() => {
  const colorMap = {
    green: 'bg-green-600 border-green-600',
    blue: 'bg-blue-600 border-blue-600',
    purple: 'bg-purple-600 border-purple-600',
    red: 'bg-red-600 border-red-600'
  }
  return colorMap[props.color] || colorMap.green
})

const inactiveClasses = computed(() => {
  return 'bg-gray-200 border-gray-300'
})

const updateAriaChecked = (value) => {
  if (!toggleButton.value) {
    return
  }
  toggleButton.value.setAttribute('aria-checked', value ? 'true' : 'false')
}

const handleToggle = () => {
  if (!props.disabled) {
    const newValue = !props.modelValue
    emit('update:modelValue', newValue)
    emit('change', newValue)
  }
}

onMounted(() => {
  updateAriaChecked(props.modelValue)
})

watch(() => props.modelValue, (value) => {
  updateAriaChecked(value)
})
</script>

<style scoped>
.base-toggle-switch {
  @apply w-full;
}
</style>

