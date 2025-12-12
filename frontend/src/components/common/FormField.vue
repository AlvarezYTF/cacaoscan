<template>
  <div :class="containerClass">
    <label :for="id" class="block text-sm font-semibold text-gray-700 mb-2">
      {{ label }}
      <span v-if="required" class="text-red-500">*</span>
    </label>
    <div class="relative">
      <input
        v-if="type !== 'select'"
        :id="id"
        :name="name"
        :type="type"
        :value="modelValue"
        @input="$emit('update:modelValue', $event.target.value)"
        :autocomplete="autocomplete"
        :required="required"
        :disabled="disabled"
        :placeholder="placeholder"
        :max="max"
        :min="min"
        :class="inputClasses"
      />
      <select
        v-else
        :id="id"
        :name="name"
        :value="modelValue"
        @change="$emit('update:modelValue', $event.target.value)"
        :required="required"
        :disabled="disabled"
        :class="inputClasses"
      >
        <slot name="options">
          <option v-if="loading" value="">Cargando...</option>
          <option v-else-if="options.length === 0" value="">{{ emptyMessage }}</option>
          <option v-for="option in options" :key="getOptionValue(option)" :value="getOptionValue(option)">
            {{ getOptionLabel(option) }}
          </option>
        </slot>
      </select>
      <slot name="suffix"></slot>
    </div>
    <p v-if="error" class="text-red-600 text-xs mt-1">{{ error }}</p>
    <p v-if="hint && !error" class="text-gray-500 text-xs mt-1">{{ hint }}</p>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  id: {
    type: String,
    required: true
  },
  name: {
    type: String,
    default: ''
  },
  label: {
    type: String,
    required: true
  },
  modelValue: {
    type: [String, Number],
    default: ''
  },
  type: {
    type: String,
    default: 'text'
  },
  required: {
    type: Boolean,
    default: false
  },
  disabled: {
    type: Boolean,
    default: false
  },
  placeholder: {
    type: String,
    default: ''
  },
  error: {
    type: String,
    default: ''
  },
  hint: {
    type: String,
    default: ''
  },
  autocomplete: {
    type: String,
    default: ''
  },
  max: {
    type: String,
    default: ''
  },
  min: {
    type: String,
    default: ''
  },
  containerClass: {
    type: String,
    default: ''
  },
  inputClass: {
    type: String,
    default: ''
  },
  hasError: {
    type: Boolean,
    default: false
  },
  options: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  },
  emptyMessage: {
    type: String,
    default: 'No hay opciones disponibles'
  },
  optionValue: {
    type: String,
    default: 'value'
  },
  optionLabel: {
    type: String,
    default: 'label'
  }
})

const emit = defineEmits(['update:modelValue'])

const baseInputClasses = 'w-full px-4 py-2.5 border rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500 disabled:bg-gray-100 transition-all duration-200'

const inputClasses = computed(() => {
  const classes = [baseInputClasses]
  if (props.hasError || props.error) {
    classes.push('border-red-500')
  } else {
    classes.push('border-gray-300')
  }
  if (props.inputClass) {
    classes.push(props.inputClass)
  }
  return classes.join(' ')
})

const getOptionValue = (option) => {
  if (typeof option === 'string' || typeof option === 'number') {
    return option
  }
  return option[props.optionValue] || option.value || option.id || option.codigo
}

const getOptionLabel = (option) => {
  if (typeof option === 'string' || typeof option === 'number') {
    return option
  }
  return option[props.optionLabel] || option.label || option.nombre || option.name
}
</script>

