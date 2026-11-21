<script setup>
  import { computed, onMounted, ref, watch, nextTick } from 'vue'
  import { useRoute, useRouter } from 'vue-router'
  import { useCatalogoStore } from '@/stores/catalogo'
  import { useCarritoStore } from '@/stores/carrito'
  import { useAuthStore } from '@/stores/auth'
  import ProductCard from '@/components/ProductCard.vue'
  import DescuentosCarousel from '@/components/DescuentosCarousel.vue'
  import calificacionesService from '@/services/calificacionesService'
  const route = useRoute(),
    router = useRouter(),
    store = useCatalogoStore(),
    cart = useCarritoStore(),
    auth = useAuthStore()
  const marca = ref(''),
    busqueda = ref(''),
    categoria = ref(''),
    ratings = ref({}),
    ranking = ref([]),
    reputaciones = ref([]),
    reviewError = ref('')
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
  const activa = computed(() => marcas.find((m) => m.id === marca.value) || marcas[0])
  
const normalizar = (texto) =>
  String(texto ?? '')
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
    .trim()

const visibles = computed(() => {
  const texto = normalizar(busqueda.value)

  return store.lista.filter((p) => {
    const marcaProducto = normalizar(p.marca)
    const categoriaProducto = normalizar(p.categoria)

    const cumpleMarca =
      !marca.value ||
      marcaProducto === normalizar(marca.value)

    const cumpleCategoria =
      !categoria.value ||
      categoriaProducto === normalizar(categoria.value)

    const contenido = normalizar(
      [
        p.producto,
        p.marca,
        p.categoria,
        p.descripcion
      ].filter(Boolean).join(' ')
    )

    const palabras = texto.split(/\s+/).filter(Boolean)

    const cumpleBusqueda =
      !texto ||
      palabras.every((palabra) =>
        contenido.includes(palabra)
      )

    return (
      cumpleMarca &&
      cumpleCategoria &&
      cumpleBusqueda
    )
  })
}
)

  const destacados = computed(() =>
    ranking.value
      .filter((r) => !marca.value || String(r.marca).toLowerCase() === marca.value.toLowerCase())
      .slice(0, 4),
  )
  const reputacionActual = computed(() =>
    reputaciones.value.find((r) => String(r.marca).toLowerCase() === marca.value.toLowerCase()),
  )
  function seleccionar(id) {
    marca.value = id
    router.replace({ path: '/', query: { ...route.query, marca: id || undefined } })
  }
  function limpiar() {
    busqueda.value = ''
    categoria.value = ''
    seleccionar('')
    router.replace('/')
  }
  
async function buscar() {
  const texto = busqueda.value.trim()

  await router.push({
    path: '/',
    query: {
      q: texto || undefined,
      marca: marca.value || undefined,
      categoria: categoria.value || undefined
    },
    hash: '#ofertas'
  })

  document.getElementById('ofertas')?.scrollIntoView({
    behavior: 'smooth',
    block: 'start'
  })
}

  async function cargar() {
    try {
      await store.cargar()
    } catch {}
  }
  async function cargarReviews() {
    reviewError.value = ''
    const [res, top, rep] = await Promise.allSettled([
      calificacionesService.resumenes(),
      calificacionesService.ranking({ limite: 8 }),
      calificacionesService.reputacionMarcas(),
    ])
    if (res.status === 'fulfilled')
      ratings.value = Object.fromEntries(
        (res.value.data.resumenes || []).map((r) => [r.id_producto, r]),
      )
    if (top.status === 'fulfilled') ranking.value = top.value.data.ranking || []
    if (rep.status === 'fulfilled') reputaciones.value = rep.value.data.marcas || []
    if ([res, top, rep].every((x) => x.status === 'rejected'))
      reviewError.value = 'Las calificaciones no están disponibles en este momento.'
  }
  watch(
    () => route.query,
    (q) => {
      busqueda.value = String(q.q || '')
      categoria.value = String(q.categoria || '')
      marca.value = marcas.some((m) => m.id.toLowerCase() === String(q.marca || '').toLowerCase())
        ? marcas.find((m) => m.id.toLowerCase() === String(q.marca || '').toLowerCase()).id
        : ''
    },
    { immediate: true },
  )
  
  
