<template>
  <!-- Vista de Política de Privacidad - Diseño profesional con navegación interna -->
  <LegalLayout>
    <!-- Encabezado con título y fecha -->
    <template #header>
      <div>
        <h1 id="inicio" class="text-3xl md:text-4xl font-bold text-gray-900 mb-2">
          Política de Privacidad
        </h1>
        <p class="text-sm text-gray-500 mt-1">
          Última actualización: Octubre 2025
        </p>
      </div>
    </template>

    <!-- Índice de navegación interna -->
    <template #index>
      <div class="bg-green-50 border border-green-200 rounded-xl p-6 mb-8">
        <h2 class="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
          <svg class="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
          </svg>
          Índice de Contenido
        </h2>
        <nav class="grid grid-cols-1 md:grid-cols-2 gap-2">
          <a href="#introduccion" class="text-gray-700 hover:text-green-600 transition-colors text-sm py-1">
            • Introducción
          </a>
          <a href="#informacion" class="text-gray-700 hover:text-green-600 transition-colors text-sm py-1">
            • Información que recopilamos
          </a>
          <a href="#uso" class="text-gray-700 hover:text-green-600 transition-colors text-sm py-1">
            • Uso de la información
          </a>
          <a href="#proteccion" class="text-gray-700 hover:text-green-600 transition-colors text-sm py-1">
            • Protección y seguridad
          </a>
          <a href="#derechos" class="text-gray-700 hover:text-green-600 transition-colors text-sm py-1">
            • Derechos del usuario
          </a>
          <a href="#cookies" class="text-gray-700 hover:text-green-600 transition-colors text-sm py-1">
            • Cookies y tecnologías
          </a>
          <a href="#terceros" class="text-gray-700 hover:text-green-600 transition-colors text-sm py-1">
            • Compartición con terceros
          </a>
          <a href="#modificaciones" class="text-gray-700 hover:text-green-600 transition-colors text-sm py-1">
            • Modificaciones
          </a>
          <a href="#contacto" class="text-gray-700 hover:text-green-600 transition-colors text-sm py-1">
            • Contacto
          </a>
        </nav>
      </div>
    </template>

    <!-- Contenido principal -->
    <template #content>
      <!-- Banner informativo legal -->
      <div class="bg-green-50 border border-green-200 text-green-800 p-4 md:p-6 rounded-xl mb-8">
        <div class="flex items-start gap-3">
          <svg class="w-6 h-6 text-green-600 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
          </svg>
          <div>
            <p class="font-semibold text-green-900 mb-2">Protección de Datos Personales</p>
            <p class="text-green-800 text-sm leading-relaxed">
              Esta política describe cómo CacaoScan protege la información personal de los agricultores, administradores y usuarios registrados, cumpliendo con la Ley 1581 de 2012 y el Decreto 1377 de 2013 de Colombia.
            </p>
          </div>
        </div>
      </div>

      <!-- Introducción -->
      <div id="introduccion" class="mb-8">
        <p class="text-lg text-gray-700 leading-relaxed">
          CacaoScan cumple estrictamente con la <strong class="text-gray-900">Ley 1581 de 2012</strong> sobre protección de datos personales y el <strong class="text-gray-900">Decreto 1377 de 2013</strong> de Colombia. Esta política explica cómo recopilamos, utilizamos, protegemos y compartimos su información personal.
        </p>
      </div>

      <hr class="my-6 border-gray-200" />

      <!-- Sección 1: Información que recopilamos -->
      <div id="informacion" class="mb-8">
        <h2 class="text-2xl font-bold text-gray-900 mb-4 flex items-center gap-2">
          <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
          </svg>
          <span>1. Información que recopilamos</span>
        </h2>
        
        <div class="space-y-4 text-gray-700 leading-relaxed">
          <div>
            <h3 class="text-lg font-semibold text-gray-900 mb-2 mt-4">1.1. Información de Registro y Perfil:</h3>
            <ul class="list-disc list-inside ml-4 space-y-2">
              <li><strong>Datos de identificación:</strong> Tipo y número de documento de identidad (CC, CE, etc.), nombre completo (primer nombre, segundo nombre opcional, primer apellido, segundo apellido opcional)</li>
              <li><strong>Datos de contacto:</strong> Correo electrónico (requerido para verificación), número de teléfono (requerido), dirección de residencia (opcional)</li>
              <li><strong>Datos demográficos:</strong> Género (Masculino, Femenino u Otro), fecha de nacimiento (opcional)</li>
              <li><strong>Datos geográficos:</strong> Departamento y municipio de residencia (requeridos)</li>
              <li><strong>Credenciales:</strong> Contraseña (almacenada encriptada, nunca visible)</li>
              <li><strong>Rol y permisos:</strong> Rol asignado (Agricultor por defecto, Administrador o Técnico/Analista por asignación), estado de verificación de correo</li>
            </ul>
          </div>

          <div>
            <h3 class="text-lg font-semibold text-gray-900 mb-2 mt-4">1.2. Información de Uso y Contenido Generado:</h3>
            <ul class="list-disc list-inside ml-4 space-y-2">
              <li><strong>Imágenes de granos:</strong> Imágenes subidas (máx. 20MB), metadatos (nombre, tamaño, tipo), fecha/hora de subida</li>
              <li><strong>Resultados de análisis:</strong> Dimensiones (alto, ancho, grosor en mm), peso estimado (g), niveles de confianza, tiempo de procesamiento, versión del modelo ML (YOLOv8), dispositivo usado (CPU/GPU)</li>
              <li><strong>Información de fincas:</strong> Nombre, ubicación, municipio, departamento, área en hectáreas, coordenadas GPS, descripción, estado, fecha de registro</li>
              <li><strong>Información de lotes:</strong> Identificador, variedad de cacao, fechas de plantación/cosecha, área en hectáreas, coordenadas GPS, estado del lote, descripción</li>
              <li><strong>Asociaciones:</strong> Relación imágenes-lotes, notas y observaciones</li>
              <li><strong>Historial:</strong> Registro de análisis, reportes generados, operaciones realizadas</li>
            </ul>
          </div>

          <div>
            <h3 class="text-lg font-semibold text-gray-900 mb-2 mt-4">1.3. Información Técnica y de Sistema:</h3>
            <ul class="list-disc list-inside ml-4 space-y-2">
              <li><strong>Datos de conexión:</strong> Dirección IP, tipo y versión de navegador, sistema operativo</li>
              <li><strong>Datos de uso:</strong> Fecha y hora de acceso, páginas visitadas, tiempo de sesión, acciones realizadas</li>
              <li><strong>Datos de seguridad:</strong> Tokens de autenticación, logs de acceso, intentos de inicio de sesión</li>
            </ul>
          </div>
        </div>
      </div>

      <hr class="my-6 border-gray-200" />

      <!-- Sección 2: Uso de la información -->
      <div id="uso" class="mb-8">
        <h2 class="text-2xl font-bold text-gray-900 mb-4 flex items-center gap-2">
          <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
          <span>2. Cómo utilizamos su información</span>
        </h2>
        <ul class="list-disc list-inside ml-4 space-y-2 text-gray-700 leading-relaxed">
          <li><strong class="text-gray-900">2.1.</strong> Para proporcionar y mejorar nuestros servicios de análisis mediante modelos de machine learning (YOLOv8) que calculan dimensiones (alto, ancho, grosor) y peso de los granos</li>
          <li><strong class="text-gray-900">2.2.</strong> Para personalizar su experiencia según su rol (Agricultor, Técnico/Analista, Administrador) y mostrarle funcionalidades y datos correspondientes a sus permisos</li>
          <li><strong class="text-gray-900">2.3.</strong> Para comunicarnos sobre su cuenta (verificación de correo), análisis realizados, notificaciones sobre fincas/lotes, y actualizaciones del servicio</li>
          <li><strong class="text-gray-900">2.4.</strong> Para gestionar y organizar sus fincas y lotes, permitiendo seguimiento de análisis por lote y generación de reportes estadísticos</li>
          <li><strong class="text-gray-900">2.5.</strong> Para cumplir con obligaciones legales en Colombia, incluyendo la Ley 1581 de 2012 sobre protección de datos personales</li>
          <li><strong class="text-gray-900">2.6.</strong> Para entrenar y mejorar nuestros modelos ML (utilizando únicamente imágenes anonimizadas, sin asociación con datos personales identificables). Las imágenes para entrenamiento no incluyen información que permita identificar al agricultor o la finca específica</li>
          <li><strong class="text-gray-900">2.7.</strong> Para generar reportes y estadísticas agregadas sobre calidad del cacao por regiones (sin información personal identificable)</li>
        </ul>
      </div>

      <hr class="my-6 border-gray-200" />

      <!-- Sección 3: Protección y seguridad -->
      <div id="proteccion" class="mb-8">
        <h2 class="text-2xl font-bold text-gray-900 mb-4 flex items-center gap-2">
          <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
          </svg>
          <span>3. Protección y seguridad de los datos</span>
        </h2>
        <div class="space-y-3 text-gray-700 leading-relaxed">
          <p>
            <strong class="text-gray-900">3.1.</strong> Implementamos medidas de seguridad técnicas y organizacionales de acuerdo con los estándares de protección de datos personales. Esto incluye encriptación de datos sensibles, control de acceso, y monitoreo continuo de seguridad.
          </p>
          <p>
            <strong class="text-gray-900">3.2.</strong> Utilizamos tecnologías de encriptación (SSL/TLS) para proteger la transmisión de datos entre su dispositivo y nuestros servidores.
          </p>
          <p>
            <strong class="text-gray-900">3.3.</strong> Sin embargo, ningún método de transmisión por Internet o almacenamiento electrónico es 100% seguro. Aunque nos esforzamos por proteger su información, no podemos garantizar seguridad absoluta.
          </p>
        </div>
      </div>

      <hr class="my-6 border-gray-200" />

      <!-- Sección 4: Derechos del usuario -->
      <div id="derechos" class="mb-8">
        <h2 class="text-2xl font-bold text-gray-900 mb-4 flex items-center gap-2">
          <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
          </svg>
          <span>4. Derechos del usuario</span>
        </h2>
        <p class="text-gray-700 leading-relaxed mb-4">
          De acuerdo con la <strong class="text-gray-900">Ley 1581 de 2012</strong> de Colombia, usted tiene los siguientes derechos sobre sus datos personales:
        </p>
        <ul class="list-disc list-inside ml-4 space-y-2 text-gray-700 leading-relaxed">
          <li><strong class="text-gray-900">4.1.</strong> Conocer, actualizar y rectificar sus datos personales en cualquier momento</li>
          <li><strong class="text-gray-900">4.2.</strong> Solicitar prueba de la autorización otorgada para el tratamiento de sus datos</li>
          <li><strong class="text-gray-900">4.3.</strong> Revocar la autorización y/o solicitar la supresión del dato cuando considere que el tratamiento no respeta los principios constitucionales y legales</li>
          <li><strong class="text-gray-900">4.4.</strong> Acceder de forma gratuita a sus datos personales que hayan sido objeto de tratamiento</li>
          <li><strong class="text-gray-900">4.5.</strong> Presentar quejas ante la Superintendencia de Industria y Comercio (SIC) por infracciones a la normativa de protección de datos</li>
        </ul>
        <p class="text-gray-700 leading-relaxed mt-4">
          Para ejercer cualquiera de estos derechos, puede contactarnos a través de los canales oficiales del SENA.
        </p>
      </div>

      <hr class="my-6 border-gray-200" />

      <!-- Sección 5: Cookies y tecnologías similares -->
      <div id="cookies" class="mb-8">
        <h2 class="text-2xl font-bold text-gray-900 mb-4 flex items-center gap-2">
          <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
          </svg>
          <span>5. Cookies y tecnologías similares</span>
        </h2>
        <div class="space-y-3 text-gray-700 leading-relaxed">
          <p>
            <strong class="text-gray-900">5.1.</strong> Utilizamos cookies y tecnologías similares para mejorar su experiencia en la plataforma, recordar sus preferencias, y analizar el uso del servicio.
          </p>
          <p>
            <strong class="text-gray-900">5.2.</strong> Puede configurar su navegador para rechazar cookies, aunque esto puede afectar algunas funcionalidades de la plataforma. Las cookies esenciales para el funcionamiento del servicio no pueden ser deshabilitadas.
          </p>
        </div>
      </div>

      <hr class="my-6 border-gray-200" />

      <!-- Sección 6: Compartición con terceros -->
      <div id="terceros" class="mb-8">
        <h2 class="text-2xl font-bold text-gray-900 mb-4 flex items-center gap-2">
          <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
          </svg>
          <span>6. Compartición de datos con terceros</span>
        </h2>
        <div class="space-y-3 text-gray-700 leading-relaxed">
          <p>
            <strong class="text-gray-900">6.1.</strong> <strong class="text-green-600">No vendemos ni alquilamos su información personal a terceros.</strong> Respetamos su privacidad y tratamos sus datos con la máxima confidencialidad.
          </p>
          <p>
            <strong class="text-gray-900">6.2.</strong> Podemos compartir información únicamente en las siguientes circunstancias:
          </p>
          <ul class="list-disc list-inside ml-4 space-y-2 mt-3">
            <li>Con proveedores de servicios que nos ayudan a operar la plataforma (hosting, análisis), bajo estrictos acuerdos de confidencialidad</li>
            <li>Cuando sea requerido por ley o proceso legal en Colombia</li>
            <li>Para proteger los derechos, seguridad y propiedad de CacaoScan y sus usuarios</li>
          </ul>
        </div>
      </div>

      <hr class="my-6 border-gray-200" />

      <!-- Sección 7: Retención de datos -->
      <div class="mb-8">
        <h2 class="text-2xl font-bold text-gray-900 mb-4 flex items-center gap-2">
          <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4" />
          </svg>
          <span>7. Retención de datos</span>
        </h2>
        <div class="space-y-3 text-gray-700 leading-relaxed">
          <p>
            <strong class="text-gray-900">7.1.</strong> Conservamos su información mientras su cuenta esté activa o según sea necesario para proporcionar nuestros servicios.
          </p>
          <p>
            <strong class="text-gray-900">7.2.</strong> Podemos retener cierta información incluso después del cierre de su cuenta para cumplir con obligaciones legales, resolver disputas y hacer cumplir nuestros acuerdos.
          </p>
        </div>
      </div>

      <hr class="my-6 border-gray-200" />

      <!-- Sección 8: Menores de edad -->
      <div class="mb-8">
        <h2 class="text-2xl font-bold text-gray-900 mb-4 flex items-center gap-2">
          <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
          </svg>
          <span>8. Menores de edad</span>
        </h2>
        <p class="text-gray-700 leading-relaxed">
          CacaoScan no está dirigido a menores de 18 años. No recopilamos intencionalmente información personal de menores. Si descubrimos que hemos recopilado información de un menor sin el consentimiento apropiado, tomaremos medidas para eliminar esa información de nuestros sistemas.
        </p>
      </div>

      <hr class="my-6 border-gray-200" />

      <!-- Sección 9: Modificaciones de la política -->
      <div id="modificaciones" class="mb-8">
        <h2 class="text-2xl font-bold text-gray-900 mb-4 flex items-center gap-2">
          <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
          </svg>
          <span>9. Modificaciones de la política</span>
        </h2>
        <p class="text-gray-700 leading-relaxed">
          Podemos actualizar esta política de privacidad ocasionalmente para reflejar cambios en nuestras prácticas o por razones legales, operativas o regulatorias. Le notificaremos de cambios significativos mediante un aviso en la plataforma o por correo electrónico. La fecha de última actualización se muestra al inicio de este documento.
        </p>
      </div>

      <hr class="my-6 border-gray-200" />

      <!-- Sección 10: Contacto -->
      <div id="contacto" class="mb-8">
        <h2 class="text-2xl font-bold text-gray-900 mb-4 flex items-center gap-2">
          <svg class="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
          </svg>
          <span>10. Contacto</span>
        </h2>
        <p class="text-gray-700 leading-relaxed">
          Para ejercer sus derechos de protección de datos, hacer consultas sobre esta política, solicitar acceso, rectificación, supresión o revocación de autorización sobre sus datos personales, puede contactarnos a través de los canales oficiales del <strong class="text-gray-900">SENA Guaviare</strong>.
        </p>
      </div>

      <hr class="my-6 border-gray-200" />

      <!-- Fecha de actualización -->
      <div class="mt-8 pt-6 border-t border-gray-200">
        <p class="text-sm text-gray-600">
          <strong>Fecha de última actualización:</strong> Octubre 2025
        </p>
      </div>
    </template>

    <!-- Acciones al final -->
    <template #actions>
      <div class="flex flex-col sm:flex-row gap-4 justify-center">
        <router-link
          to="/registro"
          class="inline-flex items-center justify-center gap-2 px-6 py-3 bg-green-500 hover:bg-green-600 text-white font-semibold rounded-lg shadow-md hover:shadow-lg transition-all duration-200 hover:scale-[1.02] focus:ring-4 focus:ring-green-300"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
          </svg>
          Ir al registro
        </router-link>
        <router-link
          to="/"
          class="inline-flex items-center justify-center gap-2 px-6 py-3 bg-white border-2 border-green-500 text-green-600 hover:bg-green-50 font-semibold rounded-lg shadow-md hover:shadow-lg transition-all duration-200 hover:scale-[1.02] focus:ring-4 focus:ring-green-300"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
          </svg>
          Volver al inicio
        </router-link>
      </div>
    </template>
  </LegalLayout>
</template>

<script setup>
import LegalLayout from '@/components/legal/LegalLayout.vue'

/**
 * Vista de Política de Privacidad
 * 
 * Esta vista muestra la política de privacidad de la plataforma CacaoScan.
 * El contenido es completamente estático y se renderiza en el frontend, por lo que
 * no requiere llamadas al backend. Incluye navegación interna mediante anclas HTML.
 * 
 * @component PrivacyPolicyView
 */
</script>

<style scoped>
/* Scroll suave para navegación con anclas */
html {
  scroll-behavior: smooth;
}

/* Offset para anclas con header sticky */
section[id] {
  scroll-margin-top: 100px;
}
</style>
