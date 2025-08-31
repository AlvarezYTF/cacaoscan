# Guía de Testing - Sistema de Navegación y Guards

Esta guía documenta cómo probar el sistema completo de guards de navegación en CacaoScan.

## 🧪 Plan de Testing Manual

### **1. Testing de Autenticación Básica**

#### Test 1.1: Acceso a rutas protegidas sin autenticación
```bash
# Pasos:
1. Abrir aplicación (sin estar logueado)
2. Intentar navegar a /agricultor-dashboard
3. Intentar navegar a /admin/dashboard
4. Intentar navegar a /prediccion

# Resultado esperado:
- Redirección automática a /login
- Query param con redirect URL
- Mensaje "Debes iniciar sesión para acceder a esta página"
```

#### Test 1.2: Redirección después de login exitoso
```bash
# Pasos:
1. Navegar a /agricultor-dashboard (sin login)
2. Ser redirigido a /login?redirect=/agricultor-dashboard
3. Hacer login exitoso
4. Verificar redirección automática

# Resultado esperado:
- Redirección a la URL original (/agricultor-dashboard)
- Usuario logueado correctamente
```

### **2. Testing de Roles y Permisos**

#### Test 2.1: Agricultor intentando acceder a admin
```bash
# Pasos:
1. Login como agricultor (farmer)
2. Intentar navegar a /admin/dashboard
3. Intentar navegar a /admin/training

# Resultado esperado:
- Redirección a /acceso-denegado
- Query param con error: access_denied
- Mensaje contextual según rol
```

#### Test 2.2: Analista intentando acceder a admin
```bash
# Pasos:
1. Login como analista (analyst)
2. Intentar navegar a /admin/dashboard
3. Intentar navegar a /admin/training

# Resultado esperado:
- Redirección a /acceso-denegado
- Acceso permitido a /analisis y /reportes
```

#### Test 2.3: Admin acceso completo
```bash
# Pasos:
1. Login como administrador (admin)
2. Navegar a diferentes rutas:
   - /admin/dashboard ✅
   - /admin/training ✅
   - /analisis ✅
   - /prediccion ✅

# Resultado esperado:
- Acceso permitido a todas las rutas
- Sin redirecciones no deseadas
```

### **3. Testing de Verificación de Email**

#### Test 3.1: Usuario no verificado intentando subir imágenes
```bash
# Pasos:
1. Login como agricultor NO verificado
2. Intentar navegar a /prediccion
3. Intentar navegar a /user/prediction

# Resultado esperado:
- Redirección a /verificar-email
- Mensaje sobre necesidad de verificación
- Query param con mensaje contextual
```

#### Test 3.2: Usuario verificado accediendo a predicción
```bash
# Pasos:
1. Login como agricultor verificado
2. Navegar a /prediccion

# Resultado esperado:
- Acceso permitido sin redirecciones
- Interfaz de subida de imágenes disponible
```

### **4. Testing de Estados de Loading**

#### Test 4.1: Loading en navegación entre rutas
```bash
# Pasos:
1. Estar logueado en cualquier página
2. Navegar a otra ruta (ej: /perfil)
3. Observar estado de loading

# Resultado esperado:
- Overlay de loading aparece inmediatamente
- Spinner con mensaje contextual
- Barra de progreso animada
- Loading desaparece cuando la página carga
```

#### Test 4.2: Loading en operaciones de API
```bash
# Pasos:
1. Ir a /login
2. Intentar hacer login
3. Observar estado de loading

# Resultado esperado:
- Loading con mensaje "Verificando credenciales..."
- Botón deshabilitado durante loading
- Loading desaparece al completarse
```

### **5. Testing de Prevención de Loops**

#### Test 5.1: Redirecciones circulares
```bash
# Pasos:
1. Login como farmer
2. Navegar a /agricultor-dashboard
3. Verificar que no hay redirecciones adicionales

# Resultado esperado:
- Usuario permanece en la página correcta
- No hay redirecciones infinitas
- Console sin errores de navegación
```

#### Test 5.2: Token expirado durante navegación
```bash
# Pasos:
1. Login normal
2. Simular token expirado (Dev Tools: localStorage.clear())
3. Intentar navegar a ruta protegida

# Resultado esperado:
- Redirección automática a /login
- Mensaje de sesión expirada
- No loops de redirección
```

## 🔧 Herramientas de Testing

### **Console Logs de Debugging**

En modo desarrollo, los guards generan logs útiles:

```javascript
// Logs de navegación
🧭 Navigating: /login → /agricultor-dashboard

// Logs de autenticación
🚫 Acceso denegado: Usuario no autenticado
👤 Usuario ya autenticado, redirigiendo...

// Logs de actividad
👤 Activity updated for usuario@email.com on /perfil

// Logs de roles
🚫 Acceso denegado: Rol 'farmer' no autorizado. Roles permitidos: admin
```

### **Browser Dev Tools**

#### Network Tab:
- Verificar requests de verificación de usuario
- Comprobar refresh de tokens automático
- Monitorear tiempo de respuesta de APIs

