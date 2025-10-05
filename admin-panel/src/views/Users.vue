<template>
  <div class="users">
    <div class="page-header">
      <h2>User Management</h2>
      <button @click="showCreateModal = true" class="btn btn-primary">
        <span>➕</span>
        New User
      </button>
    </div>

    <div class="table-container">
      <table class="table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Username</th>
            <th>Email</th>
            <th>Role</th>
            <th>Status</th>
            <th>Last Login</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading">
            <td colspan="7" class="text-center">Loading...</td>
          </tr>
          <tr v-else v-for="user in users" :key="user.id">
            <td>{{ user.id }}</td>
            <td>{{ user.username }}</td>
            <td>{{ user.email || '-' }}</td>
            <td>{{ user.role?.name || '-' }}</td>
            <td>
              <span class="status-badge" :class="user.is_active ? 'active' : 'inactive'">
                {{ user.is_active ? 'Active' : 'Inactive' }}
              </span>
            </td>
            <td>{{ formatDate(user.last_login) }}</td>
            <td>
              <div class="action-buttons">
                <button class="btn btn-outline btn-sm">✏️</button>
                <button class="btn btn-danger btn-sm">🗑️</button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Basic Modal -->
    <div v-if="showCreateModal" class="modal-overlay" @click.self="showCreateModal = false">
      <div class="modal">
        <div class="modal-header">
          <h3>New User</h3>
          <button @click="showCreateModal = false" class="btn btn-outline">✕</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label class="form-label">Username *</label>
            <input v-model="userForm.username" type="text" class="form-control" required />
          </div>
          <div class="form-group">
            <label class="form-label">Email</label>
            <input v-model="userForm.email" type="email" class="form-control" />
          </div>
          <div class="form-group">
            <label class="form-label">Password *</label>
            <input v-model="userForm.password" type="password" class="form-control" required />
          </div>
        </div>
        <div class="modal-footer">
          <button @click="showCreateModal = false" class="btn btn-outline">Cancel</button>
          <button @click="saveUser" class="btn btn-primary">Save</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import api from '@/composables/api'
import { format } from 'date-fns'
import { es } from 'date-fns/locale'

export default {
  name: 'Users',
  setup() {
    const users = ref([])
    const loading = ref(false)
    const showCreateModal = ref(false)
    const userForm = reactive({ username: '', email: '', password: '' })

    const fetchUsers = async () => {
      loading.value = true
      try {
        const response = await api.get('/users/')
        users.value = response.data
      } catch (error) {
        console.error('Error fetching users:', error)
      } finally {
        loading.value = false
      }
    }

    const saveUser = async () => {
      try {
        await api.post('/users/', userForm)
        await fetchUsers()
        showCreateModal.value = false
        Object.assign(userForm, { username: '', email: '', password: '' })
      } catch (error) {
        console.error('Error creating user:', error)
      }
    }

    const formatDate = (dateString) => {
      if (!dateString) return '-'
      return format(new Date(dateString), 'dd/MM/yyyy HH:mm', { locale: es })
    }

    onMounted(() => fetchUsers())

    return {
      users,
      loading,
      showCreateModal,
      userForm,
      saveUser,
      formatDate
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