import { defineStore } from 'pinia'
import http from '../http'
import router from '../router'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || '',
    user: null,
  }),
  getters: {
    isAuthenticated: (state) => !!state.token,
  },
  actions: {
    async login(username: string, password: string) {
      try {
        const response = await http.post('/token-auth/', { username, password })
        this.token = response.data.token
        localStorage.setItem('token', this.token)
        router.push('/')
        return true
      } catch (error) {
        console.error('Login failed', error)
        throw error
      }
    },
    logout() {
      this.token = ''
      this.user = null
      localStorage.removeItem('token')
      router.push('/login')
    },
  },
})
