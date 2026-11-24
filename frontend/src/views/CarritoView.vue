
<script setup>
import { ref } from 'vue'
import { useCarritoStore } from '@/stores/carrito'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
import { imagenPrincipal } from '@/utils/imagenes'

const cart = useCarritoStore()
const auth = useAuthStore()
const router = useRouter()

const imagenesFallidas = ref({})

const money = (n) =>
  new Intl.NumberFormat('es-CO', {
    style: 'currency',
    currency: 'COP',
    maximumFractionDigits: 0,
  }).format(n)

function fotoProducto(p) {
  return imagenPrincipal(p) || p.imagen || ''
}

function cambiarCantidad(p, cambio) {
  const nueva = Number(p.cantidad) + cambio
  const maximo = Number(p.stock)

  if (nueva >= 1 && nueva <= maximo) {
    cart.cantidad(p.clave, nueva)
  }
}

function continuar() {
  router.push(
    auth.estaAutenticado
      ? '/checkout'
      : {
          path: '/login',
          query: { redirect: '/checkout' }
        }
  )
}
</script>

<template>
  <div class="container py-5">

    <RouterLink
      to="/"
      class="text-secondary text-decoration-none"
    >
      ← Seguir explorando
    </RouterLink>

    <h1 class="section-title my-4">
      Tu carrito
      <span class="text-danger">
        ({{ cart.unidades }})
      </span>
    </h1>

    <!-- CARRITO VACIO -->

    <div v-if="!cart.items.length" class="empty-state">

      <h2 class="h4">
        Tu carrito está esperando algo increíble.
      </h2>

      <RouterLink
        to="/"
        class="btn btn-dark mt-3"
      >
        Explorar descuentos
      </RouterLink>

    </div>

    <!-- PRODUCTOS DEL CARRITO -->

    <div v-else class="row g-4">

      <div class="col-lg-8">

        <div
          v-for="p in cart.items"
          :key="p.clave"
          class="cart-item d-flex gap-3 align-items-center mb-3"
        >

          <!-- IMAGEN REAL DEL PRODUCTO -->

          <RouterLink
            :to="`/producto/${p.id_producto}`"
            class="cart-thumb"
          >

            <img
              v-if="
                fotoProducto(p) &&
                !imagenesFallidas[p.id_producto]
              "
              :src="fotoProducto(p)"
              :alt="p.producto"
              loading="lazy"
              @error="imagenesFallidas[p.id_producto] = true"
            />

            <span v-else>MB</span>

          </RouterLink>

          <!-- INFORMACION DEL PRODUCTO -->

          <div class="cart-product-info flex-grow-1">

            <small class="text-secondary">
              {{ p.marca }} · Talla {{ p.talla }}
            </small>

            <RouterLink
              :to="`/producto/${p.id_producto}`"
              class="cart-product-name"
            >
              {{ p.producto }}
            </RouterLink>

            <div
              v-if="Number(p.precio) > Number(p.precio_final)"
              class="cart-old-price"
            >
              {{ money(p.precio) }}
            </div>

            <div class="cart-product-price">
              {{ money(p.precio_final) }}
            </div>

            <button
              type="button"
              class="cart-remove"
              @click="cart.quitar(p.clave)"
            >

              <svg viewBox="0 0 24 24">
                <path d="M3 6h18M8 6V3h8v3M5 6l1 15h12l1-15M10 10v7M14 10v7"/>
              </svg>

              Eliminar

            </button>

          </div>

          <!-- CONTROL DE CANTIDAD -->

          <div class="cart-quantity">

            <label class="small d-block mb-2">
              Cantidad
            </label>

            <div class="quantity-control">

              <button
                type="button"
                class="quantity-btn"
                aria-label="Disminuir cantidad"
                :disabled="p.cantidad <= 1"
                @click="cambiarCantidad(p, -1)"
              >
                −
              </button>

              <span
                class="quantity-value"
                aria-live="polite"
              >
                {{ p.cantidad }}
              </span>

              <button
                type="button"
                class="quantity-btn"
                aria-label="Aumentar cantidad"
                :disabled="p.cantidad >= Number(p.stock)"
                @click="cambiarCantidad(p, 1)"
              >
                +
              </button>

            </div>

            <small class="cart-item-total">
              {{ money(p.precio_final * p.cantidad) }}
            </small>

          </div>

        </div>

      </div>

      <!-- RESUMEN DE COMPRA -->

      <div class="col-lg-4">

        <div class="checkout-summary">

          <h2 class="h4 fw-bold">
            Resumen
          </h2>

          <div class="d-flex justify-content-between mt-4">
            <span>Subtotal</span>
            <span>{{ money(cart.subtotal) }}</span>
          </div>

          <div class="d-flex justify-content-between text-success mt-2">
            <span>Ahorras</span>
            <span>-{{ money(cart.ahorro) }}</span>
          </div>

          <hr />

          <div class="d-flex justify-content-between fs-4 fw-bold">
            <span>Total</span>
            <span>{{ money(cart.total) }}</span>
          </div>

          <button
            class="btn btn-dark btn-lg w-100 mt-4"
            @click="continuar"
          >
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

