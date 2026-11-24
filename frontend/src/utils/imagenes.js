
const fotosImportadas = {
  'air force 1': [
    '/productos/nike-air-force-1-foto-1.webp',
    '/productos/nike-air-force-1-foto-2.webp',
    '/productos/nike-air-force-1-foto-3.webp',
    '/productos/nike-air-force-1-foto-4.webp'
  ],

  'baseball cap': [
    '/productos/adidas-baseball-cap-foto-1.avif',
    '/productos/adidas-baseball-cap-foto-2.avif',
    '/productos/adidas-baseball-cap-foto-3.avif'
  ],

  'classic backpack': [
    '/productos/adidas-classic-backpack-foto-1.avif',
    '/productos/adidas-classic-backpack-foto-2.avif',
    '/productos/adidas-classic-backpack-foto-3.avif',
    '/productos/adidas-classic-backpack-foto-4.avif'
  ],

  'club fleece jogger': [
    '/productos/nike-club-fleece-jogger-foto-1.webp',
    '/productos/nike-club-fleece-jogger-foto-2.webp',
    '/productos/nike-club-fleece-jogger-foto-3.jpg'
  ],

  'court vision low': [
    '/productos/nike-court-vision-low-foto-1.webp',
    '/productos/nike-court-vision-low-foto-2.webp',
    '/productos/nike-court-vision-low-foto-3.webp',
    '/productos/nike-court-vision-low-foto-4.webp'
  ],

  'entrada 22 jersey': [
    '/productos/adidas-entrada-22-foto-1.avif',
    '/productos/adidas-entrada-22-foto-2.avif'
  ],

  'essentials hoodie': [
    '/productos/adidas-essentials-hoodie-foto-1.avif',
    '/productos/adidas-essentials-hoodie-foto-2.avif'
  ],

  'grand court base': [
    '/productos/adidas-grand-court-base-foto-1.avif',
    '/productos/adidas-grand-court-base-foto-2.avif',
    '/productos/adidas-grand-court-base-foto-3.avif',
    '/productos/adidas-grand-court-base-foto-4.avif'
  ],

  'heritage backpack': [
    '/productos/nike-heritage-backpack-foto-1.webp',
    '/productos/nike-heritage-backpack-foto-2.webp',
    '/productos/nike-heritage-backpack-foto-3.webp',
    '/productos/nike-heritage-backpack-foto-4.webp'
  ],

  'dri-fit training tee': [
    '/productos/nike-dri-fit-tee-foto-1.webp',
    '/productos/nike-dri-fit-tee-foto-2.webp',
    '/productos/nike-dri-fit-tee-foto-3.webp'
  ],

  'revolution 7': [
    '/productos/nike-revolution-7-foto-1.webp',
    '/productos/nike-revolution-7-foto-2.webp',
    '/productos/nike-revolution-7-foto-3.webp',
    '/productos/nike-revolution-7-foto-4.webp'
  ],

  'runfalcon 3': [
    '/productos/adidas-runfalcon-3-foto-1.webp',
    '/productos/adidas-runfalcon-3-foto-2.webp',
    '/productos/adidas-runfalcon-3-foto-3.webp',
    '/productos/adidas-runfalcon-3-foto-4.webp'
  ],

  'sportswear cap': [
    '/productos/nike-sportswear-cap-foto-1.avif',
    '/productos/nike-sportswear-cap-foto-2.avif',
    '/productos/nike-sportswear-cap-foto-3.avif',
    '/productos/nike-sportswear-cap-foto-4.avif'
  ],

  'superstar': [
    '/productos/adidas-superstar-foto-1.avif',
    '/productos/adidas-superstar-foto-2.avif',
    '/productos/adidas-superstar-foto-3.avif',
    '/productos/adidas-superstar-foto-4.avif'
  ],

  'tech fleece hoodie': [
    '/productos/nike-tech-fleece-hoodie-foto-1.webp',
    '/productos/nike-tech-fleece-hoodie-foto-2.webp'
  ],

  'tiro track pants': [
    '/productos/adidas-tiro-pants-foto-1.webp',
    '/productos/adidas-tiro-pants-foto-2.webp'
  ],

  'essentials small logo tee': [
    '/productos/essentials-small-logo-tee-2.webp'
  ],

  'evostripe hoodie': [
    '/productos/Evostripe Hoodie 1.webp',
    '/productos/Evostripe Hoodie 2.webp'
  ],

  'smash v2': [
    '/productos/Smash V2 (1).webp',
    '/productos/Smash V2 (2).webp',
    '/productos/Smash V2 (3).webp',
    '/productos/Smash V2 (4).webp'
  ],

  'classic logo tee': [
    '/productos/Classic Logo Tee 1.jpg',
    '/productos/Classic Logo Tee 2.jpg'
  ],

  'phase backpack': [
    '/productos/Phase Backpack 1.webp',
    '/productos/Phase Backpack 2.webp'
  ],

  'metal cat cap': [
    '/productos/Metal Cat Cap 1.webp',
    '/productos/Metal Cat Cap 2.webp'
  ],

  'future rider': [
    '/productos/future rider 1.webp',
    '/productos/future rider 2.webp',
    '/productos/future rider 3.webp',
    '/productos/future rider 4.webp'
  ],

  'carina street': [
    '/productos/Carina Street 1.webp',
    '/productos/Carina Street 2.webp',
    '/productos/Carina Street 3.webp',
    '/productos/Carina Street 4.webp'
  ]
}

// Fotografías originales del proyecto

const fotografias = [
  {
    patron: /air\s*max\s*270/i,
    slug: 'nike-air-max-270'
  },
  {
    patron: /forum\s*low/i,
    slug: 'adidas-forum-low'
  },
  {
    patron: /rs[\s-]*x/i,
    slug: 'puma-rs-x'
  }
]

// Normalizar nombres de productos

function normalizar(texto) {
  return String(texto || '')
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
    .trim()
    .replace(/\s+/g, ' ')
}

// Obtener únicamente fotografías reales

export function imagenesProducto(producto) {

  if (!producto) return []

  const nombre = normalizar(
    producto.producto || producto.nombre
  )

  const marca = normalizar(producto.marca)

  // Buscar fotografías importadas

  const importadas =
    fotosImportadas[nombre] ||
    Object.entries(fotosImportadas).find(
      ([clave]) => nombre.includes(clave)
    )?.[1] ||
    []

  // Eliminar rutas duplicadas

  if (importadas.length) {
    return [...new Set(importadas)]
  }

  // Buscar fotografías originales

  const foto = fotografias.find(
    ({ patron, slug }) =>
      patron.test(nombre) &&
      (!marca || slug.startsWith(marca))
  )

  if (foto) {
    return [
      'principal',
      'lateral',
      'posterior',
      'detalle'
    ].map(
      vista => `/productos/${foto.slug}-${vista}.jpg`
    )
  }

  // No agregar ilustraciones de relleno

  return []
}

// Obtener fotografía principal

export function imagenPrincipal(producto) {

  return imagenesProducto(producto)[0] || null

}
