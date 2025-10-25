# 🔧 Corrección de Navigation Guard - Vue Router 4

## 📋 Problema Original

El navigation guard estaba usando el formato **antiguo con `next()`** de Vue Router 3, lo que causaba estos errores:

```
[Vue Router warn]: The "next" callback was never called inside of ...
Error: Invalid navigation guard
```

### ❌ Código Problemático (Formato Antiguo)

```javascript
router.beforeEach(async (to, from, next) => {
  try {
    if (!authStore.accessToken) {
      next({ name: 'Login', replace: true })
      return  // ⚠️ PROBLEMA: return después de next()
    }
    
    if (authStore.isAuthenticated) {
      next({ path: redirectPath, replace: true })
      return  // ⚠️ PROBLEMA: return después de next()
    }
    
    next()  // ⚠️ PROBLEMA: múltiples llamadas a next()
  } catch (error) {
    next({ path: '/acceso-denegado' })
    return  // ⚠️ PROBLEMA: return después de next()
  }
})
```

### 🔴 Problemas del Formato Antiguo:

1. **Llamadas múltiples a `next()`**: Cada `return` después de `next()` no detiene la ejecución del guard
2. **Flujos sin retorno explícito**: Vue Router 4 no sabe si debe continuar o abortar
3. **Mezcla de `next()` y `return`**: Causa comportamiento impredecible
4. **Error "next callback was never called"**: Ocurre cuando hay un `return` antes de llamar a `next()`

---

## ✅ Solución Implementada (Formato Moderno)

### 🎯 Cambios Clave:

1. **Eliminado el parámetro `next`** de la firma del guard
2. **Usar `return` directamente** con objetos de redirección
3. **Flujos de control claros** con returns explícitos

### ✨ Código Corregido

```javascript
// ✅ CORRECTO: Formato moderno "return-based" de Vue Router 4
router.beforeEach(async (to, from) => {  // ← Sin 'next'
  // Prevenir navegación múltiple simultánea
  if (isNavigating) {
    return false  // ← Abortar navegación
  }
  
  isNavigating = true
  
  try {
    // Actualizar título
    document.title = to.meta?.title || 'CacaoScan'
    
    const authStore = useAuthStore()
    
    // Verificar autenticación
    if (to.meta.requiresAuth || to.matched.some(record => record.meta.requiresAuth)) {
      
      // Si no hay token, redirigir al login
      if (!authStore.accessToken) {
        return {  // ← Return directo con objeto de redirección
          name: 'Login',
          replace: true,
          query: { 
            redirect: to.fullPath,
            message: 'Debes iniciar sesión para acceder a esta página'
          }
        }
      }
      
      // Si hay token pero no hay usuario, intentar obtenerlo
      if (!authStore.user) {
        try {
          await authStore.getCurrentUser()
        } catch (error) {
          authStore.clearAll()
          return {  // ← Return directo con objeto de redirección
            name: 'Login',
            replace: true,
            query: { 
              redirect: to.fullPath,
              message: 'Tu sesión ha expirado. Inicia sesión nuevamente.',
              expired: 'true'
            }
          }
        }
      }
      
      // Verificar si la sesión ha expirado por inactividad
      if (authStore.checkSessionTimeout()) {
        return false  // ← Abortar navegación
      }
      
      // Actualizar actividad del usuario
      authStore.updateLastActivity()
    }
    
    // Verificar rutas públicas (requiresGuest)
    if (to.meta.requiresGuest || to.matched.some(record => record.meta.requiresGuest)) {
      if (authStore.isAuthenticated) {
        const redirectPath = getRedirectPathByRole(authStore.userRole)
        return { path: redirectPath, replace: true }  // ← Return directo
      }
    }
    
    // Permitir navegación
    return true  // ← O simplemente 'return' (undefined también funciona)
    
  } catch (error) {
    console.error('Error en navigation guard:', error)
    return { path: '/acceso-denegado', replace: true }  // ← Return directo
  } finally {
    setTimeout(() => {
      isNavigating = false
      window.dispatchEvent(new CustomEvent('route-loading-end'))
    }, 100)
  }
})
```

