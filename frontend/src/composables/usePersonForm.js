/**
 * Composable for person form logic (catalogos, validation, etc.)
 * Used by CreateFarmerModal, EditFarmerModal, and other person forms
 */
import { computed } from 'vue'
import { useCatalogos } from '@/composables/useCatalogos'
import { useFormValidation } from '@/composables/useFormValidation'
import { useBirthdateRange } from '@/composables/useBirthdateRange'

/**
 * Creates person form composable
 * @param {Object} options - Configuration options
 * @param {Function} options.onDepartamentoChange - Callback when departamento changes
 * @returns {Object} Composable return object
 */
export function usePersonForm(options = {}) {
  const {
    onDepartamentoChange: customOnDepartamentoChange
  } = options

  // Catalogos
  const {
    tiposDocumento,
    generos,
    departamentos,
    municipios,
    isLoadingCatalogos,
    cargarCatalogos,
    cargarMunicipios,
    limpiarMunicipios
  } = useCatalogos()

  // Form validation
  const {
    errors,
    isValidEmail,
    isValidPhone,
    isValidDocument,
    isValidBirthdate,
    clearErrors
  } = useFormValidation()

  // Birthdate range
  const { maxBirthdate, minBirthdate } = useBirthdateRange()

  // Handle departamento change
  const onDepartamentoChange = async () => {
    limpiarMunicipios()
    if (customOnDepartamentoChange) {
      await customOnDepartamentoChange()
    }
  }

  // Base input classes
  const baseInputClasses = computed(() => {
    return 'w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500/50 focus:border-green-500'
  })

  // Get input classes with error state
  const getInputClasses = (fieldName) => {
    return [
      baseInputClasses.value,
      errors[fieldName] ? 'border-red-500' : ''
    ].filter(Boolean).join(' ')
  }

  return {
    // Catalogos
    tiposDocumento,
    generos,
    departamentos,
    municipios,
    isLoadingCatalogos,
    cargarCatalogos,
    cargarMunicipios,
    limpiarMunicipios,

    // Validation
    errors,
    isValidEmail,
    isValidPhone,
    isValidDocument,
    isValidBirthdate,
    clearErrors,

    // Birthdate
    maxBirthdate,
    minBirthdate,

    // Methods
    onDepartamentoChange,
    baseInputClasses,
    getInputClasses
  }
}

