<template>
  <div class="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden hover:shadow-md transition-all duration-300">
    <div class="overflow-x-auto">
      <table class="min-w-full divide-y divide-gray-200">
        <thead class="bg-gray-50">
          <tr>
            <th 
              v-for="column in columns" 
              :key="column.key"
              scope="col" 
              class="px-3 md:px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
              :class="column.align === 'right' ? 'text-right' : 'text-left'"
            >
              {{ column.label }}
            </th>
          </tr>
        </thead>
        <tbody class="bg-white divide-y divide-gray-200">
          <tr 
            v-for="(row, index) in data" 
            :key="index"
            class="hover:bg-gray-50 transition-all duration-200"
          >
            <td 
              v-for="column in columns" 
              :key="column.key"
              class="px-3 md:px-6 py-3 md:py-4 whitespace-nowrap"
              :class="column.align === 'right' ? 'text-right' : 'text-left'"
            >
              <slot :name="`cell-${column.key}`" :row="row" :column="column">
                {{ row[column.key] }}
              </slot>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    
    <!-- Paginación -->
    <slot name="pagination"></slot>
  </div>
</template>

<script>
export default {
  name: 'DataTable',
  props: {
    columns: {
      type: Array,
      required: true,
      validator: (value) => value.every(col => 'key' in col && 'label' in col)
    },
    data: {
      type: Array,
      required: true
    }
  }
};
</script>
