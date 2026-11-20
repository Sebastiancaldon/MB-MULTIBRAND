import {defineStore} from 'pinia'
import {useAuthStore} from './auth'
import comprasService from '@/services/comprasService'
const KEY='mb_favoritos_local'
function initial(){try{return JSON.parse(localStorage.getItem(KEY)||'[]')}catch{return []}}
export const useFavoritosStore=defineStore('favoritos',{
 state:()=>({items:initial(),busy:false,error:''}),
 getters:{contiene:s=>id=>s.items.some(x=>Number(x.id_producto)===Number(id)),total:s=>s.items.length},
 actions:{
  async sincronizar(){if(!useAuthStore().estaAutenticado)return;try{const {data}=await comprasService.favoritos();const remote=data.favoritos||[];for(const item of this.items){if(!remote.some(x=>Number(x.id_producto)===Number(item.id_producto))){await comprasService.agregarFavorito(item.id_producto)}}const {data:updated}=await comprasService.favoritos();this.items=updated.favoritos||[];localStorage.setItem(KEY,JSON.stringify(this.items))}catch(e){this.error=e.response?.data?.error||'No fue posible sincronizar favoritos'}},
  async alternar(producto){if(this.busy)return;this.busy=true;this.error='';const id=Number(producto.id_producto);const exists=this.contiene(id);const prev=[...this.items];this.items=exists?this.items.filter(x=>Number(x.id_producto)!==id):[...this.items,producto];localStorage.setItem(KEY,JSON.stringify(this.items));try{if(useAuthStore().estaAutenticado){if(exists)await comprasService.quitarFavorito(id);else await comprasService.agregarFavorito(id)}window.dispatchEvent(new CustomEvent('mb-toast',{detail:exists?'Eliminado de favoritos':'Agregado a favoritos ♡'}))}catch(e){this.items=prev;localStorage.setItem(KEY,JSON.stringify(prev));this.error=e.response?.data?.error||'No se pudo guardar el favorito'}finally{this.busy=false}}
 }
})
