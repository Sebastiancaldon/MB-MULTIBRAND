<script setup>
  import { ref, onMounted, computed, watch } from 'vue'
  import { useRoute, useRouter } from 'vue-router'
  import catalogoService from '@/services/catalogoService'
  import calificacionesService from '@/services/calificacionesService'
  import { useCarritoStore } from '@/stores/carrito'
  import { useAuthStore } from '@/stores/auth'
  import ProductCard from '@/components/ProductCard.vue'
  import { useFavoritosStore } from '@/stores/favoritos'
  import { imagenesProducto, imagenPrincipal } from '@/utils/imagenes'
  const fav = useFavoritosStore()
  const route = useRoute(),
    router = useRouter(),
    cart = useCarritoStore(),
    auth = useAuthStore(),
    p = ref(null),
    resumen = ref(null),
    relacionados = ref([]),
    cantidad = ref(1),
    loading = ref(true),
    error = ref(''),
    ratingError = ref(''),
    puntuacion = ref(5),
    comentario = ref(''),
    enviando = ref(false)
  const galeria = computed(() => (p.value ? imagenesProducto(p.value) : []))
  const imagenActiva = ref('')
  const imagenDetalle = computed(() => imagenActiva.value || imagenPrincipal(p.value))
  const imagenFallida = ref(false)
  function seleccionarImagen(foto) {
    imagenActiva.value = foto
    imagenFallida.value = false
  }
  const money = (n) =>
    new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      maximumFractionDigits: 0,
    }).format(Number(n) || 0)
  const ahorro = computed(() =>
    p.value ? Number(p.value.precio) - Number(p.value.precio_final) : 0,
  )
  async function cargar() {
    loading.value = true
    error.value = ''
    resumen.value = null
    cantidad.value = 1
    imagenActiva.value = ''
    imagenFallida.value = false
    try {
      const { data } = await catalogoService.obtenerProducto(route.params.id)
      p.value = data
      const all = await catalogoService.obtenerOfertas({ categoria: data.categoria })
      relacionados.value = (all.data.ofertas || [])
        .filter((x) => x.id_producto !== data.id_producto)
        .slice(0, 4)
    } catch (e) {
      error.value = e.response?.data?.error || 'No se pudo cargar el producto'
    } finally {
      loading.value = false
    }
    try {
      const { data } = await calificacionesService.resumen(route.params.id)
      resumen.value = data
    } catch {
      ratingError.value = 'No se pudieron cargar las reseñas'
    }
  }
  async function calificar() {
    enviando.value = true
    ratingError.value = ''
    try {
      await calificacionesService.calificar(
        Number(route.params.id),
        Number(puntuacion.value),
        comentario.value,
      )
      await cargar()
      window.dispatchEvent(new CustomEvent('mb-toast', { detail: 'Tu reseña fue publicada' }))
    } catch (e) {
      ratingError.value = e.response?.data?.error || 'No se pudo publicar la reseña'
    } finally {
      enviando.value = false
    }
  }
  watch(() => route.params.id, cargar)
  onMounted(cargar)
