import { ref } from 'vue'
import api from './api'
import { useToast } from 'vue-toastification'
import { useTimezone } from './useTimezone'

export function useUsers() {
  const users = ref([])
  const loading = ref(false)
  const toast = useToast()

  const fetchUsers = async (warehouseId = null) => {
    loading.value = true
    try {
      let url = '/users/'
      if (warehouseId) {
        url += `?warehouse_id=${warehouseId}`
      }
      const response = await api.get(url)
      users.value = response.data
    } catch (error) {
      toast.error('Error loading users')
      console.error('Error fetching users:', error)
    } finally {
      loading.value = false
    }
  }

  const createUser = async (userData) => {
    loading.value = true
    try {
      // Get record timezone for user creation
      const { getTimezoneWithFallback } = useTimezone()
      const recordTimezone = getTimezoneWithFallback()
      
      const userDataWithTimezone = {
        ...userData,
        record_timezone: recordTimezone  // NEW: Include record timezone
      }
      
      const response = await api.post('/users/', userDataWithTimezone)
      // Refresh the full user list to get complete relationship data
      await fetchUsers()
      toast.success('User created successfully')
      return { success: true, data: response.data }
    } catch (error) {
      const errorMessage = error.response?.data?.detail || 'Error creating user'
      toast.error(errorMessage)
      return { success: false, error: errorMessage }
    } finally {
      loading.value = false
    }
  }

  const updateUser = async (id, userData) => {
    loading.value = true
    try {
      const response = await api.put(`/users/${id}`, userData)
      // Refresh the full user list to get complete relationship data
      await fetchUsers()
      toast.success('User updated successfully')
      return { success: true, data: response.data }
    } catch (error) {
      const errorMessage = error.response?.data?.detail || 'Error updating user'
      toast.error(errorMessage)
      return { success: false, error: errorMessage }
    } finally {
      loading.value = false
    }
  }

  const deleteUser = async (id) => {
    loading.value = true
    try {
      await api.delete(`/users/${id}`)
      users.value = users.value.filter(u => u.id !== id)
      toast.success('User deleted successfully')
      return { success: true }
    } catch (error) {
      const errorMessage = error.response?.data?.detail || 'Error deleting user'
      toast.error(errorMessage)
      return { success: false, error: errorMessage }
    } finally {
      loading.value = false
    }
  }

  const getUser = async (id) => {
    loading.value = true
    try {
      const response = await api.get(`/users/${id}`)
      return { success: true, data: response.data }
    } catch (error) {
      toast.error('Error getting user')
      return { success: false, error: error.response?.data?.detail || 'Unknown error' }
    } finally {
      loading.value = false
    }
  }

  const getCurrentUser = async () => {
    loading.value = true
    try {
      const response = await api.get('/users/me')
      return { success: true, data: response.data }
    } catch (error) {
      toast.error('Error getting current user')
      return { success: false, error: error.response?.data?.detail || 'Unknown error' }
    } finally {
      loading.value = false
    }
  }

  return {
    users,
    loading,
    fetchUsers,
    createUser,
    updateUser,
    deleteUser,
    getUser,
    getCurrentUser
  }
}