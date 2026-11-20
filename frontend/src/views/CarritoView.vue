<script setup>
  import { useCarritoStore } from '@/stores/carrito'
  import { useAuthStore } from '@/stores/auth'
  import { useRouter } from 'vue-router'
  const cart = useCarritoStore(),
    auth = useAuthStore(),
    router = useRouter()
  const money = (n) =>
    new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      maximumFractionDigits: 0,
    }).format(n)
  function continuar() {
    router.push(
      auth.estaAutenticado ? '/checkout' : { path: '/login', query: { redirect: '/checkout' } },
    )
  }
</script>
<template>
  <div class="container py-5">
    <RouterLink to="/" class="text-secondary text-decoration-none">← Seguir explorando</RouterLink>
    <h1 class="section-title my-4">
      Tu carrito <span class="text-danger">({{ cart.unidades }})</span>
    </h1>
    <div v-if="!cart.items.length" class="empty-state">
      <h2 class="h4">Tu carrito está esperando algo increíble.</h2>
      <RouterLink to="/" class="btn btn-dark mt-3">Explorar descuentos</RouterLink>
    </div>
    <div v-else class="row g-4">
      <div class="col-lg-8">
        <div
          v-for="p in cart.items"
          :key="p.id_producto"
          class="cart-item d-flex gap-3 align-items-center mb-3"
        >
          <div class="cart-thumb">MB</div>
          <div class="flex-grow-1">
            <small class="text-secondary">{{ p.marca }}</small><RouterLink
              :to="`/producto/${p.id_producto}`"
              class="d-block fw-bold text-dark"
              >{{ p.producto }}</RouterLink
            >
            <div class="fw-bold">{{ money(p.precio_final) }}</div>
            <button class="btn btn-link p-0 text-danger btn-sm" @click="cart.quitar(p.id_producto)">
              Eliminar
            </button>
          </div>
          <div>
            <label class="small d-block" :for="`qty-${p.id_producto}`">Cantidad</label
            ><input
              :id="`qty-${p.id_producto}`"
              type="number"
              min="1"
              :max="Math.min(p.stock, 10)"
              :value="p.cantidad"
              class="form-control"
              style="width: 82px"
              @change="cart.cantidad(p.id_producto, $event.target.value)"
            />
          </div>
        </div>
      </div>
      <div class="col-lg-4">
        <div class="checkout-summary">
          <h2 class="h4 fw-bold">Resumen</h2>
          <div class="d-flex justify-content-between mt-4">
            <span>Subtotal</span><span>{{ money(cart.subtotal) }}</span>
          </div>
          <div class="d-flex justify-content-between text-success mt-2">
            <span>Ahorras</span><span>-{{ money(cart.ahorro) }}</span>
          </div>
          <hr />
          <div class="d-flex justify-content-between fs-4 fw-bold">
            <span>Total</span><span>{{ money(cart.total) }}</span>
          </div>
          <button class="btn btn-dark btn-lg w-100 mt-4" @click="continuar">
            Finalizar compra →
          </button>
          <p class="text-secondary small mt-3 mb-0">
            {{
              auth.estaAutenticado
                ? 'Confirma tu pedido en el siguiente paso.'
                : 'Solo necesitarás iniciar sesión al confirmar.'
            }}
          </p>
        </div>
      </div>
    </div>
  </div>
</template>
