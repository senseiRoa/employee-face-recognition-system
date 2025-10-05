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
      toast.error('Error al cargar warehouses')
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
      toast.success('Warehouse creado exitosamente')
      return { success: true, data: response.data }
    } catch (error) {
      toast.error('Error al crear warehouse')
      return { success: false, error: error.response?.data?.detail || 'Error desconocido' }
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
      toast.success('Warehouse actualizado exitosamente')
      return { success: true, data: response.data }
    } catch (error) {
      toast.error('Error al actualizar warehouse')
      return { success: false, error: error.response?.data?.detail || 'Error desconocido' }
    } finally {
      loading.value = false
    }
  }

  const deleteWarehouse = async (id) => {
    loading.value = true
    try {
      await api.delete(`/warehouses/${id}`)
      warehouses.value = warehouses.value.filter(w => w.id !== id)
      toast.success('Warehouse eliminado exitosamente')
      return { success: true }
    } catch (error) {
      toast.error('Error al eliminar warehouse')
      return { success: false, error: error.response?.data?.detail || 'Error desconocido' }
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
      toast.error('Error al obtener warehouse')
      return { success: false, error: error.response?.data?.detail || 'Error desconocido' }
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