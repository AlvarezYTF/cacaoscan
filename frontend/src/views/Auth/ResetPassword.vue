<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-b from-green-50 to-white">
    <div class="bg-white rounded-2xl shadow-lg p-8 sm:p-10 w-full max-w-md">
      <div class="text-center mb-6">
        <h2 class="text-3xl font-bold text-green-700">🔐 Restablecer Contraseña</h2>
        <p class="text-gray-600 text-sm mt-2">Ingresa tu nueva contraseña para continuar</p>
      </div>

      <form @submit.prevent="handleSubmit" class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700">Nueva Contraseña</label>
          <input
            v-model="password"
            type="password"
            placeholder="••••••••"
            class="mt-1 w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-green-600 focus:outline-none"
            required
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700">Confirmar Contraseña</label>
          <input
            v-model="confirmPassword"
            type="password"
            placeholder="••••••••"
            class="mt-1 w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-green-600 focus:outline-none"
            required
          />
        </div>

        <button
          type="submit"
          :disabled="loading"
          class="w-full bg-green-600 text-white py-2 rounded-lg font-semibold hover:bg-green-700 transition disabled:opacity-50"
        >
          {{ loading ? "Procesando..." : "Restablecer Contraseña" }}
        </button>

        <p v-if="message" :class="messageColor" class="text-center text-sm mt-3">
          {{ message }}
        </p>

        <div class="text-center mt-6">
          <router-link
            to="/login"
            class="text-green-700 font-semibold hover:underline text-sm"
          >
            ← Volver al inicio de sesión
          </router-link>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import api from "@/services/api";

export default {
  name: "ResetPassword",
  data() {
    return {
      password: "",
      confirmPassword: "",
      loading: false,
      message: "",
      success: false,
    };
  },
  computed: {
    token() {
      return this.$route.query.token; // lee el token de la URL
    },
    messageColor() {
      return this.success ? "text-green-700" : "text-red-600";
    },
  },
  mounted() {
    // Validar que existe token en la URL
    if (!this.token) {
      this.message = "❌ Token no encontrado. El enlace es inválido.";
      setTimeout(() => {
        this.$router.push("/reset-password");
      }, 2000);
    }
  },
  methods: {
    async handleSubmit() {
      this.loading = true;
      this.message = "";
      this.success = false;

      try {
        const res = await api.post("/auth/reset-password/", {
          token: this.token,
          new_password: this.password,
          confirm_password: this.confirmPassword,
        });

        if (res.data.success) {
          this.message = "✅ Contraseña actualizada correctamente. Redirigiendo...";
          this.success = true;
          setTimeout(() => this.$router.push("/login"), 2500);
        } else {
          this.message = res.data.message || "⚠️ No fue posible restablecer la contraseña.";
        }
      } catch (err) {
        this.message =
          err.response?.data?.message ||
          "❌ Error al conectar con el servidor. Intenta nuevamente.";
      } finally {
        this.loading = false;
      }
    },
  },
};
</script>

