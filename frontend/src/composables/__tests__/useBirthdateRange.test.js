import { describe, it, expect } from 'vitest'
import { useDateFormatting } from '../useDateFormatting'

describe('useBirthdateRange', () => {
  it('should calculate max birthdate (14 years ago)', () => {
    const { getMaxBirthdate } = useDateFormatting()
    const today = new Date()
    const expectedMaxDate = new Date(today.getFullYear() - 14, today.getMonth(), today.getDate())
    const expectedMaxDateString = expectedMaxDate.toISOString().split('T')[0]

    expect(getMaxBirthdate()).toBe(expectedMaxDateString)
  })

  it('should calculate min birthdate (120 years ago)', () => {
    const { getMinBirthdate } = useDateFormatting()
    const today = new Date()
    const expectedMinDate = new Date(today.getFullYear() - 120, today.getMonth(), today.getDate())
    const expectedMinDateString = expectedMinDate.toISOString().split('T')[0]

    expect(getMinBirthdate()).toBe(expectedMinDateString)
  })

  it('should return date in YYYY-MM-DD format', () => {
    const { getMaxBirthdate, getMinBirthdate } = useDateFormatting()

    expect(getMaxBirthdate()).toMatch(/^\d{4}-\d{2}-\d{2}$/)
    expect(getMinBirthdate()).toMatch(/^\d{4}-\d{2}-\d{2}$/)
  })

  it('should have minBirthdate before maxBirthdate', () => {
    const { getMaxBirthdate, getMinBirthdate } = useDateFormatting()

    expect(new Date(getMinBirthdate()) < new Date(getMaxBirthdate())).toBe(true)
  })
})

