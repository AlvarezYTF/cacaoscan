import { describe, it, expect } from 'vitest'
import { useBirthdateRange } from '../useBirthdateRange'

describe('useBirthdateRange', () => {
  it('should calculate max birthdate (14 years ago)', () => {
    const { maxBirthdate } = useBirthdateRange()
    const today = new Date()
    const expectedMaxDate = new Date(today.getFullYear() - 14, today.getMonth(), today.getDate())
    const expectedMaxDateString = expectedMaxDate.toISOString().split('T')[0]

    expect(maxBirthdate.value).toBe(expectedMaxDateString)
  })

  it('should calculate min birthdate (120 years ago)', () => {
    const { minBirthdate } = useBirthdateRange()
    const today = new Date()
    const expectedMinDate = new Date(today.getFullYear() - 120, today.getMonth(), today.getDate())
    const expectedMinDateString = expectedMinDate.toISOString().split('T')[0]

    expect(minBirthdate.value).toBe(expectedMinDateString)
  })

  it('should return date in YYYY-MM-DD format', () => {
    const { maxBirthdate, minBirthdate } = useBirthdateRange()

    expect(maxBirthdate.value).toMatch(/^\d{4}-\d{2}-\d{2}$/)
    expect(minBirthdate.value).toMatch(/^\d{4}-\d{2}-\d{2}$/)
  })

  it('should have minBirthdate before maxBirthdate', () => {
    const { maxBirthdate, minBirthdate } = useBirthdateRange()

    expect(new Date(minBirthdate.value) < new Date(maxBirthdate.value)).toBe(true)
  })
})

