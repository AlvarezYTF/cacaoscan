/**
 * Google Authentication Utility
 * Maneja la inicialización y callback de Google Identity Services
 * 
 * IMPORTANTE: Configuración de Google OAuth
 * 
 * Si ves el error "The given origin is not allowed for the given client ID":
 * 1. Ve a Google Cloud Console: https://console.cloud.google.com/
 * 2. Selecciona tu proyecto
 * 3. Ve a "APIs & Services" > "Credentials"
 * 4. Encuentra tu OAuth 2.0 Client ID
 * 5. En "Authorized JavaScript origins", agrega:
 *    - http://localhost:8000 (para desarrollo)
 *    - http://localhost:5173 (si usas Vite en puerto 5173)
 *    - https://tu-dominio.com (para producción)
 * 6. En "Authorized redirect URIs", agrega:
 *    - http://localhost:8000/api/v1/auth/google-login/
 *    - https://tu-dominio.com/api/v1/auth/google-login/
 * 7. Guarda los cambios y espera unos minutos para que se propaguen
 */

// ← Pegar aquí el CLIENT_ID de Google
// Ejemplo: const GOOGLE_CLIENT_ID = '621115501106-r3hvdjosijrrt5o6323nn5a32teaqq37.apps.googleusercontent.com'
const GOOGLE_CLIENT_ID = '621115501106-r3hvdjosijrrt5o6323nn5a32teaqq37.apps.googleusercontent.com' 

let googleInitialized = false
let initializePromise = null

/**
 * Inicializa Google Identity Services
 * @returns {Promise<void>}
 */
export function initializeGoogleAuth() {
  if (googleInitialized) {
    return Promise.resolve()
  }

  if (initializePromise) {
    return initializePromise
  }

  initializePromise = new Promise((resolve, reject) => {
    // Verificar si el script de Google ya está cargado
    if (typeof window.google !== 'undefined' && window.google.accounts) {
      try {
        window.google.accounts.id.initialize({
          client_id: GOOGLE_CLIENT_ID,
          callback: handleGoogleCredential
        })
        googleInitialized = true
        resolve()
      } catch (error) {
        console.error('Error inicializando Google Auth:', error)
        reject(error)
      }
    } else {
      // Esperar a que el script se cargue
      const checkInterval = setInterval(() => {
        if (typeof window.google !== 'undefined' && window.google.accounts) {
          clearInterval(checkInterval)
          try {
            window.google.accounts.id.initialize({
              client_id: GOOGLE_CLIENT_ID,
              callback: handleGoogleCredential
            })
            googleInitialized = true
            resolve()
          } catch (error) {
            console.error('Error inicializando Google Auth:', error)
            reject(error)
          }
        }
      }, 100)

      // Timeout después de 10 segundos
      setTimeout(() => {
        clearInterval(checkInterval)
        if (!googleInitialized) {
          reject(new Error('Google Identity Services no se cargó en el tiempo esperado'))
        }
      }, 10000)
    }
  })

  return initializePromise
}

/**
 * Callback global para manejar la respuesta de Google
 * @param {Object} response - Respuesta de Google Identity
 */
let credentialCallback = null

function handleGoogleCredential(response) {
  if (credentialCallback) {
    credentialCallback(response.credential)
    credentialCallback = null
  }
}

/**
 * Renderiza el botón de Google Sign-In en un contenedor
 * @param {string} containerId - ID del elemento contenedor
 * @param {Function} onCredential - Callback cuando se recibe el credential
 */
export async function renderGoogleButton(containerId, onCredential) {
  try {
    await initializeGoogleAuth()

    // Guardar callback
    credentialCallback = onCredential

    // Limpiar contenedor
    const container = document.getElementById(containerId)
    if (!container) {
      throw new Error(`Contenedor con ID "${containerId}" no encontrado`)
    }

    container.innerHTML = ''

    // Renderizar botón de Google
    window.google.accounts.id.renderButton(
      container,
      {
        theme: 'outline',
        size: 'large',
        text: 'signin_with',
        width: container.offsetWidth || 300,
        locale: 'es'
      }
    )
  } catch (error) {
    console.error('Error renderizando botón de Google:', error)
    throw error
  }
}

/**
 * Inicializa y renderiza el botón de Google en un contenedor
 * Versión simplificada que combina inicialización y renderizado
 * @param {string} containerId - ID del elemento contenedor
 * @param {Function} onCredential - Callback cuando se recibe el credential
 */
export async function setupGoogleLogin(containerId, onCredential) {
  return renderGoogleButton(containerId, onCredential)
}

