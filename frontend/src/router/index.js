import { createRouter,createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
const routes=[
 {path:'/',name:'home',component:()=>import('@/views/CatalogoView.vue')},
 {path:'/catalogo',redirect:'/'},
 {path:'/producto/:id',name:'producto',component:()=>import('@/views/ProductoDetalleView.vue')},
 {path:'/carrito',name:'carrito',component:()=>import('@/views/CarritoView.vue')},
 {path:'/login',name:'login',component:()=>import('@/views/LoginView.vue')},
 {path:'/register',name:'register',component:()=>import('@/views/RegisterView.vue')},
 {path:'/checkout',name:'checkout',component:()=>import('@/views/CheckoutView.vue'),meta:{requiereAuth:true}},
 {path:'/perfil',name:'perfil',component:()=>import('@/views/PerfilView.vue'),meta:{requiereAuth:true}},
 {path:'/:pathMatch(.*)*',redirect:'/'}]
const router=createRouter({history:createWebHistory(import.meta.env.BASE_URL),routes,scrollBehavior(to,from,saved){if(saved)return saved;if(to.hash)return {el:to.hash,behavior:"smooth"};return {top:0,left:0}}})
router.beforeEach(to=>{if(to.meta.requiereAuth&&!useAuthStore().estaAutenticado)return {name:'login',query:{redirect:to.fullPath}}})
export default router
