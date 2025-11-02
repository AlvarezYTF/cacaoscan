/**
 * Utilidades para normalizar respuestas de la API
 * Estandariza arrays provenientes de endpoints paginados ({results: [...]})
 * o no paginados ([...]).
 */

export function normalizeResponse(data) {
  if (data && Array.isArray(data.results)) return data.results
  if (Array.isArray(data)) return data
  return []
}


