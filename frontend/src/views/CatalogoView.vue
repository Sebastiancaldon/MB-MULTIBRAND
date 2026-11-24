
<script setup>
import { computed, onMounted, ref, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useCatalogoStore } from '@/stores/catalogo'
import { useCarritoStore } from '@/stores/carrito'
import { useAuthStore } from '@/stores/auth'
import ProductCard from '@/components/ProductCard.vue'
import DescuentosCarousel from '@/components/DescuentosCarousel.vue'
import calificacionesService from '@/services/calificacionesService'

const route = useRoute()
const router = useRouter()
const store = useCatalogoStore()
const cart = useCarritoStore()
const auth = useAuthStore()

const marca = ref('')
const busqueda = ref('')
const categoria = ref('')
const ratings = ref({})
const ranking = ref([])
const reputaciones = ref([])
const reviewError = ref('')

const marcas = [
  {
    id: '',
    nombre: 'Todas',
    tag: 'MB',
    claim: 'TODAS LAS MARCAS. UN SOLO LUGAR.',
    sub: 'Encuentra ofertas reales en ropa, calzado y accesorios.',
  },
  {
    id: 'Nike',
    nombre: 'Nike',
    tag: 'NIKE',
    claim: 'JUST DO IT. AHORA CON DESCUENTO.',
    sub: 'Movimiento, energía y ofertas para tu próximo look.',
  },
  {
    id: 'Adidas',
    nombre: 'Adidas',
    tag: 'adidas',
    claim: 'ORIGINALS. ESTILO SIN LÍMITES.',
    sub: 'Descubre las ofertas Adidas de nuestro catálogo.',
  },
  {
    id: 'Puma',
    nombre: 'Puma',
    tag: 'PUMA',
    claim: 'FOREVER FASTER. MEJOR PRECIO.',
    sub: 'Explora Puma y lleva tu estilo más lejos.',
  },
]

const activa = computed(() => {
  const lista = Array.isArray(marcas) ? marcas : []

  return (
    lista.find((m) => m && m.id === marca.value) ||
    lista[0] || {
      id: '',
      nombre: 'Todas',
      claim: 'TODAS LAS MARCAS. UN SOLO LUGAR.',
      sub: 'Encuentra ofertas reales en ropa, calzado y accesorios.'
    }
  )
})

// NORMALIZAR TEXTOS PARA EL BUSCADOR
const normalizar = (texto) =>
  String(texto ?? '')
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
    .trim()


// FILTRAR PRODUCTOS POR MARCA, CATEGORIA Y BUSQUEDA
const visibles = computed(() => {
  const texto = normalizar(busqueda.value)
  const marcaSeleccionada = normalizar(marca.value)
  const categoriaSeleccionada = normalizar(categoria.value)

  const productos = Array.isArray(store.lista)
    ? store.lista
    : []

  return productos.filter((p) => {
    if (!p) return false

    const marcaProducto = normalizar(p.marca)
    const categoriaProducto = normalizar(p.categoria)

    const cumpleMarca =
      !marcaSeleccionada ||
      marcaProducto === marcaSeleccionada

    const cumpleCategoria =
      !categoriaSeleccionada ||
      categoriaProducto === categoriaSeleccionada

    const contenido = normalizar([
      p.producto,
      p.marca,
      p.categoria,
      p.descripcion
    ].filter(Boolean).join(' '))

    const palabras = texto.split(/\s+/).filter(Boolean)

    const cumpleBusqueda = palabras.every(
      palabra => contenido.includes(palabra)
    )

    return cumpleMarca &&
           cumpleCategoria &&
           cumpleBusqueda
  })
})

// RANKING DE PRODUCTOS

const destacados = computed(() => {
  return [...ranking.value]
    .filter((producto) => {
      return (
        !marca.value ||
        normalizar(producto.marca) === normalizar(marca.value)
      )
    })
    .sort((a, b) => {
      const promedioA = Number(a.promedio) || 0
      const promedioB = Number(b.promedio) || 0

      const votosA = Number(a.votos) || 0
      const votosB = Number(b.votos) || 0

      if (promedioB !== promedioA) {
        return promedioB - promedioA
      }

      return votosB - votosA
    })
    .slice(0, 4)
})


const reputacionActual = computed(() =>
  reputaciones.value.find(
    (r) =>
      String(r.marca).toLowerCase() ===
      marca.value.toLowerCase()
  )
)

// SELECCIONAR MARCA

// SELECCIONAR MARCA
async function seleccionar(id) {
  marca.value = id || ''
  busqueda.value = ''
  categoria.value = ''

  await router.replace({
    path: '/',
    query: id ? { marca: id } : {},
    hash: '#ofertas'
  })

  await nextTick()

  document.getElementById('ofertas')?.scrollIntoView({
    behavior: 'smooth',
    block: 'start'
  })
}

