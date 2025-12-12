<template>
  <div :class="['base-auth-form', containerClass]">
    <!-- Header -->
    <div v-if="showHeader" class="text-center mb-6">
      <h2 :class="['base-auth-title', titleClass]">
        <slot name="title">{{ title }}</slot>
      </h2>
      <p v-if="subtitle || $slots.subtitle" :class="['base-auth-subtitle', subtitleClass]">
        <slot name="subtitle">{{ subtitle }}</slot>
      </p>
    </div>

    <!-- Form Fields -->
    <form @submit.prevent="handleSubmit" class="space-y-4">
      <slot name="fields" :form-data="modelValue" :errors="errors" :update-field="updateField">
        <!-- Default fields can be provided via props or slots -->
      </slot>

      <!-- Submit Button -->
      <div v-if="showSubmitButton || $slots['submit-button']" class="mt-6">
        <slot name="submit-button">
          <button
            type="submit"
            :disabled="loading || disabled"
            :class="[
              'w-full py-2 rounded-lg font-semibold transition',
              submitButtonClass,
              (loading || disabled) ? 'opacity-50 cursor-not-allowed' : ''
            ]"
          >
            <span v-if="loading" class="flex items-center justify-center gap-2">
              <BaseSpinner size="sm" color="white" />
              {{ loadingText }}
            </span>
            <span v-else>{{ submitButtonText }}</span>
          </button>
        </slot>
      </div>

      <!-- Status Message -->
      <div v-if="statusMessage || $slots['status-message']" class="mt-4">
        <slot name="status-message" :message="statusMessage" :type="statusMessageType">
          <p
            v-if="statusMessage"
            :class="[
              'text-center text-sm',
              statusMessageType === 'success' ? 'text-green-700' : 'text-red-600'
            ]"
          >
            {{ statusMessage }}
          </p>
        </slot>
      </div>
    </form>

    <!-- Footer -->
    <div v-if="showFooter || $slots.footer" class="mt-6">
      <slot name="footer">
        <!-- Default footer content -->
      </slot>
    </div>
  </div>
</template>

<script setup>
import BaseSpinner from './BaseSpinner.vue'

const props = defineProps({
  modelValue: {
    type: Object,
    required: true,
    default: () => ({})
  },
  mode: {
    type: String,
    default: 'login',
    validator: (value) => ['login', 'register', 'reset'].includes(value)
  },
  title: {
    type: String,
    default: ''
  },
  subtitle: {
    type: String,
    default: ''
  },
  showHeader: {
    type: Boolean,
    default: true
  },
  showSubmitButton: {
    type: Boolean,
    default: true
  },
  submitButtonText: {
    type: String,
    default: 'Enviar'
  },
  submitButtonClass: {
    type: String,
    default: 'bg-green-600 text-white hover:bg-green-700'
  },
  loading: {
    type: Boolean,
    default: false
  },
  loadingText: {
    type: String,
    default: 'Procesando...'
  },
  disabled: {
    type: Boolean,
    default: false
  },
  statusMessage: {
    type: String,
    default: ''
  },
  statusMessageType: {
    type: String,
    default: 'error',
    validator: (value) => ['success', 'error', 'info', 'warning'].includes(value)
  },
  errors: {
    type: Object,
    default: () => ({})
  },
  showFooter: {
    type: Boolean,
    default: false
  },
  containerClass: {
    type: String,
    default: ''
  },
  titleClass: {
    type: String,
    default: 'text-3xl font-bold text-green-700'
  },
  subtitleClass: {
    type: String,
    default: 'text-gray-600 text-sm mt-2'
  }
})

const emit = defineEmits(['update:modelValue', 'submit', 'field-update'])

const updateField = (field, value) => {
  const updated = { ...props.modelValue, [field]: value }
  emit('update:modelValue', updated)
  emit('field-update', field, value)
}

const handleSubmit = () => {
  emit('submit', props.modelValue)
}
</script>

<style scoped>
.base-auth-form {
  @apply w-full;
}

.base-auth-title {
  @apply text-3xl font-bold text-green-700;
}

.base-auth-subtitle {
  @apply text-gray-600 text-sm mt-2;
}
</style>

