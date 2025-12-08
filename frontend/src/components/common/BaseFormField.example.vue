<!--
  EJEMPLO DE USO DE BaseFormField
  
  Este componente demuestra cómo usar BaseFormField para reducir
  la duplicación de código en formularios.
  
  ANTES (código duplicado):
  <div>
    <label for="email" class="block text-sm font-semibold text-gray-700 mb-2">
      Email <span class="text-red-500">*</span>
    </label>
    <input 
      id="email"
      v-model="form.email" 
      type="email" 
      required
      class="w-full px-4 py-2.5 border rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500"
      :class="errors.email ? 'border-red-500' : 'border-gray-300'" 
      placeholder="juan@ejemplo.com" 
    />
    <p v-if="errors.email" class="text-red-600 text-xs mt-1">{{ errors.email }}</p>
  </div>
  
  DESPUÉS (usando BaseFormField):
  <BaseFormField 
    id="email"
    label="Email"
    :error="errors.email"
    :required="true"
  >
    <input 
      id="email"
      v-model="form.email" 
      type="email" 
      required
      class="w-full px-4 py-2.5 border rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500"
      :class="errors.email ? 'border-red-500' : 'border-gray-300'" 
      placeholder="juan@ejemplo.com" 
    />
  </BaseFormField>
-->

<template>
  <div class="p-6 space-y-4">
    <h2 class="text-2xl font-bold mb-4">Ejemplo de uso de BaseFormField</h2>
    
    <form @submit.prevent="handleSubmit" class="space-y-4">
      <!-- Ejemplo 1: Campo de texto simple -->
      <BaseFormField 
        name="nombre"
        label="Nombre"
        :error="errors.nombre"
        :required="true"
      >
        <template #default="{ fieldId }">
          <input 
            :id="fieldId"
            v-model="form.nombre" 
            type="text" 
            required
            class="w-full px-4 py-2.5 border rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500"
            :class="errors.nombre ? 'border-red-500' : 'border-gray-300'" 
            placeholder="Juan" 
          />
        </template>
      </BaseFormField>

      <!-- Ejemplo 2: Campo de email -->
      <BaseFormField 
        name="email"
        label="Email"
        :error="errors.email"
        :required="true"
        help-text="Ingresa un email válido"
      >
        <template #default="{ fieldId }">
          <input 
            :id="fieldId"
            v-model="form.email" 
            type="email" 
            required
            class="w-full px-4 py-2.5 border rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500"
            :class="errors.email ? 'border-red-500' : 'border-gray-300'" 
            placeholder="juan@ejemplo.com" 
          />
        </template>
      </BaseFormField>

      <!-- Ejemplo 3: Campo de teléfono -->
      <BaseFormField 
        name="telefono"
        label="Teléfono"
        :error="errors.telefono"
        help-text="Formato: +57 300 123 4567"
      >
        <template #default="{ fieldId }">
          <input 
            :id="fieldId"
            v-model="form.telefono" 
            type="tel" 
            class="w-full px-4 py-2.5 border rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500"
            :class="errors.telefono ? 'border-red-500' : 'border-gray-300'" 
            placeholder="+57 300 123 4567" 
          />
        </template>
      </BaseFormField>

      <!-- Ejemplo 4: Select -->
      <BaseFormField 
        name="pais"
        label="País"
        :error="errors.pais"
        :required="true"
      >
        <template #default="{ fieldId }">
          <select 
            :id="fieldId"
            v-model="form.pais" 
            required
            class="w-full px-4 py-2.5 border rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500"
            :class="errors.pais ? 'border-red-500' : 'border-gray-300'"
          >
            <option value="">Selecciona un país</option>
            <option value="CO">Colombia</option>
            <option value="EC">Ecuador</option>
            <option value="PE">Perú</option>
          </select>
        </template>
      </BaseFormField>

      <!-- Ejemplo 5: Textarea -->
      <BaseFormField 
        name="comentarios"
        label="Comentarios"
        :error="errors.comentarios"
        help-text="Máximo 500 caracteres"
      >
        <template #default="{ fieldId }">
          <textarea 
            :id="fieldId"
            v-model="form.comentarios" 
            rows="4"
            maxlength="500"
            class="w-full px-4 py-2.5 border rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500"
            :class="errors.comentarios ? 'border-red-500' : 'border-gray-300'" 
            placeholder="Escribe tus comentarios aquí..."
          ></textarea>
        </template>
      </BaseFormField>

      <div class="flex justify-end gap-3">
        <button 
          type="button" 
          @click="resetForm"
          class="px-6 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600"
        >
          Limpiar
        </button>
        <button 
          type="submit"
          class="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
        >
          Enviar
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { reactive } from 'vue'
import BaseFormField from './BaseFormField.vue'
import { useFormValidation } from '@/composables/useFormValidation'

const { isValidEmail } = useFormValidation()

const form = reactive({
  nombre: '',
  email: '',
  telefono: '',
  pais: '',
  comentarios: ''
})

const errors = reactive({
  nombre: '',
  email: '',
  telefono: '',
  pais: '',
  comentarios: ''
})

const resetForm = () => {
  for (const key of Object.keys(form)) {
    form[key] = ''
    errors[key] = ''
  }
}

const handleSubmit = () => {
  // Validación simple de ejemplo
  if (form.nombre) {
    errors.nombre = ''
  } else {
    errors.nombre = 'El nombre es requerido'
  }

  if (form.email) {
    // Use secure email validation function to prevent ReDoS attacks
    if (isValidEmail(form.email)) {
      errors.email = ''
    } else {
      errors.email = 'Ingresa un email válido'
    }
  } else {
    errors.email = 'El email es requerido'
  }

  // Si no hay errores, enviar formulario
  const hasErrors = Object.values(errors).some(Boolean)
  if (hasErrors) {
    return
  }
  alert('Formulario enviado correctamente')
}
</script>

