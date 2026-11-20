<script setup>
  import { ref, onMounted, onUnmounted } from 'vue'
  import NavBar from '@/components/layout/NavBar.vue'
  import { useAuthStore } from '@/stores/auth'
  const toast = ref('')
  const auth = useAuthStore()
  let timer
  function notify(e) {
    toast.value = e.detail
    clearTimeout(timer)
    timer = setTimeout(() => (toast.value = ''), 3200)
  }
  function expired() {
    auth.logout()
    notify({ detail: 'Tu sesión expiró. Inicia sesión para continuar.' })
  }
  onMounted(() => {
    window.addEventListener('mb-toast', notify)
    window.addEventListener('mb-session-expired', expired)
  })
  onUnmounted(() => {
    window.removeEventListener('mb-toast', notify)
    window.removeEventListener('mb-session-expired', expired)
    clearTimeout(timer)
  })
</script>
<template>
  <NavBar />
  <main><RouterView /></main>
  <div
    v-if="toast"
    class="toast show position-fixed bottom-0 end-0 m-4 shadow"
    role="status"
    style="z-index: 1090"
  >
    <div class="toast-body d-flex justify-content-between gap-3">
      {{ toast }}<button class="btn-close" aria-label="Cerrar" @click="toast = ''" />
    </div>
  </div>
  <footer class="footer py-5 mt-5">
    <div class="container d-flex justify-content-between flex-wrap gap-2">
      <strong>MB / MULTIBRAND</strong
      ><span>Ofertas de tus marcas favoritas · Compras de demostración</span>
    </div>
  </footer>
</template>
