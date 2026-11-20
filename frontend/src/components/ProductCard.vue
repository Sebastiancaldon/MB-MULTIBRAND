<script setup>
  import { computed, ref } from 'vue'
  import { imagenPrincipal } from '@/utils/imagenes'
  import { useCarritoStore } from '@/stores/carrito'
  import { useFavoritosStore } from '@/stores/favoritos'
  const props = defineProps({
    producto: { type: Object, required: true },
    rating: { type: Object, default: null },
  })
  const fav = useFavoritosStore(),
    cart = useCarritoStore(),
    p = computed(() => props.producto),
    imagenFallida = ref(false),
    imagen = computed(() => imagenPrincipal(p.value))
  const money = (n) =>
    new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      maximumFractionDigits: 0,
    }).format(Number(n) || 0)
</script>
<template>
  <article class="card product-card premium-product-card h-100 border-0">
    <div class="product-visual">
      <RouterLink
        :to="`/producto/${p.id_producto}`"
        class="product-image-link"
        :aria-label="`Ver detalles de ${p.producto}`"
      >
        <img
          v-if="imagen && !imagenFallida"
          :src="imagen"
          :alt="p.producto"
          loading="lazy"
          @error="imagenFallida = true"
        />
        <div v-else class="product-fallback">
          <span class="fallback-mark">MB</span><span>{{ p.categoria || 'MULTIBRAND' }}</span>
        </div>
      </RouterLink>
      <button
        type="button"
        class="favorite-heart"
        :class="{ selected: fav.contiene(p.id_producto) }"
        :aria-label="fav.contiene(p.id_producto) ? 'Quitar de favoritos' : 'Agregar a favoritos'"
        :aria-pressed="fav.contiene(p.id_producto)"
        @click="fav.alternar(p)"
      >
        {{ fav.contiene(p.id_producto) ? '♥' : '♡' }}
      </button>
      <span v-if="imagen?.endsWith('.svg')" class="demo-image-label">Imagen ilustrativa</span>
      <span v-if="p.descuento > 0" class="badge text-bg-danger discount-badge"
        >-{{ p.descuento }}%</span
      >
    </div>
    <div class="card-body d-flex flex-column">
      <div class="d-flex justify-content-between align-items-center gap-2">
        <small class="text-uppercase fw-bold premium-brand">{{ p.marca }}</small><span
          class="premium-rating"
          v-if="rating?.votos || rating?.total_calificaciones"
          >★ {{ Number(rating.promedio).toFixed(1) }}</span
        >
      </div>
      <RouterLink :to="`/producto/${p.id_producto}`" class="product-title">{{
        p.producto
      }}</RouterLink>
      <div class="small mt-2" :class="p.stock <= 5 ? 'text-danger' : 'text-success'">
        {{
          p.stock > 0
            ? p.stock <= 5
              ? `¡Últimas ${p.stock} unidades!`
              : '● Disponible'
            : 'Agotado'
        }}
      </div>
      <div class="mt-auto pt-3">
        <div class="old-price">{{ money(p.precio) }}</div>
        <div class="offer-price">{{ money(p.precio_final) }}</div>
        <div v-if="Number(p.descuento) > 0" class="premium-save">
          Ahorras {{ money(Math.max(0, Number(p.precio) - Number(p.precio_final))) }}
        </div>
      </div>
      <div class="premium-card-actions mt-3">
        <RouterLink :to="`/producto/${p.id_producto}`" class="premium-view-btn"
          >Ver oferta <span>↗</span></RouterLink
        ><button class="premium-cart-btn" :disabled="p.stock <= 0" @click="cart.agregar(p)">
          🛒 Agregar al carrito</button
        ><RouterLink :to="`/producto/${p.id_producto}#opiniones`" class="premium-review-link"
          >★ Ver opiniones y calificar ↗</RouterLink
        >
      </div>
    </div>
  </article>
</template>