</script>
<template>
  <div class="container py-5">
    <RouterLink to="/" class="text-decoration-none text-secondary">← Volver a ofertas</RouterLink>
    <div v-if="loading" class="skeleton mt-4" />
    <div v-else-if="error" class="alert alert-danger mt-4">
      {{ error }} <button class="btn btn-outline-danger btn-sm" @click="cargar">Reintentar</button>
    </div>
    <template v-else-if="p"
      ><div class="row g-5 mt-1">
        <div class="col-lg-6">
          <div class="detail-visual">
            <img
              v-if="imagenDetalle && !imagenFallida"
              :src="imagenDetalle"
              :alt="p.producto"
              @error="imagenFallida = true"
            />
            <div v-if="!imagenDetalle || imagenFallida" class="detail-fallback">
              <strong>MB</strong><span>{{ p.categoria }}</span>
            </div>
            <span v-if="p.descuento" class="badge text-bg-danger discount-badge"
              >-{{ p.descuento }}%</span
            >
          </div>
          <div v-if="galeria.length" class="gallery-thumbs mt-3">
            <button
              v-for="(foto, i) in galeria"
              :key="foto"
              type="button"
              class="gallery-thumb"
              :class="{ active: imagenDetalle === foto }"
              :aria-label="`Ver imagen ${i + 1}`"
              @click="seleccionarImagen(foto)"
            >
              <img :src="foto" :alt="`${p.producto} vista ${i + 1}`" />
            </button>
          </div>
        </div>
        <div class="col-lg-6">
          <div class="section-kicker">{{ p.marca }} / {{ p.categoria }}</div>
          <h1 class="detail-title">{{ p.producto }}</h1>
          <div class="mb-3 text-secondary">
            ⭐ {{ resumen?.promedio ? Number(resumen.promedio).toFixed(1) : 'Sin calificaciones' }}
            <span v-if="resumen?.total_calificaciones"
              >({{ resumen.total_calificaciones }} reseñas)</span
            >
          </div>
          <p class="text-secondary">
            {{ p.descripcion || 'Descubre este producto de nuestra selección multimarca.' }}
          </p>
          <div class="old-price fs-5">{{ money(p.precio) }}</div>
          <div class="detail-price">{{ money(p.precio_final) }}</div>
          <p v-if="ahorro > 0" class="text-success fw-bold">
            Ahorras {{ money(ahorro) }} por unidad
          </p>
          <p class="fw-semibold" :class="p.stock <= 5 ? 'text-danger' : 'text-success'">
            {{
              p.stock === 0
                ? 'Agotado'
                : p.stock <= 5
                  ? `¡Últimas ${p.stock} unidades disponibles!`
                  : 'En stock'
            }}
          </p>
          <div class="d-flex gap-3 align-items-center mb-4">
            <label for="qty" class="fw-bold">Cantidad</label
            ><input
              id="qty"
              v-model.number="cantidad"
              type="number"
              class="form-control"
              style="max-width: 100px"
              min="1"
              :max="Number(p.stock)"
              :disabled="p.stock === 0"
            />
          </div>
          <button
            class="btn btn-dark btn-lg w-100"
            :disabled="
              p.stock === 0 ||
              cantidad < 1 ||
              cantidad > Math.min(p.stock, 10) ||
              !Number.isInteger(cantidad)
            "
            @click="cart.agregar(p, cantidad)"
          >
            Agregar al carrito →
          </button>
          <div class="d-grid d-sm-flex gap-2 mt-3">
            <button
              class="btn btn-outline-danger btn-lg flex-fill"
              :aria-pressed="fav.contiene(p.id_producto)"
              @click="fav.alternar(p)"
            >
              {{
                fav.contiene(p.id_producto) ? '♥ Guardado en favoritos' : '♡ Agregar a favoritos'
              }}</button><RouterLink to="/carrito" class="btn btn-outline-dark btn-lg flex-fill"
              >Ir al carrito ↗</RouterLink
            >
          </div>
          <a href="#opiniones" class="btn btn-link mt-2">★ Leer opiniones y calificar ↓</a>
          <p v-if="fav.error" class="alert alert-warning mt-2">{{ fav.error }}</p>
          <p class="small text-secondary mt-3">
            Puedes comprar sin crear cuenta hasta el momento de confirmar el pedido.
          </p>
        </div>
      </div>
      <section id="opiniones" class="reviews-showcase mt-5">
        <div class="reviews-heading">
          <div>
            <span class="section-kicker">TU EXPERIENCIA IMPORTA</span>
            <h2 class="section-title">Opiniones y calificaciones ★</h2>
            <p>Consulta experiencias reales y comparte la tuya después de comprar.</p>
          </div>
          <div class="reviews-score">
            <strong>{{
              resumen?.promedio ? Number(resumen.promedio).toFixed(1) : '—'
            }}</strong><span class="text-warning">★★★★★</span
            ><small>{{ resumen?.total_calificaciones || 0 }} reseñas</small>
          </div>
        </div>
        <div class="row g-4">
          <div class="col-lg-5">
            <div class="review-product-card">
              <img v-if="imagenPrincipal(p)" :src="imagenPrincipal(p)" :alt="p.producto" />
              <div v-else class="detail-fallback">MB</div>
              <div class="p-3">
                <small>{{ p.marca }}</small>
                <h3 class="h4">{{ p.producto }}</h3>
                <p class="offer-price mb-2">{{ money(p.precio_final) }}</p>
                <button class="btn btn-outline-danger w-100" @click="fav.alternar(p)">
                  {{
                    fav.contiene(p.id_producto) ? '♥ En mis favoritos' : '♡ Guardar en favoritos'
                  }}
                </button>
              </div>
            </div>
          </div>
          <div class="col-lg-7">
            <div class="review-form-panel">
              <h3 class="h3 fw-bold">Califica este producto</h3>
              <p class="text-secondary">
                Selecciona las estrellas y cuéntanos cómo fue tu experiencia.
              </p>
              <div v-if="ratingError" class="alert alert-warning" role="alert">
                {{ ratingError }}
              </div>
              <div v-if="!auth.estaAutenticado" class="alert alert-light border">
                Para publicar una reseña debes iniciar sesión y tener una compra aprobada.
                <div class="mt-3">
                  <RouterLink
                    class="btn btn-dark"
                    :to="{ name: 'login', query: { redirect: route.fullPath } }"
                    >Iniciar sesión para calificar ↗</RouterLink
                  >
                </div>
              </div>
              <form v-else @submit.prevent="calificar">
                <div
                  class="rating-picker"
                  role="group"
                  aria-label="Selecciona una calificación de 1 a 5 estrellas"
                >
                  <button
                    v-for="n in 5"
                    :key="n"
                    type="button"
                    class="rating-star"
                    :class="{ active: n <= puntuacion }"
                    :aria-label="`${n} estrellas`"
                    :aria-pressed="puntuacion === n"
                    @click="puntuacion = n"
                  >
                    ★
                  </button>
                </div>
                <p class="fw-semibold">
                  {{ ['', 'Muy malo', 'Malo', 'Regular', 'Bueno', 'Excelente'][puntuacion] }}
                </p>
                <label for="comment" class="form-label fw-semibold">Tu opinión</label
                ><textarea
                  id="comment"
                  v-model="comentario"
                  maxlength="255"
                  class="form-control mb-2"
                  rows="5"
                  placeholder="¿Qué te gustó del producto? ¿Lo recomendarías?"
                />
                <div class="text-end small text-secondary mb-3">
                  {{ comentario.length }} / 255 caracteres
                </div>
                <button class="btn btn-dark btn-lg w-100" :disabled="enviando">
                  {{ enviando ? 'Publicando…' : 'Publicar mi calificación ★' }}
                </button>
                <p class="small text-secondary mt-2">
                  Solo clientes con compra aprobada pueden publicar reseñas.
                </p>
              </form>
            </div>
          </div>
        </div>
        <h3 class="h4 mt-5 mb-3">Lo que dicen los compradores</h3>
        <p v-if="!resumen?.ultimos_comentarios?.length" class="text-secondary">
          Todavía no hay comentarios publicados.
        </p>
        <div class="row g-3">
          <div v-for="(r, i) in resumen?.ultimos_comentarios || []" :key="i" class="col-md-6">
            <div class="review h-100">
              <span class="text-warning fs-4">{{ '★'.repeat(Number(r.puntuacion) || 0) }}</span>
              <p class="mb-2">{{ r.comentario }}</p>
              <strong>{{ r.cliente }}</strong>
            </div>
          </div>
        </div>
      </section>
      <section v-if="relacionados.length" class="mt-5">
        <h2 class="section-title">También te puede gustar</h2>
        <div class="row g-3 mt-2">
          <div v-for="item in relacionados" :key="item.id_producto" class="col-6 col-lg-3">
            <ProductCard :producto="item" />
          </div>
        </div></section
    ></template>
  </div>
</template>
