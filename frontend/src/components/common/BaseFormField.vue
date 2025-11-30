
<template>
  <div class="form-field" :class="fieldClass">
    <label 
      v-if="label" 
      :for="fieldId"
      class="block text-sm font-semibold text-gray-700 mb-2"
      :class="labelClass"
    >
      {{ label }}
      <span v-if="required" class="text-red-500 ml-1">*</span>
    </label>

    <!-- Input Text -->
    <input
      v-if="type === 'text' || type === 'email' || type === 'tel'"
      :id="fieldId"
      :name="name"
      :type="type"
      :value="modelValue"
      :placeholder="placeholder"
      :required="required"
      :disabled="disabled"
      :autocomplete="autocomplete"
      :class="inputClass"
      @input="handleInput"
      @blur="handleBlur"
      @focus="handleFocus"
    />

    <!-- Textarea -->
    <textarea
      v-else-if="type === 'textarea'"
      :id="fieldId"
      :name="name"
      :value="modelValue"
      :placeholder="placeholder"
      :required="required"
      :disabled="disabled"
      :rows="rows"
      :class="inputClass"
      @input="handleInput"
      @blur="handleBlur"
      @focus="handleFocus"
    ></textarea>

    <!-- Select -->
    <select
      v-else-if="type === 'select'"
      :id="fieldId"
      :name="name"
      :value="modelValue"
      :required="required"
      :disabled="disabled"
      :class="inputClass"
      @change="handleChange"
      @blur="handleBlur"
      @focus="handleFocus"
    >
      <option v-if="placeholder" value="">{{ placeholder }}</option>
      <option 
        v-for="option in options" 
        :key="getOptionValue(option)" 
        :value="getOptionValue(option)"
      >
        {{ getOptionLabel(option) }}
      </option>
    </select>

    <!-- Date Input -->
    <input
      v-else-if="type === 'date'"
      :id="fieldId"
      :name="name"
      type="date"
      :value="modelValue"
      :required="required"
      :disabled="disabled"
      :min="min"
      :max="max"
      :class="inputClass"
      @input="handleInput"
      @blur="handleBlur"
      @focus="handleFocus"
    />

    <!-- Password Input -->
    <div v-else-if="type === 'password'" class="relative">
      <input
        :id="fieldId"
        :name="name"
        :type="showPassword ? 'text' : 'password'"
        :value="modelValue"
        :placeholder="placeholder"
        :required="required"
        :disabled="disabled"
        :autocomplete="autocomplete"
        :class="inputClass"
        @input="handleInput"
        @blur="handleBlur"
        @focus="handleFocus"
      />
      <button
        v-if="showPasswordToggle"
        type="button"
        @click="togglePassword"
        class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700"
        :aria-label="showPassword ? 'Ocultar contraseña' : 'Mostrar contraseña'"
      >
        <i :class="showPassword ? 'fas fa-eye-slash' : 'fas fa-eye'"></i>
      </button>
    </div>

    <!-- Custom Content Slot (for custom inputs) -->
    <slot v-else :fieldId="fieldId"></slot>

    <!-- Error Message -->
    <p v-if="error" class="text-red-600 text-xs mt-1">
      {{ error }}
    </p>

    <!-- Help Text -->
    <p v-if="helpText && !error" class="text-gray-500 text-xs mt-1">
      {{ helpText }}
    </p>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'

const props = defineProps({
  modelValue: {
    type: [String, Number, Boolean],
    default: ''
  },
  name: {
    type: String,
    required: true
  },
  label: {
    type: String,
    default: ''
  },
  type: {
    type: String,
    default: 'text',
    validator: (value) => ['text', 'email', 'tel', 'password', 'textarea', 'select', 'date'].includes(value)
  },
  placeholder: {
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
    default: null
  },
  helpText: {
    type: String,
    default: ''
  },
  autocomplete: {
    type: String,
    default: ''
  },
  options: {
    type: Array,
    default: () => []
  },
  optionValue: {
    type: String,
    default: 'value'
  },
  optionLabel: {
    type: String,
    default: 'label'
  },
  rows: {
    type: Number,
    default: 4
  },
  min: {
    type: String,
    default: null
  },
  max: {
    type: String,
    default: null
  },
  showPasswordToggle: {
    type: Boolean,
    default: false
  },
  fieldClass: {
    type: String,
    default: ''
  },
  labelClass: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['update:modelValue', 'blur', 'focus', 'change'])

/**
 * Generates a unique field ID using cryptographically secure methods
 * SonarQube S2245: Uses crypto.getRandomValues() instead of Math.random() for security
 */
const generateFieldId = () => {
  // Use cryptographically secure random number generator for unique ID
  if (typeof crypto !== 'undefined' && crypto.randomUUID) {
    return `field-${crypto.randomUUID()}`
  }
  if (typeof crypto !== 'undefined' && crypto.getRandomValues) {
    const array = new Uint8Array(9)
    crypto.getRandomValues(array)
    const randomStr = Array.from(array, byte => byte.toString(36)).join('').substring(0, 9)
    return `field-${randomStr}`
  }
  // Fallback: Use timestamp + counter for uniqueness
  const timestamp = Date.now().toString(36)
  const counter = (globalThis.__fieldIdCounter = (globalThis.__fieldIdCounter || 0) + 1)
  return `field-${timestamp}-${counter.toString(36)}`
}

// Generate unique field ID
const fieldId = computed(() => {
  return props.name || generateFieldId()
})

// Password visibility
const showPassword = ref(false)

const togglePassword = () => {
  showPassword.value = !showPassword.value
}

// Input class with error state
const inputClass = computed(() => {
  const baseClasses = 'w-full px-4 py-2.5 border rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500 disabled:bg-gray-100 transition-all duration-200'
  const errorClasses = props.error ? 'border-red-500' : 'border-gray-300'
  return `${baseClasses} ${errorClasses}`
})

// Option helpers
const getOptionValue = (option) => {
  if (typeof option === 'string') {
    return option
  }
  if (typeof option === 'object') {
    return option[props.optionValue] || option.value || option.codigo || option.id
  }
  return option
}

const getOptionLabel = (option) => {
  if (typeof option === 'string') {
    return option
  }
  if (typeof option === 'object') {
    return option[props.optionLabel] || option.label || option.nombre || option.name || String(option)
  }
  return String(option)
}

// Event handlers
const handleInput = (event) => {
  emit('update:modelValue', event.target.value)
}

const handleChange = (event) => {
  emit('update:modelValue', event.target.value)
  emit('change', event.target.value)
}

const handleBlur = (event) => {
  emit('blur', event)
}

const handleFocus = (event) => {
  emit('focus', event)
}
</script>

<style scoped>
.form-field {
  @apply w-full;
}
</style>