// LIMPIAR FILTROS
function limpiar() {
  busqueda.value = ''
  categoria.value = ''
  marca.value = ''

  router.replace({
    path: '/',
    query: {},
  })
}

// DESPLAZAMIENTO A SECCIONES
async function desplazarA(id) {
  await nextTick()

  const elemento = document.getElementById(id)

  if (!elemento) return

  elemento.scrollIntoView({
    behavior: 'smooth',
    block: 'start',
  })
}

// IR AL RANKING
async function irAlRanking() {
  await desplazarA('valoraciones')
}

// IR A PRODUCTOS
async function irAOfertas() {
  await desplazarA('ofertas')
}

// BUSCADOR PRINCIPAL DEL CATÁLOGO

async function buscar() {
  const texto = busqueda.value.trim()

  marca.value = ''
  categoria.value = ''

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

// CARGAR PRODUCTOS
async function cargar() {
  try {
    await store.cargar()
  } catch (error) {
    console.error('Error al cargar productos:', error)
  }
}

// CARGAR RESEÑAS Y RANKING
async function cargarReviews() {
  reviewError.value = ''

  const [res, top, rep] = await Promise.allSettled([
    calificacionesService.resumenes(),
    calificacionesService.ranking({ limite: 8 }),
    calificacionesService.reputacionMarcas(),
  ])

  if (res.status === 'fulfilled') {
    ratings.value = Object.fromEntries(
      (res.value.data.resumenes || []).map(
        (r) => [r.id_producto, r]
      )
    )
  }

  if (top.status === 'fulfilled') {
    ranking.value = top.value.data.ranking || []
  }

  if (rep.status === 'fulfilled') {
    reputaciones.value = rep.value.data.marcas || []
  }

  if (
    [res, top, rep].every(
      (resultado) => resultado.status === 'rejected'
    )
  ) {
    reviewError.value =
      'Las calificaciones no están disponibles en este momento.'
  }
}

// SINCRONIZAR FILTROS CON LA URL
watch(
  () => route.query,
  (q) => {
    busqueda.value = String(q.q || '')
    categoria.value = String(q.categoria || '')

    const marcaEncontrada = marcas.find(
      (m) =>
        m.id.toLowerCase() ===
        String(q.marca || '').toLowerCase()
    )

    marca.value = marcaEncontrada
      ? marcaEncontrada.id
      : ''
  },
  { immediate: true }
)

// CARGAR DATOS AL ENTRAR
onMounted(async () => {
  await Promise.allSettled([
    cargar(),
    cargarReviews(),
  ])

  await nextTick()

  if (route.hash === '#valoraciones') {
    await irAlRanking()
  }

  if (route.hash === '#ofertas') {
    await irAOfertas()
  }
})

// DETECTAR CAMBIOS DE NAVEGACIÓN
watch(
  () => route.hash,
  async (hash) => {
    if (hash === '#valoraciones') {
      await irAlRanking()
    }

    if (hash === '#ofertas') {
      await irAOfertas()
    }
  }
)
</script>

<template>
  <div
    class="brand-page"
    :class="'theme-' + (marca || 'all').toLowerCase()"
  >
    <!-- ENCABEZADO PRINCIPAL -->
    <section class="brand-hero">
      <div class="container brand-hero-inner">
        <div class="brand-hero-copy">
          <div class="brand-eyebrow">
            MB MULTIBRAND /
            {{ activa.nombre.toUpperCase() }} /
            DESCUENTOS VIGENTES
          </div>

          <h1>{{ activa.claim }}</h1>

          <p>{{ activa.sub }}</p>

          <div class="d-flex gap-3 flex-wrap">
            <a
              href="#ofertas"
              class="btn brand-primary btn-lg"
              @click.prevent="irAOfertas"
            >
              Comprar ofertas
              <span aria-hidden="true">↗</span>
            </a>

            <a
              href="#valoraciones"
              class="btn brand-secondary btn-lg"
              @click.prevent="irAlRanking"
            >
              ★ Mejor valorados
            </a>

            <RouterLink
              to="/carrito"
              class="btn brand-secondary btn-lg"
            >
              Mi carrito ({{ cart.unidades }})
            </RouterLink>
          </div>

          <div class="brand-hero-foot">
            PRODUCTOS Y PRECIOS CONSULTADOS EN EL
            CATÁLOGO EN TIEMPO REAL
          </div>
        </div>

        <div class="hero-carousel-panel">
          <DescuentosCarousel
            :productos="visibles"
            modo="hero"
          />
        </div>
      </div>
    </section>

    <div class="container">
      <!-- SELECCIÓN DE MARCAS -->
      <section
        class="brand-picker"
        aria-label="Elegir marca"
      >
        <div class="brand-picker-heading">
          <div>
            <span class="section-kicker">
              ELIGE TU ESTILO
            </span>

            <h2 class="h3 fw-bold mb-1">
              Compra por marca
            </h2>

            <p class="text-secondary mb-0">
              Selecciona un logo para cambiar la
              colección y su identidad visual.
            </p>
          </div>

          <button
            class="btn btn-sm btn-outline-dark"
            @click="limpiar"
          >
            Ver todas ↺
          </button>
        </div>

        <div class="brand-grid">
          
<button
  v-for="m in marcas"
  :key="m.id || 'all'"
  class="brand-tile"
  :class="{ 'is-active': marca === m.id }"
  :aria-pressed="marca === m.id"
  @click="seleccionar(m.id)"
>

            <span
              v-if="m.id"
              class="official-logo-box"
            >
              <img
                :src="`/marcas/${m.id.toLowerCase()}.png`"
                :alt="`Logo original de ${m.nombre}`"
              />
            </span>

            <span v-else class="mb-logo">
              <b>MB</b>
              <small>MULTIBRAND</small>
            </span>

            <span class="brand-tile-label">
              {{
                m.id
                  ? `Ver ${m.nombre}`
                  : 'Todas las marcas'
              }}
            </span>
          </button>
        </div>
      </section>

      <!-- SERVICIOS -->
      <section class="service-strip row g-3">
        <div class="col-md-4">
          <RouterLink
            to="/carrito"
            class="service-panel"
          >
            <span class="service-icon">🛒</span>

            <div>
              <strong>Compra interactiva</strong>

              <p>
                {{ cart.unidades }} artículos ·
                {{
                  auth.estaAutenticado
                    ? 'Listo para confirmar'
                    : 'Agrega sin iniciar sesión'
                }}
              </p>
            </div>

            <span>↗</span>
          </RouterLink>
        </div>

        <div class="col-md-4">
          <a
            href="#valoraciones"
            class="service-panel"
            @click.prevent="irAlRanking"
          >
            <span class="service-icon">★</span>

            <div>
              <strong>Opiniones verificadas</strong>
              <p>Consulta el ranking de clientes</p>
            </div>

            <span>↗</span>
          </a>
        </div>

        <div class="col-md-4">
          <RouterLink
            :to="
              auth.estaAutenticado
                ? '/perfil'
                : '/login?redirect=/perfil'
            "
            class="service-panel"
          >
            <span class="service-icon">♡</span>

            <div>
              <strong>Favoritos y reseñas</strong>

              <p>
                {{
                  auth.estaAutenticado
                    ? 'Ver mi actividad'
                    : 'Ingresa para calificar compras'
                }}
              </p>
            </div>

            <span>↗</span>
          </RouterLink>
        </div>
      </section>

      <!-- CATÁLOGO DE PRODUCTOS -->
      <section id="ofertas" class="py-5">
        <div
          class="d-flex justify-content-between align-items-end flex-wrap gap-3 mb-4"
        >
          <div>
            <span class="section-kicker">
              OFERTAS SELECCIONADAS
            </span>

            <h2 class="section-title mb-1">
              {{
                marca
                  ? `Colección ${marca}`
                  : 'Descubre las ofertas'
              }}
              <span class="brand-dot">.</span>
            </h2>

            <p class="text-secondary mb-0">
              {{ visibles.length }} productos encontrados
            </p>
          </div>

          <div class="d-flex flex-wrap gap-2">
            <button
              v-for="c in [
                '',
                'Ropa',
                'Calzado',
                'Accesorios',
              ]"
              :key="c"
              class="btn btn-sm rounded-pill category-pill"
              :class="categoria === c ? 'selected' : ''"
              @click="categoria = c"
            >
              {{ c || 'Todo' }}
            </button>
          </div>
        </div>

        <!-- BUSCADOR DE PRODUCTOS -->
        <div class="mb-4 d-flex gap-2">
          <input
            v-model="busqueda"
            class="form-control brand-search"
            placeholder="Buscar dentro de las ofertas…"
            aria-label="Buscar productos"
            @keyup.enter="buscar"
          />

          <button
            class="btn brand-primary"
            @click="buscar"
          >
            Buscar
          </button>
        </div>

        <!-- ERRORES DEL CATÁLOGO -->
        <div
          v-if="store.error"
          class="alert alert-danger"
          role="alert"
        >
          {{ store.error }}

          <button
            class="btn btn-sm btn-outline-danger"
            @click="cargar"
          >
            Reintentar
          </button>
        </div>

        <!-- CARGANDO PRODUCTOS -->
        <div
          v-if="store.cargando"
          class="row g-3"
        >
          <div
            v-for="n in 8"
            :key="n"
            class="col-6 col-lg-3"
          >
            <div class="skeleton"></div>
          </div>
        </div>

        <!-- SIN RESULTADOS -->
        <div
          v-else-if="!visibles.length"
          class="empty-state"
        >
          <h3 class="h5">
            No encontramos productos para esta selección.
          </h3>

          <p>
            Prueba con otro nombre, marca o categoría.
          </p>

          <button
            class="btn brand-primary"
            @click="limpiar"
          >
            Explorar todas las marcas
          </button>
        </div>

        <!-- PRODUCTOS DISPONIBLES -->
        <div
          v-else
          class="row g-3 g-lg-4"
        >
          <div
            v-for="p in visibles"
            :key="p.id_producto"
            class="col-6 col-lg-3"
          >
            <ProductCard
              :producto="p"
              :rating="ratings[p.id_producto]"
            />
          </div>
        </div>
      </section>

      <!-- RANKING DE PRODUCTOS -->
      <section
        id="valoraciones"
        class="ratings-section mb-5"
      >
        <div
          class="d-flex justify-content-between flex-wrap align-items-end gap-3 mb-4"
        >
          <div>
            <span class="section-kicker">
              MICROSERVICIO DE CALIFICACIONES
            </span>

            <h2 class="section-title mb-1">
              Lo mejor valorado
              <span class="brand-dot">★</span>
            </h2>

            <p class="text-secondary mb-0">
              Ranking calculado con reseñas reales
              de clientes.
            </p>
          </div>

          <button
            class="btn btn-outline-dark"
            @click="cargarReviews"
          >
            Actualizar reseñas ↻
          </button>
        </div>

        <!-- ERROR DE RESEÑAS -->
        <div
          v-if="reviewError"
          class="alert alert-warning"
        >
          {{ reviewError }}
        </div>

        <!-- REPUTACIÓN DE LA MARCA -->
        <div
          v-if="reputacionActual"
          class="reputation-banner"
        >
          <span class="fs-2">★</span>

          <div>
            <strong>
              {{ marca }} ·
              {{
                reputacionActual.promedio == null
                  ? 'Sin calificaciones'
                  : Number(
                      reputacionActual.promedio
                    ).toFixed(1) + ' / 5'
              }}
            </strong>

            <p class="mb-0">
              {{ reputacionActual.total_votos }}
              opiniones ·
              {{ reputacionActual.productos_activos }}
              productos activos
            </p>
          </div>
        </div>

        <!-- PRODUCTOS MEJOR VALORADOS -->
        <div
          v-if="destacados.length"
          class="row g-3"
        >
          
