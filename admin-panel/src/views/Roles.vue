<template>
  <div class="roles">
    <div class="page-header">
      <h2>Gestión de Roles</h2>
      <button @click="showCreateModal = true" class="btn btn-primary">
        <span>➕</span>
        Nuevo Rol
      </button>
    </div>

    <div class="table-container">
      <table class="table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Nombre</th>
            <th>Descripción</th>
            <th>Permisos</th>
            <th>Usuarios</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading">
            <td colspan="6" class="text-center">Cargando...</td>
          </tr>
          <tr v-else v-for="role in roles" :key="role.id">
            <td>{{ role.id }}</td>
            <td>{{ role.name }}</td>
            <td>{{ role.description || '-' }}</td>
            <td>
              <div class="permissions-list">
                <span v-for="permission in role.permissions" :key="permission" class="permission-tag">
                  {{ permission }}
                </span>
              </div>
            </td>
            <td>{{ role.users_count || 0 }}</td>
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

    <!-- Modal -->
    <div v-if="showCreateModal" class="modal-overlay" @click.self="showCreateModal = false">
      <div class="modal">
        <div class="modal-header">
          <h3>Nuevo Rol</h3>
          <button @click="showCreateModal = false" class="btn btn-outline">✕</button>
        </div>
        <div class="modal-body">
          <div class="form-group">
            <label class="form-label">Nombre *</label>
            <input v-model="roleForm.name" type="text" class="form-control" required />
          </div>
          <div class="form-group">
            <label class="form-label">Descripción</label>
            <textarea v-model="roleForm.description" class="form-control" rows="3"></textarea>
          </div>
          <div class="form-group">
            <label class="form-label">Permisos</label>
            <div class="permissions-grid">
              <label v-for="permission in availablePermissions" :key="permission" class="checkbox-label">
                <input 
                  v-model="roleForm.permissions" 
                  :value="permission" 
                  type="checkbox" 
                />
                <span>{{ permission }}</span>
              </label>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button @click="showCreateModal = false" class="btn btn-outline">Cancelar</button>
          <button @click="saveRole" class="btn btn-primary">Guardar</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import api from '@/composables/api'

export default {
  name: 'Roles',
  setup() {
    const roles = ref([])
    const loading = ref(false)
    const showCreateModal = ref(false)
    
    const roleForm = reactive({
      name: '',
      description: '',
      permissions: []
    })

    const availablePermissions = ref([
      'admin',
      'manager',
      'employee_read',
      'employee_write',
      'company_read',
      'company_write',
      'warehouse_read',
      'warehouse_write',
      'logs_read',
      'reports_read'
    ])

    const fetchRoles = async () => {
      loading.value = true
      try {
        const response = await api.get('/roles/')
        roles.value = response.data
      } catch (error) {
        console.error('Error fetching roles:', error)
      } finally {
        loading.value = false
      }
    }

    const saveRole = async () => {
      try {
        await api.post('/roles/', roleForm)
        await fetchRoles()
        showCreateModal.value = false
        Object.assign(roleForm, { name: '', description: '', permissions: [] })
      } catch (error) {
        console.error('Error creating role:', error)
      }
    }

    onMounted(() => fetchRoles())

    return {
      roles,
      loading,
      showCreateModal,
      roleForm,
      availablePermissions,
      saveRole
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