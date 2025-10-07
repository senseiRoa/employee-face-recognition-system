import { ref } from 'vue'
import api from './api'
import { useToast } from 'vue-toastification'

export function useEmployees() {
  const employees = ref([])
  const loading = ref(false)
  const toast = useToast()

  const fetchEmployees = async (warehouseId = null) => {
    loading.value = true
    try {
      let url = '/employees/'
      if (warehouseId) {
        url += `?warehouse_id=${warehouseId}`
      }
      const response = await api.get(url)
      employees.value = response.data
    } catch (error) {
      toast.error('Error loading employees')
      console.error('Error fetching employees:', error)
    } finally {
      loading.value = false
    }
  }

  const createEmployee = async (employeeData) => {
    loading.value = true
    try {
      const response = await api.post('/employees/', employeeData)
      employees.value.push(response.data)
      toast.success('Employee created successfully')
      return { success: true, data: response.data }
    } catch (error) {
      const errorMessage = error.response?.data?.detail || 'Error creating employee'
      toast.error(errorMessage)
      return { success: false, error: errorMessage }
    } finally {
      loading.value = false
    }
  }

  const updateEmployee = async (id, employeeData) => {
    loading.value = true
    try {
      const response = await api.put(`/employees/${id}`, employeeData)
      const index = employees.value.findIndex(e => e.id === id)
      if (index !== -1) {
        employees.value[index] = response.data
      }
      toast.success('Employee updated successfully')
      return { success: true, data: response.data }
    } catch (error) {
      const errorMessage = error.response?.data?.detail || 'Error updating employee'
      toast.error(errorMessage)
      return { success: false, error: errorMessage }
    } finally {
      loading.value = false
    }
  }

  const deleteEmployee = async (id) => {
    loading.value = true
    try {
      await api.delete(`/employees/${id}`)
      employees.value = employees.value.filter(e => e.id !== id)
      toast.success('Employee deleted successfully')
      return { success: true }
    } catch (error) {
      const errorMessage = error.response?.data?.detail || 'Error deleting employee'
      toast.error(errorMessage)
      return { success: false, error: errorMessage }
    } finally {
      loading.value = false
    }
  }

  const getEmployee = async (id) => {
    loading.value = true
    try {
      const response = await api.get(`/employees/${id}`)
      return { success: true, data: response.data }
    } catch (error) {
      toast.error('Error getting employee')
      return { success: false, error: error.response?.data?.detail || 'Unknown error' }
    } finally {
      loading.value = false
    }
  }

  const uploadEmployeePhoto = async (id, photoFile) => {
    loading.value = true
    try {
      const formData = new FormData()
      formData.append('file', photoFile)
      
      const response = await api.post(`/employees/${id}/upload-photo`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })
      
      toast.success('Foto de empleado cargada exitosamente')
      return { success: true, data: response.data }
    } catch (error) {
      toast.error('Error al cargar foto de empleado')
      return { success: false, error: error.response?.data?.detail || 'Error desconocido' }
    } finally {
      loading.value = false
    }
  }

  return {
    employees,
    loading,
    fetchEmployees,
    createEmployee,
    updateEmployee,
    deleteEmployee,
    getEmployee,
    uploadEmployeePhoto
  }
}