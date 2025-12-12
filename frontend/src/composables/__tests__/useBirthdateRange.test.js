/**
 * Unit tests for useBirthdateRange composable
 * @deprecated This composable is deprecated but tests are kept for backward compatibility
 */

import { describe, it, expect, vi } from 'vitest'
// eslint-disable-next-line deprecation/deprecation
import { useBirthdateRange } from '../useBirthdateRange.js'
import { getMaxBirthdate, getMinBirthdate } from '../useDateFormatting'

// Mock useDateFormatting
vi.mock('../useDateFormatting', () => ({
  getMaxBirthdate: vi.fn(() => '2010-01-01'),
  getMinBirthdate: vi.fn(() => '1900-01-01')
}))

describe('useBirthdateRange', () => {
  // eslint-disable-next-line deprecation/deprecation
  it('should return computed maxBirthdate', () => {
    // eslint-disable-next-line deprecation/deprecation
    const { maxBirthdate } = useBirthdateRange()
    
    expect(maxBirthdate.value).toBe('2010-01-01')
    expect(getMaxBirthdate).toHaveBeenCalled()
  })

  // eslint-disable-next-line deprecation/deprecation
  it('should return computed minBirthdate', () => {
    // eslint-disable-next-line deprecation/deprecation
    const { minBirthdate } = useBirthdateRange()
    
    expect(minBirthdate.value).toBe('1900-01-01')
    expect(getMinBirthdate).toHaveBeenCalled()
  })
})

