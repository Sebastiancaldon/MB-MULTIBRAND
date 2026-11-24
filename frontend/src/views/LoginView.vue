
<script setup>
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()

const username = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')
const mostrarContrasena = ref(false)

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
    error.value =
      e.response?.data?.error ||
      'No se pudo iniciar sesión. Revisa el servidor.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="auth-screen">
    <div class="auth-panel">

      <RouterLink
        to="/"
        class="text-secondary text-decoration-none"
      >
        ← Volver a ofertas
      </RouterLink>

      <div class="section-kicker mt-4">
        BIENVENIDO A MB
      </div>

      <h1 class="section-title">
        Inicia sesión<span class="text-danger">.</span>
      </h1>

      <p class="text-secondary">
        {{
          redirect === '/checkout'
            ? 'Inicia sesión para asegurar tus descuentos y completar tu pedido.'
            : 'Entra a tu cuenta y sigue descubriendo ofertas.'
        }}
      </p>

      <div
        v-if="route.query.expirada"
        class="alert alert-info"
      >
        Tu sesión expiró.
      </div>

      <div
        v-if="error"
        class="alert alert-danger"
        role="alert"
      >
        {{ error }}
      </div>

      <form @submit.prevent="submit">

        <!-- USUARIO -->

        <label class="form-label" for="username">
          Usuario
        </label>

        <input
          id="username"
          v-model="username"
          class="form-control mb-3"
          required
          autocomplete="username"
        />

        <!-- CONTRASEÑA -->

        <label class="form-label" for="password">
          Contraseña
        </label>

        <div class="password-wrapper mb-4">

          <input
            id="password"
            v-model="password"
            class="form-control password-input"
            :type="mostrarContrasena ? 'text' : 'password'"
            required
            autocomplete="current-password"
          />

          <!-- MOSTRAR U OCULTAR CONTRASEÑA -->

          <button
            type="button"
            class="password-toggle"
            :aria-label="mostrarContrasena
              ? 'Ocultar contraseña'
              : 'Mostrar contraseña'"
            :title="mostrarContrasena
              ? 'Ocultar contraseña'
              : 'Mostrar contraseña'"
            @click="mostrarContrasena = !mostrarContrasena"
          >

            <!-- OJO ABIERTO -->

            <svg
              v-if="!mostrarContrasena"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path
                d="M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7-10-7-10-7Z"
              />
              <circle cx="12" cy="12" r="3" />
            </svg>

            <!-- OJO TACHADO -->

            <svg
              v-else
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path d="M3 3l18 18" />
              <path
                d="M10.6 10.6a2 2 0 0 0 2.8 2.8"
              />
              <path
                d="M9 5.4A11 11 0 0 1 12 5c6.4 0 10 7 10 7a16 16 0 0 1-3 3.8"
              />
              <path
                d="M6 6C3.4 8.2 2 12 2 12s3.6 7 10 7a10 10 0 0 0 4-.8"
              />
            </svg>

          </button>

        </div>

        <!-- BOTON INICIAR SESION -->

        <button
          type="submit"
          class="btn btn-dark btn-lg w-100"
          :disabled="loading"
        >
          {{ loading ? 'Ingresando...' : 'Iniciar sesión →' }}
        </button>

      </form>

      <p class="mt-4">
        ¿Aún no tienes cuenta?

        <RouterLink
          :to="{ name: 'register', query: { redirect } }"
        >
          Regístrate
        </RouterLink>
      </p>

    </div>

    <div class="auth-promo">
      <span>MB / MULTIBRAND</span>

      <h2>
        ENCUENTRA TU<br />
        PRÓXIMO LOOK.
      </h2>

      <p>Las mejores oportunidades comienzan aquí.</p>
    </div>

  </div>
</template>

<style scoped>

/* CONTENEDOR DE CONTRASEÑA */

.password-wrapper {
  position: relative;
  width: 100%;
}

/* CAMPO DE CONTRASEÑA */

.password-input {
  width: 100%;
  padding-right: 48px !important;
}

/* BOTON DEL OJO */

.password-toggle {
  position: absolute;
  top: 50%;
  right: 8px;
  transform: translateY(-50%);
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  padding: 0;
  background: transparent;
  border: none;
  color: var(--bs-secondary-color, #666);
  cursor: pointer;
  border-radius: 6px;
  transition: color 0.2s ease;
}

.password-toggle svg {
  width: 22px;
  height: 22px;
  fill: none;
  stroke: currentColor;
  stroke-width: 1.7;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.password-toggle:hover {
  color: #ed2947;
}

.password-toggle:focus-visible {
  outline: 2px solid #ed2947;
  outline-offset: 2px;
}

/* ADAPTACION PARA CELULARES */

@media (max-width: 767px) {

  .password-input {
    padding-right: 48px !important;
    font-size: 16px;
  }

  .password-toggle {
    width: 40px;
    height: 40px;
    right: 4px;
  }
}

</style>
