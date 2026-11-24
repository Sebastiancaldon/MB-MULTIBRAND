
<script setup>
import { ref, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import authService from '@/services/authService'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()

const nombre = ref('')
const correo = ref('')
const username = ref('')
const password = ref('')
const confirmarPassword = ref('')
const loading = ref(false)
const error = ref('')

const mostrarContrasena = ref(false)
const mostrarConfirmacion = ref(false)

const redirect = computed(() =>
  typeof route.query.redirect === 'string' &&
  route.query.redirect.startsWith('/') &&
  !route.query.redirect.startsWith('//')
    ? route.query.redirect
    : '/',
)

async function submit() {
  error.value = ''

  // Validar longitud de la contraseña
  if (password.value.length < 8) {
    error.value = 'La contraseña debe tener mínimo 8 caracteres.'
    return
  }

  // Validar que las contraseñas coincidan
  if (password.value !== confirmarPassword.value) {
    error.value = 'Las contraseñas no coinciden.'
    return
  }

  loading.value = true

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
    error.value =
      e.response?.data?.error ||
      'No fue posible completar el registro.'
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
        ÚNETE A MB
      </div>

      <h1 class="section-title">
        Crea tu cuenta<span class="text-danger">.</span>
      </h1>

      <p class="text-secondary">
        {{
          redirect === '/checkout'
            ? 'Crea tu cuenta para completar tu pedido. Tu carrito seguirá guardado.'
            : 'Regístrate y guarda tus descuentos favoritos.'
        }}
      </p>

      <div
        v-if="error"
        class="alert alert-danger"
        role="alert"
      >
        {{ error }}
      </div>

      <form @submit.prevent="submit">

        <!-- NOMBRE COMPLETO -->

        <label class="form-label" for="nombre">
          Nombre completo
        </label>

        <input
          id="nombre"
          v-model="nombre"
          class="form-control mb-3"
          autocomplete="name"
          required
        />

        <!-- CORREO -->

        <label class="form-label" for="correo">
          Correo
        </label>

        <input
          id="correo"
          v-model="correo"
          type="email"
          class="form-control mb-3"
          autocomplete="email"
          required
        />

        <!-- USUARIO -->

        <label class="form-label" for="usuario">
          Usuario
        </label>

        <input
          id="usuario"
          v-model="username"
          class="form-control mb-3"
          autocomplete="username"
          required
        />

        <!-- CONTRASEÑA -->

        <label class="form-label" for="password">
          Contraseña (mínimo 8 caracteres)
        </label>

        <div class="password-wrapper mb-3">

          <input
            id="password"
            v-model="password"
            :type="mostrarContrasena ? 'text' : 'password'"
            minlength="8"
            class="form-control password-input"
            autocomplete="new-password"
            required
          />

          <button
            type="button"
            class="password-toggle"
            :aria-label="mostrarContrasena
              ? 'Ocultar contraseña'
              : 'Mostrar contraseña'"
            @click="mostrarContrasena = !mostrarContrasena"
          >

            <svg
              v-if="!mostrarContrasena"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path d="M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7-10-7-10-7Z"/>
              <circle cx="12" cy="12" r="3"/>
            </svg>

            <svg
              v-else
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path d="M3 3l18 18"/>
              <path d="M10.6 10.6a2 2 0 0 0 2.8 2.8"/>
              <path d="M9 5.4A11 11 0 0 1 12 5c6.4 0 10 7 10 7a16 16 0 0 1-3 3.8"/>
              <path d="M6 6C3.4 8.2 2 12 2 12s3.6 7 10 7a10 10 0 0 0 4-.8"/>
            </svg>

          </button>

        </div>

        <!-- CONFIRMAR CONTRASEÑA -->

        <label class="form-label" for="confirmarPassword">
          Confirmar contraseña
        </label>

        <div class="password-wrapper mb-2">

          <input
            id="confirmarPassword"
            v-model="confirmarPassword"
            :type="mostrarConfirmacion ? 'text' : 'password'"
            class="form-control password-input"
            :class="{
              'is-invalid':
                confirmarPassword &&
                password !== confirmarPassword,

              'is-valid':
                confirmarPassword &&
                password.length >= 8 &&
                password === confirmarPassword
            }"
            minlength="8"
            autocomplete="new-password"
            required
          />

          <button
            type="button"
            class="password-toggle"
            :aria-label="mostrarConfirmacion
              ? 'Ocultar confirmación'
              : 'Mostrar confirmación'"
            @click="mostrarConfirmacion = !mostrarConfirmacion"
          >

            <svg
              v-if="!mostrarConfirmacion"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path d="M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7-10-7-10-7Z"/>
              <circle cx="12" cy="12" r="3"/>
            </svg>

            <svg
              v-else
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path d="M3 3l18 18"/>
              <path d="M10.6 10.6a2 2 0 0 0 2.8 2.8"/>
              <path d="M9 5.4A11 11 0 0 1 12 5c6.4 0 10 7 10 7a16 16 0 0 1-3 3.8"/>
              <path d="M6 6C3.4 8.2 2 12 2 12s3.6 7 10 7a10 10 0 0 0 4-.8"/>
            </svg>

          </button>

        </div>

        <!-- VALIDACION EN TIEMPO REAL -->

        <small
          v-if="confirmarPassword && password !== confirmarPassword"
          class="text-danger d-block mb-3"
        >
          Las contraseñas no coinciden.
        </small>

        <small
          v-else-if="
            confirmarPassword &&
            password.length >= 8 &&
            password === confirmarPassword
          "
          class="text-success d-block mb-3"
        >
          ✓ Las contraseñas coinciden.
        </small>

        <!-- CREAR CUENTA -->

        <button
          type="submit"
          class="btn btn-dark btn-lg w-100 mt-3"
          :disabled="loading"
        >
          {{ loading ? 'Creando cuenta...' : 'Crear cuenta →' }}
        </button>

      </form>

      <p class="mt-4">

        ¿Ya tienes cuenta?

        <RouterLink
          :to="{ name: 'login', query: { redirect } }"
        >
          Inicia sesión
        </RouterLink>

      </p>

    </div>

    <div class="auth-promo">

      <span>MB / MULTIBRAND</span>

      <h2>
        BUEN ESTILO.<br />
        MEJOR PRECIO.
      </h2>

      <p>Explora, elige y ahorra.</p>

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

/* EVITAR QUE LOS ICONOS DE BOOTSTRAP
   SE SUPERPONGAN CON EL OJO */

.password-input.is-valid,
.password-input.is-invalid {
  background-image: none !important;
  padding-right: 48px !important;
}

/* BOTON MOSTRAR CONTRASEÑA */

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
