<script setup>
  import { ref, onMounted } from 'vue'
  import { useAuthStore } from '@/stores/auth'
  import comprasService from '@/services/comprasService'
  import calificacionesService from '@/services/calificacionesService'
  import { useFavoritosStore } from '@/stores/favoritos'
  import { imagenPrincipal } from '@/utils/imagenes'
  const fav = useFavoritosStore(),
    auth = useAuthStore(),
    favoritos = ref([]),
    pendientes = ref([]),
    error = ref('')
  onMounted(async () => {
    try {
      const [a, b] = await Promise.all([
        comprasService.favoritos(),
        calificacionesService.pendientes(),
      ])
      favoritos.value = a.data.favoritos || []
      await fav.sincronizar()
      favoritos.value = fav.items
      pendientes.value = b.data.pendientes_por_calificar || []
    } catch (e) {
      error.value = e.response?.data?.error || 'No se pudo cargar el perfil'
    }
  })
  async function quitar(id) {
    try {
      await fav.alternar({ id_producto: id })
      favoritos.value = fav.items
    } catch (e) {
      error.value = e.response?.data?.error || 'No se pudo eliminar'
    }
  }
</script>
<template>
  <div class="container py-5">
    <h1 class="section-title">Hola, {{ auth.username }}</h1>
    <div class="row g-3 mb-4">
      <div class="col-md-4">
        <RouterLink to="/carrito" class="service-panel"
          ><span class="service-icon">🛒</span>
          <div>
            <strong>Mi carrito</strong>
            <p>Revisa tus productos y confirma la compra</p>
          </div>
          <span>↗</span></RouterLink
        >
      </div>
      <div class="col-md-4">
        <a href="#pendientes" class="service-panel"
          ><span class="service-icon">★</span>
          <div>
            <strong>Calificar compras</strong>
            <p>Comparte tu experiencia real</p>
          </div>
          <span>↗</span></a
        >
      </div>
      <div class="col-md-4">
        <RouterLink to="/#valoraciones" class="service-panel"
          ><span class="service-icon">🏆</span>
          <div>
            <strong>Ranking de productos</strong>
            <p>Descubre los mejor valorados</p>
          </div>
          <span>↗</span></RouterLink
        >
      </div>
    </div>
    <p class="text-secondary">Tu espacio personal de MB Multibrand</p>
    <div v-if="error" class="alert alert-warning">{{ error }}</div>
    <div class="row g-4">
      <div class="col-lg-6">
        <div class="checkout-summary">
          <h2 class="h4">Mis favoritos</h2>
          <p v-if="!favoritos.length" class="text-secondary">Aún no tienes favoritos.</p>
          <div
            v-for="p in favoritos"
            :key="p.id_producto"
            class="d-flex justify-content-between border-bottom py-2"
          >
            <RouterLink :to="`/producto/${p.id_producto}`">{{ p.producto }}</RouterLink><button
              class="btn btn-link btn-sm text-danger"
              @click="quitar(p.id_producto)"
            >
              Quitar
            </button>
          </div>
        </div>
      </div>
      <div class="col-lg-6" id="pendientes">
        <div class="checkout-summary">
          <h2 class="h4">Pendientes por calificar</h2>
          <p v-if="!pendientes.length" class="text-secondary">
            No tienes productos pendientes de reseña.
          </p>
          <RouterLink
            v-for="p in pendientes"
            :key="p.id_producto"
            :to="`/producto/${p.id_producto}#opiniones`"
            class="pending-review-card"
            ><img v-if="imagenPrincipal(p)" :src="imagenPrincipal(p)" :alt="p.producto" />
            <div>
              <strong>{{ p.producto }}</strong><small class="d-block text-secondary">{{
                p.marca || 'Producto comprado'
              }}</small
              ><span class="btn btn-dark btn-sm mt-2">★ Calificar ahora ↗</span>
            </div></RouterLink
          >
        </div>
      </div>
    </div>
    <p class="small text-secondary mt-4">
      El backend original no expone un endpoint para listar el historial completo de compras; los
      comprobantes de la sesión actual se muestran en checkout.
    </p>
  </div>
</template>
