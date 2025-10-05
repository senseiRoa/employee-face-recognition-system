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

export default {
  name: 'Warehouses',
  setup() {
    const {
      warehouses,
      loading,
      fetchWarehouses,
      createWarehouse,
      updateWarehouse,
      deleteWarehouse
    } = useWarehouses()

    const searchTerm = ref('')
    const showCreateModal = ref(false)
    const showEditModal = ref(false)
    const editingWarehouse = ref(null)

    const warehouseForm = reactive({
      name: '',
      location: '',
      is_active: true
    })

    const filteredWarehouses = computed(() => {
      if (!searchTerm.value) return warehouses.value
      const term = searchTerm.value.toLowerCase()
      return warehouses.value.filter(w => 
        w.name.toLowerCase().includes(term) ||
        (w.location && w.location.toLowerCase().includes(term))
      )
    })

    const resetForm = () => {
      Object.assign(warehouseForm, {
        name: '',
        location: '',
        is_active: true
      })
    }

    const editWarehouse = (warehouse) => {
      editingWarehouse.value = warehouse
      Object.assign(warehouseForm, {
        name: warehouse.name,
        location: warehouse.location || '',
        is_active: warehouse.is_active
      })
      showEditModal.value = true
    }

    const deleteWarehouseConfirm = async (warehouse) => {
      if (confirm(`¿Eliminar warehouse "${warehouse.name}"?`)) {
        await deleteWarehouse(warehouse.id)
      }
    }

    const saveWarehouse = async () => {
      const data = { ...warehouseForm }
      
      if (editingWarehouse.value) {
        await updateWarehouse(editingWarehouse.value.id, data)
      } else {
        await createWarehouse(data)
      }
      
      closeModals()
    }

    const closeModals = () => {
      showCreateModal.value = false
      showEditModal.value = false
      editingWarehouse.value = null
      resetForm()
    }

    onMounted(() => {
      fetchWarehouses()
    })

    return {
      warehouses,
      loading,
      searchTerm,
      filteredWarehouses,
      showCreateModal,
      showEditModal,
      editingWarehouse,
      warehouseForm,
      editWarehouse,
      deleteWarehouseConfirm,
      saveWarehouse,
      closeModals
    }
  }
}
</script>

<style scoped>
/* Reutilizar estilos similares a Companies */
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