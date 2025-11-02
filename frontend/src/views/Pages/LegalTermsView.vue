<template>
  <!-- Vista de Términos y Condiciones - Diseño profesional con navegación interna -->
  <LegalLayout>
    <!-- Encabezado con título y fecha -->
    <template #header>
      <div>
        <h1 id="inicio" class="text-3xl md:text-4xl font-bold text-gray-900 mb-2">
          Términos y Condiciones
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
          <a href="#aceptacion" class="text-gray-700 hover:text-green-600 transition-colors text-sm py-1">
            • Aceptación de los términos
          </a>
          <a href="#descripcion" class="text-gray-700 hover:text-green-600 transition-colors text-sm py-1">
            • Descripción del servicio
          </a>
          <a href="#registro" class="text-gray-700 hover:text-green-600 transition-colors text-sm py-1">
            • Registro y cuenta de usuario
          </a>
          <a href="#uso" class="text-gray-700 hover:text-green-600 transition-colors text-sm py-1">
            • Uso permitido y restricciones
          </a>
          <a href="#propiedad" class="text-gray-700 hover:text-green-600 transition-colors text-sm py-1">
            • Propiedad intelectual
          </a>
          <a href="#responsabilidad" class="text-gray-700 hover:text-green-600 transition-colors text-sm py-1">
            • Limitación de responsabilidad
          </a>
          <a href="#privacidad" class="text-gray-700 hover:text-green-600 transition-colors text-sm py-1">
            • Privacidad y protección de datos
          </a>
          <a href="#modificaciones" class="text-gray-700 hover:text-green-600 transition-colors text-sm py-1">
            • Modificaciones de los términos
          </a>
          <a href="#legislacion" class="text-gray-700 hover:text-green-600 transition-colors text-sm py-1">
            • Legislación aplicable
          </a>
        </nav>
      </div>
    </template>

    <!-- Contenido principal -->
    <template #content>
      <!-- Introducción -->
      <div id="introduccion" class="mb-8">
        <p class="text-lg text-gray-700 leading-relaxed">
          CacaoScan es una plataforma desarrollada por aprendices del SENA como parte del programa de formación técnica en análisis de sistemas. Esta plataforma proporciona herramientas avanzadas para el análisis y gestión de calidad del cacao mediante inteligencia artificial y machine learning.
        </p>
      </div>

      <hr class="my-6 border-gray-200" />

      <!-- Sección 1: Aceptación de los términos -->
      <div id="aceptacion" class="mb-8">
        <h2 class="text-2xl font-bold text-gray-900 mb-4 flex items-center gap-2">
          <span class="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center text-green-600 font-semibold text-sm">1</span>
          Aceptación de los términos
        </h2>
        <p class="text-gray-700 leading-relaxed mb-4">
          Al acceder y utilizar CacaoScan, usted acepta estar sujeto a estos términos y condiciones de uso. Si no está de acuerdo con alguna parte de estos términos, no debe utilizar nuestra plataforma.
        </p>
        <p class="text-gray-700 leading-relaxed">
          El uso continuado de nuestros servicios implica la aceptación de estos términos y cualquier modificación posterior que realicemos.
        </p>
      </div>

      <hr class="my-6 border-gray-200" />

          <!-- Sección 2: Descripción del servicio -->
          <div id="descripcion" class="mb-8">
            <h2 class="text-2xl font-bold text-gray-900 mb-4 flex items-center gap-2">
              <span class="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center text-green-600 font-semibold text-sm">2</span>
              Descripción del servicio CacaoScan
            </h2>
            <p class="text-gray-700 leading-relaxed mb-4">
              CacaoScan proporciona herramientas especializadas para el análisis de granos de cacao mediante técnicas de machine learning (YOLOv8) y visión artificial, permitiendo a los usuarios:
            </p>
            <ul class="list-disc list-inside ml-4 space-y-2 text-gray-700">
              <li>Subir y gestionar imágenes de granos de cacao para análisis automatizado (máximo 20MB por imagen)</li>
              <li>Realizar análisis precisos de dimensiones en milímetros: alto, ancho y grosor de los granos</li>
              <li>Calcular el peso estimado de los granos en gramos mediante modelos de machine learning</li>
              <li>Análisis individual y por lotes (múltiples imágenes en una operación)</li>
              <li>Gestión completa de fincas con información de ubicación (nombre, dirección, municipio, departamento, coordenadas GPS, hectáreas)</li>
              <li>Gestión de lotes dentro de fincas (identificador, variedad de cacao, fechas de plantación y cosecha, área en hectáreas, coordenadas GPS)</li>
              <li>Generar reportes detallados y estadísticas sobre la calidad del cacao y rendimiento por lote</li>
              <li>Acceder a historiales completos de análisis y comparar resultados a lo largo del tiempo</li>
              <li>Sistema de roles diferenciados: Administrador, Técnico/Analista y Agricultor, cada uno con permisos específicos</li>
            </ul>
          </div>

      <hr class="my-6 border-gray-200" />

          <!-- Sección 3: Registro y cuenta de usuario -->
          <div id="registro" class="mb-8">
            <h2 class="text-2xl font-bold text-gray-900 mb-4 flex items-center gap-2">
              <span class="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center text-green-600 font-semibold text-sm">3</span>
              Registro y cuenta de usuario
            </h2>
            <div class="space-y-3 text-gray-700 leading-relaxed">
              <p>
                <strong class="text-gray-900">3.1.</strong> Para utilizar ciertas funciones de CacaoScan, debe registrarse y crear una cuenta de usuario. El registro es gratuito y requiere proporcionar información veraz y actualizada, incluyendo:
              </p>
              <ul class="list-disc list-inside ml-6 mt-2 mb-4 space-y-1 text-gray-600">
                <li>Correo electrónico (requerido) y contraseña segura (mínimo 8 caracteres)</li>
                <li>Tipo y número de documento de identidad (requeridos)</li>
                <li>Nombre completo (primer nombre y apellido requeridos; segundo nombre y apellido opcionales)</li>
                <li>Teléfono de contacto (requerido)</li>
                <li>Dirección de residencia (opcional)</li>
                <li>Género (requerido: M, F u O)</li>
                <li>Fecha de nacimiento (opcional)</li>
                <li>Departamento y municipio de residencia (requeridos)</li>
              </ul>
              <p>
                <strong class="text-gray-900">3.2.</strong> Al registrarse, recibirá un correo electrónico de verificación. Debe verificar su correo para activar completamente su cuenta y acceder a todas las funcionalidades del sistema.
              </p>
              <p>
                <strong class="text-gray-900">3.3.</strong> Usted es responsable de mantener la confidencialidad de su cuenta y contraseña. Cualquier actividad realizada bajo su cuenta será de su responsabilidad.
              </p>
              <p>
                <strong class="text-gray-900">3.4.</strong> Debe proporcionar información precisa, completa y actualizada durante el proceso de registro. Cualquier información falsa o desactualizada puede resultar en la suspensión de su cuenta.
              </p>
              <p>
                <strong class="text-gray-900">3.5.</strong> Por defecto, los usuarios registrados obtienen el rol de "Agricultor". Los roles de "Administrador" y "Técnico/Analista" son asignados exclusivamente por los administradores del sistema.
              </p>
              <p>
                <strong class="text-gray-900">3.6.</strong> CacaoScan se reserva el derecho de rechazar o cancelar cuentas que violen estos términos, realicen actividades fraudulentas o comprometan la seguridad del sistema.
              </p>
            </div>
          </div>

      <hr class="my-6 border-gray-200" />

      <!-- Sección 4: Uso permitido y restricciones -->
      <div id="uso" class="mb-8">
        <h2 class="text-2xl font-bold text-gray-900 mb-4 flex items-center gap-2">
          <span class="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center text-green-600 font-semibold text-sm">4</span>
          Uso permitido y restricciones
        </h2>
        <p class="text-gray-700 leading-relaxed mb-4">
          <strong class="text-gray-900">4.1.</strong> Usted se compromete a utilizar CacaoScan únicamente para fines legales y apropiados relacionados con el análisis y gestión de cacao.
        </p>
        <p class="text-gray-700 leading-relaxed mb-4">
          <strong class="text-gray-900">4.2.</strong> Está estrictamente prohibido:
        </p>
        <ul class="list-disc list-inside ml-4 space-y-2 text-gray-700 mb-4">
          <li>Intentar acceder a áreas no autorizadas de la plataforma o sistemas relacionados</li>
          <li>Interferir, interrumpir o dañar el funcionamiento del servicio</li>
          <li>Cargar contenido malicioso, virus, código dañino o que viole derechos de terceros</li>
          <li>Utilizar la plataforma para actividades comerciales no autorizadas</li>
          <li>Suplantar la identidad de otros usuarios o proporcionar información falsa</li>
          <li>Realizar ingeniería inversa, descompilar o intentar extraer el código fuente del sistema</li>
        </ul>
        <p class="text-gray-700 leading-relaxed">
          El incumplimiento de estas restricciones puede resultar en la suspensión inmediata de su cuenta y acciones legales si corresponde.
        </p>
      </div>

      <hr class="my-6 border-gray-200" />

      <!-- Sección 5: Propiedad intelectual -->
      <div id="propiedad" class="mb-8">
        <h2 class="text-2xl font-bold text-gray-900 mb-4 flex items-center gap-2">
          <span class="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center text-green-600 font-semibold text-sm">5</span>
          Propiedad intelectual
        </h2>
        <div class="space-y-3 text-gray-700 leading-relaxed">
          <p>
            <strong class="text-gray-900">5.1.</strong> Todos los contenidos de CacaoScan, incluyendo diseño, textos, gráficos, logotipos, iconos, imágenes, código fuente y software, son propiedad de los desarrolladores del SENA o sus licenciantes, y están protegidos por las leyes de propiedad intelectual de Colombia.
          </p>
          <p>
            <strong class="text-gray-900">5.2.</strong> El contenido generado por los usuarios mediante la plataforma (imágenes, datos de análisis, información de fincas) pertenece al usuario. Sin embargo, al utilizar el servicio, usted otorga a CacaoScan una licencia no exclusiva para utilizar, procesar y analizar dicho contenido para mejorar el servicio.
          </p>
        </div>
      </div>

      <hr class="my-6 border-gray-200" />

          <!-- Sección 6: Limitación de responsabilidad -->
          <div id="responsabilidad" class="mb-8">
            <h2 class="text-2xl font-bold text-gray-900 mb-4 flex items-center gap-2">
              <span class="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center text-green-600 font-semibold text-sm">6</span>
              Limitación de responsabilidad
            </h2>
            <div class="space-y-3 text-gray-700 leading-relaxed">
              <p>
                <strong class="text-gray-900">6.1.</strong> CacaoScan se proporciona "tal cual" sin garantías de ningún tipo, expresas o implícitas. No garantizamos que el servicio esté libre de errores, interrupciones o que cumpla con todos sus requisitos específicos.
              </p>
              <p>
                <strong class="text-gray-900">6.2.</strong> CacaoScan no será responsable por daños directos, indirectos, incidentales o consecuentes resultantes del uso o la imposibilidad de usar la plataforma.
              </p>
              <p>
                <strong class="text-gray-900">6.3.</strong> Los resultados de los análisis proporcionados por CacaoScan (dimensiones en milímetros: alto, ancho, grosor; y peso estimado en gramos) son estimaciones basadas en algoritmos de machine learning (YOLOv8) y modelos predictivos. Estos resultados incluyen niveles de confianza, pero <strong>no deben ser considerados como mediciones oficiales certificadas sin validación adicional mediante métodos tradicionales de laboratorio</strong>.
              </p>
              <p>
                <strong class="text-gray-900">6.4.</strong> Los análisis se realizan sobre imágenes digitales. La calidad de los resultados depende directamente de la calidad y claridad de las imágenes proporcionadas. Imágenes borrosas, con poca iluminación o ángulos inadecuados pueden afectar la precisión de las mediciones.
              </p>
            </div>
          </div>

      <hr class="my-6 border-gray-200" />

      <!-- Sección 7: Privacidad y protección de datos -->
      <div id="privacidad" class="mb-8">
        <h2 class="text-2xl font-bold text-gray-900 mb-4 flex items-center gap-2">
          <span class="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center text-green-600 font-semibold text-sm">7</span>
          Privacidad y protección de datos
        </h2>
        <p class="text-gray-700 leading-relaxed">
          El uso de sus datos personales se rige por nuestra 
          <router-link to="/legal/privacy" class="text-green-600 hover:text-green-700 underline font-semibold">
            Política de Privacidad
          </router-link>, 
          que forma parte integral de estos términos. CacaoScan cumple con la Ley 1581 de 2012 sobre protección de datos personales y el Decreto 1377 de 2013 de Colombia.
        </p>
      </div>

      <hr class="my-6 border-gray-200" />

      <!-- Sección 8: Modificaciones de los términos -->
      <div id="modificaciones" class="mb-8">
        <h2 class="text-2xl font-bold text-gray-900 mb-4 flex items-center gap-2">
          <span class="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center text-green-600 font-semibold text-sm">8</span>
          Modificaciones de los términos
        </h2>
        <p class="text-gray-700 leading-relaxed">
          Nos reservamos el derecho de modificar estos términos y condiciones en cualquier momento. Los cambios entrarán en vigor al publicarlos en la plataforma. Es su responsabilidad revisar periódicamente estos términos. El uso continuado del servicio después de los cambios implica la aceptación de los términos modificados.
        </p>
      </div>

      <hr class="my-6 border-gray-200" />

      <!-- Sección 9: Legislación aplicable y jurisdicción -->
      <div id="legislacion" class="mb-8">
        <h2 class="text-2xl font-bold text-gray-900 mb-4 flex items-center gap-2">
          <span class="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center text-green-600 font-semibold text-sm">9</span>
          Legislación aplicable y jurisdicción
        </h2>
        <div class="space-y-3 text-gray-700 leading-relaxed">
          <p>
            Estos términos se rigen por las leyes de la República de Colombia. Cualquier disputa relacionada con estos términos o con el uso de CacaoScan será resuelta en los tribunales competentes de Colombia.
          </p>
          <p>
            Para consultas sobre estos términos, puede contactarnos a través de los canales oficiales del SENA Guaviare.
          </p>
        </div>
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
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          Aceptar y continuar al registro
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

// Vista de términos y condiciones con contenido estático y navegación interna
// No requiere llamadas al backend - todo el contenido está en el frontend
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
