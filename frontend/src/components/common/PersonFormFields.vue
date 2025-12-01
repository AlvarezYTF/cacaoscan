<template>
  <div class="space-y-6">
    <!-- Nombres -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div>
        <label :for="`${fieldPrefix}-primer-nombre`" class="block text-sm font-semibold text-gray-700 mb-2">
          Primer Nombre <span v-if="required" class="text-red-500">*</span>
        </label>
        <input
          :id="`${fieldPrefix}-primer-nombre`"
          v-model="modelValue.primer_nombre"
          type="text"
          autocomplete="given-name"
          :class="getInputClasses('primer_nombre')"
          :placeholder="placeholders.primer_nombre || 'Juan'"
        />
        <p v-if="errors?.primer_nombre" class="text-red-600 text-xs mt-1">{{ errors.primer_nombre }}</p>
      </div>
      <div>
        <label :for="`${fieldPrefix}-segundo-nombre`" class="block text-sm font-semibold text-gray-700 mb-2">
          Segundo Nombre
        </label>
        <input
          :id="`${fieldPrefix}-segundo-nombre`"
          v-model="modelValue.segundo_nombre"
          type="text"
          autocomplete="additional-name"
          :class="baseInputClasses"
          :placeholder="placeholders.segundo_nombre || 'Carlos (opcional)'"
        />
      </div>
    </div>

    <!-- Apellidos -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div>
        <label :for="`${fieldPrefix}-primer-apellido`" class="block text-sm font-semibold text-gray-700 mb-2">
          Primer Apellido <span v-if="required" class="text-red-500">*</span>
        </label>
        <input
          :id="`${fieldPrefix}-primer-apellido`"
          v-model="modelValue.primer_apellido"
          type="text"
          autocomplete="family-name"
          :class="getInputClasses('primer_apellido')"
          :placeholder="placeholders.primer_apellido || 'Pérez'"
        />
        <p v-if="errors?.primer_apellido" class="text-red-600 text-xs mt-1">{{ errors.primer_apellido }}</p>
      </div>
      <div>
        <label :for="`${fieldPrefix}-segundo-apellido`" class="block text-sm font-semibold text-gray-700 mb-2">
          Segundo Apellido
        </label>
        <input
          :id="`${fieldPrefix}-segundo-apellido`"
          v-model="modelValue.segundo_apellido"
          type="text"
          autocomplete="family-name"
          :class="baseInputClasses"
          :placeholder="placeholders.segundo_apellido || 'García (opcional)'"
        />
      </div>
    </div>

    <!-- Tipo Documento y Número -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div>
        <label :for="`${fieldPrefix}-tipo-documento`" class="block text-sm font-semibold text-gray-700 mb-2">
          Tipo de Documento <span v-if="required" class="text-red-500">*</span>
        </label>
        <select
          :id="`${fieldPrefix}-tipo-documento`"
          v-model="modelValue.tipo_documento"
          :class="getInputClasses('tipo_documento')"
        >
          <option value="">Seleccionar...</option>
          <option v-for="tipo in tiposDocumento" :key="tipo.codigo" :value="tipo.codigo">
            {{ tipo.nombre }}
          </option>
        </select>
        <p v-if="errors?.tipo_documento" class="text-red-600 text-xs mt-1">{{ errors.tipo_documento }}</p>
      </div>
      <div>
        <label :for="`${fieldPrefix}-numero-documento`" class="block text-sm font-semibold text-gray-700 mb-2">
          Número de Documento <span v-if="required" class="text-red-500">*</span>
        </label>
        <input
          :id="`${fieldPrefix}-numero-documento`"
          v-model="modelValue.numero_documento"
          type="text"
          autocomplete="off"
          :class="getInputClasses('numero_documento')"
          :placeholder="placeholders.numero_documento || '1012345678'"
        />
        <p v-if="errors?.numero_documento" class="text-red-600 text-xs mt-1">{{ errors.numero_documento }}</p>
      </div>
    </div>

    <!-- Género y Fecha de Nacimiento -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div>
        <label :for="`${fieldPrefix}-genero`" class="block text-sm font-semibold text-gray-700 mb-2">
          Género <span v-if="required" class="text-red-500">*</span>
        </label>
        <select
          :id="`${fieldPrefix}-genero`"
          v-model="modelValue.genero"
          :class="getInputClasses('genero')"
        >
          <option value="">Seleccionar...</option>
          <option v-for="gen in generos" :key="gen.codigo" :value="gen.codigo">{{ gen.nombre }}</option>
        </select>
        <p v-if="errors?.genero" class="text-red-600 text-xs mt-1">{{ errors.genero }}</p>
      </div>
      <div>
        <label :for="`${fieldPrefix}-fecha-nacimiento`" class="block text-sm font-semibold text-gray-700 mb-2">
          Fecha de Nacimiento
        </label>
        <input
          :id="`${fieldPrefix}-fecha-nacimiento`"
          type="date"
          v-model="modelValue.fecha_nacimiento"
          autocomplete="bday"
          :max="maxBirthdate"
          :min="minBirthdate"
          :class="getInputClasses('fecha_nacimiento')"
        />
        <p v-if="errors?.fecha_nacimiento" class="text-red-600 text-xs mt-1">{{ errors.fecha_nacimiento }}</p>
      </div>
    </div>

    <!-- Email y Teléfono -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div>
        <label :for="`${fieldPrefix}-email`" class="block text-sm font-semibold text-gray-700 mb-2">
          Email <span v-if="required" class="text-red-500">*</span>
        </label>
        <input
          :id="`${fieldPrefix}-email`"
          :value="emailModel || modelValue.email"
          @input="$emit('update:emailModel', $event.target.value)"
          type="email"
          autocomplete="email"
          :class="getInputClasses('email')"
          :placeholder="placeholders.email || 'nombre@email.com'"
        />
        <p v-if="errors?.email" class="text-red-600 text-xs mt-1">{{ errors.email }}</p>
      </div>
      <div>
        <label :for="`${fieldPrefix}-telefono`" class="block text-sm font-semibold text-gray-700 mb-2">
          Teléfono <span v-if="required" class="text-red-500">*</span>
        </label>
        <input
          :id="`${fieldPrefix}-telefono`"
          v-model="modelValue.telefono"
          type="tel"
          autocomplete="tel"
          :class="getInputClasses('telefono')"
          :placeholder="placeholders.telefono || '+57 300 123 4567'"
        />
        <p v-if="errors?.telefono" class="text-red-600 text-xs mt-1">{{ errors.telefono }}</p>
      </div>
    </div>

    <!-- Dirección -->
    <div>
      <label :for="`${fieldPrefix}-direccion`" class="block text-sm font-semibold text-gray-700 mb-2">
        Dirección
      </label>
      <input
        :id="`${fieldPrefix}-direccion`"
        name="direccion"
        v-model="modelValue.direccion"
        type="text"
        autocomplete="address-line1"
        :class="baseInputClasses"
        :placeholder="placeholders.direccion || 'Calle 10 #5-20'"
      />
    </div>

    <!-- Ubicación -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div>
        <label :for="`${fieldPrefix}-departamento`" class="block text-sm font-semibold text-gray-700 mb-2">
          Departamento
        </label>
        <select
          :id="`${fieldPrefix}-departamento`"
          v-model="modelValue.departamento"
          @change="onDepartamentoChange"
          :class="baseInputClasses"
        >
          <option value="">Seleccionar...</option>
          <option v-for="depto in departamentos" :key="depto.id" :value="depto.id">{{ depto.nombre }}</option>
        </select>
      </div>
      <div>
        <label :for="`${fieldPrefix}-municipio`" class="block text-sm font-semibold text-gray-700 mb-2">
          Municipio
        </label>
        <select
          :id="`${fieldPrefix}-municipio`"
          v-model="modelValue.municipio"
          :disabled="!modelValue.departamento"
          :class="baseInputClasses"
        >
          <option value="">Seleccionar...</option>
          <option v-for="mun in municipios" :key="mun.id" :value="mun.id">{{ mun.nombre }}</option>
        </select>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  modelValue: {
    type: Object,
    required: true
  },
  emailModel: {
    type: String,
    default: ''
  },
  errors: {
    type: Object,
    default: () => ({})
  },
  tiposDocumento: {
    type: Array,
    required: true
  },
  generos: {
    type: Array,
    required: true
  },
  departamentos: {
    type: Array,
    required: true
  },
  municipios: {
    type: Array,
    required: true
  },
  maxBirthdate: {
    type: String,
    required: true
  },
  minBirthdate: {
    type: String,
    required: true
  },
  baseInputClasses: {
    type: String,
    default: 'w-full px-4 py-3 border-2 border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500/50 focus:border-green-500'
  },
  getInputClasses: {
    type: Function,
    default: (fieldName) => props.baseInputClasses
  },
  fieldPrefix: {
    type: String,
    default: 'person'
  },
  required: {
    type: Boolean,
    default: true
  },
  placeholders: {
    type: Object,
    default: () => ({})
  },
  onDepartamentoChange: {
    type: Function,
    default: () => {}
  }
})

const emit = defineEmits(['update:modelValue', 'update:emailModel'])
</script>

