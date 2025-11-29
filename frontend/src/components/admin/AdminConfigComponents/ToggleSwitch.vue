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
        ref="toggleButton"
        type="button"
        role="switch"
        aria-checked="false"
        :aria-label="ariaLabel"
        :class="[
          'relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 transition-colors duration-200 ease-in-out',
          'focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2',
          modelValue ? 'bg-green-600 border-green-600' : 'bg-gray-200 border-gray-300',
          disabled ? 'opacity-50 cursor-not-allowed' : ''
        ]"
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
import { computed, onMounted, ref, watch } from 'vue'

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
    // Generate a unique ID using cryptographically secure random generation
    const generateSecureId = () => {
      // Use crypto.randomUUID() if available (modern browsers)
      if (typeof crypto !== 'undefined' && crypto.randomUUID) {
        return crypto.randomUUID()
      }
      // Fallback to crypto.getRandomValues() for older browsers
      if (typeof crypto !== 'undefined' && crypto.getRandomValues) {
        const randomArray = new Uint32Array(1)
        crypto.getRandomValues(randomArray)
        return randomArray[0].toString(36)
      }
      // Last resort: use timestamp (not cryptographically secure but better than Math.random())
      return Date.now().toString(36)
    }
    const id = `toggle-${generateSecureId()}`
    
    const ariaLabel = computed(() => {
      return props.label || 'Toggle switch'
    })

    const toggleButton = ref(null)

    const updateAriaChecked = (value) => {
      if (!toggleButton.value) {
        return
      }
      toggleButton.value.setAttribute('aria-checked', value ? 'true' : 'false')
    }

    onMounted(() => {
      updateAriaChecked(props.modelValue)
    })

    watch(() => props.modelValue, (value) => {
      updateAriaChecked(value)
    })
    
    const toggle = () => {
      if (!props.disabled) {
        emit('update:modelValue', !props.modelValue)
      }
    }
    
    return { id, toggle, ariaLabel, toggleButton }
  }
}
</script>

