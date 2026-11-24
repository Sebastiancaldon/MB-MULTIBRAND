
<script setup>
import { ref, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { useCarritoStore } from '@/stores/carrito'

const auth = useAuthStore()
const cart = useCarritoStore()
const router = useRouter()

const q = ref('')
const menuAbierto = ref(false)
const buscadorAbierto = ref(false)
const inputMovil = ref(null)

function cerrarPaneles() {
  menuAbierto.value = false
  buscadorAbierto.value = false
}

function abrirMenu() {
  menuAbierto.value = !menuAbierto.value
  buscadorAbierto.value = false
}

async function abrirBuscador() {
  buscadorAbierto.value = !buscadorAbierto.value
  menuAbierto.value = false

  if (buscadorAbierto.value) {
    await nextTick()
    inputMovil.value?.focus()
  }
}

async function buscar() {
  const texto = q.value.trim()

  cerrarPaneles()

  await router.push({
    path: '/',
    query: texto ? { q: texto } : {},
    hash: '#ofertas'
  })

  await nextTick()

  document.getElementById('ofertas')?.scrollIntoView({
    behavior: 'smooth',
    block: 'start'
  })
}

function salir() {
  auth.logout()
  cerrarPaneles()
  router.push('/')
}
</script>

<template>

  <!-- BARRA PUBLICITARIA -->

  <div class="announcement announcement-marquee">
    <div class="announcement-track">
      <span
        v-for="i in 2"
        :key="i"
        class="announcement-group"
      >
        <span>✦ DESCUENTOS EN MARCAS SELECCIONADAS</span>
        <span>✦ DESCUBRE TU PRÓXIMA OFERTA</span>
        <span>✦ ENCUENTRA TU ESTILO FAVORITO</span>
        <span>✦ MARCAS QUE TE ENCANTAN, PRECIOS QUE SORPRENDEN</span>
      </span>
    </div>
  </div>

  <header class="sticky-top bg-white border-bottom mb-header">

    <!-- =================================
         NAVEGACION PARA COMPUTADORES
    ================================== -->

    <nav class="navbar navbar-expand-lg container py-3 d-none d-lg-flex">

      <RouterLink
        to="/"
        class="navbar-brand fw-black brand"
      >
        <span class="brand-box">MB</span>
        MULTIBRAND
      </RouterLink>

      <div class="navbar-collapse">

        <form
          class="d-flex nav-search mx-lg-auto"
          role="search"
          @submit.prevent="buscar"
        >
          <input
            v-model="q"
            class="form-control"
            placeholder="Buscar marcas, tenis, ropa..."
            aria-label="Buscar productos"
          />

          <button class="btn btn-dark" type="submit">
            Buscar
          </button>
        </form>

        <div class="d-flex align-items-center gap-3 ms-lg-3">

          <RouterLink
            :to="{ path: '/', hash: '#valoraciones' }"
            class="nav-link"
          >
            ★ Reseñas
          </RouterLink>

          <RouterLink
            to="/carrito"
            class="cart-link"
            aria-label="Ver carrito"
          >
            🛒
            <span class="badge rounded-pill text-bg-danger">
              {{ cart.unidades }}
            </span>
          </RouterLink>

          <template v-if="auth.estaAutenticado">

            <RouterLink
              to="/perfil"
              class="btn btn-outline-dark btn-sm"
            >
              Mi perfil
            </RouterLink>

            <button
              class="btn btn-link text-dark btn-sm"
              @click="salir"
            >
              Salir
            </button>

          </template>

          <template v-else>

            <RouterLink
              to="/login"
              class="btn btn-link text-dark btn-sm"
            >
              Ingresar
            </RouterLink>

            <RouterLink
              to="/register"
              class="btn btn-dark btn-sm"
            >
              Crear cuenta
            </RouterLink>

          </template>

        </div>
      </div>
    </nav>

    <!-- =================================
         NAVEGACION PARA CELULARES
    ================================== -->

    <nav class="mb-mobile-nav d-lg-none">

      <div class="mb-mobile-bar">

        <!-- MENU Y FAVORITOS -->

        <div class="mb-mobile-left">

          <button
            type="button"
            class="mb-icon-btn"
            aria-label="Abrir menú"
            :aria-expanded="menuAbierto"
            @click="abrirMenu"
          >
            <svg viewBox="0 0 24 24">
              <path
                v-if="!menuAbierto"
                d="M3 6h18M3 12h18M3 18h18"
              />
              <path
                v-else
                d="M5 5l14 14M19 5L5 19"
              />
            </svg>
          </button>

          <RouterLink
            :to="auth.estaAutenticado
              ? '/perfil'
              : '/login'"
            class="mb-icon-btn"
            aria-label="Mis favoritos"
            @click="cerrarPaneles"
          >
            <svg viewBox="0 0 24 24">
              <path
                d="M20.8 4.6a5.5 5.5 0 0 0-7.8 0L12 5.7l-1.1-1.1a5.5 5.5 0 0 0-7.8 7.8L12 21l8.8-8.6a5.5 5.5 0 0 0 0-7.8Z"
              />
            </svg>
          </RouterLink>

        </div>

        <!-- LOGO CENTRAL -->

        <RouterLink
          to="/"
          class="mb-mobile-logo"
          aria-label="MB Multibrand Inicio"
          @click="cerrarPaneles"
        >
          <span class="mb-mobile-logo-box">MB</span>
          <span class="mb-mobile-logo-text">
            MULTIBRAND
          </span>
        </RouterLink>

        <!-- PERFIL, BUSQUEDA Y CARRITO -->

        <div class="mb-mobile-right">

          <RouterLink
            :to="auth.estaAutenticado
              ? '/perfil'
              : '/login'"
            class="mb-icon-btn"
            aria-label="Mi cuenta"
            @click="cerrarPaneles"
          >
            <svg viewBox="0 0 24 24">
              <circle cx="12" cy="7" r="4" />
              <path d="M4 22v-3a8 8 0 0 1 16 0v3" />
            </svg>
          </RouterLink>

          <button
            type="button"
            class="mb-icon-btn"
            aria-label="Buscar productos"
            :aria-expanded="buscadorAbierto"
            @click="abrirBuscador"
          >
            <svg viewBox="0 0 24 24">
              <circle cx="10.5" cy="10.5" r="7.5" />
              <path d="m16 16 6 6" />
            </svg>
          </button>

          <RouterLink
            to="/carrito"
            class="mb-icon-btn mb-mobile-cart"
            aria-label="Carrito de compras"
            @click="cerrarPaneles"
          >
            <svg viewBox="0 0 24 24">
              <path d="M4 7h16v15H4z" />
              <path d="M8 9V5a4 4 0 0 1 8 0v4" />
            </svg>

            <span
              v-if="cart.unidades > 0"
              class="mb-cart-count"
            >
              {{ cart.unidades }}
            </span>

          </RouterLink>

        </div>

      </div>

      <!-- BUSCADOR DESPLEGABLE -->

      <Transition name="mb-slide">

        <div
          v-if="buscadorAbierto"
          class="mb-mobile-search"
        >

          <form
            role="search"
            @submit.prevent="buscar"
          >

            <input
              ref="inputMovil"
              v-model="q"
              type="search"
              placeholder="Buscar marcas, tenis, ropa..."
              aria-label="Buscar productos"
            />

            <button type="submit">
              Buscar
            </button>

          </form>

        </div>

      </Transition>

      <!-- MENU DESPLEGABLE -->

      <Transition name="mb-slide">

        <div
          v-if="menuAbierto"
          class="mb-mobile-menu"
        >

          <RouterLink
            to="/"
            @click="cerrarPaneles"
          >
            Inicio
          </RouterLink>

          <RouterLink
            :to="{ path: '/', hash: '#ofertas' }"
            @click="cerrarPaneles"
          >
            Todas las ofertas
          </RouterLink>

          <RouterLink
            :to="{
              path: '/',
              query: { marca: 'Nike' },
              hash: '#ofertas'
            }"
            @click="cerrarPaneles"
          >
            Nike
          </RouterLink>

          <RouterLink
            :to="{
              path: '/',
              query: { marca: 'Adidas' },
              hash: '#ofertas'
            }"
            @click="cerrarPaneles"
          >
            Adidas
          </RouterLink>

          <RouterLink
            :to="{
              path: '/',
              query: { marca: 'Puma' },
              hash: '#ofertas'
            }"
            @click="cerrarPaneles"
          >
            Puma
          </RouterLink>

          <RouterLink
            :to="{ path: '/', hash: '#valoraciones' }"
            @click="cerrarPaneles"
          >
            Reseñas y valoraciones
          </RouterLink>

          <RouterLink
            to="/carrito"
            @click="cerrarPaneles"
          >
            Mi carrito
          </RouterLink>

          <template v-if="auth.estaAutenticado">

            <RouterLink
              to="/perfil"
              @click="cerrarPaneles"
            >
              Mi perfil
            </RouterLink>

            <button
              class="mb-logout"
              @click="salir"
            >
              Cerrar sesión
            </button>

          </template>

          <template v-else>

            <RouterLink
              to="/login"
              @click="cerrarPaneles"
            >
              Iniciar sesión
            </RouterLink>

            <RouterLink
              to="/register"
              @click="cerrarPaneles"
            >
              Crear cuenta
            </RouterLink>

          </template>

        </div>

      </Transition>

    </nav>

  </header>

