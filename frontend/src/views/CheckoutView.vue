<script setup>
  import { useCarritoStore } from '@/stores/carrito'
  const cart = useCarritoStore()
  const money = (n) =>
    new Intl.NumberFormat('es-CO', {
      style: 'currency',
      currency: 'COP',
      maximumFractionDigits: 0,
    }).format(n)
</script>
<template>
  <div class="container py-5" style="max-width: 800px">
    <h1 class="section-title">Confirmar pedido</h1>
    <p class="text-secondary">
      Esta versión realiza compras simuladas. No se realiza un cobro bancario real.
    </p>
    <div v-if="cart.resultado.length" class="alert alert-success">
      <strong>Compras procesadas:</strong>
      <ul class="mb-0">
        <li v-for="r in cart.resultado" :key="r.id_pago">
          {{ r.producto }} · Pago #{{ r.id_pago }} · {{ money(r.total_pagado) }}
        </li>
      </ul>
    </div>
    <div v-if="cart.error" class="alert alert-danger" role="alert">{{ cart.error }}</div>
    <div v-if="cart.items.length" class="checkout-summary">
      <div
        v-for="p in cart.items"
        :key="p.id_producto"
        class="d-flex justify-content-between py-2 border-bottom"
      >
        <span>{{ p.producto }} × {{ p.cantidad }}</span
        ><strong>{{ money(p.precio_final * p.cantidad) }}</strong>
      </div>
      <div class="d-flex justify-content-between fs-4 fw-bold mt-4">
        <span>Total pendiente</span><span>{{ money(cart.total) }}</span>
      </div>
      <button
        class="btn btn-dark btn-lg mt-4 w-100"
        :disabled="cart.procesando"
        @click="cart.finalizar()"
      >
        {{ cart.procesando ? 'Procesando...' : 'Confirmar compra simulada' }}
      </button>
    </div>
    <div v-else class="empty-state">
      <h2 class="h4">No hay productos pendientes.</h2>
      <RouterLink to="/" class="btn btn-dark mt-3">Volver al catálogo</RouterLink>
    </div>
    <p class="small text-secondary mt-3">
      Cada producto se procesa por separado en el backend. Si falla uno, los anteriores no se
      revierten y los pendientes permanecen en el carrito.
    </p>
  </div>
</template>