onMounted(async () => {
  await Promise.allSettled([
    cargar(),
    cargarReviews()
  ])

  await nextTick()

  if (route.hash === '#valoraciones') {
    await irAlRanking()
  }
})

watch(
  () => route.hash,
  async (hash) => {
    if (hash === '#valoraciones') {
      await irAlRanking()
    }
  }
)

</script>
<template>
  <div class="brand-page" :class="'theme-' + (marca || 'all').toLowerCase()">
    <section class="brand-hero">
      <div class="container brand-hero-inner">
        <div class="brand-hero-copy">
          <div class="brand-eyebrow">
            MB MULTIBRAND / {{ activa.nombre.toUpperCase() }} / DESCUENTOS VIGENTES
          </div>
          <h1>{{ activa.claim }}</h1>
          <p>{{ activa.sub }}</p>
          <div class="d-flex gap-3 flex-wrap">
            <a href="#ofertas" class="btn brand-primary btn-lg"
              >Comprar ofertas <span aria-hidden="true">↗</span></a
            ><a href="#valoraciones" class="btn brand-secondary btn-lg">★ Mejor valorados</a
            ><RouterLink to="/carrito" class="btn brand-secondary btn-lg"
              >Mi carrito ({{ cart.unidades }})</RouterLink
            >
          </div>
          <div class="brand-hero-foot">
            PRODUCTOS Y PRECIOS CONSULTADOS EN EL CATÁLOGO EN TIEMPO REAL
          </div>
        </div>
        <div class="hero-carousel-panel">
          <DescuentosCarousel :productos="visibles" modo="hero" />
        </div>
      </div>
    </section>
    <div class="container">
      <section class="brand-picker" aria-label="Elegir marca">
        <div class="brand-picker-heading">
          <div>
            <span class="section-kicker">ELIGE TU ESTILO</span>
            <h2 class="h3 fw-bold mb-1">Compra por marca</h2>
            <p class="text-secondary mb-0">
              Selecciona un logo para cambiar la colección y su identidad visual.
            </p>
          </div>
          <button class="btn btn-sm btn-outline-dark" @click="limpiar">Ver todas ↺</button>
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
            <span v-if="m.id" class="official-logo-box"
              ><img
                :src="`/marcas/${m.id.toLowerCase()}.png`"
                :alt="`Logo original de ${m.nombre}`" /></span
            ><span v-else class="mb-logo"><b>MB</b><small>MULTIBRAND</small></span
            ><span class="brand-tile-label">{{
              m.id ? `Ver ${m.nombre}` : 'Todas las marcas'
            }}</span>
          </button>
        </div>
      </section>
      <section class="service-strip row g-3">
        <div class="col-md-4">
          <RouterLink to="/carrito" class="service-panel"
            ><span class="service-icon">🛒</span>
            <div>
              <strong>Compra interactiva</strong>
              <p>
                {{ cart.unidades }} artículos ·
                {{ auth.estaAutenticado ? 'Listo para confirmar' : 'Agrega sin iniciar sesión' }}
              </p>
            </div>
            <span>↗</span></RouterLink
          >
        </div>
        <div class="col-md-4">
          <a href="#valoraciones" class="service-panel"
            ><span class="service-icon">★</span>
            <div>
              <strong>Opiniones verificadas</strong>
              <p>Consulta el ranking de clientes</p>
            </div>
            <span>↗</span></a
          >
        </div>
        <div class="col-md-4">
          <RouterLink
            :to="auth.estaAutenticado ? '/perfil' : '/login?redirect=/perfil'"
            class="service-panel"
            ><span class="service-icon">♡</span>
            <div>
              <strong>Favoritos y reseñas</strong>
              <p>
                {{ auth.estaAutenticado ? 'Ver mi actividad' : 'Ingresa para calificar compras' }}
              </p>
            </div>
            <span>↗</span></RouterLink
          >
        </div>
      </section>
      <section id="ofertas" class="py-5">
        <div class="d-flex justify-content-between align-items-end flex-wrap gap-3 mb-4">
          <div>
            <span class="section-kicker">OFERTAS SELECCIONADAS</span>
            <h2 class="section-title mb-1">
              {{ marca ? `Colección ${marca}` : 'Descubre las ofertas'
              }}<span class="brand-dot">.</span>
            </h2>
            <p class="text-secondary mb-0">{{ visibles.length }} productos encontrados</p>
          </div>
          <div class="d-flex flex-wrap gap-2">
            <button
              v-for="c in ['', 'Ropa', 'Calzado', 'Accesorios']"
              :key="c"
              class="btn btn-sm rounded-pill category-pill"
              :class="categoria === c ? 'selected' : ''"
              @click="categoria = c"
            >
              {{ c || 'Todo' }}
            </button>
          </div>
        </div>
        <div class="mb-4 d-flex gap-2">
          <input
            v-model="busqueda"
            class="form-control brand-search"
            placeholder="Buscar dentro de las ofertas…"
            aria-label="Buscar productos"
          /><button class="btn brand-primary" @click="buscar">Buscar</button>
        </div>
        <div v-if="store.error" class="alert alert-danger" role="alert">
          {{ store.error }}
          <button class="btn btn-sm btn-outline-danger" @click="cargar">Reintentar</button>
        </div>
        <div v-if="store.cargando" class="row g-3">
          <div v-for="n in 8" :key="n" class="col-6 col-lg-3"><div class="skeleton" /></div>
        </div>
        <div v-else-if="!visibles.length" class="empty-state">
          <h3 class="h5">No encontramos productos para esta selección.</h3>
          <p>Prueba con otra marca o categoría.</p>
          <button class="btn brand-primary" @click="limpiar">Explorar todas las marcas</button>
        </div>
        <div v-else class="row g-3 g-lg-4">
          <div v-for="p in visibles" :key="p.id_producto" class="col-6 col-lg-3">
            <ProductCard :producto="p" :rating="ratings[p.id_producto]" />
          </div>
        </div>
      </section>
      <section id="valoraciones" class="ratings-section mb-5">
        <div class="d-flex justify-content-between flex-wrap align-items-end gap-3 mb-4">
          <div>
            <span class="section-kicker">MICROSERVICIO DE CALIFICACIONES</span>
            <h2 class="section-title mb-1">Lo mejor valorado <span class="brand-dot">★</span></h2>
            <p class="text-secondary mb-0">Ranking calculado con reseñas reales de clientes.</p>
          </div>
          <button class="btn btn-outline-dark" @click="cargarReviews">Actualizar reseñas ↻</button>
        </div>
        <div v-if="reviewError" class="alert alert-warning">{{ reviewError }}</div>
        <div v-if="reputacionActual" class="reputation-banner">
          <span class="fs-2">★</span>
          <div>
            <strong
              >{{ marca }} ·
              {{
                reputacionActual.promedio == null
                  ? 'Sin calificaciones'
                  : Number(reputacionActual.promedio).toFixed(1) + ' / 5'
              }}</strong
            >
            <p class="mb-0">
              {{ reputacionActual.total_votos }} opiniones ·
              {{ reputacionActual.productos_activos }} productos activos
            </p>
          </div>
        </div>
        <div v-if="destacados.length" class="row g-3">
          <div v-for="r in destacados" :key="r.id_producto" class="col-md-6 col-xl-3">
            <RouterLink :to="`/producto/${r.id_producto}`" class="ranking-card">
              ><span class="ranking-position">#{{ r.posicion }}</span
              ><span class="text-warning fs-4">★★★★★</span><strong>{{ r.producto }}</strong
              ><span class="text-secondary small"
                >{{ r.marca }} · {{ Number(r.promedio).toFixed(1) }} / 5 ·
                {{ r.votos }} reseñas</span
              ><span class="ranking-cta">Ver producto y calificar ★ ↗</span></RouterLink
            >
          </div>
        </div>
        <div v-else class="empty-state py-4">
          Todavía no hay suficientes reseñas para mostrar un ranking. Puedes revisar las opiniones
          en cada producto.
        </div>
        <div class="ratings-cta mt-4">
          <div>
            <strong>¿Ya compraste? Tu opinión cuenta.</strong>
            <p class="mb-0">Califica tus productos desde tu perfil y ayuda a otros compradores.</p>
          </div>
          <RouterLink
            :to="auth.estaAutenticado ? '/perfil' : '/login?redirect=/perfil'"
            class="btn brand-primary"
            >{{
              auth.estaAutenticado ? 'Calificar mis compras' : 'Ingresar para calificar'
            }}
            ↗</RouterLink
          >
        </div>
      </section>
    </div>
  </div>
</template>
