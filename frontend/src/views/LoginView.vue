<script setup>
  import { ref, computed } from 'vue'
  import { useRouter, useRoute } from 'vue-router'
  import { useAuthStore } from '@/stores/auth'
  const router = useRouter(),
    route = useRoute(),
    auth = useAuthStore(),
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
      await auth.login(username.value, password.value)
      router.replace(redirect.value)
    } catch (e) {
      error.value = e.response?.data?.error || 'No se pudo iniciar sesión. Revisa el servidor.'
    } finally {
      loading.value = false
    }
  }
</script>
<template>
  <div class="auth-screen">
    <div class="auth-panel">
      <RouterLink to="/" class="text-secondary text-decoration-none">← Volver a ofertas</RouterLink>
      <div class="section-kicker mt-4">BIENVENIDO A MB</div>
      <h1 class="section-title">Inicia sesión<span class="text-danger">.</span></h1>
      <p class="text-secondary">
        {{
          redirect === '/checkout'
            ? 'Inicia sesión para asegurar tus descuentos y completar tu pedido.'
            : 'Entra a tu cuenta y sigue descubriendo ofertas.'
        }}
      </p>
      <div v-if="route.query.expirada" class="alert alert-info">Tu sesión expiró.</div>
      <div v-if="error" class="alert alert-danger" role="alert">{{ error }}</div>
      <form @submit.prevent="submit">
        <label class="form-label" for="username">Usuario</label
        ><input
          id="username"
          v-model="username"
          class="form-control mb-3"
          required
          autocomplete="username"
        /><label class="form-label" for="password">Contraseña</label
        ><input
          id="password"
          v-model="password"
          class="form-control mb-4"
          type="password"
          required
          autocomplete="current-password"
        /><button class="btn btn-dark btn-lg w-100" :disabled="loading">
          {{ loading ? 'Ingresando...' : 'Iniciar sesión →' }}
        </button>
      </form>
      <p class="mt-4">
        ¿Aún no tienes cuenta?
        <RouterLink :to="{ name: 'register', query: { redirect } }">Regístrate</RouterLink>
      </p>
    </div>
    <div class="auth-promo">
      <span>MB / MULTIBRAND</span>
      <h2>ENCUENTRA TU<br />PRÓXIMO LOOK.</h2>
      <p>Las mejores oportunidades comienzan aquí.</p>
    </div>
  </div>
</template>
