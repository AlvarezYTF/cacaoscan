/**
 * Composable para manejar rangos de fechas de nacimiento
 * Re-exporta desde useDateFormatting para mantener compatibilidad
 * @deprecated Use useDateFormatting().getMinBirthdate() and getMaxBirthdate() directly
 */
import { computed } from 'vue'
import { getMaxBirthdate, getMinBirthdate } from './useDateFormatting'

/**
 * @deprecated Use useDateFormatting() instead
 */
export function useBirthdateRange() {
  const maxBirthdate = computed(() => getMaxBirthdate())
  const minBirthdate = computed(() => getMinBirthdate())

  return {
    maxBirthdate,
    minBirthdate
  }
}