#### Application Tab:
- localStorage: access_token, refresh_token, user
- Verificar limpieza automática en logout
- Comprobar persistencia entre reloads

#### Console Tab:
- Logs de guards y navegación
- Errores de autenticación
- Warnings de permisos

### **Vue DevTools**

#### Pinia Store:
```javascript
// Estado de auth store
authStore.isAuthenticated: true/false
authStore.user: { role: 'farmer', is_verified: true }
authStore.userRole: 'farmer'
authStore.canUploadImages: true/false
```

#### Router:
- Current route y params
- Navigation history
- Route guards execution

## 📋 Checklist de Testing Completo

### **Autenticación**
- [ ] ✅ Login con credenciales válidas
- [ ] ✅ Login con credenciales inválidas
- [ ] ✅ Logout correcto y limpieza de tokens
- [ ] ✅ Redirección después de login exitoso
- [ ] ✅ Acceso denegado sin autenticación

### **Roles y Permisos**
- [ ] ✅ Farmer accede solo a sus rutas
- [ ] ✅ Analyst accede a rutas de análisis
- [ ] ✅ Admin accede a todas las rutas
- [ ] ✅ Redirección correcta según rol después de login
- [ ] ✅ Acceso denegado con mensaje contextual

### **Verificación de Email**
- [ ] ✅ Usuario no verificado bloqueado en upload
- [ ] ✅ Usuario verificado accede sin problemas
- [ ] ✅ Redirección a verificación con mensaje

### **Estados de Loading**
- [ ] ✅ Loading en navegación entre rutas
- [ ] ✅ Loading en operaciones de API
- [ ] ✅ Mensajes contextuales por operación
- [ ] ✅ Loading desaparece correctamente

### **Manejo de Errores**
- [ ] ✅ Token expirado maneja logout automático
- [ ] ✅ Errores de red muestran mensaje apropiado
- [ ] ✅ No hay loops de redirección
- [ ] ✅ Fallbacks para estados de error

### **Performance y UX**
- [ ] ✅ Navegación fluida sin delays innecesarios
- [ ] ✅ Estados de loading no demasiado rápidos/lentos
- [ ] ✅ Mensajes claros y accionables
- [ ] ✅ Breadcrumbs y navegación intuitiva

## 🚨 Casos Edge a Probar

### **1. Multiples Tabs**
```bash
# Escenario:
1. Login en Tab A
2. Logout en Tab B
3. Intentar navegar en Tab A

# Resultado esperado:
- Tab A detecta logout y redirige a login
- Sincronización entre tabs
```

### **2. Refresh de Página**
```bash
# Escenario:
1. Login y navegar a ruta protegida
2. Refresh de página (F5)
3. Verificar estado después de refresh

# Resultado esperado:
- Usuario sigue logueado
- Permanece en la misma ruta
- Token válido restaurado
```

### **3. Navegación Browser**
```bash
# Escenario:
1. Login y navegar entre rutas
2. Usar botones Back/Forward del browser
3. Verificar guards en cada navegación

# Resultado esperado:
- Guards se ejecutan en back/forward
- Estados consistentes
- No navegación a rutas no permitidas
```

### **4. Token Refresh Durante Navegación**
```bash
# Escenario:
1. Token próximo a expirar
2. Navegar a nueva ruta
3. Token se refresca automáticamente

# Resultado esperado:
- Navegación completa exitosamente
- Token refrescado transparentemente
- Usuario no nota la operación
```

## 📊 Métricas de Performance

### **Tiempos Esperados**
- **Guard execution**: < 50ms
- **Route loading**: < 200ms
- **Token refresh**: < 500ms
- **API calls**: < 1s

### **Memoria y Bundle**
- **Initial bundle**: < 1MB gzipped
- **Route chunks**: < 100KB cada uno
- **Memory leaks**: Ninguno detectado

## 🐛 Debugging de Problemas Comunes

### **Problema**: Redirecciones infinitas
```javascript
// Causa: Guards mal configurados
// Solución: Verificar condiciones en guards
if (to.name !== 'Login') {
  next({ name: 'Login' })
} else {
  next()
}
```

### **Problema**: Loading no desaparece
```javascript
// Causa: Eventos no emitidos correctamente
// Solución: Asegurar finally block
try {
  // operación
} finally {
  window.dispatchEvent(new CustomEvent('api-loading-end'))
}
```

### **Problema**: Estado inconsistente entre componentes
```javascript
// Causa: Store no reactivo
// Solución: Usar computed en lugar de refs
const isAuthenticated = computed(() => authStore.isAuthenticated)
```

---

## ✅ **Conclusión**

Este plan de testing asegura que:

1. **Todos los guards funcionan correctamente**
2. **Los permisos por rol se respetan**
3. **La navegación es fluida y predecible**
4. **Los estados de loading mejoran la UX**
5. **No hay vulnerabilidades de seguridad**

Para ejecutar este plan, simplemente sigue los pasos en orden y verifica que cada resultado esperado se cumple. El sistema está diseñado para ser robusto y manejar todos estos casos de uso automáticamente.
