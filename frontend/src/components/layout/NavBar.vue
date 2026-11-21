<script setup>
  import { ref } from 'vue'
  import { useRouter } from 'vue-router'
  import { useAuthStore } from '@/stores/auth'
  import { useCarritoStore } from '@/stores/carrito'
  const auth = useAuthStore(),
    cart = useCarritoStore(),
    router = useRouter(),
    q = ref('')
  
async function buscar() {
  const texto = q.value.trim()

  await router.push({
    path: '/',
    query: texto ? { q: texto } : {},
    hash: '#ofertas'
  })
}

  function salir() {
    auth.logout()
    router.push('/')
  }
</script>
<template>
  <div class="announcement text-center py-2">
    DESCUENTOS EN MARCAS SELECCIONADAS · DESCUBRE TU PRÓXIMA OFERTA
  </div>
  <header class="sticky-top bg-white border-bottom">
    <nav class="navbar navbar-expand-lg container py-3">
      <RouterLink to="/" class="navbar-brand fw-black brand"
        ><span class="brand-box">MB</span> MULTIBRAND</RouterLink
      ><button
        class="navbar-toggler"
        type="button"
        data-bs-toggle="collapse"
        data-bs-target="#navContent"
        aria-controls="navContent"
        aria-expanded="false"
        aria-label="Abrir menú"
      >
        <span class="navbar-toggler-icon" />
      </button>
      <div id="navContent" class="collapse navbar-collapse">
        <form
          class="d-flex nav-search mx-lg-auto my-3 my-lg-0"
          role="search"
          @submit.prevent="buscar"
        >
          <input
            v-model="q"
            class="form-control"
            placeholder="Buscar marcas, tenis, ropa..."
            aria-label="Buscar productos"
          /><button class="btn btn-dark" type="submit">Buscar</button>
        </form>
        <div class="d-flex align-items-center gap-3 ms-lg-3 flex-wrap">
          
          <RouterLink to="/#valoraciones" class="nav-link">★ Reseñas</RouterLink>
          <RouterLink to="/carrito" class="cart-link" aria-label="Ver carrito"
            >🛒
            <span class="badge rounded-pill text-bg-danger">{{ cart.unidades }}</span></RouterLink
          ><template v-if="auth.estaAutenticado"
            ><RouterLink to="/perfil" class="btn btn-outline-dark btn-sm">Mi perfil</RouterLink
            ><button class="btn btn-link text-dark btn-sm" @click="salir">Salir</button></template
          ><template v-else
            ><RouterLink to="/login" class="btn btn-link text-dark btn-sm">Ingresar</RouterLink
            ><RouterLink to="/register" class="btn btn-dark btn-sm"
              >Crear cuenta</RouterLink
            ></template
          >
        </div>
      </div>
    </nav>
  </header>
</template>
