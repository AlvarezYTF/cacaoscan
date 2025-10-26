<template>
  <div class="bg-white rounded-xl shadow-lg border border-gray-200 p-6">
    <div class="flex items-center gap-4">
      <div class="flex-1 relative">
        <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
          <svg class="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
          </svg>
        </div>
        <input 
          type="text" 
          :value="searchQuery"
          @input="$emit('update:searchQuery', $event.target.value)"
          :placeholder="placeholder"
          class="w-full pl-12 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500 transition-all duration-200 bg-gray-50"
        />
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'FarmersSearchBar',
  props: {
    searchQuery: {
      type: String,
      required: true
    },
    placeholder: {
      type: String,
      default: 'Buscar agricultor por nombre, email o finca...'
    }
  },
  emits: ['update:searchQuery']
};
</script>

