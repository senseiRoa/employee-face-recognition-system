<template>
  <div class="employees">
    <div class="page-header">
      <h2>Employee Management</h2>
      <button @click="showCreateModal = true" class="btn btn-primary">
        <span>➕</span>
        New Employee
      </button>
    </div>

    <!-- Filters -->
    <div class="filters">
      <div class="search-box">
        <input
          v-model="searchTerm"
          type="text"
          placeholder="Search employees..."
          class="form-control"
        />
      </div>
      <div class="filter-group">
        <select v-model="selectedWarehouse" class="form-control">
          <option value="">All Warehouses</option>
          <option v-for="warehouse in warehouses" :key="warehouse.id" :value="warehouse.id">
            {{ warehouse.name }}
          </option>
        </select>
      </div>
    </div>

    <div class="table-container">
      <table class="table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Email</th>
            <th>Warehouse</th>
            <th>Face Registered</th>
            <th>Created At</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading">
            <td colspan="7" class="text-center">Loading...</td>
          </tr>
          <tr v-else-if="filteredEmployees.length === 0">
            <td colspan="7" class="text-center">No employees found</td>
          </tr>
          <tr v-else v-for="employee in filteredEmployees" :key="employee.id">
            <td>{{ employee.id }}</td>
            <td>{{ getEmployeeFullName(employee) }}</td>
            <td>{{ employee.email || '-' }}</td>
            <td>{{ employee.warehouse?.name || '-' }}</td>
            <td>
              <span class="status-badge" :class="employee.has_face ? 'active' : 'inactive'">
                {{ employee.has_face ? 'Yes' : 'No' }}
              </span>
            </td>
            <td>{{ formatDate(employee.created_at) }}</td>
            <td>
              <div class="action-buttons">
                <button @click="editEmployee(employee)" class="btn btn-outline btn-sm" title="Edit">✏️</button>
                <button @click="registerFace(employee)" class="btn btn-success btn-sm" title="Register Face">📷</button>
                <button @click="deleteEmployeeConfirm(employee)" class="btn btn-danger btn-sm" title="Delete">🗑️</button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Create/Edit Employee Modal -->
    <div v-if="showCreateModal || showEditModal" class="modal-overlay" @click.self="closeModals">
      <div class="modal">
        <div class="modal-header">
          <h3>{{ editingEmployee ? 'Edit Employee' : 'New Employee' }}</h3>
          <button @click="closeModals" class="btn btn-outline">✕</button>
        </div>
        
        <form @submit.prevent="saveEmployee" class="modal-body">
          <div class="form-group">
            <label class="form-label">First Name *</label>
            <input
              v-model="employeeForm.first_name"
              type="text"
              class="form-control"
              :class="{ error: errors.first_name }"
              required
            />
            <div v-if="errors.first_name" class="form-error">{{ errors.first_name }}</div>
          </div>

          <div class="form-group">
            <label class="form-label">Last Name *</label>
            <input
              v-model="employeeForm.last_name"
              type="text"
              class="form-control"
              :class="{ error: errors.last_name }"
              required
            />
            <div v-if="errors.last_name" class="form-error">{{ errors.last_name }}</div>
          </div>

          <div class="form-group">
            <label class="form-label">Email</label>
            <input
              v-model="employeeForm.email"
              type="email"
              class="form-control"
              :class="{ error: errors.email }"
            />
            <div v-if="errors.email" class="form-error">{{ errors.email }}</div>
          </div>

          <div class="form-group">
            <label class="form-label">Warehouse *</label>
            <select
              v-model="employeeForm.warehouse_id"
              class="form-control"
              :class="{ error: errors.warehouse_id }"
              required
            >
              <option value="">Select Warehouse</option>
              <option v-for="warehouse in warehouses" :key="warehouse.id" :value="warehouse.id">
                {{ warehouse.name }}
              </option>
            </select>
            <div v-if="errors.warehouse_id" class="form-error">{{ errors.warehouse_id }}</div>
          </div>
        </form>
        
        <div class="modal-footer">
          <button @click="closeModals" type="button" class="btn btn-outline">
            Cancel
          </button>
          <button @click="saveEmployee" type="submit" class="btn btn-primary" :disabled="loading">
            {{ loading ? 'Saving...' : 'Save' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Face Registration Modal -->
    <div v-if="showFaceModal" class="modal-overlay" @click.self="showFaceModal = false">
      <div class="modal">
        <div class="modal-header">
          <h3>Register Face for {{ faceEmployee?.first_name }} {{ faceEmployee?.last_name }}</h3>
          <button @click="showFaceModal = false" class="btn btn-outline">✕</button>
        </div>
        
        <div class="modal-body">
          <div class="form-group">
            <label class="form-label">Upload Photo *</label>
            <input
              @change="handlePhotoUpload"
              type="file"
              accept="image/*"
              class="form-control"
              :class="{ error: errors.photo }"
              required
            />
            <div v-if="errors.photo" class="form-error">{{ errors.photo }}</div>
            <small class="form-hint">
              Please upload a clear photo with the person's face clearly visible.
            </small>
          </div>

          <div v-if="photoPreview" class="photo-preview-container">
            <img :src="photoPreview" alt="Photo preview" class="photo-preview" />
          </div>
        </div>
        
        <div class="modal-footer">
          <button @click="showFaceModal = false" type="button" class="btn btn-outline">
            Cancel
          </button>
          <button @click="submitFaceRegistration" class="btn btn-primary" :disabled="loading || !photoBase64">
            {{ loading ? 'Registering...' : 'Register Face' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div v-if="showDeleteModal" class="modal-overlay" @click.self="showDeleteModal = false">
      <div class="modal">
        <div class="modal-header">
          <h3>Confirm Delete</h3>
          <button @click="showDeleteModal = false" class="btn btn-outline">✕</button>
        </div>
        <div class="modal-body">
          <p>Are you sure you want to delete employee <strong>{{ employeeToDelete?.first_name }} {{ employeeToDelete?.last_name }}</strong>?</p>
          <p class="text-danger">This action cannot be undone and will remove all associated face recognition data.</p>
        </div>
        <div class="modal-footer">
          <button @click="showDeleteModal = false" class="btn btn-outline">Cancel</button>
          <button @click="confirmDeleteEmployee" class="btn btn-danger" :disabled="loading">
            {{ loading ? 'Deleting...' : 'Delete' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useEmployees } from '@/composables/useEmployees'
import { useWarehouses } from '@/composables/useWarehouses'
import { format } from 'date-fns'
import api from '@/composables/api'

export default {
  name: 'Employees',
  setup() {
    const { employees, loading, fetchEmployees, createEmployee, updateEmployee, deleteEmployee } = useEmployees()
    const { warehouses, fetchWarehouses } = useWarehouses()
    
    const searchTerm = ref('')
    const selectedWarehouse = ref('')
    const showCreateModal = ref(false)
    const showEditModal = ref(false)
    const showFaceModal = ref(false)
    const showDeleteModal = ref(false)
    const editingEmployee = ref(null)
    const faceEmployee = ref(null)
    const employeeToDelete = ref(null)
    const photoPreview = ref('')
    const photoBase64 = ref('')
    const errors = ref({})

    const employeeForm = reactive({
      first_name: '',
      last_name: '',
      email: '',
      warehouse_id: ''
    })

    const filteredEmployees = computed(() => {
      let filtered = employees.value

      if (searchTerm.value) {
        const search = searchTerm.value.toLowerCase()
        filtered = filtered.filter(employee => 
          employee.first_name?.toLowerCase().includes(search) ||
          employee.last_name?.toLowerCase().includes(search) ||
          employee.email?.toLowerCase().includes(search)
        )
      }

      if (selectedWarehouse.value) {
        filtered = filtered.filter(employee => employee.warehouse_id === parseInt(selectedWarehouse.value))
      }

      return filtered
    })

    const getEmployeeFullName = (employee) => {
      return `${employee.first_name} ${employee.last_name}`
    }

    const formatDate = (dateString) => {
      if (!dateString) return '-'
      try {
        return format(new Date(dateString), 'MMM dd, yyyy')
      } catch {
        return '-'
      }
    }

    const resetForm = () => {
      Object.assign(employeeForm, {
        first_name: '',
        last_name: '',
        email: '',
        warehouse_id: ''
      })
      errors.value = {}
    }

    const resetFaceForm = () => {
      photoPreview.value = ''
      photoBase64.value = ''
      errors.value = {}
    }

    const closeModals = () => {
      showCreateModal.value = false
      showEditModal.value = false
      showFaceModal.value = false
      showDeleteModal.value = false
      editingEmployee.value = null
      faceEmployee.value = null
      employeeToDelete.value = null
      resetForm()
      resetFaceForm()
    }

    const editEmployee = (employee) => {
      editingEmployee.value = employee
      Object.assign(employeeForm, {
        first_name: employee.first_name,
        last_name: employee.last_name,
        email: employee.email || '',
        warehouse_id: employee.warehouse_id
      })
      showEditModal.value = true
    }

    const registerFace = (employee) => {
      faceEmployee.value = employee
      resetFaceForm()
      showFaceModal.value = true
    }

    const validateForm = () => {
      errors.value = {}
      let isValid = true

      if (!employeeForm.first_name.trim()) {
        errors.value.first_name = 'First name is required'
        isValid = false
      }

      if (!employeeForm.last_name.trim()) {
        errors.value.last_name = 'Last name is required'
        isValid = false
      }

      if (employeeForm.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(employeeForm.email)) {
        errors.value.email = 'Please enter a valid email address'
        isValid = false
      }

      if (!employeeForm.warehouse_id) {
        errors.value.warehouse_id = 'Warehouse is required'
        isValid = false
      }

      return isValid
    }

    const saveEmployee = async () => {
      if (!validateForm()) return

      const employeeData = {
        ...employeeForm,
        warehouse_id: parseInt(employeeForm.warehouse_id)
      }

      // Remove empty email
      if (!employeeData.email) {
        delete employeeData.email
      }

      let result
      if (editingEmployee.value) {
        result = await updateEmployee(editingEmployee.value.id, employeeData)
      } else {
        result = await createEmployee(employeeData)
      }

      if (result.success) {
        closeModals()
        await fetchEmployees()
      } else {
        // Handle API validation errors
        if (result.error && typeof result.error === 'object') {
          errors.value = result.error
        }
      }
    }

    const handlePhotoUpload = (event) => {
      const file = event.target.files[0]
      if (!file) return

      // Validate file type
      if (!file.type.startsWith('image/')) {
        errors.value.photo = 'Please select a valid image file'
        return
      }

      // Validate file size (max 5MB)
      if (file.size > 5 * 1024 * 1024) {
        errors.value.photo = 'Image file size must be less than 5MB'
        return
      }

      const reader = new FileReader()
      reader.onload = (e) => {
        photoPreview.value = e.target.result
        // Extract base64 without data:image prefix
        photoBase64.value = e.target.result.split(',')[1]
        errors.value.photo = ''
      }
      reader.readAsDataURL(file)
    }

    const submitFaceRegistration = async () => {
      if (!photoBase64.value) {
        errors.value.photo = 'Please select a photo'
        return
      }

      try {
        const faceData = {
          employee_id: faceEmployee.value.id,
          warehouse_id: faceEmployee.value.warehouse_id,
          first_name: faceEmployee.value.first_name,
          last_name: faceEmployee.value.last_name,
          email: faceEmployee.value.email,
          image_base64: photoBase64.value
        }

        const response = await api.post('/employees/register_face', faceData)
        
        if (response.data.status === 'ok') {
          closeModals()
          await fetchEmployees()
        }
      } catch (error) {
        console.error('Error registering face:', error)
        errors.value.photo = error.response?.data?.detail || 'Error registering face'
      }
    }

    const deleteEmployeeConfirm = (employee) => {
      employeeToDelete.value = employee
      showDeleteModal.value = true
    }

    const confirmDeleteEmployee = async () => {
      if (!employeeToDelete.value) return

      const result = await deleteEmployee(employeeToDelete.value.id)
      if (result.success) {
        closeModals()
        await fetchEmployees()
      }
    }

    // Watch for warehouse filter changes
    watch(selectedWarehouse, () => {
      if (selectedWarehouse.value) {
        fetchEmployees(parseInt(selectedWarehouse.value))
      } else {
        fetchEmployees()
      }
    })

    onMounted(async () => {
      await Promise.all([
        fetchEmployees(),
        fetchWarehouses()
      ])
    })

    return {
      employees,
      loading,
      searchTerm,
      selectedWarehouse,
      showCreateModal,
      showEditModal,
      showFaceModal,
      showDeleteModal,
      editingEmployee,
      faceEmployee,
      employeeToDelete,
      employeeForm,
      errors,
      warehouses,
      filteredEmployees,
      photoPreview,
      photoBase64,
      getEmployeeFullName,
      formatDate,
      closeModals,
      editEmployee,
      registerFace,
      saveEmployee,
      handlePhotoUpload,
      submitFaceRegistration,
      deleteEmployeeConfirm,
      confirmDeleteEmployee
    }
  }
}
</script>

<style scoped>
.employees {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-header h2 {
  margin: 0;
  color: var(--text-primary);
  font-size: 24px;
  font-weight: 600;
}

.table-container {
  background: var(--card-background);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.photo-preview {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--background-color);
}

.photo-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.status-badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge.active {
  background: rgba(16, 185, 129, 0.1);
  color: var(--success-color);
}

.status-badge.inactive {
  background: rgba(239, 68, 68, 0.1);
  color: var(--error-color);
}

.action-buttons {
  display: flex;
  gap: 8px;
}

.btn-sm {
  padding: 4px 8px;
  font-size: 12px;
}
</style>