<style scoped>

/* TARJETA DEL PRODUCTO */

.cart-item {
  padding: 24px;
  border-radius: 12px;
  background: var(--bs-body-bg);
  border: 1px solid var(--bs-border-color);
}

/* IMAGEN DEL PRODUCTO */

.cart-thumb {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 120px;
  height: 120px;
  flex-shrink: 0;
  border-radius: 10px;
  overflow: hidden;
  background: #f5f5f5;
  text-decoration: none;
}

.cart-thumb img {
  display: block;
  width: 100%;
  height: 100%;
  padding: 5px;
  object-fit: contain;
  object-position: center;
  box-sizing: border-box;
}

/* INFORMACION */

.cart-product-info {
  min-width: 0;
}

.cart-product-name {
  display: block;
  font-size: 17px;
  font-weight: 700;
  color: var(--bs-body-color);
  text-decoration: none;
  overflow-wrap: anywhere;
}

.cart-product-name:hover {
  color: #ed2947;
}

.cart-old-price {
  color: var(--bs-secondary-color);
  text-decoration: line-through;
  font-size: 13px;
  margin-top: 5px;
}

.cart-product-price {
  font-size: 18px;
  font-weight: 800;
}

/* ELIMINAR PRODUCTO */

.cart-remove {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  margin-top: 8px;
  padding: 0;
  border: none;
  background: transparent;
  color: #ed2947;
  font-size: 13px;
  cursor: pointer;
}

.cart-remove svg {
  width: 15px;
  height: 15px;
  fill: none;
  stroke: currentColor;
  stroke-width: 1.6;
  stroke-linecap: round;
  stroke-linejoin: round;
}

/* CANTIDAD */

.cart-quantity {
  flex-shrink: 0;
}

.quantity-control {
  display: inline-flex;
  align-items: center;
  border: 1px solid var(--bs-border-color);
  border-radius: 8px;
  overflow: hidden;
}

.quantity-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 42px;
  padding: 0;
  border: none;
  background: transparent;
  color: var(--bs-body-color);
  font-size: 23px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.quantity-btn:hover:not(:disabled) {
  background: #ed2947;
  color: white;
}

.quantity-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.quantity-value {
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 36px;
  height: 42px;
  font-weight: 700;
  border-left: 1px solid var(--bs-border-color);
  border-right: 1px solid var(--bs-border-color);
}

.cart-item-total {
  display: block;
  margin-top: 8px;
  text-align: center;
  font-weight: 700;
}

/* ADAPTACION PARA CELULARES */

@media (max-width: 767px) {

  .cart-item {
    display: grid !important;
    grid-template-columns: 95px minmax(0, 1fr);
    gap: 12px !important;
    padding: 15px !important;
  }

  .cart-thumb {
    width: 95px;
    height: 110px;
  }

  .cart-product-name {
    font-size: 15px;
  }

  .cart-product-price {
    font-size: 17px;
  }

  .cart-quantity {
    grid-column: 2;
  }

  .quantity-btn {
    width: 36px;
    height: 38px;
  }

  .quantity-value {
    height: 38px;
    min-width: 32px;
  }

  .cart-item-total {
    text-align: left;
  }

}

</style>
