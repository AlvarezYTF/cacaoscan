<template>
  <div class="auth-background min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
    <div class="auth-form-container w-full max-w-md py-8 px-6 sm:px-10">
      <LoginForm />
    </div>
  </div>
</template>

<script setup>
import LoginForm from '@/components/auth/LoginForm.vue'
</script>