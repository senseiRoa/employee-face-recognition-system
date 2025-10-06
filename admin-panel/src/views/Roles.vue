<template>
  <div class="roles">
    <div class="page-header">
      <h2>Role Management</h2>
      <button @click="showCreateModal = true" class="btn btn-primary">
        <span>➕</span>
        New Role
      </button>
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
            <th>Scope</th>
            <th>Permissions</th>
            <th>Users Count</th>
            <th>Created At</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading">
            <td colspan="8" class="text-center">Loading...</td>
          </tr>
          <tr v-else-if="filteredRoles.length === 0">
            <td colspan="8" class="text-center">No roles found</td>
          </tr>
          <tr v-else v-for="role in filteredRoles" :key="role.id">
            <td>{{ role.id }}</td>
            <td>{{ role.name }}</td>
            <td>{{ role.description || '-' }}</td>
            <td>
              <span class="scope-badge" :class="role.scope">
                {{ role.scope || 'warehouse' }}
              </span>
            </td>
            <td>
              <div class="permissions-list">
                <span v-for="permission in getPermissionsList(role.permissions)" :key="permission" class="permission-tag">
                  {{ permission }}
                </span>
                <span v-if="!role.permissions || Object.keys(role.permissions).length === 0" class="text-muted">
                  No permissions
                </span>
              </div>
            </td>
            <td>{{ role.users_count || 0 }}</td>
            <td>{{ formatDate(role.created_at) }}</td>
            <td>
              <div class="action-buttons">
                <button @click="editRole(role)" class="btn btn-outline btn-sm" title="Edit">✏️</button>
                <button @click="deleteRoleConfirm(role)" class="btn btn-danger btn-sm" title="Delete" :disabled="role.users_count > 0">🗑️</button>
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
          <h3>{{ editingRole ? 'Edit Role' : 'New Role' }}</h3>
          <button @click="closeModals" class="btn btn-outline">✕</button>
        </div>
        
        <form @submit.prevent="saveRole" class="modal-body">
          <div class="form-group">
            <label class="form-label">Name *</label>
            <input
              v-model="roleForm.name"
              type="text"
              class="form-control"
              :class="{ error: errors.name }"
              required
            />
            <div v-if="errors.name" class="form-error">{{ errors.name }}</div>
          </div>

          <div class="form-group">
            <label class="form-label">Description</label>
            <textarea
              v-model="roleForm.description"
              class="form-control"
              :class="{ error: errors.description }"
              rows="3"
              placeholder="Describe the role's responsibilities..."
            ></textarea>
            <div v-if="errors.description" class="form-error">{{ errors.description }}</div>
          </div>

          <div class="form-group">
            <label class="form-label">Scope</label>
            <select
              v-model="roleForm.scope"
              class="form-control"
              :class="{ error: errors.scope }"
            >
              <option value="global">Global</option>
              <option value="warehouse">Warehouse</option>
              <option value="local">Local</option>
            </select>
            <div v-if="errors.scope" class="form-error">{{ errors.scope }}</div>
          </div>

          <div class="form-group">
            <label class="form-label">Permissions</label>
            <div class="permissions-grid">
              <div v-for="category in permissionCategories" :key="category.key" class="permission-category">
                <h4>{{ category.name }}</h4>
                <label v-for="permission in category.permissions" :key="permission" class="checkbox-label">
                  <input 
                    v-model="roleForm.permissions[category.key]" 
                    :value="permission" 
                    type="checkbox" 
                  />
                  <span>{{ formatPermissionName(permission) }}</span>
                </label>
              </div>
            </div>
          </div>
        </form>
        
        <div class="modal-footer">
          <button @click="closeModals" type="button" class="btn btn-outline">
            Cancel
          </button>
          <button @click="saveRole" type="submit" class="btn btn-primary" :disabled="loading">
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
          <p>Are you sure you want to delete role <strong>{{ roleToDelete?.name }}</strong>?</p>
          <p v-if="roleToDelete?.users_count > 0" class="text-danger">
            This role is assigned to {{ roleToDelete.users_count }} user(s). Please reassign users before deleting.
          </p>
          <p v-else class="text-danger">This action cannot be undone.</p>
        </div>
        <div class="modal-footer">
          <button @click="showDeleteModal = false" class="btn btn-outline">Cancel</button>
          <button 
            @click="confirmDeleteRole" 
            class="btn btn-danger" 
            :disabled="loading || (roleToDelete?.users_count > 0)"
          >
            {{ loading ? 'Deleting...' : 'Delete' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoles } from '@/composables/useRoles'
import { format } from 'date-fns'

export default {
  name: 'Roles',
  setup() {
    const { roles, loading, fetchRoles, createRole, updateRole, deleteRole } = useRoles()
    
    const searchTerm = ref('')
    const showCreateModal = ref(false)
    const showEditModal = ref(false)
    const showDeleteModal = ref(false)
    const editingRole = ref(null)
    const roleToDelete = ref(null)
    const errors = ref({})
    
    const roleForm = reactive({
      name: '',
      description: '',
      scope: 'warehouse',
      permissions: {}
    })

    const permissionCategories = ref([
      {
        key: 'warehouse_access',
        name: 'Warehouse Access',
        permissions: ['read', 'write', 'delete']
      },
      {
        key: 'employee_management',
        name: 'Employee Management',
        permissions: ['read', 'write', 'delete']
      },
      {
        key: 'user_management',
        name: 'User Management',
        permissions: ['read', 'write', 'delete']
      },
      {
        key: 'company_management',
        name: 'Company Management',
        permissions: ['read', 'write', 'delete']
      },
      {
        key: 'reports',
        name: 'Reports & Analytics',
        permissions: ['read', 'export']
      },
      {
        key: 'logs',
        name: 'System Logs',
        permissions: ['read', 'audit']
      }
    ])

    const filteredRoles = computed(() => {
      if (!searchTerm.value) return roles.value
      
      const search = searchTerm.value.toLowerCase()
      return roles.value.filter(role => 
        role.name?.toLowerCase().includes(search) ||
        role.description?.toLowerCase().includes(search)
      )
    })

    const getPermissionsList = (permissions) => {
      if (!permissions || typeof permissions !== 'object') return []
      
      const permList = []
      Object.keys(permissions).forEach(category => {
        if (Array.isArray(permissions[category]) && permissions[category].length > 0) {
          permissions[category].forEach(perm => {
            permList.push(`${category}:${perm}`)
          })
        }
      })
      return permList
    }

    const formatPermissionName = (permission) => {
      return permission.charAt(0).toUpperCase() + permission.slice(1)
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
      Object.assign(roleForm, {
        name: '',
        description: '',
        scope: 'warehouse',
        permissions: {}
      })
      errors.value = {}
    }

    const closeModals = () => {
      showCreateModal.value = false
      showEditModal.value = false
      showDeleteModal.value = false
      editingRole.value = null
      roleToDelete.value = null
      resetForm()
    }

    const editRole = (role) => {
      editingRole.value = role
      Object.assign(roleForm, {
        name: role.name,
        description: role.description || '',
        scope: role.scope || 'warehouse',
        permissions: role.permissions || {}
      })
      showEditModal.value = true
    }

    const validateForm = () => {
      errors.value = {}
      let isValid = true

      if (!roleForm.name.trim()) {
        errors.value.name = 'Role name is required'
        isValid = false
      }

      return isValid
    }

    const saveRole = async () => {
      if (!validateForm()) return

      const roleData = {
        name: roleForm.name,
        description: roleForm.description || null,
        scope: roleForm.scope,
        permissions: roleForm.permissions
      }

      let result
      if (editingRole.value) {
        result = await updateRole(editingRole.value.id, roleData)
      } else {
        result = await createRole(roleData)
      }

      if (result.success) {
        closeModals()
        await fetchRoles()
      } else {
        // Handle API validation errors
        if (result.error && typeof result.error === 'object') {
          errors.value = result.error
        }
      }
    }

    const deleteRoleConfirm = (role) => {
      roleToDelete.value = role
      showDeleteModal.value = true
    }

    const confirmDeleteRole = async () => {
      if (!roleToDelete.value || roleToDelete.value.users_count > 0) return

      const result = await deleteRole(roleToDelete.value.id)
      if (result.success) {
        closeModals()
        await fetchRoles()
      }
    }

    onMounted(() => {
      fetchRoles()
    })

    return {
      roles,
      loading,
      searchTerm,
      showCreateModal,
      showEditModal,
      showDeleteModal,
      editingRole,
      roleToDelete,
      roleForm,
      errors,
      permissionCategories,
      filteredRoles,
      getPermissionsList,
      formatPermissionName,
      formatDate,
      closeModals,
      editRole,
      saveRole,
      deleteRoleConfirm,
      confirmDeleteRole
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

.permissions-list {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.permission-tag {
  background: rgba(59, 130, 246, 0.1);
  color: var(--primary-color);
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 500;
}

.permissions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 8px;
  margin-top: 8px;
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
</style>