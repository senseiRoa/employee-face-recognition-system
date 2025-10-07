<template>
  <div class="roles">
    <div class="page-header">
      <h2>Roles & Permissions</h2>
      <div class="header-info">
        <p class="info-text">📋 View system roles and their permissions (Read-only)</p>
        <button @click="refreshRoles" class="btn btn-secondary" :disabled="loading">
          <span>🔄</span>
          Refresh
        </button>
      </div>
    </div>

    <!-- Filters -->
    <div class="filters">
      <div class="search-box">
        <input
          v-model="searchTerm"
          type="text"
          placeholder="Search roles..."
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
            <th>Description</th>
            <th>Permissions</th>
            <th>Created At</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading">
            <td colspan="6" class="text-center">Loading...</td>
          </tr>
          <tr v-else-if="filteredRoles.length === 0">
            <td colspan="6" class="text-center">No roles found</td>
          </tr>
          <tr v-else v-for="role in filteredRoles" :key="role.id">
            <td>{{ role.id }}</td>
            <td>
              <div class="role-name">
                <strong>{{ role.name }}</strong>
              </div>
            </td>
            <td>{{ role.description || '-' }}</td>
            <td>
              <div class="permissions-container">
                <div v-if="role.permissions && role.permissions.length > 0" class="permissions-list">
                  <div v-for="permission in role.permissions" :key="permission.permission" class="permission-item">
                    <span class="permission-name">{{ permission.permission }}</span>
                    <div class="permission-actions">
                      <span v-for="action in permission.actions" :key="action" class="action-tag">
                        {{ action }}
                      </span>
                    </div>
                  </div>
                </div>
                <span v-else class="text-muted">No permissions assigned</span>
              </div>
            </td>
            <td>{{ formatDate(role.created_at) }}</td>
            <td>
              <div class="action-buttons">
                <button @click="viewRoleDetails(role)" class="btn btn-outline btn-sm" title="View Details">
                  👁️ View
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Role Details Modal -->
    <div v-if="showDetailsModal" class="modal-overlay" @click.self="closeModals">
      <div class="modal modal-large">
        <div class="modal-header">
          <h3>Role Details: {{ selectedRole?.name }}</h3>
          <button @click="closeModals" class="btn btn-outline">✕</button>
        </div>
        
        <div class="modal-body">
          <div class="role-details">
            <div class="detail-section">
              <h4>Basic Information</h4>
              <div class="detail-grid">
                <div class="detail-item">
                  <label>ID:</label>
                  <span>{{ selectedRole?.id }}</span>
                </div>
                <div class="detail-item">
                  <label>Name:</label>
                  <span>{{ selectedRole?.name }}</span>
                </div>
                <div class="detail-item">
                  <label>Description:</label>
                  <span>{{ selectedRole?.description || 'No description' }}</span>
                </div>
                <div class="detail-item">
                  <label>Created At:</label>
                  <span>{{ formatDate(selectedRole?.created_at) }}</span>
                </div>
              </div>
            </div>

            <div class="detail-section">
              <h4>Permissions & Actions</h4>
              <div v-if="selectedRole?.permissions && selectedRole.permissions.length > 0" class="permissions-detailed">
                <div v-for="permission in selectedRole.permissions" :key="permission.permission" class="permission-card">
                  <div class="permission-header">
                    <h5>{{ permission.permission }}</h5>
                  </div>
                  <div class="permission-body">
                    <div class="actions-grid">
                      <span v-for="action in permission.actions" :key="action" class="action-badge">
                        {{ action }}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
              <div v-else class="no-permissions">
                <p>No permissions assigned to this role</p>
              </div>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button @click="closeModals" class="btn btn-secondary">Close</button>
        </div>
      </div>
    </div>
  </div>
           
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRoles } from '@/composables/useRoles'
import { usePermissions } from '@/composables/usePermissions'
import { useAccessControl } from '@/composables/useAccessControl'
import { format } from 'date-fns'

