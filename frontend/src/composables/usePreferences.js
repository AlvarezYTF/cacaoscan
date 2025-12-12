/**
 * Composable for preferences component logic
 * Extracts common preferences handling logic
 * @param {Object} props - Component props
 * @param {Function} emit - Component emit function
 * @returns {Object} Preferences composable methods
 */
export function usePreferences(props, emit) {
  /**
   * Updates a single value in the preferences model
   * @param {string} key - Key to update
   * @param {*} value - New value
   * @returns {void}
   */
  const updateValue = (key, value) => {
    const updated = { ...props.modelValue, [key]: value }
    emit('update:modelValue', updated)
  }

  /**
   * Handles save action
   * @returns {void}
   */
  const handleSave = () => {
    emit('save', props.modelValue)
  }

  /**
   * Handles reset action
   * @returns {void}
   */
  const handleReset = () => {
    emit('reset')
  }

  return {
    updateValue,
    handleSave,
    handleReset
  }
}

