import { defineStore } from 'pinia'
import comprasService from '@/services/comprasService'
import { imagenPrincipal } from '@/utils/imagenes'
const key='mb-carrito-v2'
function read(){try{const v=JSON.parse(localStorage.getItem(key)||'[]');return Array.isArray(v)?v:[]}catch{return []}}
export const useCarritoStore=defineStore('carrito',{
 state:()=>({items:read(),procesando:false,resultado:[],error:''}),
 getters:{unidades:s=>s.items.reduce((n,p)=>n+p.cantidad,0),subtotal:s=>s.items.reduce((n,p)=>n+Number(p.precio)*p.cantidad,0),total:s=>s.items.reduce((n,p)=>n+Number(p.precio_final)*p.cantidad,0),ahorro(){return this.subtotal-this.total}},
 actions:{
  persistir(){localStorage.setItem(key,JSON.stringify(this.items))},
 
agregar(p, cantidad = 1) {

  const id = Number(p.id_producto)
  const stock = Math.max(0, Number(p.stock) || 0)

  const actual = this.items.find(
    x => x.id_producto === id
  )

  const imagen = imagenPrincipal(p) || p.imagen || null

  const n = Math.min(
    stock,
    10,
    (actual?.cantidad || 0) + Number(cantidad)
  )

  if (!n) return false

  if (actual) {

    actual.cantidad = n

    Object.assign(actual, {
      stock,
      precio: Number(p.precio),
      precio_final: Number(p.precio_final),
      descuento: Number(p.descuento) || 0,
      imagen: imagen || actual.imagen || null,
      categoria: p.categoria || actual.categoria
    })

  } else {

    this.items.push({
      id_producto: id,
      producto: p.producto,
      marca: p.marca,
      categoria: p.categoria,
      precio: Number(p.precio),
      precio_final: Number(p.precio_final),
      descuento: Number(p.descuento) || 0,
      stock,
      cantidad: n,
      imagen
    })

  }

  this.persistir()

  window.dispatchEvent(
    new CustomEvent('mb-toast', {
      detail: 'Producto agregado al carrito'
    })
  )

  return true
},


  cantidad(id,n){const x=this.items.find(p=>p.id_producto===id);if(!x)return;x.cantidad=Math.max(1,Math.min(10,Number(x.stock),Number(n)||1));this.persistir()},
  quitar(id){this.items=this.items.filter(p=>p.id_producto!==id);this.persistir()},
  async finalizar(){this.procesando=true;this.error='';this.resultado=[];try{for(const item of [...this.items]){try{const {data}=await comprasService.procesar(item.id_producto,item.cantidad);this.resultado.push(data);this.quitar(item.id_producto)}catch(e){this.error=`No se completó ${item.producto}: ${e.response?.data?.error||e.message}. Las compras anteriores sí se procesaron.`;break}}return !this.error}finally{this.procesando=false}}
 }
})