</template>

<style scoped>

/* BARRA DE NAVEGACION MOVIL */

.mb-mobile-nav {
  width: 100%;
  background: var(--bs-body-bg, #fff);
  color: var(--bs-body-color, #111);
}

.mb-mobile-bar {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto minmax(0, 1fr);
  align-items: center;
  width: 100%;
  min-height: 68px;
  padding: 10px 12px;
  gap: 4px;
  box-sizing: border-box;
}

.mb-mobile-left,
.mb-mobile-right {
  display: flex;
  align-items: center;
  gap: 5px;
}

.mb-mobile-left {
  justify-content: flex-start;
}

.mb-mobile-right {
  justify-content: flex-end;
}

/* ICONOS MINIMALISTAS */

.mb-icon-btn {
  display: inline-flex;
  justify-content: center;
  align-items: center;
  flex-shrink: 0;
  width: 28px;
  height: 40px;
  padding: 2px;
  border: none;
  background: transparent;
  color: inherit;
  text-decoration: none;
  cursor: pointer;
  position: relative;
}

.mb-icon-btn svg {
  width: 23px;
  height: 23px;
  fill: none;
  stroke: currentColor;
  stroke-width: 1.5;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.mb-icon-btn:hover {
  color: #ed2947;
}

/* LOGO PERFECTAMENTE CENTRADO */

.mb-mobile-logo {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
  margin: 0;
  padding: 0;
  color: inherit;
  text-decoration: none;
  white-space: nowrap;
}

.mb-mobile-logo-box {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 34px;
  border-radius: 6px;
  background: #ed2947;
  color: #fff;
  font-size: 16px;
  font-weight: 900;
  letter-spacing: -1px;
}

.mb-mobile-logo-text {
  font-size: 11px;
  font-weight: 900;
  letter-spacing: -0.5px;
}

/* CONTADOR DEL CARRITO */

.mb-cart-count {
  position: absolute;
  top: 0;
  right: -3px;
  min-width: 17px;
  height: 17px;
  padding: 0 3px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 20px;
  background: #ed2947;
  color: #fff;
  font-size: 10px;
  font-weight: 700;
}

/* BUSCADOR */

.mb-mobile-search {
  padding: 8px 14px 16px;
  border-top: 1px solid var(--bs-border-color, #eee);
}

.mb-mobile-search form {
  display: flex;
  width: 100%;
  overflow: hidden;
  border-radius: 6px;
  background: var(--bs-tertiary-bg, #f4f4f4);
}

.mb-mobile-search input {
  flex: 1;
  min-width: 0;
  border: none;
  outline: none;
  padding: 12px;
  background: transparent;
  color: inherit;
  font-size: 14px;
}

.mb-mobile-search button {
  border: none;
  padding: 0 16px;
  background: #171717;
  color: white;
  font-size: 13px;
  font-weight: 600;
}

/* MENU DESPLEGABLE */

.mb-mobile-menu {
  display: flex;
  flex-direction: column;
  max-height: 70vh;
  overflow-y: auto;
  padding: 8px 20px 16px;
  background: var(--bs-body-bg, #fff);
  border-top: 1px solid var(--bs-border-color, #eee);
}

.mb-mobile-menu a,
.mb-mobile-menu button {
  display: block;
  width: 100%;
  padding: 13px 0;
  border: none;
  border-bottom: 1px solid var(--bs-border-color, #eee);
  background: transparent;
  color: inherit;
  text-align: left;
  text-decoration: none;
  font-size: 14px;
  font-weight: 600;
}

.mb-mobile-menu .mb-logout {
  color: #ed2947;
}

/* ANIMACIONES */

.mb-slide-enter-active,
.mb-slide-leave-active {
  transition: opacity 0.2s ease,
              transform 0.2s ease;
}

.mb-slide-enter-from,
.mb-slide-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}

/* CELULARES PEQUEÑOS */

@media (max-width: 380px) {

  .mb-mobile-bar {
    padding: 8px 8px;
    gap: 2px;
    min-height: 62px;
  }

  .mb-mobile-left,
  .mb-mobile-right {
    gap: 2px;
  }

  .mb-icon-btn {
    width: 25px;
  }

  .mb-icon-btn svg {
    width: 21px;
    height: 21px;
  }

  .mb-mobile-logo-box {
    width: 27px;
    height: 30px;
    font-size: 14px;
  }

  .mb-mobile-logo-text {
    font-size: 9px;
  }

  .mb-mobile-logo {
    gap: 3px;
  }
}

@media (max-width: 340px) {
  .mb-mobile-logo-text {
    display: none;
  }
}

/* MODO OSCURO */

:global([data-bs-theme="dark"]) .mb-mobile-nav {
  background: #151515;
  color: #fff;
}

:global([data-bs-theme="dark"]) .mb-mobile-menu {
  background: #151515;
  color: #fff;
}

</style>