---

## 📚 Valores de Retorno en Vue Router 4

### 1️⃣ **`return false`** - Abortar navegación
```javascript
if (isNavigating) {
  return false  // Cancela la navegación completamente
}
```

### 2️⃣ **`return true`** o **`return undefined`** - Permitir navegación
```javascript
// Ambas formas son válidas para permitir la navegación
return true
// o simplemente
return
```

### 3️⃣ **`return { ... }`** - Redirigir a otra ruta
```javascript
// Redirigir con nombre de ruta
return {
  name: 'Login',
  replace: true,
  query: { redirect: to.fullPath }
}

// Redirigir con path
return {
  path: '/admin/dashboard',
  replace: true
}
```

### 4️⃣ **`return '/path'`** - Redirigir (forma corta)
```javascript
return '/login'  // Equivalente a { path: '/login' }
```

---

## 🎯 Por Qué Este Cambio Evita el Error

### Problema con `next()`:

```javascript
// ❌ MAL: Mezcla next() y return
if (!authStore.accessToken) {
  next({ name: 'Login' })
  return  // ← Vue Router no sabe que debe detenerse aquí
}
next()  // ← Podría ejecutarse accidentalmente
```

**Resultado:** Vue Router detecta múltiples llamadas a `next()` o ninguna llamada, causando el error.

### Solución con `return`:

```javascript
// ✅ BIEN: Return directo
if (!authStore.accessToken) {
  return { name: 'Login' }  // ← Detiene la ejecución inmediatamente
}
return true  // ← Solo se ejecuta si no hay return anterior
```

**Resultado:** Flujo de control claro y predecible. Vue Router sabe exactamente qué hacer.

---

## 🔄 Comparación Lado a Lado

| Aspecto | Formato Antiguo (`next`) | Formato Moderno (`return`) |
|---------|--------------------------|----------------------------|
| **Firma** | `async (to, from, next)` | `async (to, from)` |
| **Abortar** | `next(false)` | `return false` |
| **Permitir** | `next()` | `return true` o `return` |
| **Redirigir** | `next({ name: 'Login' })` | `return { name: 'Login' }` |
| **Claridad** | ⚠️ Confuso (múltiples `next()`) | ✅ Claro (un solo `return`) |
| **Errores** | ❌ Propenso a errores | ✅ Seguro |
| **Async** | ⚠️ Requiere cuidado extra | ✅ Funciona naturalmente |

---

## 🚀 Beneficios del Formato Moderno

1. **✅ Sin errores de "next callback"**: Imposible olvidar llamar a `next()`
2. **✅ Código más limpio**: Menos boilerplate, más legible
3. **✅ Mejor con async/await**: Los returns funcionan naturalmente con código asíncrono
4. **✅ Menos bugs**: Imposible llamar a `next()` múltiples veces
5. **✅ TypeScript friendly**: Mejor inferencia de tipos
6. **✅ Más intuitivo**: Similar a otros guards (canActivate en Angular, etc.)

---

## 📖 Documentación Oficial

- [Vue Router 4 - Navigation Guards](https://router.vuejs.org/guide/advanced/navigation-guards.html)
- [Migration from Vue Router 3](https://router.vuejs.org/guide/migration/#removal-of-the-next-callback-in-navigation-guards)

---

## ✅ Checklist de Migración

- [x] Eliminar parámetro `next` de la firma del guard
- [x] Reemplazar `next()` por `return true` o `return`
- [x] Reemplazar `next(false)` por `return false`
- [x] Reemplazar `next({ ... })` por `return { ... }`
- [x] Eliminar todos los `return` después de redirecciones (ya no son necesarios)
- [x] Verificar que todos los flujos tienen un return explícito
- [x] Probar navegación en todos los escenarios (auth, guest, timeout, etc.)

---

## 🎉 Resultado

**Antes:** Errores de "Invalid navigation guard" y comportamiento impredecible

**Después:** Navegación fluida, sin warnings, código más limpio y mantenible

---

**Fecha de actualización:** 25/10/2025
**Vue Router versión:** 4.x
**Estado:** ✅ Implementado y funcionando