<div
  v-for="(r, index) in destacados"
  :key="r.id_producto"
  class="col-md-6 col-xl-3"
>

            <RouterLink
              :to="`/producto/${r.id_producto}`"
              class="ranking-card"
            >
              <span class="ranking-position">
                #{{ index + 1 }}
              </span>

              <span class="text-warning fs-4">
                ★★★★★
              </span>

              <strong>
                {{ r.producto }}
              </strong>

              <span class="text-secondary small">
                {{ r.marca }} ·
                {{ Number(r.promedio).toFixed(1) }}
                / 5 ·
                {{ r.votos }} reseñas
              </span>

              <span class="ranking-cta">
                Ver producto y calificar ★ ↗
              </span>
            </RouterLink>
          </div>
        </div>

        <!-- SIN RANKING -->
        <div
          v-else
          class="empty-state py-4"
        >
          Todavía no hay suficientes reseñas
          para mostrar un ranking. Puedes revisar
          las opiniones en cada producto.
        </div>

        <!-- INVITACIÓN A CALIFICAR -->
        <div class="ratings-cta mt-4">
          <div>
            <strong>
              ¿Ya compraste? Tu opinión cuenta.
            </strong>

            <p class="mb-0">
              Califica tus productos desde tu perfil
              y ayuda a otros compradores.
            </p>
          </div>

          <RouterLink
            :to="
              auth.estaAutenticado
                ? '/perfil'
                : '/login?redirect=/perfil'
            "
            class="btn brand-primary"
          >
            {{
              auth.estaAutenticado
                ? 'Calificar mis compras'
                : 'Ingresar para calificar'
            }}
            ↗
          </RouterLink>
        </div>
      </section>
    </div>
  </div>
</template>
