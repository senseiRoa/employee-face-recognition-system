<template>
  <div class="warehouses">
    <div class="page-header">
      <h2>Warehouse Management</h2>
      <button @click="showCreateModal = true" class="btn btn-primary">
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
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading">
            <td colspan="7" class="text-center">Loading...</td>
          </tr>
          <tr v-else-if="filteredWarehouses.length === 0">
            <td colspan="7" class="text-center">No warehouses registered</td>
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
            <td>
              <div class="action-buttons">
                <button @click="editWarehouse(warehouse)" class="btn btn-outline btn-sm">✏️</button>
                <button @click="deleteWarehouseConfirm(warehouse)" class="btn btn-danger btn-sm">🗑️</button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Create/Edit Modal (simplified for brevity) -->
    <div v-if="showCreateModal || showEditModal" class="modal-overlay" @click.self="closeModals">
      <div class="modal">
        <div class="modal-header">
          <h3>{{ editingWarehouse ? 'Edit Warehouse' : 'New Warehouse' }}</h3>
          <button @click="closeModals" class="btn btn-outline">✕</button>
        </div>
        
        <form @submit.prevent="saveWarehouse" class="modal-body">
          <div class="form-group">
            <label class="form-label">Name *</label>
            <input v-model="warehouseForm.name" type="text" class="form-control" required />
          </div>
          <div class="form-group">
            <label class="form-label">Location</label>
            <input v-model="warehouseForm.location" type="text" class="form-control" />
          </div>
          <div class="form-group">
            <label class="checkbox-label">
              <input v-model="warehouseForm.is_active" type="checkbox" />
              <span>Active warehouse</span>
            </label>
          </div>
        </form>
        
        <div class="modal-footer">
          <button @click="closeModals" type="button" class="btn btn-outline">Cancel</button>
          <button @click="saveWarehouse" class="btn btn-primary">Save</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import { useWarehouses } from '@/composables/useWarehouses'
import { useCompanies } from '@/composables/useCompanies'
import { format } from 'date-fns'

export default {
  name: 'Warehouses',
  setup() {
    const { warehouses, loading, fetchWarehouses, createWarehouse, updateWarehouse, deleteWarehouse } = useWarehouses()
    const { companies, fetchCompanies } = useCompanies()
    
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
      timezone: 'UTC',
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
        timezone: 'UTC',
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
        timezone: warehouse.timezone || 'UTC',
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
        // Handle API validation errors
        if (result.error && typeof result.error === 'object') {
          errors.value = result.error
        }
      }
    }

    const deleteWarehouseConfirm = (warehouse) => {
      warehouseToDelete.value = warehouse
      showDeleteModal.value = true
    }

    const confirmDeleteWarehouse = async () => {
      if (!warehouseToDelete.value) return

      const result = await deleteWarehouse(warehouseToDelete.value.id)
      if (result.success) {
        closeModals()
        await fetchWarehouses()
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
      confirmDeleteWarehouse
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
</style>