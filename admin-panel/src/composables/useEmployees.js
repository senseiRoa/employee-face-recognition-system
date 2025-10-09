import { ref } from 'vue'
import api from './api'
import { useToast } from 'vue-toastification'
import { useTimezone } from './useTimezone'

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
      // Get record timezone for employee creation
      const { getTimezoneWithFallback } = useTimezone()
      const recordTimezone = getTimezoneWithFallback()
      
      const employeeDataWithTimezone = {
        ...employeeData,
        record_timezone: recordTimezone
      }
      
      const response = await api.post('/employees/', employeeDataWithTimezone)
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
      // Get record timezone for employee update
      const { getTimezoneWithFallback } = useTimezone()
      const recordTimezone = getTimezoneWithFallback()
      
      const employeeDataWithTimezone = {
        ...employeeData,
        record_timezone: recordTimezone
      }
      
      const response = await api.put(`/employees/${id}`, employeeDataWithTimezone)
      const index = employees.value.findIndex(emp => emp.id === id)
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
      employees.value = employees.value.filter(emp => emp.id !== id)
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

  const registerFace = async (employeeId, imageData) => {
    loading.value = true
    try {
      // Get device timezone for face registration
      const { getTimezoneWithFallback } = useTimezone()
      const deviceTimezone = getTimezoneWithFallback()
      
      const requestData = {
        employee_id: employeeId,
        image_data: imageData,
        device_timezone: deviceTimezone
      }
      
      const response = await api.post('/employees/register_face', requestData)
      toast.success('Face registered successfully')
      return { success: true, data: response.data }
    } catch (error) {
      const errorMessage = error.response?.data?.detail || 'Error registering face'
      toast.error(errorMessage)
      return { success: false, error: errorMessage }
    } finally {
      loading.value = false
    }
  }

  const clockInOut = async (imageData) => {
    loading.value = true
    try {
      // Get device timezone for clock in/out
      const { getTimezoneWithFallback } = useTimezone()
      const deviceTimezone = getTimezoneWithFallback()
      
      const requestData = {
        image_data: imageData,
        device_timezone: deviceTimezone
      }
      
      const response = await api.post('/employees/check', requestData)
      toast.success('Clock in/out successful')
      return { success: true, data: response.data }
    } catch (error) {
      const errorMessage = error.response?.data?.detail || 'Error with clock in/out'
      toast.error(errorMessage)
      return { success: false, error: errorMessage }
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
    registerFace,
    clockInOut
  }
}
