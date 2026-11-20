import { defineStore } from 'pinia'
import catalogoService from '@/services/catalogoService'
export const useCatalogoStore = defineStore('catalogo', {
 state: () => ({lista:[],marcas:[],categorias:[],cargando:false,error:''}),
 actions: {
  async cargar(filtros={}) {this.cargando=true;this.error='';try {const {data}=await catalogoService.obtenerOfertas(filtros);this.lista=data.ofertas||[]}catch(e){this.error=e.response?.data?.error||'No se pudo cargar el catálogo';throw e}finally{this.cargando=false}},
  async cargarFiltros() {const [m,c]=await Promise.all([catalogoService.obtenerMarcas(),catalogoService.obtenerCategorias()]);this.marcas=m.data.marcas||[];this.categorias=(c.data.categorias||[]).map(x=>x.categoria)}
 }
})
