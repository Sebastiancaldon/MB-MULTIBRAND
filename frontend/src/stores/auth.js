import { defineStore } from 'pinia'
import authService from '@/services/authService'
export const useAuthStore = defineStore('auth', {
 state: () => ({token:localStorage.getItem('token'),username:localStorage.getItem('username')}),
 getters: {estaAutenticado: s => !!s.token},
 actions: {
  async login(username,password) {const {data}=await authService.login(username,password);this.token=data.token;this.username=username;localStorage.setItem('token',data.token);localStorage.setItem('username',username)},
  logout() {this.token=null;this.username=null;localStorage.removeItem('token');localStorage.removeItem('username')}
 }
})
