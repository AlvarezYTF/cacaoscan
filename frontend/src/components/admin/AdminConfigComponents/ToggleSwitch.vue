<template>
  <div class="mb-4">
    <div class="flex items-center justify-between">
      <div class="flex-1">
        <label v-if="label" :for="id" class="block text-sm font-medium text-gray-700">
          {{ label }}
          <span v-if="required" class="text-red-500">*</span>
        </label>
        <p v-if="description" class="text-sm text-gray-500 mt-1">{{ description }}</p>
      </div>
      <button
        :id="id"
        type="button"
        :class="[
          'relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 transition-colors duration-200 ease-in-out',
          'focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2',
          modelValue ? 'bg-green-600 border-green-600' : 'bg-gray-200 border-gray-300',
          disabled ? 'opacity-50 cursor-not-allowed' : ''
        ]"
        role="switch"
        :aria-checked="modelValue"
        :disabled="disabled"
        @click="toggle"
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

<script>
export default {
  name: 'ToggleSwitch',
  props: {
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
    }
  },
  emits: ['update:modelValue'],
  setup(props, { emit }) {
    const id = `toggle-${Math.random().toString(36).substr(2, 9)}`
    
    const toggle = () => {
      if (!props.disabled) {
        emit('update:modelValue', !props.modelValue)
      }
    }
    
    return { id, toggle }
  }
}
</script>

