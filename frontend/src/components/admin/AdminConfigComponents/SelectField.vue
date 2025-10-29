<template>
  <div class="mb-4">
    <label v-if="label" :for="id" class="block text-sm font-medium text-gray-700 mb-2">
      {{ label }}
      <span v-if="required" class="text-red-500">*</span>
    </label>
    <select
      :id="id"
      :value="modelValue"
      :required="required"
      :disabled="disabled"
      :class="[
        'block w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm',
        'focus:ring-2 focus:ring-green-500 focus:border-green-500 transition-all',
        'disabled:bg-gray-100 disabled:cursor-not-allowed',
        error ? 'border-red-500 focus:ring-red-500' : ''
      ]"
      @change="$emit('update:modelValue', $event.target.value)"
    >
      <option value="" disabled>{{ placeholder }}</option>
      <option v-for="option in options" :key="option.value" :value="option.value">
        {{ option.label }}
      </option>
    </select>
    <p v-if="error" class="mt-1 text-sm text-red-600">{{ error }}</p>
    <p v-if="helperText && !error" class="mt-1 text-sm text-gray-500">{{ helperText }}</p>
  </div>
</template>

<script>
export default {
  name: 'SelectField',
  props: {
    modelValue: {
      type: [String, Number],
      default: ''
    },
    label: {
      type: String,
      default: ''
    },
    placeholder: {
      type: String,
      default: 'Selecciona una opción'
    },
    options: {
      type: Array,
      required: true
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
  emits: ['update:modelValue'],
  setup(props) {
    const id = `select-${Math.random().toString(36).substr(2, 9)}`
    return { id }
  }
}
</script>

