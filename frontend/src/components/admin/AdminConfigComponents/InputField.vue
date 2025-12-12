<template>
  <div class="mb-4">
    <label v-if="label" :for="id" class="block text-sm font-medium text-gray-700 mb-2">
      {{ label }}
      <span v-if="required" class="text-red-500">*</span>
    </label>
    <input
      :id="id"
      :type="type"
      :value="modelValue"
      :placeholder="placeholder"
      :required="required"
      :disabled="disabled"
      :class="[
        'block w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm',
        'focus:ring-2 focus:ring-green-500 focus:border-green-500 transition-all',
        'disabled:bg-gray-100 disabled:cursor-not-allowed',
        error ? 'border-red-500 focus:ring-red-500' : ''
      ]"
      @input="$emit('update:modelValue', $event.target.value)"
      @blur="$emit('blur', $event)"
    />
    <p v-if="error" class="mt-1 text-sm text-red-600">{{ error }}</p>
    <p v-if="helperText && !error" class="mt-1 text-sm text-gray-500">{{ helperText }}</p>
  </div>
</template>

<script>
export default {
  name: 'InputField',
  props: {
    modelValue: {
      type: [String, Number],
      default: ''
    },
    label: {
      type: String,
      default: ''
    },
    type: {
      type: String,
      default: 'text'
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
      default: ''
    },
    helperText: {
      type: String,
      default: ''
    }
  },
  emits: ['update:modelValue', 'blur'],
  setup(props) {
    // Generate a unique ID for the input field using cryptographically secure random values
    // Note: Using crypto.getRandomValues() instead of Math.random() for better security
    // This generates a UI identifier, not for cryptographic purposes, but using secure RNG
    // is a best practice to avoid security warnings from static analysis tools
    const randomArray = new Uint32Array(1)
    crypto.getRandomValues(randomArray)
    const id = `input-${randomArray[0].toString(36)}`
    return { id }
  }
}
</script>

