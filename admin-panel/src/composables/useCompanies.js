import { ref } from 'vue'
import api from './api'
import { useToast } from 'vue-toastification'

export function useCompanies() {
  const companies = ref([])
  const loading = ref(false)
  const toast = useToast()

  const fetchCompanies = async () => {
    loading.value = true
    try {
      const response = await api.get('/companies/')
      companies.value = response.data
    } catch (error) {
      toast.error('Error al cargar empresas')
      console.error('Error fetching companies:', error)
    } finally {
      loading.value = false
    }
  }

  const createCompany = async (companyData) => {
    loading.value = true
    try {
      const response = await api.post('/companies/', companyData)
      companies.value.push(response.data)
      toast.success('Empresa creada exitosamente')
      return { success: true, data: response.data }
    } catch (error) {
      toast.error('Error al crear empresa')
      return { success: false, error: error.response?.data?.detail || 'Error desconocido' }
    } finally {
      loading.value = false
    }
  }

  const updateCompany = async (id, companyData) => {
    loading.value = true
    try {
      const response = await api.put(`/companies/${id}`, companyData)
      const index = companies.value.findIndex(c => c.id === id)
      if (index !== -1) {
        companies.value[index] = response.data
      }
      toast.success('Empresa actualizada exitosamente')
      return { success: true, data: response.data }
    } catch (error) {
      toast.error('Error al actualizar empresa')
      return { success: false, error: error.response?.data?.detail || 'Error desconocido' }
    } finally {
      loading.value = false
    }
  }

  const deleteCompany = async (id) => {
    loading.value = true
    try {
      await api.delete(`/companies/${id}`)
      companies.value = companies.value.filter(c => c.id !== id)
      toast.success('Empresa eliminada exitosamente')
      return { success: true }
    } catch (error) {
      toast.error('Error al eliminar empresa')
      return { success: false, error: error.response?.data?.detail || 'Error desconocido' }
    } finally {
      loading.value = false
    }
  }

  const getCompany = async (id) => {
    loading.value = true
    try {
      const response = await api.get(`/companies/${id}`)
      return { success: true, data: response.data }
    } catch (error) {
      toast.error('Error al obtener empresa')
      return { success: false, error: error.response?.data?.detail || 'Error desconocido' }
    } finally {
      loading.value = false
    }
  }

  return {
    companies,
    loading,
    fetchCompanies,
    createCompany,
    updateCompany,
    deleteCompany,
    getCompany
  }
}