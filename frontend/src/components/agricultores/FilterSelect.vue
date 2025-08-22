<template>
  <div>
    <label :for="id" class="block text-xs md:text-sm font-medium text-gray-700 mb-1">{{ label }}</label>
    <select 
      :id="id"
      :value="modelValue"
      @change="$emit('update:modelValue', $event.target.value)"
      class="block w-full rounded-md border-gray-300 shadow-sm focus:border-green-500 focus:ring-green-500 text-xs md:text-sm transition-all duration-200"
    >
      <option v-for="option in options" :key="option.value" :value="option.value">
        {{ option.label }}
      </option>
    </select>
  </div>
</template>

<script>
export default {
  name: 'FilterSelect',
  props: {
    id: {
      type: String,
      required: true
    },
    label: {
      type: String,
      required: true
    },
    modelValue: {
      type: String,
      default: ''
    },
    options: {
      type: Array,
      required: true,
      validator: (value) => value.every(option => 'value' in option && 'label' in option)
    }
  },
  emits: ['update:modelValue']
};
</script>
