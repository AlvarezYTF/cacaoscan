/**
 * Common form field configurations
 * Centralized definitions for reusable form fields
 */

/**
 * Field configuration type definitions
 * @typedef {Object} FieldConfig
 * @property {string} name - Field name (key)
 * @property {string} label - Display label
 * @property {string} type - Input type (text, email, tel, date, select, etc.)
 * @property {string} placeholder - Placeholder text
 * @property {boolean} required - Whether field is required
 * @property {Function} validator - Validation function
 * @property {string} errorMessage - Error message template
 */

/**
 * Common field configurations
 */
export const COMMON_FIELDS = {
  firstName: {
    name: 'firstName',
    label: 'Nombre',
    type: 'text',
    placeholder: 'Juan',
    required: true,
    autocomplete: 'given-name',
    validator: (value) => {
      if (!value?.trim()) {
        return 'El nombre es requerido'
      }
      if (!/^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s]+$/.test(value)) {
        return 'El nombre solo puede contener letras'
      }
      return null
    }
  },

  segundoNombre: {
    name: 'segundoNombre',
    label: 'Segundo Nombre',
    type: 'text',
    placeholder: 'Carlos',
    required: false,
    autocomplete: 'additional-name',
    validator: (value) => {
      if (value && !/^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s]+$/.test(value)) {
        return 'El segundo nombre solo puede contener letras'
      }
      return null
    }
  },

  lastName: {
    name: 'lastName',
    label: 'Apellido',
    type: 'text',
    placeholder: 'Pérez',
    required: true,
    autocomplete: 'family-name',
    validator: (value) => {
      if (!value?.trim()) {
        return 'El apellido es requerido'
      }
      if (!/^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s]+$/.test(value)) {
        return 'El apellido solo puede contener letras'
      }
      return null
    }
  },

  segundoApellido: {
    name: 'segundoApellido',
    label: 'Segundo Apellido',
    type: 'text',
    placeholder: 'Gómez',
    required: false,
    autocomplete: 'family-name',
    validator: (value) => {
      if (value && !/^[a-zA-ZáéíóúÁÉÍÓÚñÑüÜ\s]+$/.test(value)) {
        return 'El segundo apellido solo puede contener letras'
      }
      return null
    }
  },

  email: {
    name: 'email',
    label: 'Correo Electrónico',
    type: 'email',
    placeholder: 'juan.perez@example.com',
    required: true,
    autocomplete: 'email',
    validator: (value, isValidEmail) => {
      if (!value?.trim()) {
        return 'El email es requerido'
      }
      if (!isValidEmail(value)) {
        return 'Ingresa un email válido'
      }
      return null
    }
  },

  phoneNumber: {
    name: 'phoneNumber',
    label: 'Teléfono',
    type: 'tel',
    placeholder: '+57 300 123 4567',
    required: false,
    autocomplete: 'tel',
    validator: (value, isValidPhone) => {
      if (value && !isValidPhone(value)) {
        return 'El teléfono debe tener entre 7 y 15 dígitos'
      }
      return null
    }
  },

  tipoDocumento: {
    name: 'tipoDocumento',
    label: 'Tipo Documento',
    type: 'select',
    required: true,
    options: [], // Should be loaded from catalogos
    validator: (value) => {
      if (!value) {
        return 'El tipo de documento es requerido'
      }
      return null
    }
  },

  numeroDocumento: {
    name: 'numeroDocumento',
    label: 'Número de Documento',
    type: 'text',
    placeholder: '1234567890',
    required: true,
    autocomplete: 'off',
    validator: (value, isValidDocument) => {
      if (!value?.trim()) {
        return 'El número de documento es requerido'
      }
      if (!isValidDocument(value)) {
        return 'El documento debe tener entre 6 y 11 dígitos'
      }
      return null
    }
  },

  genero: {
    name: 'genero',
    label: 'Género',
    type: 'select',
    required: true,
    options: [], // Should be loaded from catalogos
    validator: (value) => {
      if (!value) {
        return 'El género es requerido'
      }
      return null
    }
  },

  fechaNacimiento: {
    name: 'fechaNacimiento',
    label: 'Fecha de Nacimiento',
    type: 'date',
    required: false,
    autocomplete: 'bday',
    validator: (value, isValidBirthdate) => {
      if (value && !isValidBirthdate(value)) {
        return 'Debes tener al menos 14 años'
      }
      return null
    }
  },

  direccion: {
    name: 'direccion',
    label: 'Dirección',
    type: 'text',
    placeholder: 'Calle 123 #45-67',
    required: false,
    autocomplete: 'street-address',
    validator: () => null // No validation needed
  },

  departamento: {
    name: 'departamento',
    label: 'Departamento',
    type: 'select',
    required: true,
    options: [], // Should be loaded from catalogos
    validator: (value) => {
      if (!value) {
        return 'El departamento es requerido'
      }
      return null
    }
  },

  municipio: {
    name: 'municipio',
    label: 'Municipio',
    type: 'select',
    required: true,
    options: [], // Should be loaded from catalogos
    validator: (value) => {
      if (!value) {
        return 'El municipio es requerido'
      }
      return null
    }
  },

  password: {
    name: 'password',
    label: 'Contraseña',
    type: 'password',
    placeholder: 'Mínimo 8 caracteres',
    required: true,
    autocomplete: 'new-password',
    validator: (value, validatePassword) => {
      if (!value) {
        return 'La contraseña es requerida'
      }
      const checks = validatePassword(value)
      if (!checks.isValid) {
        return 'La contraseña debe tener al menos 8 caracteres, una mayúscula, una minúscula y un número'
      }
      return null
    }
  },

  confirmPassword: {
    name: 'confirmPassword',
    label: 'Confirmar Contraseña',
    type: 'password',
    placeholder: 'Repite la contraseña',
    required: true,
    autocomplete: 'new-password',
    validator: (value, password, validatePassword) => {
      if (!value) {
        return 'La confirmación de contraseña es requerida'
      }
      if (value !== password) {
        return 'Las contraseñas no coinciden'
      }
      return null
    }
  }
}

/**
 * Get field configuration by name
 * @param {string} fieldName - Field name
 * @returns {FieldConfig|null} Field configuration or null
 */
export function getFieldConfig(fieldName) {
  return COMMON_FIELDS[fieldName] || null
}

/**
 * Get multiple field configurations
 * @param {string[]} fieldNames - Array of field names
 * @returns {Object} Object with field configurations
 */
export function getFieldConfigs(fieldNames) {
  const configs = {}
  for (const name of fieldNames) {
    const config = getFieldConfig(name)
    if (config) {
      configs[name] = config
    }
  }
  return configs
}

/**
 * Common form field groups
 */
export const FIELD_GROUPS = {
  personalInfo: ['firstName', 'segundoNombre', 'lastName', 'segundoApellido', 'phoneNumber', 'genero', 'fechaNacimiento'],
  documentInfo: ['tipoDocumento', 'numeroDocumento'],
  locationInfo: ['departamento', 'municipio', 'direccion'],
  accountInfo: ['email', 'password', 'confirmPassword']
}

/**
 * Get field group configurations
 * @param {string} groupName - Group name
 * @returns {FieldConfig[]} Array of field configurations
 */
export function getFieldGroup(groupName) {
  const fieldNames = FIELD_GROUPS[groupName] || []
  return fieldNames.map(name => getFieldConfig(name)).filter(Boolean)
}

