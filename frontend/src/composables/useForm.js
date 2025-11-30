/**
 * Composable for complete form management
 * Provides form state, validation, error handling, and submission logic
 */
import { reactive, ref, computed, watch } from 'vue'
import { useFormValidation } from './useFormValidation'
import { useCatalogos } from './useCatalogos'

/**
 * Creates form state and handlers
 * @param {Object} options - Form options
 * @param {Object} options.initialValues - Initial form values
 * @param {Function} options.onSubmit - Submit handler function
 * @param {Function} options.validator - Custom validator function
 * @param {Object} options.fieldMapping - Mapping from server field names to form field names
 * @param {boolean} options.autoLoadCatalogos - Auto-load catalogos (default: true)
 * @returns {Object} Form state and methods
 */
export function useForm(options = {}) {
  const {
    initialValues = {},
    onSubmit = null,
    validator = null,
    fieldMapping = {},
    autoLoadCatalogos = true
  } = options

  // Form validation composable
  const {
    errors,
    isValidEmail,
    isValidPhone,
    isValidDocument,
    isValidBirthdate,
    validatePassword,
    clearErrors,
    setError,
    removeError,
    hasErrors,
    mapServerErrors,
    handleFormSubmit: handleFormSubmitValidation,
    scrollToFirstError,
    validateNameField,
    validateEmailField,
    validatePhoneField,
    validateDocumentField,
    validatePasswordFields,
    validateBirthdateField
  } = useFormValidation()

  // Catalogos composable
  const catalogos = useCatalogos()

  // Form state
  const form = reactive({ ...initialValues })
  const isSubmitting = ref(false)
  const isDirty = ref(false)
  const submitCount = ref(0)

  // Watch for form changes
  watch(() => form, () => {
    isDirty.value = true
    // Clear errors when user starts typing
    if (submitCount.value > 0) {
      // Only clear on user interaction after first submit attempt
    }
  }, { deep: true })

  // Load catalogos if needed
  if (autoLoadCatalogos) {
    catalogos.cargarCatalogos()
  }

  // Computed
  const isValid = computed(() => {
    if (validator && typeof validator === 'function') {
      return validator(form)
    }
    return !hasErrors()
  })

  const canSubmit = computed(() => {
    return isValid.value && !isSubmitting.value
  })

  // Methods - Form state
  const resetForm = (newValues = {}) => {
    for (const key of Object.keys(form)) {
      delete form[key]
    }
    Object.assign(form, { ...initialValues, ...newValues })
    clearErrors()
    isDirty.value = false
    submitCount.value = 0
  }

  const updateField = (field, value) => {
    form[field] = value
    removeError(field)
  }

  const updateFields = (fields) => {
    Object.assign(form, fields)
    // Clear errors for updated fields
    for (const key of Object.keys(fields)) {
      removeError(key)
    }
  }

  // Methods - Validation
  const validateField = (fieldName, value = null) => {
    const fieldValue = value === null ? form[fieldName] : value
    let error = null

    // Use field-specific validators
    switch (fieldName) {
      case 'firstName':
      case 'primer_nombre':
      case 'first_name':
        error = validateNameField(fieldValue, 'firstName')
        break
      case 'lastName':
      case 'primer_apellido':
      case 'last_name':
        error = validateNameField(fieldValue, 'lastName')
        break
      case 'email':
        error = validateEmailField(fieldValue)
        break
      case 'phoneNumber':
      case 'telefono':
      case 'phone_number':
        error = validatePhoneField(fieldValue)
        break
      case 'numeroDocumento':
      case 'numero_documento':
        error = validateDocumentField(fieldValue)
        break
      case 'fechaNacimiento':
      case 'fecha_nacimiento':
        error = validateBirthdateField(fieldValue)
        break
      case 'password':
        if (form.confirmPassword || form.confirm_password) {
          const passwordErrors = validatePasswordFields(
            fieldValue,
            form.confirmPassword || form.confirm_password
          )
          error = passwordErrors.password
        } else {
          const passwordChecks = validatePassword(fieldValue)
          if (!passwordChecks.isValid) {
            error = 'La contraseña debe tener al menos 8 caracteres, una mayúscula, una minúscula y un número'
          }
        }
        break
      case 'confirmPassword':
      case 'confirm_password':
        if (form.password) {
          const passwordErrors = validatePasswordFields(form.password, fieldValue)
          error = passwordErrors.confirmPassword
        }
        break
    }

    if (error) {
      setError(fieldName, error)
      return false
    } else {
      removeError(fieldName)
      return true
    }
  }

  const validateForm = () => {
    clearErrors()
    let isValid = true

    // Validate all fields in form
    for (const fieldName of Object.keys(form)) {
      if (!validateField(fieldName)) {
        isValid = false
      }
    }

    // Run custom validator if provided
    if (validator && typeof validator === 'function') {
      const customValidation = validator(form)
      if (customValidation !== true) {
        isValid = false
        if (typeof customValidation === 'object') {
          for (const [field, message] of Object.entries(customValidation)) {
            setError(field, message)
          }
        }
      }
    }

    return isValid
  }

  // Methods - Submission
  const handleSubmit = async (event = null) => {
    if (event) {
      event.preventDefault()
    }

    submitCount.value++
    isDirty.value = true

    // Validate form
    if (!validateForm()) {
      scrollToFirstError()
      return false
    }

    // If no submit handler, just return
    if (!onSubmit || typeof onSubmit !== 'function') {
      return true
    }

    isSubmitting.value = true

    try {
      const result = await handleFormSubmitValidation(
        () => onSubmit(form),
        null, // validateFn already called
        (result) => {
          // Success callback
          isDirty.value = false
          return result
        },
        (error) => {
          // Error callback
          if (error.response?.data) {
            const serverErrors = error.response.data.details || error.response.data
            mapServerErrors(serverErrors, fieldMapping)
          }
          throw error
        }
      )

      return result
    } catch (err) {
      // Error already handled in handleFormSubmitValidation
      // Log error for debugging and re-throw to allow caller to handle
      console.error('Form submission error:', err)
      throw err
    } finally {
      isSubmitting.value = false
    }
  }

  // Methods - Field helpers
  const getFieldValue = (fieldName) => {
    return form[fieldName]
  }

  const setFieldValue = (fieldName, value) => {
    updateField(fieldName, value)
  }

  const getFieldError = (fieldName) => {
    return errors[fieldName] || null
  }

  const hasFieldError = (fieldName) => {
    return !!errors[fieldName]
  }

  return {
    // State
    form,
    errors,
    isSubmitting,
    isDirty,
    submitCount,

    // Computed
    isValid,
    canSubmit,

    // Validation methods
    validateField,
    validateForm,
    clearErrors,
    setError,
    removeError,
    hasErrors,
    getFieldError,
    hasFieldError,

    // Form state methods
    resetForm,
    updateField,
    updateFields,
    getFieldValue,
    setFieldValue,

    // Submission
    handleSubmit,

    // Utilities
    scrollToFirstError,

    // Catalogos (re-exported)
    ...catalogos,

    // Validation helpers (re-exported)
    isValidEmail,
    isValidPhone,
    isValidDocument,
    isValidBirthdate,
    validatePassword
  }
}

