<script setup>
  import { ref, computed } from 'vue'
  import { useRouter, useRoute } from 'vue-router'
  import authService from '@/services/authService'
  import { useAuthStore } from '@/stores/auth'
  const router = useRouter(),
    route = useRoute(),
    auth = useAuthStore(),
    nombre = ref(''),
    correo = ref(''),
    username = ref(''),
    password = ref(''),
    loading = ref(false),
    error = ref('')
  const redirect = computed(() =>
    typeof route.query.redirect === 'string' &&
    route.query.redirect.startsWith('/') &&
    !route.query.redirect.startsWith('//')
      ? route.query.redirect
      : '/',
  )
  async function submit() {
    loading.value = true
    error.value = ''
    try {
      await authService.registrar({
        nombre: nombre.value,
        correo: correo.value,
        username: username.value,
        password: password.value,
      })
      await auth.login(username.value, password.value)
      router.replace(redirect.value)
    } catch (e) {
      error.value = e.response?.data?.error || 'No fue posible completar el registro.'
    } finally {
      loading.value = false
    }
  }
</script>
<template>
  <div class="auth-screen">
    <div class="auth-panel">
      <RouterLink to="/" class="text-secondary text-decoration-none">← Volver a ofertas</RouterLink>
      <div class="section-kicker mt-4">ÚNETE A MB</div>
      <h1 class="section-title">Crea tu cuenta<span class="text-danger">.</span></h1>
      <p class="text-secondary">
        {{
          redirect === '/checkout'
            ? 'Crea tu cuenta para completar tu pedido. Tu carrito seguirá guardado.'
            : 'Regístrate y guarda tus descuentos favoritos.'
        }}
      </p>
      <div v-if="error" class="alert alert-danger" role="alert">{{ error }}</div>
      <form @submit.prevent="submit">
        <label class="form-label" for="nombre">Nombre completo</label
        ><input id="nombre" v-model="nombre" class="form-control mb-3" required /><label
          class="form-label"
          for="correo"
          >Correo</label
        ><input
          id="correo"
          v-model="correo"
          type="email"
          class="form-control mb-3"
          required
        /><label class="form-label" for="usuario">Usuario</label
        ><input id="usuario" v-model="username" class="form-control mb-3" required /><label
          class="form-label"
          for="password"
          >Contraseña (mínimo 8 caracteres)</label
        ><input
          id="password"
          v-model="password"
          type="password"
          minlength="8"
          class="form-control mb-4"
          required
        /><button class="btn btn-dark btn-lg w-100" :disabled="loading">
          {{ loading ? 'Creando cuenta...' : 'Crear cuenta →' }}
        </button>
      </form>
      <p class="mt-4">
        ¿Ya tienes cuenta?
        <RouterLink :to="{ name: 'login', query: { redirect } }">Inicia sesión</RouterLink>
      </p>
    </div>
    <div class="auth-promo">
      <span>MB / MULTIBRAND</span>
      <h2>BUEN ESTILO.<br />MEJOR PRECIO.</h2>
      <p>Explora, elige y ahorra.</p>
    </div>
  </div>
</template>
