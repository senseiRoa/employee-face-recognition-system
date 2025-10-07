<template>
  <div class="warehouses">
    <div class="page-header">
      <h2>Warehouse Management</h2>
      <button 
        v-if="permissions.canCreate.value"
        @click="showCreateModal = true" 
        class="btn btn-primary"
      >
        <span>➕</span>
        New Warehouse
      </button>
    </div>

    <div class="filters">
      <div class="search-box">
        <input
          v-model="searchTerm"
          type="text"
          placeholder="Search warehouses..."
          class="form-control"
        />
      </div>
    </div>

    <div class="table-container">
      <table class="table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Company</th>
            <th>Location</th>
            <th>Status</th>
            <th>Employees</th>
            <th v-if="showActionsColumn">Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading">
            <td :colspan="showActionsColumn ? 7 : 6" class="text-center">Loading...</td>
          </tr>
          <tr v-else-if="filteredWarehouses.length === 0">
            <td :colspan="showActionsColumn ? 7 : 6" class="text-center">No warehouses registered</td>
          </tr>
          <tr v-else v-for="warehouse in filteredWarehouses" :key="warehouse.id">
            <td>{{ warehouse.id }}</td>
            <td>{{ warehouse.name }}</td>
            <td>{{ warehouse.company?.name || '-' }}</td>
            <td>{{ warehouse.location || '-' }}</td>
            <td>
              <span class="status-badge" :class="warehouse.is_active ? 'active' : 'inactive'">
                {{ warehouse.is_active ? 'Active' : 'Inactive' }}
              </span>
            </td>
            <td>{{ warehouse.employees_count || 0 }}</td>
            <td v-if="showActionsColumn">
              <div class="action-buttons">
                <button 
                  v-if="permissions.canUpdate.value"
                  @click="editWarehouse(warehouse)" 
                  class="btn btn-outline btn-sm"
                  title="Edit"
                >
                  ✏️
                </button>
                <button 
                  v-if="permissions.canDelete.value"
                  @click="deleteWarehouseConfirm(warehouse)" 
                  class="btn btn-danger btn-sm"
                  title="Delete"
                >
                  🗑️
                </button>
                <span v-if="!permissions.hasAnyAction.value" class="text-muted text-sm">
                  No actions available
                </span>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Create/Edit Modal -->
    <div v-if="showCreateModal || showEditModal" class="modal-overlay" @click.self="closeModals">
      <div class="modal">
        <div class="modal-header">
          <h3>{{ editingWarehouse ? 'Edit Warehouse' : 'New Warehouse' }}</h3>
          <button @click="closeModals" class="btn btn-outline">✕</button>
        </div>
        
        <form @submit.prevent="saveWarehouse" class="modal-body">
          <div class="form-group">
            <label class="form-label">Company *</label>
            <select
              v-model="warehouseForm.company_id"
              class="form-control"
              :class="{ error: errors.company_id }"
              required
            >
              <option value="">Select Company</option>
              <option v-for="company in companies" :key="company.id" :value="company.id">
                {{ company.name }}
              </option>
            </select>
            <div v-if="errors.company_id" class="form-error">{{ errors.company_id }}</div>
          </div>

          <div class="form-group">
            <label class="form-label">Warehouse Name *</label>
            <input
              v-model="warehouseForm.name"
              type="text"
              class="form-control"
              :class="{ error: errors.name }"
              placeholder="Enter warehouse name"
              required
            />
            <div v-if="errors.name" class="form-error">{{ errors.name }}</div>
          </div>

          <div class="form-group">
            <label class="form-label">Location</label>
            <input
              v-model="warehouseForm.location"
              type="text"
              class="form-control"
              :class="{ error: errors.location }"
              placeholder="Enter warehouse location"
            />
            <div v-if="errors.location" class="form-error">{{ errors.location }}</div>
          </div>

          <div class="form-group">
            <label class="checkbox-label">
              <input
                v-model="warehouseForm.is_active"
                type="checkbox"
                class="form-checkbox"
              />
              <span class="checkbox-text">Active warehouse</span>
            </label>
          </div>

          <div v-if="errors.general" class="alert alert-error">
            {{ errors.general }}
          </div>
        </form>
        
        <div class="modal-footer">
          <button @click="closeModals" type="button" class="btn btn-outline">Cancel</button>
          <button @click="saveWarehouse" class="btn btn-primary" :disabled="loading">
            {{ loading ? 'Saving...' : 'Save' }}
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
          <p>Are you sure you want to delete warehouse <strong>{{ warehouseToDelete?.name }}</strong>?</p>
          <p class="text-danger">This action cannot be undone and may affect associated employees.</p>
          <div v-if="errors.delete" class="alert alert-error">
            {{ errors.delete }}
          </div>
        </div>
        <div class="modal-footer">
          <button @click="showDeleteModal = false" class="btn btn-outline">Cancel</button>
          <button @click="confirmDeleteWarehouse" class="btn btn-danger" :disabled="loading">
            {{ loading ? 'Deleting...' : 'Delete' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import { useWarehouses } from '@/composables/useWarehouses'
import { useCompanies } from '@/composables/useCompanies'
import { useViewPermissions, shouldShowActionsColumn } from '@/composables/useViewPermissions'
import { format } from 'date-fns'

export default {
  name: 'Warehouses',
  setup() {
    const { warehouses, loading, fetchWarehouses, createWarehouse, updateWarehouse, deleteWarehouse } = useWarehouses()
    const { companies, fetchCompanies } = useCompanies()
    
    // Permisos usando el composable reutilizable
    const permissions = useViewPermissions('warehouses')
    const showActionsColumn = computed(() => shouldShowActionsColumn(permissions))
    
    const searchTerm = ref('')
    const selectedCompany = ref('')
    const showCreateModal = ref(false)
    const showEditModal = ref(false)
    const showDeleteModal = ref(false)
    const editingWarehouse = ref(null)
    const warehouseToDelete = ref(null)
    const errors = ref({})

    const warehouseForm = reactive({
      name: '',
      location: '',
      company_id: '',
      is_active: true
    })

    const filteredWarehouses = computed(() => {
      let filtered = warehouses.value

      if (searchTerm.value) {
        const search = searchTerm.value.toLowerCase()
        filtered = filtered.filter(warehouse => 
          warehouse.name?.toLowerCase().includes(search) ||
          warehouse.location?.toLowerCase().includes(search) ||
          warehouse.company?.name?.toLowerCase().includes(search)
        )
      }

      if (selectedCompany.value) {
        filtered = filtered.filter(warehouse => warehouse.company_id === parseInt(selectedCompany.value))
      }

      return filtered
    })

    const formatDate = (dateString) => {
      if (!dateString) return '-'
      try {
        return format(new Date(dateString), 'MMM dd, yyyy')
      } catch {
        return '-'
      }
    }

    const resetForm = () => {
      Object.assign(warehouseForm, {
        name: '',
        location: '',
        company_id: '',
        is_active: true
      })
      errors.value = {}
    }

    const closeModals = () => {
      showCreateModal.value = false
      showEditModal.value = false
      showDeleteModal.value = false
      editingWarehouse.value = null
      warehouseToDelete.value = null
      resetForm()
    }

    const editWarehouse = (warehouse) => {
      editingWarehouse.value = warehouse
      Object.assign(warehouseForm, {
        name: warehouse.name,
        location: warehouse.location || '',
        company_id: warehouse.company_id,
        is_active: warehouse.is_active !== undefined ? warehouse.is_active : true
      })
      showEditModal.value = true
    }

    const validateForm = () => {
      errors.value = {}
      let isValid = true

      if (!warehouseForm.name.trim()) {
        errors.value.name = 'Warehouse name is required'
        isValid = false
      }

      if (!warehouseForm.company_id) {
        errors.value.company_id = 'Company is required'
        isValid = false
      }

      return isValid
    }

    const saveWarehouse = async () => {
      if (!validateForm()) return

      const warehouseData = {
        ...warehouseForm,
        company_id: parseInt(warehouseForm.company_id)
      }

      // Remove empty location
      if (!warehouseData.location) {
        delete warehouseData.location
      }

      let result
      if (editingWarehouse.value) {
        result = await updateWarehouse(editingWarehouse.value.id, warehouseData)
      } else {
        result = await createWarehouse(warehouseData)
      }

      if (result.success) {
        closeModals()
        await fetchWarehouses()
      } else {
        // Handle API validation errors - composable already extracts detail
        if (typeof result.error === 'object') {
          errors.value = result.error
        } else {
          errors.value.general = result.error || 'Error saving warehouse'
        }
      }
    }

    const deleteWarehouseConfirm = (warehouse) => {
      warehouseToDelete.value = warehouse
      errors.value.delete = ''
      showDeleteModal.value = true
    }

    const confirmDeleteWarehouse = async () => {
      if (!warehouseToDelete.value) return

      errors.value.delete = ''
      const result = await deleteWarehouse(warehouseToDelete.value.id)
      if (result.success) {
        closeModals()
        await fetchWarehouses()
      } else {
        // Show error message from API - composable already extracts detail
        errors.value.delete = result.error || 'Error deleting warehouse'
      }
    }

    onMounted(async () => {
      await Promise.all([
        fetchWarehouses(),
        fetchCompanies()
      ])
    })

    return {
      warehouses,
      companies,
      loading,
      searchTerm,
      selectedCompany,
      showCreateModal,
      showEditModal,
      showDeleteModal,
      editingWarehouse,
      warehouseToDelete,
      warehouseForm,
      errors,
      filteredWarehouses,
      formatDate,
      closeModals,
      editWarehouse,
      saveWarehouse,
      deleteWarehouseConfirm,
      confirmDeleteWarehouse,
      // Permisos
      permissions,
      showActionsColumn
    }
  }
}
</script>

<style scoped>
/* Reuse similar styles to Companies */
.warehouses {
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

.filters {
  display: flex;
  gap: 16px;
}

.search-box {
  flex: 1;
  max-width: 400px;
}

.table-container {
  background: var(--card-background);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.action-buttons {
  display: flex;
  gap: 8px;
}

.btn-sm {
  padding: 4px 8px;
  font-size: 12px;
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

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
  cursor: pointer;
}

.form-checkbox {
  width: 16px;
  height: 16px;
  margin: 0;
}

.checkbox-text {
  color: var(--text-primary);
}

.modal {
  max-width: 500px;
  width: 90vw;
}

.modal-body {
  padding: 24px;
  gap: 20px;
}

.form-group {
  margin-bottom: 20px;
}

.form-label {
  display: block;
  margin-bottom: 6px;
  font-weight: 500;
  color: var(--text-primary);
}

.form-control {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  background: var(--input-background);
  color: var(--text-primary);
  font-size: 14px;
  transition: border-color 0.2s ease;
}

.form-control:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(var(--primary-rgb), 0.1);
}

.form-control.error {
  border-color: var(--error-color);
}

.form-error {
  color: var(--error-color);
  font-size: 12px;
  margin-top: 4px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px;
  border-top: 1px solid var(--border-color);
  background: var(--background-secondary);
}

.alert {
  padding: 12px 16px;
  border-radius: 6px;
  margin-top: 12px;
  font-size: 14px;
}

.alert-error {
  background: rgba(239, 68, 68, 0.1);
  color: var(--error-color);
  border: 1px solid rgba(239, 68, 68, 0.2);
}
</style>