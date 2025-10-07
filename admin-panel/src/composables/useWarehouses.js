import { ref } from 'vue'
import api from './api'
import { useToast } from 'vue-toastification'

export function useWarehouses() {
  const warehouses = ref([])
  const loading = ref(false)
  const toast = useToast()

  const fetchWarehouses = async (companyId = null) => {
    loading.value = true
    try {
      let url = '/warehouses/'
      if (companyId) {
        url += `?company_id=${companyId}`
      }
      const response = await api.get(url)
      warehouses.value = response.data
    } catch (error) {
      toast.error('Error loading warehouses')
      console.error('Error fetching warehouses:', error)
    } finally {
      loading.value = false
    }
  }

  const createWarehouse = async (warehouseData) => {
    loading.value = true
    try {
      const response = await api.post('/warehouses/', warehouseData)
      warehouses.value.push(response.data)
      toast.success('Warehouse created successfully')
      return { success: true, data: response.data }
    } catch (error) {
      const errorMessage = error.response?.data?.detail || 'Error creating warehouse'
      toast.error(errorMessage)
      return { success: false, error: errorMessage }
    } finally {
      loading.value = false
    }
  }

  const updateWarehouse = async (id, warehouseData) => {
    loading.value = true
    try {
      const response = await api.put(`/warehouses/${id}`, warehouseData)
      const index = warehouses.value.findIndex(w => w.id === id)
      if (index !== -1) {
        warehouses.value[index] = response.data
      }
      toast.success('Warehouse updated successfully')
      return { success: true, data: response.data }
    } catch (error) {
      const errorMessage = error.response?.data?.detail || 'Error updating warehouse'
      toast.error(errorMessage)
      return { success: false, error: errorMessage }
    } finally {
      loading.value = false
    }
  }

  const deleteWarehouse = async (id) => {
    loading.value = true
    try {
      await api.delete(`/warehouses/${id}`)
      warehouses.value = warehouses.value.filter(w => w.id !== id)
      toast.success('Warehouse deleted successfully')
      return { success: true }
    } catch (error) {
      const errorMessage = error.response?.data?.detail || 'Error deleting warehouse'
      toast.error(errorMessage)
      return { success: false, error: errorMessage }
    } finally {
      loading.value = false
    }
  }

  const getWarehouse = async (id) => {
    loading.value = true
    try {
      const response = await api.get(`/warehouses/${id}`)
      return { success: true, data: response.data }
    } catch (error) {
      toast.error('Error getting warehouse')
      return { success: false, error: error.response?.data?.detail || 'Unknown error' }
    } finally {
      loading.value = false
    }
  }

  return {
    warehouses,
    loading,
    fetchWarehouses,
    createWarehouse,
    updateWarehouse,
    deleteWarehouse,
    getWarehouse
  }
}