// Fotografías suministradas por el usuario. Si una referencia tiene menos de cuatro,
// se completan las miniaturas con las ilustraciones existentes sin duplicar fotos.
const fotosImportadas = {
  'air force 1': ["/productos/nike-air-force-1-foto-1.webp", "/productos/nike-air-force-1-foto-2.webp", "/productos/nike-air-force-1-foto-3.webp", "/productos/nike-air-force-1-foto-4.webp"],
  'baseball cap': ["/productos/adidas-baseball-cap-foto-1.avif", "/productos/adidas-baseball-cap-foto-2.avif", "/productos/adidas-baseball-cap-foto-3.avif"],
  'classic backpack': ["/productos/adidas-classic-backpack-foto-1.avif", "/productos/adidas-classic-backpack-foto-2.avif", "/productos/adidas-classic-backpack-foto-3.avif", "/productos/adidas-classic-backpack-foto-4.avif"],
  'club fleece jogger': ["/productos/nike-club-fleece-jogger-foto-1.webp", "/productos/nike-club-fleece-jogger-foto-2.webp", "/productos/nike-club-fleece-jogger-foto-3.jpg"],
  'court vision low': ["/productos/nike-court-vision-low-foto-1.webp", "/productos/nike-court-vision-low-foto-2.webp", "/productos/nike-court-vision-low-foto-3.webp", "/productos/nike-court-vision-low-foto-4.webp"],
  'entrada 22 jersey': ["/productos/adidas-entrada-22-foto-1.avif", "/productos/adidas-entrada-22-foto-2.avif"],
  'essentials hoodie': ["/productos/adidas-essentials-hoodie-foto-1.avif", "/productos/adidas-essentials-hoodie-foto-2.avif"],
  'grand court base': ["/productos/adidas-grand-court-base-foto-1.avif", "/productos/adidas-grand-court-base-foto-2.avif", "/productos/adidas-grand-court-base-foto-3.avif", "/productos/adidas-grand-court-base-foto-4.avif"],
  'heritage backpack': ["/productos/nike-heritage-backpack-foto-1.webp", "/productos/nike-heritage-backpack-foto-2.webp", "/productos/nike-heritage-backpack-foto-3.webp", "/productos/nike-heritage-backpack-foto-4.webp"],
  'dri-fit training tee': ["/productos/nike-dri-fit-tee-foto-1.webp", "/productos/nike-dri-fit-tee-foto-2.webp", "/productos/nike-dri-fit-tee-foto-3.webp"],
  'revolution 7': ["/productos/nike-revolution-7-foto-1.webp", "/productos/nike-revolution-7-foto-2.webp", "/productos/nike-revolution-7-foto-3.webp", "/productos/nike-revolution-7-foto-4.webp"],
  'runfalcon 3': ["/productos/adidas-runfalcon-3-foto-1.webp", "/productos/adidas-runfalcon-3-foto-2.webp", "/productos/adidas-runfalcon-3-foto-3.webp", "/productos/adidas-runfalcon-3-foto-4.webp"],
  'sportswear cap': ["/productos/nike-sportswear-cap-foto-1.avif", "/productos/nike-sportswear-cap-foto-2.avif", "/productos/nike-sportswear-cap-foto-3.avif", "/productos/nike-sportswear-cap-foto-4.avif"],
  'superstar': ["/productos/adidas-superstar-foto-1.avif", "/productos/adidas-superstar-foto-2.avif", "/productos/adidas-superstar-foto-3.avif", "/productos/adidas-superstar-foto-4.avif"],
  'tech fleece hoodie': ["/productos/nike-tech-fleece-hoodie-foto-1.webp", "/productos/nike-tech-fleece-hoodie-foto-2.webp"],
  'tiro track pants': ["/productos/adidas-tiro-pants-foto-1.webp", "/productos/adidas-tiro-pants-foto-2.webp"],
  'essentials small logo tee': ["/productos/essentials-small-logo-tee-2.webp", "/productos/essentials-small-logo-tee-2.webp"],
  
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
  '/productos/future rider 4.webp',
],

'carina street': [
  '/productos/Carina Street 1.webp',
  '/productos/Carina Street 2.webp',
  '/productos/Carina Street 3.webp',
  '/productos/Carina Street 4.webp',
],



}

/** Imágenes reales incluidas en el proyecto + ilustraciones identificadas para el catálogo demo. */
const fotografias = [
  { patron: /air\s*max\s*270/i, slug: 'nike-air-max-270' },
  { patron: /forum\s*low/i, slug: 'adidas-forum-low' },
  { patron: /rs[\s-]*x/i, slug: 'puma-rs-x' },
]

const ilustraciones = {
  'court vision low': 'nike-court-vision-low',
  'revolution 7': 'nike-revolution-7',
  'air force 1': 'nike-air-force-1',
  'dri-fit training tee': 'nike-dri-fit-tee',
  'club fleece jogger': 'nike-club-fleece-jogger',
  'heritage backpack': 'nike-heritage-backpack',
  'sportswear cap': 'nike-sportswear-cap',
  'grand court base': 'adidas-grand-court-base',
  'runfalcon 3': 'adidas-runfalcon-3',
  'superstar': 'adidas-superstar',
  'entrada 22 jersey': 'adidas-entrada-22',
  'tiro track pants': 'adidas-tiro-pants',
  'classic backpack': 'adidas-classic-backpack',
  'baseball cap': 'adidas-baseball-cap',
  'smash v2': 'puma-smash-v2',
  'carina street': 'puma-carina-street',
  'future rider': 'puma-future-rider',
  'essentials small logo tee': 'puma-essentials-tee',
  'evostripe hoodie': 'puma-evostripe-hoodie',
  'phase backpack': 'puma-phase-backpack',
  'metal cat cap': 'puma-metal-cat-cap',
  'essentials small logo tee': 'puma-essentials-tee',
  'evostripe hoodie': 'puma-evostripe-hoodie',
  'smash v2': 'puma-smash-v2',
  'classic logo tee': 'puma-classic-logo-tee',
  'phase backpack': 'puma-phase-backpack',
  'metal cat cap': 'puma-metal-cat-cap',
  'future rider': 'puma-future-rider',

 }

export function imagenesProducto(producto) {
  const nombre = String(producto?.producto || producto?.nombre || '').trim()
  const marca = String(producto?.marca || '').toLowerCase()
  const foto = fotografias.find(({ patron, slug }) => patron.test(nombre) && (!marca || slug.startsWith(marca)))
  if (foto) {
    return ['principal', 'lateral', 'posterior', 'detalle'].map(v => `/productos/${foto.slug}-${v}.jpg`)
  }
  const key = nombre.toLowerCase()
  const slug = ilustraciones[key]
  const base = slug ? [`/productos/${slug}.svg`, ...[2, 3, 4].map(n => `/productos/${slug}-vista-${n}.svg`)] : []
  // Priorizar imágenes aportadas; conservar las ilustraciones para vistas faltantes.
  const importadas = Object.entries(fotosImportadas).find(([nombreFoto]) => key.includes(nombreFoto))?.[1] || []
  return [...importadas, ...base].slice(0, 4)
}

export function imagenPrincipal(producto) {
  return imagenesProducto(producto)[0] || producto?.imagen || null
}
