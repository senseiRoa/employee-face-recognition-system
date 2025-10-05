import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAppStore = defineStore('app', () => {
  const sidebarOpen = ref(true)
  const loading = ref(false)
  const darkMode = ref(localStorage.getItem('darkMode') === 'true')

  const toggleSidebar = () => {
    sidebarOpen.value = !sidebarOpen.value
  }

  const setLoading = (value) => {
    loading.value = value
  }

  const toggleDarkMode = () => {
    darkMode.value = !darkMode.value
    localStorage.setItem('darkMode', darkMode.value.toString())
    document.documentElement.classList.toggle('dark', darkMode.value)
  }

  return {
    sidebarOpen,
    loading,
    darkMode,
    toggleSidebar,
    setLoading,
    toggleDarkMode
  }
})