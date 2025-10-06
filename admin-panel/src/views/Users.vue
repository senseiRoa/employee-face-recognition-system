<template>
  <div class="users">
    <div class="page-header">
      <h2>User Management</h2>
      <button @click="showCreateModal = true" class="btn btn-primary">
        <span>➕</span>
        New User
      </button>
    </div>

    <!-- Filters -->
    <div class="filters">
      <div class="search-box">
        <input
          v-model="searchTerm"
          type="text"
          placeholder="Search users..."
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
            <th>Username</th>
            <th>Email</th>
            <th>Full Name</th>
            <th>Role</th>
            <th>Warehouse</th>
            <th>Status</th>
            <th>Last Login</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading">
            <td colspan="9" class="text-center">Loading...</td>
          </tr>
          <tr v-else-if="filteredUsers.length === 0">
            <td colspan="9" class="text-center">No users found</td>
          </tr>
          <tr v-else v-for="user in filteredUsers" :key="user.id">
            <td>{{ user.id }}</td>
            <td>{{ user.username }}</td>
            <td>{{ user.email || '-' }}</td>
            <td>{{ getUserFullName(user) }}</td>
            <td>{{ user.role?.name || '-' }}</td>
            <td>{{ user.warehouse?.name || '-' }}</td>
            <td>
              <span class="status-badge" :class="user.is_active ? 'active' : 'inactive'">
                {{ user.is_active ? 'Active' : 'Inactive' }}
              </span>
            </td>
            <td>{{ formatDate(user.last_login) }}</td>
            <td>
              <div class="action-buttons">
                <button @click="editUser(user)" class="btn btn-outline btn-sm" title="Edit">✏️</button>
                <button @click="deleteUserConfirm(user)" class="btn btn-danger btn-sm" title="Delete">🗑️</button>
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
          <h3>{{ editingUser ? 'Edit User' : 'New User' }}</h3>
          <button @click="closeModals" class="btn btn-outline">✕</button>
        </div>
        
        <form @submit.prevent="saveUser" class="modal-body">
          <div class="form-group">
            <label class="form-label">Username *</label>
            <input
              v-model="userForm.username"
              type="text"
              class="form-control"
              :class="{ error: errors.username }"
              required
            />
            <div v-if="errors.username" class="form-error">{{ errors.username }}</div>
          </div>

          <div class="form-group">
            <label class="form-label">Email *</label>
            <input
              v-model="userForm.email"
              type="email"
              class="form-control"
              :class="{ error: errors.email }"
              required
            />
            <div v-if="errors.email" class="form-error">{{ errors.email }}</div>
          </div>

          <div class="form-group">
            <label class="form-label">{{ editingUser ? 'New Password (leave empty to keep current)' : 'Password *' }}</label>
            <input
              v-model="userForm.password"
              type="password"
              class="form-control"
              :class="{ error: errors.password }"
              :required="!editingUser"
            />
            <div v-if="errors.password" class="form-error">{{ errors.password }}</div>
          </div>

          <div class="form-group">
            <label class="form-label">First Name</label>
            <input
              v-model="userForm.first_name"
              type="text"
              class="form-control"
              :class="{ error: errors.first_name }"
            />
            <div v-if="errors.first_name" class="form-error">{{ errors.first_name }}</div>
          </div>

          <div class="form-group">
            <label class="form-label">Last Name</label>
            <input
              v-model="userForm.last_name"
              type="text"
              class="form-control"
              :class="{ error: errors.last_name }"
            />
            <div v-if="errors.last_name" class="form-error">{{ errors.last_name }}</div>
          </div>

          <div class="form-group">
            <label class="form-label">Warehouse *</label>
            <select
              v-model="userForm.warehouse_id"
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

          <div class="form-group">
            <label class="form-label">Role *</label>
            <select
              v-model="userForm.role_id"
              class="form-control"
              :class="{ error: errors.role_id }"
              required
            >
              <option value="">Select Role</option>
              <option v-for="role in roles" :key="role.id" :value="role.id">
                {{ role.name }}
              </option>
            </select>
            <div v-if="errors.role_id" class="form-error">{{ errors.role_id }}</div>
          </div>

          <div class="form-group">
            <label class="checkbox-label">
              <input
                v-model="userForm.is_active"
                type="checkbox"
              />
              <span>Active user</span>
            </label>
          </div>
        </form>
        
        <div class="modal-footer">
          <button @click="closeModals" type="button" class="btn btn-outline">
            Cancel
          </button>
          <button @click="saveUser" type="submit" class="btn btn-primary" :disabled="loading">
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
          <p>Are you sure you want to delete user <strong>{{ userToDelete?.username }}</strong>?</p>
          <p class="text-danger">This action cannot be undone.</p>
        </div>
        <div class="modal-footer">
          <button @click="showDeleteModal = false" class="btn btn-outline">Cancel</button>
          <button @click="confirmDeleteUser" class="btn btn-danger" :disabled="loading">
            {{ loading ? 'Deleting...' : 'Delete' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useUsers } from '@/composables/useUsers'
import { useRoles } from '@/composables/useRoles'
import { useWarehouses } from '@/composables/useWarehouses'
import { format } from 'date-fns'

export default {
  name: 'Users',
  setup() {
    const { users, loading, fetchUsers, createUser, updateUser, deleteUser } = useUsers()
    const { roles, fetchRoles } = useRoles()
    const { warehouses, fetchWarehouses } = useWarehouses()
    
    const searchTerm = ref('')
    const selectedWarehouse = ref('')
    const showCreateModal = ref(false)
    const showEditModal = ref(false)
    const showDeleteModal = ref(false)
    const editingUser = ref(null)
    const userToDelete = ref(null)
    const errors = ref({})

    const userForm = reactive({
      username: '',
      email: '',
      password: '',
      first_name: '',
      last_name: '',
      warehouse_id: '',
      role_id: 3, // Default to employee role
      is_active: true
    })

    const filteredUsers = computed(() => {
      let filtered = users.value

      if (searchTerm.value) {
        const search = searchTerm.value.toLowerCase()
        filtered = filtered.filter(user => 
          user.username?.toLowerCase().includes(search) ||
          user.email?.toLowerCase().includes(search) ||
          user.first_name?.toLowerCase().includes(search) ||
          user.last_name?.toLowerCase().includes(search)
        )
      }

      if (selectedWarehouse.value) {
        filtered = filtered.filter(user => user.warehouse_id === parseInt(selectedWarehouse.value))
      }

      return filtered
    })

    const getUserFullName = (user) => {
      const parts = [user.first_name, user.last_name].filter(Boolean)
      return parts.length > 0 ? parts.join(' ') : '-'
    }

    const formatDate = (dateString) => {
      if (!dateString) return '-'
      try {
        return format(new Date(dateString), 'MMM dd, yyyy HH:mm')
      } catch {
        return '-'
      }
    }

    const resetForm = () => {
      Object.assign(userForm, {
        username: '',
        email: '',
        password: '',
        first_name: '',
        last_name: '',
        warehouse_id: '',
        role_id: 3,
        is_active: true
      })
      errors.value = {}
    }

    const closeModals = () => {
      showCreateModal.value = false
      showEditModal.value = false
      showDeleteModal.value = false
      editingUser.value = null
      userToDelete.value = null
      resetForm()
    }

    const editUser = (user) => {
      editingUser.value = user
      Object.assign(userForm, {
        username: user.username,
        email: user.email,
        password: '', // Don't populate password for security
        first_name: user.first_name || '',
        last_name: user.last_name || '',
        warehouse_id: user.warehouse_id,
        role_id: user.role_id,
        is_active: user.is_active
      })
      showEditModal.value = true
    }

    const validateForm = () => {
      errors.value = {}
      let isValid = true

      if (!userForm.username.trim()) {
        errors.value.username = 'Username is required'
        isValid = false
      }

      if (!userForm.email.trim()) {
        errors.value.email = 'Email is required'
        isValid = false
      } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(userForm.email)) {
        errors.value.email = 'Please enter a valid email address'
        isValid = false
      }

      if (!editingUser.value && !userForm.password.trim()) {
        errors.value.password = 'Password is required'
        isValid = false
      }

      if (!userForm.warehouse_id) {
        errors.value.warehouse_id = 'Warehouse is required'
        isValid = false
      }

      if (!userForm.role_id) {
        errors.value.role_id = 'Role is required'
        isValid = false
      }

      return isValid
    }

    const saveUser = async () => {
      if (!validateForm()) return

      const userData = { ...userForm }
      
      // Remove empty password for updates
      if (editingUser.value && !userData.password) {
        delete userData.password
      }

      // Convert string IDs to numbers
      userData.warehouse_id = parseInt(userData.warehouse_id)
      userData.role_id = parseInt(userData.role_id)

      let result
      if (editingUser.value) {
        result = await updateUser(editingUser.value.id, userData)
      } else {
        result = await createUser(userData)
      }

      if (result.success) {
        closeModals()
        await fetchUsers()
      } else {
        // Handle API validation errors
        if (result.error && typeof result.error === 'object') {
          errors.value = result.error
        }
      }
    }

    const deleteUserConfirm = (user) => {
      userToDelete.value = user
      showDeleteModal.value = true
    }

    const confirmDeleteUser = async () => {
      if (!userToDelete.value) return

      const result = await deleteUser(userToDelete.value.id)
      if (result.success) {
        closeModals()
        await fetchUsers()
      }
    }

    // Watch for warehouse filter changes
    watch(selectedWarehouse, () => {
      if (selectedWarehouse.value) {
        fetchUsers(parseInt(selectedWarehouse.value))
      } else {
        fetchUsers()
      }
    })

    onMounted(async () => {
      await Promise.all([
        fetchUsers(),
        fetchRoles(),
        fetchWarehouses()
      ])
    })

    return {
      users,
      loading,
      searchTerm,
      selectedWarehouse,
      showCreateModal,
      showEditModal,
      showDeleteModal,
      editingUser,
      userToDelete,
      userForm,
      errors,
      warehouses,
      roles,
      filteredUsers,
      getUserFullName,
      formatDate,
      closeModals,
      editUser,
      saveUser,
      deleteUserConfirm,
      confirmDeleteUser
    }
  }
}
</script>

<style scoped>
.users {
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