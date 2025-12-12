/**
 * Icon paths for form sections
 * Centralizes SVG path data to reduce duplication
 */
export const FORM_SECTION_ICONS = {
  PERSONAL: 'M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z',
  DOCUMENT: 'M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z',
  LOCATION: 'M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z M15 11a3 3 0 11-6 0 3 3 0 016 0z',
  CREDENTIALS: 'M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z'
}

/**
 * Gets icon path for a form section
 * @param {string} section - Section name (PERSONAL, DOCUMENT, LOCATION, CREDENTIALS)
 * @returns {string} Icon path
 */
export function getFormSectionIcon(section) {
  const iconPath = FORM_SECTION_ICONS[section]
  if (!iconPath) {
    throw new Error(`Invalid form section: ${section}. Must be one of: ${Object.keys(FORM_SECTION_ICONS).join(', ')}`)
  }
  return iconPath
}

