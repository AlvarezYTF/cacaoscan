<template>
  <div class="w-full" :class="containerClass">
    <!-- Label -->
    <label
      v-if="label"
      :for="id"
      class="block text-sm font-medium text-gray-700 mb-1"
      :class="{ 'text-red-600': hasError }"
    >
      {{ label }}
      <span v-if="required" class="text-red-500">*</span>
    </label>

    <!-- Select wrapper -->
    <div class="relative">
      <!-- Prefix icon/slot -->
      <div v-if="$slots.prefix || prefixIcon" class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none z-10">
        <slot name="prefix">
          <component v-if="prefixIcon" :is="prefixIcon" class="h-5 w-5 text-gray-400" />
        </slot>
      </div>

      <!-- Select -->
      <select
        :id="id"
        :value="modelValue"
        :disabled="disabled"
        :required="required"
        :multiple="multiple"
        :class="selectClass"
        @change="handleChange"
        @blur="handleBlur"
        @focus="handleFocus"
        v-bind="$attrs"
      >
        <!-- Placeholder option -->
        <option v-if="placeholder && !multiple" value="" disabled>{{ placeholder }}</option>
        
        <!-- Options slot -->
        <slot>
          <option
            v-for="option in options"
            :key="getOptionValue(option)"
            :value="getOptionValue(option)"
            :disabled="isOptionDisabled(option)"
          >
            {{ getOptionLabel(option) }}
          </option>
        </slot>
      </select>

      <!-- Suffix icon (chevron) -->
      <div v-if="!multiple" class="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
        <slot name="suffix">
          <svg class="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path>
          </svg>
        </slot>
      </div>
    </div>

    <!-- Helper text -->
    <p v-if="helperText && !hasError" class="mt-1 text-xs text-gray-500">{{ helperText }}</p>

    <!-- Error message -->
    <p v-if="error || hasError" class="mt-1 text-xs text-red-600">{{ error || errorMessage }}</p>
  </div>
</template>

<script setup>
import { computed, useSlots } from 'vue'
import { generateSecureId } from '@/utils/security'

const slots = useSlots()

const props = defineProps({
  modelValue: {
    type: [String, Number, Array],
    default: null
  },
  label: {
    type: String,
    default: ''
  },
  options: {
    type: Array,
    default: () => []
  },
  optionValue: {
    type: [String, Function],
    default: 'value'
  },
  optionLabel: {
    type: [String, Function],
    default: 'label'
  },
  optionDisabled: {
    type: [String, Function],
    default: 'disabled'
  },
  placeholder: {
    type: String,
    default: ''
  },
  helperText: {
    type: String,
    default: ''
  },
  error: {
    type: String,
    default: null
  },
  errorMessage: {
    type: String,
    default: null
  },
  required: {
    type: Boolean,
    default: false
  },
  disabled: {
    type: Boolean,
    default: false
  },
  multiple: {
    type: Boolean,
    default: false
  },
  size: {
    type: String,
    default: 'md',
    validator: (value) => ['sm', 'md', 'lg'].includes(value)
  },
  variant: {
    type: String,
    default: 'default',
    validator: (value) => ['default', 'filled', 'outlined'].includes(value)
  },
  prefixIcon: {
    type: [String, Object],
    default: null
  },
  id: {
    type: String,
    default: () => generateSecureId('select')
  }
})

const emit = defineEmits(['update:modelValue', 'change', 'blur', 'focus'])

const hasError = computed(() => !!props.error || !!props.errorMessage)

const selectClass = computed(() => {
  const baseClasses = 'block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500 transition-colors appearance-none bg-white'
  
  const sizeClasses = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-3 py-2 text-sm',
    lg: 'px-4 py-3 text-base'
  }

  const variantClasses = {
    default: 'border',
    filled: 'border-0 bg-gray-100',
    outlined: 'border-2'
  }

  const stateClasses = hasError.value
    ? 'border-red-300 text-red-900 focus:border-red-500 focus:ring-red-500'
    : ''

  const prefixPadding = props.prefixIcon || slots.prefix ? 'pl-10' : ''
  const suffixPadding = props.multiple ? '' : 'pr-10'

  return [
    baseClasses,
    sizeClasses[props.size],
    variantClasses[props.variant],
    stateClasses,
    prefixPadding,
    suffixPadding,
    props.disabled ? 'bg-gray-50 text-gray-500 cursor-not-allowed' : ''
  ].filter(Boolean).join(' ')
})

const containerClass = computed(() => {
  return props.size === 'sm' ? 'text-sm' : ''
})

const getOptionValue = (option) => {
  if (typeof props.optionValue === 'function') {
    return props.optionValue(option)
  }
  return typeof option === 'object' ? option[props.optionValue] : option
}

const getOptionLabel = (option) => {
  if (typeof props.optionLabel === 'function') {
    return props.optionLabel(option)
  }
  return typeof option === 'object' ? option[props.optionLabel] : String(option)
}

const isOptionDisabled = (option) => {
  if (typeof props.optionDisabled === 'function') {
    return props.optionDisabled(option)
  }
  return typeof option === 'object' ? option[props.optionDisabled] : false
}

const handleChange = (event) => {
  const value = props.multiple
    ? Array.from(event.target.selectedOptions, option => option.value)
    : event.target.value
  emit('update:modelValue', value)
  emit('change', event)
}

const handleBlur = (event) => {
  emit('blur', event)
}

const handleFocus = (event) => {
  emit('focus', event)
}
</script>

<style scoped>
/* Additional styles if needed */
</style>

