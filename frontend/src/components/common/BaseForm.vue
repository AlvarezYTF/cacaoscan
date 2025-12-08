<template>
  <form 
    @submit.prevent="handleSubmit" 
    class="base-form"
    :class="formClass"
    novalidate
  >
    <!-- Form Header -->
    <div v-if="title || $slots.header" class="form-header mb-4">
      <slot name="header">
        <h3 v-if="title">{{ title }}</h3>
        <p v-if="subtitle" class="text-muted">{{ subtitle }}</p>
      </slot>
    </div>

    <!-- Global Form Error -->
    <div v-if="globalError" class="alert alert-danger" role="alert">
      <i class="fas fa-exclamation-circle me-2"></i>
      {{ globalError }}
    </div>

    <!-- Form Fields -->
    <div class="form-body">
      <!-- Slot for custom fields -->
      <slot name="fields">
        <!-- Auto-render fields from fieldConfigs -->
        <template v-if="fieldConfigs && fieldConfigs.length > 0">
          <BaseFormField
            v-for="field in visibleFields"
            :key="field.name"
            v-bind="getFieldProps(field)"
            :model-value="getFieldValue(field.name)"
            :error="getFieldError(field.name)"
            @update:model-value="(value) => updateField(field.name, value)"
          />
        </template>
      </slot>
    </div>

    <!-- Form Footer / Actions -->
    <div class="form-footer mt-4 pt-4 border-top">
      <slot name="footer">
        <div class="d-flex justify-content-between align-items-center">
          <div>
            <button
              v-if="showCancelButton"
              type="button"
              @click="handleCancel"
              class="btn btn-secondary"
              :disabled="isSubmitting"
            >
              {{ cancelButtonText || 'Cancelar' }}
            </button>
          </div>
          <div class="d-flex gap-2">
            <button
              v-if="showResetButton"
              type="button"
              @click="handleReset"
              class="btn btn-outline-secondary"
              :disabled="isSubmitting || !isDirty"
            >
              {{ resetButtonText || 'Restablecer' }}
            </button>
            <button
              type="submit"
              class="btn"
              :class="submitButtonClass || 'btn-primary'"
              :disabled="isSubmitting || (validateOnSubmit && !isValid)"
            >
              <i v-if="isSubmitting" class="fas fa-spinner fa-spin me-2"></i>
              <i v-else-if="submitIcon" :class="submitIcon" class="me-2"></i>
              {{ isSubmitting ? submitButtonLoadingText || 'Enviando...' : submitButtonText || 'Enviar' }}
            </button>
          </div>
        </div>
      </slot>
    </div>
  </form>
</template>

<script setup>
import { computed } from 'vue'
import BaseFormField from './BaseFormField.vue'
import { useForm } from '@/composables/useForm'

const props = defineProps({
  // Form Configuration
  title: {
    type: String,
    default: ''
  },
  subtitle: {
    type: String,
    default: ''
  },
  formClass: {
    type: String,
    default: ''
  },
  
  // Form State
  initialValues: {
    type: Object,
    default: () => ({})
  },
  
  // Field Configuration
  fieldConfigs: {
    type: Array,
    default: () => []
  },
  
  // Validation
  validateOnSubmit: {
    type: Boolean,
    default: true
  },
  validator: {
    type: Function,
    default: null
  },
  
  // Submission
  onSubmit: {
    type: Function,
    required: true
  },
  
  // Global Error
  globalError: {
    type: String,
    default: null
  },
  
  // Buttons
  showCancelButton: {
    type: Boolean,
    default: false
  },
  cancelButtonText: {
    type: String,
    default: 'Cancelar'
  },
  showResetButton: {
    type: Boolean,
    default: false
  },
  resetButtonText: {
    type: String,
    default: 'Restablecer'
  },
  submitButtonText: {
    type: String,
    default: 'Enviar'
  },
  submitButtonLoadingText: {
    type: String,
    default: 'Enviando...'
  },
  submitButtonClass: {
    type: String,
    default: 'btn-primary'
  },
  submitIcon: {
    type: String,
    default: ''
  },
  
  // Field Visibility
  conditionalFields: {
    type: Object,
    default: () => ({})
  }
})

const emit = defineEmits(['submit', 'cancel', 'reset', 'update:modelValue'])

