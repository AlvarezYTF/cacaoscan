/**
 * Composable para manejar rangos de fechas de nacimiento
 */
import { computed } from 'vue'

export function useBirthdateRange() {
  /**
   * Fecha máxima permitida (14 años atrás)
   */
  const maxBirthdate = computed(() => {
    const today = new Date()
    const maxDate = new Date(today.getFullYear() - 14, today.getMonth(), today.getDate())
    return maxDate.toISOString().split('T')[0]
  })

  /**
   * Fecha mínima permitida (120 años atrás)
   */
  const minBirthdate = computed(() => {
    const today = new Date()
    const minDate = new Date(today.getFullYear() - 120, today.getMonth(), today.getDate())
    return minDate.toISOString().split('T')[0]
  })

  return {
    maxBirthdate,
    minBirthdate
  }
}

