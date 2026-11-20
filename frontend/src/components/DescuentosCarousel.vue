<script setup>
  import { computed, ref, watch, onMounted, onUnmounted } from 'vue'
  import { useRouter } from 'vue-router'
  import { imagenPrincipal } from '@/utils/imagenes'
  import { useCarritoStore } from '@/stores/carrito'
  import { useFavoritosStore } from '@/stores/favoritos'
  const props = defineProps({
    productos: { type: Array, default: () => [] },
    modo: { type: String, default: 'normal' },
  })
  const router = useRouter(),
    carrito = useCarritoStore(),
    favoritos = useFavoritosStore()
  const indice = ref(0),
    imagenFallida = ref({}),
    pausado = ref(false)
  const top = computed(() =>
    [...props.productos]
      .filter((p) => Number(p.descuento) > 0 && Number(p.stock) > 0)
      .sort((a, b) => Number(b.descuento) - Number(a.descuento))
      .slice(0, 8),
  )
  const actual = computed(() => top.value[indice.value] || null)
  const dinero = (n) =>
    new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      maximumFractionDigits: 0,
    }).format(Number(n) || 0)
  function ir(n) {
    if (top.value.length) indice.value = (n + top.value.length) % top.value.length
  }
  function detalle() {
    if (actual.value) router.push(`/producto/${actual.value.id_producto}`)
  }
  watch(top, () => {
    indice.value = 0
  })
  let timer
  onMounted(() => {
    timer = setInterval(() => {
      if (!pausado.value && top.value.length > 1) ir(indice.value + 1)
    }, 6500)
  })
  onUnmounted(() => clearInterval(timer))
</script>
<template>
  <section
    v-if="top.length"
    class="flash-carousel"
    :class="{ 'flash-carousel-hero': modo === 'hero' }"
    aria-label="Carrusel de los productos con mayor descuento"
    @mouseenter="pausado = true"
    @mouseleave="pausado = false"
    @focusin="pausado = true"
    @focusout="pausado = false"
  >
    <div v-if="modo !== 'hero'" class="flash-head">
      <div>
        <span class="flash-kicker">⚡ OFERTAS QUE NO TE PUEDES PERDER</span>
        <h2>Los descuentos <em>más grandes</em></h2>
        <p>Seleccionados automáticamente de los productos disponibles en nuestro catálogo.</p>
      </div>
      <div class="flash-navigation">
        <button type="button" aria-label="Oferta anterior" @click="ir(indice - 1)">‹</button
        ><button type="button" aria-label="Oferta siguiente" @click="ir(indice + 1)">›</button>
      </div>
    </div>
    <div v-if="modo === 'hero'" class="flash-hero-label">⚡ TOP DESCUENTOS</div>
    <div class="flash-slide" :key="actual.id_producto" aria-live="polite">
      <div class="flash-image">
        <img
          v-if="imagenPrincipal(actual) && !imagenFallida[actual.id_producto]"
          :src="imagenPrincipal(actual)"
          :alt="actual.producto"
          @error="imagenFallida[actual.id_producto] = true"
        />
        <div v-else class="flash-image-fallback">
          {{ actual.marca }}<small>OFERTA ESPECIAL</small>
        </div>
        <span class="flash-discount">-{{ actual.descuento }}% OFF</span>
      </div>
      <div class="flash-info">
        <span class="flash-brand">{{ actual.marca }} · DESCUENTO DESTACADO</span>
        <h3>{{ actual.producto }}</h3>
        <p class="flash-description">
          Aprovecha el precio especial antes de que se agoten las unidades.
        </p>
        <div class="flash-prices">
          <span>{{ dinero(actual.precio) }}</span><strong>{{ dinero(actual.precio_final) }}</strong>
        </div>
        <div class="flash-savings">
          Ahorras {{ dinero(Math.max(0, Number(actual.precio) - Number(actual.precio_final))) }}
        </div>
        <div class="flash-actions">
          <button class="btn-flash-primary" @click="detalle">Ver oferta <span>↗</span></button
          ><button class="btn-flash-cart" @click="carrito.agregar(actual)">
            🛒 Agregar al carrito</button
          ><button
            class="btn-flash-fav"
            :aria-pressed="favoritos.contiene(actual.id_producto)"
            :aria-label="
              favoritos.contiene(actual.id_producto)
                ? 'Quitar de favoritos'
                : 'Guardar en favoritos'
            "
            @click="favoritos.alternar(actual)"
          >
            {{ favoritos.contiene(actual.id_producto) ? '♥' : '♡' }}
          </button>
        </div>
        <div class="flash-stock">✓ {{ actual.stock }} unidades disponibles</div>
      </div>
    </div>
    <div class="flash-dots" aria-label="Seleccionar oferta">
      <button
        v-for="(p, i) in top"
        :key="p.id_producto"
        type="button"
        :class="{ active: indice === i }"
        :aria-label="`Ver oferta ${i + 1}: ${p.producto}`"
        :aria-current="indice === i ? 'true' : undefined"
        @click="ir(i)"
      ></button>
    </div>
  </section>
</template>