// Use form composable
const {
  form,
  errors,
  isSubmitting,
  isDirty,
  isValid,
  validateForm,
  resetForm: resetFormState,
  updateField,
  getFieldValue: getFieldValueFromForm,
  getFieldError: getFieldErrorFromForm,
  handleSubmit: handleSubmitFromComposable
} = useForm({
  initialValues: props.initialValues,
  onSubmit: props.onSubmit,
  validator: props.validator
})

// Computed: Filter visible fields based on conditions
const visibleFields = computed(() => {
  if (!props.fieldConfigs || props.fieldConfigs.length === 0) {
    return []
  }
  
  return props.fieldConfigs.filter(field => {
    // Check if field has visibility condition
    if (field.visible === false) {
      return false
    }
    
    // Check conditional visibility
    if (field.conditional) {
      const condition = props.conditionalFields[field.conditional.field]
      if (condition !== field.conditional.value) {
        return false
      }
    }
    
    return true
  })
})

// Get field props for BaseFormField
const getFieldProps = (field) => {
  return {
    name: field.name,
    label: field.label,
    type: field.type || 'text',
    placeholder: field.placeholder,
    required: field.required || false,
    disabled: field.disabled || false,
    autocomplete: field.autocomplete,
    options: field.options || [],
    optionValue: field.optionValue || 'value',
    optionLabel: field.optionLabel || 'label',
    rows: field.rows || 4,
    min: field.min,
    max: field.max,
    helpText: field.helpText,
    showPasswordToggle: field.showPasswordToggle || false
  }
}

const getFieldValue = (fieldName) => {
  return getFieldValueFromForm(fieldName)
}

const getFieldError = (fieldName) => {
  return getFieldErrorFromForm(fieldName)
}

// Form submission
const handleSubmit = async () => {
  if (props.validateOnSubmit) {
    const isValid = validateForm()
    if (!isValid) {
      return
    }
  }
  
  try {
    await handleSubmitFromComposable()
    emit('submit', form)
  } catch (error) {
    // Error is already handled by useForm composable
  }
}

// Form cancellation
const handleCancel = () => {
  emit('cancel')
}

// Form reset
const handleReset = () => {
  resetFormState()
  emit('reset')
}

// Expose form methods for parent components
defineExpose({
  form,
  errors,
  isValid,
  isDirty,
  isSubmitting,
  validateForm,
  resetForm: handleReset,
  submit: handleSubmit
})
</script>

<style scoped>
.base-form {
  width: 100%;
}

.form-header h3 {
  margin-bottom: 0.5rem;
  font-size: 1.5rem;
  font-weight: 600;
  color: #1f2937;
}

.form-header p {
  margin-bottom: 0;
  color: #6b7280;
}

.form-body {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.form-footer {
  border-top: 1px solid #e5e7eb;
  padding-top: 1rem;
}

.alert {
  padding: 0.75rem 1rem;
  border-radius: 0.375rem;
  margin-bottom: 1.5rem;
}

.alert-danger {
  background-color: #fef2f2;
  border: 1px solid #fecaca;
  color: #991b1b;
}

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid transparent;
  gap: 0.5rem;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  background-color: #2563eb;
  color: #ffffff;
  border-color: #2563eb;
}

.btn-primary:hover:not(:disabled) {
  background-color: #1d4ed8;
  border-color: #1d4ed8;
}

.btn-secondary {
  background-color: #6b7280;
  color: #ffffff;
  border-color: #6b7280;
}

.btn-secondary:hover:not(:disabled) {
  background-color: #4b5563;
  border-color: #4b5563;
}

.btn-outline-secondary {
  background-color: transparent;
  color: #6b7280;
  border-color: #6b7280;
}

.btn-outline-secondary:hover:not(:disabled) {
  background-color: #f3f4f6;
}

.d-flex {
  display: flex;
}

.justify-content-between {
  justify-content: space-between;
}

.align-items-center {
  align-items: center;
}

.gap-2 {
  gap: 0.5rem;
}

.mt-4 {
  margin-top: 1rem;
}

.mb-4 {
  margin-bottom: 1rem;
}

.pt-4 {
  padding-top: 1rem;
}

.border-top {
  border-top: 1px solid #e5e7eb;
}

.text-muted {
  color: #6b7280;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .form-footer .d-flex {
    flex-direction: column;
    gap: 0.75rem;
  }
  
  .form-footer .d-flex > div {
    width: 100%;
  }
  
  .form-footer .btn {
    width: 100%;
  }
}
</style>