export default {
  name: 'Roles',
  setup() {
    const { roles, loading, fetchRoles, refreshRoles } = useRoles()
    const permissions = usePermissions()
    const accessControl = useAccessControl()
    
    const searchTerm = ref('')
    const showDetailsModal = ref(false)
    const selectedRole = ref(null)

    // Verificar acceso a la vista
    onMounted(() => {
      if (!accessControl.checkRouteAccess('Roles')) {
        return
      }
      fetchRoles()
    })

    // Roles filtrados
    const filteredRoles = computed(() => {
      if (!searchTerm.value) return roles.value
      
      const search = searchTerm.value.toLowerCase()
      return roles.value.filter(role => 
        role.name.toLowerCase().includes(search) ||
        role.description?.toLowerCase().includes(search)
      )
    })

    // Ver detalles del rol
    const viewRoleDetails = (role) => {
      selectedRole.value = role
      showDetailsModal.value = true
    }

    // Cerrar modales
    const closeModals = () => {
      showDetailsModal.value = false
      selectedRole.value = null
    }

    // Formatear fecha
    const formatDate = (dateString) => {
      if (!dateString) return '-'
      try {
        return format(new Date(dateString), 'MMM dd, yyyy HH:mm')
      } catch (error) {
        return dateString
      }
    }

    return {
      // Estados
      roles,
      loading,
      searchTerm,
      showDetailsModal,
      selectedRole,
      filteredRoles,

      // Funciones
      viewRoleDetails,
      closeModals,
      formatDate,
      refreshRoles,

      // Permisos
      permissions,
      accessControl
    }
    }
    }
  </script>

<style scoped>
.roles {
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
  color: #1e293b;
  font-size: 24px;
  font-weight: 600;
}

.header-info {
  display: flex;
  align-items: center;
  gap: 16px;
}

.info-text {
  color: #64748b;
  font-size: 14px;
  margin: 0;
}

.table-container {
  background: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.role-name strong {
  color: #1e293b;
  font-weight: 600;
}

.permissions-container {
  max-width: 300px;
}

.permissions-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.permission-item {
  background: #f1f5f9;
  border-radius: 8px;
  padding: 8px;
}

.permission-name {
  display: block;
  font-weight: 600;
  color: #334155;
  font-size: 12px;
  margin-bottom: 4px;
  text-transform: capitalize;
}

.permission-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.action-tag {
  background: #2563eb;
  color: white;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 10px;
  font-weight: 500;
  text-transform: capitalize;
}

/* Modal Styles */
.modal-large {
  max-width: 800px;
  width: 90vw;
}

.role-details {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.detail-section h4 {
  margin: 0 0 16px 0;
  color: #1e293b;
  font-size: 18px;
  font-weight: 600;
  border-bottom: 2px solid #e2e8f0;
  padding-bottom: 8px;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 16px;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.detail-item label {
  font-weight: 600;
  color: #64748b;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.detail-item span {
  color: #1e293b;
  font-weight: 500;
}

.permissions-detailed {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 16px;
}

.permission-card {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  overflow: hidden;
}

.permission-header {
  background: #1e293b;
  color: white;
  padding: 12px 16px;
}

.permission-header h5 {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  text-transform: capitalize;
}

.permission-body {
  padding: 12px 16px;
}

.actions-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.action-badge {
  background: #2563eb;
  color: white;
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 11px;
  font-weight: 500;
  text-transform: capitalize;
}

.no-permissions {
  text-align: center;
  padding: 32px;
  color: #64748b;
  font-style: italic;
}

.text-muted {
  color: #64748b;
  font-style: italic;
}

/* Responsive */
@media (max-width: 768px) {
  .header-info {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .permissions-container {
    max-width: none;
  }
  
  .detail-grid {
    grid-template-columns: 1fr;
  }
  
  .permissions-detailed {
    grid-template-columns: 1fr;
  }
  
  .modal-large {
    width: 95vw;
  }
}
.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  cursor: pointer;
}

.action-buttons {
  display: flex;
  gap: 8px;
}

.btn-sm {
  padding: 4px 8px;
  font-size: 12px;
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