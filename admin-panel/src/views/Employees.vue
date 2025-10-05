<template>
  <div class="employees">
    <div class="page-header">
      <h2>Employee Management</h2>
      <button @click="showCreateModal = true" class="btn btn-primary">
        <span>➕</span>
        New Employee
      </button>
    </div>

    <div class="filters">
      <input v-model="searchTerm" type="text" placeholder="Search employees..." class="form-control" />
    </div>

    <div class="table-container">
      <table class="table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Email</th>
            <th>Warehouse</th>
            <th>Photo</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading">
            <td colspan="7" class="text-center">Loading...</td>
          </tr>
          <tr v-else v-for="employee in filteredEmployees" :key="employee.id">
            <td>{{ employee.id }}</td>
            <td>{{ employee.name }}</td>
            <td>{{ employee.email || '-' }}</td>
            <td>{{ employee.warehouse?.name || '-' }}</td>
            <td>
              <div class="photo-preview">
                <img v-if="employee.img_base64" :src="'data:image/jpeg;base64,' + employee.img_base64" alt="Photo" />
                <span v-else>No photo</span>
              </div>
            </td>
            <td>
              <span class="status-badge" :class="employee.is_active ? 'active' : 'inactive'">
                {{ employee.is_active ? 'Active' : 'Inactive' }}
              </span>
            </td>
            <td>
              <div class="action-buttons">
                <button @click="editEmployee(employee)" class="btn btn-outline btn-sm">✏️</button>
                <button @click="deleteEmployee(employee)" class="btn btn-danger btn-sm">🗑️</button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Simplified Modal -->
    <div v-if="showCreateModal" class="modal-overlay" @click.self="showCreateModal = false">
      <div class="modal">
        <div class="modal-header">
          <h3>New Employee</h3>
          <button @click="showCreateModal = false" class="btn btn-outline">✕</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label class="form-label">Name *</label>
            <input v-model="employeeForm.name" type="text" class="form-control" required />
          </div>
          <div class="form-group">
            <label class="form-label">Email</label>
            <input v-model="employeeForm.email" type="email" class="form-control" />
          </div>
          <div class="form-group">
            <label class="form-label">Photo</label>
            <input @change="handlePhotoUpload" type="file" accept="image/*" class="form-control" />
          </div>
        </div>
        <div class="modal-footer">
          <button @click="showCreateModal = false" class="btn btn-outline">Cancel</button>
          <button @click="saveEmployee" class="btn btn-primary">Save</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import { useEmployees } from '@/composables/useEmployees'

export default {
  name: 'Employees',
  setup() {
    const { employees, loading, fetchEmployees, createEmployee, deleteEmployee } = useEmployees()
    
    const searchTerm = ref('')
    const showCreateModal = ref(false)
    const employeeForm = reactive({ name: '', email: '', img_base64: '' })

    const filteredEmployees = computed(() => {
      if (!searchTerm.value) return employees.value
      const term = searchTerm.value.toLowerCase()
      return employees.value.filter(e => 
        e.name.toLowerCase().includes(term) ||
        (e.email && e.email.toLowerCase().includes(term))
      )
    })

    const handlePhotoUpload = (event) => {
      const file = event.target.files[0]
      if (file) {
        const reader = new FileReader()
        reader.onload = (e) => {
          employeeForm.img_base64 = e.target.result.split(',')[1]
        }
        reader.readAsDataURL(file)
      }
    }

    const saveEmployee = async () => {
      await createEmployee(employeeForm)
      showCreateModal.value = false
      Object.assign(employeeForm, { name: '', email: '', img_base64: '' })
    }

    onMounted(() => fetchEmployees())

    return {
      employees,
      loading,
      searchTerm,
      filteredEmployees,
      showCreateModal,
      employeeForm,
      handlePhotoUpload,
      saveEmployee,
      editEmployee: () => {},
      deleteEmployee: (emp) => confirm(`¿Eliminar ${emp.name}?`) && deleteEmployee(emp.id)
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