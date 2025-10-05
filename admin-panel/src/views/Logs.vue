<template>
  <div class="logs">
    <div class="page-header">
      <h2>Auditoría y Logs</h2>
      <div class="header-actions">
        <button @click="refreshLogs" class="btn btn-outline" :disabled="loading">
          🔄 Actualizar
        </button>
        <button @click="exportLogs" class="btn btn-primary">
          📊 Exportar
        </button>
      </div>
    </div>

    <!-- Filtros -->
    <div class="filters">
      <div class="filter-group">
        <label class="form-label">Desde</label>
        <input v-model="filters.dateFrom" type="date" class="form-control" />
      </div>
      <div class="filter-group">
        <label class="form-label">Hasta</label>
        <input v-model="filters.dateTo" type="date" class="form-control" />
      </div>
      <div class="filter-group">
        <label class="form-label">Tipo</label>
        <select v-model="filters.actionType" class="form-control">
          <option value="">Todos</option>
          <option value="check_in">Check-in</option>
          <option value="check_out">Check-out</option>
          <option value="login">Login</option>
        </select>
      </div>
      <div class="filter-group">
        <label class="form-label">Empleado</label>
        <input v-model="filters.employeeName" type="text" placeholder="Buscar empleado..." class="form-control" />
      </div>
    </div>

    <!-- Tabla de logs -->
    <div class="table-container">
      <table class="table">
        <thead>
          <tr>
            <th>Fecha/Hora</th>
            <th>Empleado</th>
            <th>Acción</th>
            <th>Warehouse</th>
            <th>IP</th>
            <th>Estado</th>
            <th>Detalles</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading">
            <td colspan="7" class="text-center">Cargando logs...</td>
          </tr>
          <tr v-else-if="filteredLogs.length === 0">
            <td colspan="7" class="text-center">No hay logs para mostrar</td>
          </tr>
          <tr v-else v-for="log in filteredLogs" :key="log.id">
            <td>{{ formatDateTime(log.timestamp) }}</td>
            <td>{{ log.employee_name || log.user_name || '-' }}</td>
            <td>
              <span class="action-badge" :class="log.action_type">
                {{ getActionLabel(log.action_type) }}
              </span>
            </td>
            <td>{{ log.warehouse_name || '-' }}</td>
            <td>{{ log.ip_address || '-' }}</td>
            <td>
              <span class="status-badge" :class="log.success ? 'success' : 'error'">
                {{ log.success ? 'Exitoso' : 'Error' }}
              </span>
            </td>
            <td>
              <button 
                v-if="log.details" 
                @click="showLogDetails(log)" 
                class="btn btn-outline btn-sm"
              >
                Ver
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Paginación simple -->
    <div class="pagination">
      <button 
        @click="prevPage" 
        :disabled="currentPage === 1" 
        class="btn btn-outline"
      >
        Anterior
      </button>
      <span class="page-info">
        Página {{ currentPage }} de {{ totalPages }}
      </span>
      <button 
        @click="nextPage" 
        :disabled="currentPage === totalPages" 
        class="btn btn-outline"
      >
        Siguiente
      </button>
    </div>

    <!-- Modal de detalles -->
    <div v-if="selectedLog" class="modal-overlay" @click.self="selectedLog = null">
      <div class="modal">
        <div class="modal-header">
          <h3>Detalles del Log</h3>
          <button @click="selectedLog = null" class="btn btn-outline">✕</button>
        </div>
        <div class="modal-body">
          <div class="log-detail">
            <strong>Fecha/Hora:</strong> {{ formatDateTime(selectedLog.timestamp) }}
          </div>
          <div class="log-detail">
            <strong>Empleado:</strong> {{ selectedLog.employee_name || '-' }}
          </div>
          <div class="log-detail">
            <strong>Acción:</strong> {{ getActionLabel(selectedLog.action_type) }}
          </div>
          <div class="log-detail">
            <strong>Detalles:</strong>
            <pre>{{ selectedLog.details || 'Sin detalles adicionales' }}</pre>
          </div>
        </div>
        <div class="modal-footer">
          <button @click="selectedLog = null" class="btn btn-primary">Cerrar</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import api from '@/composables/api'
import { format } from 'date-fns'
import { es } from 'date-fns/locale'

export default {
  name: 'Logs',
  setup() {
    const logs = ref([])
    const loading = ref(false)
    const selectedLog = ref(null)
    const currentPage = ref(1)
    const pageSize = ref(20)
    const totalLogs = ref(0)

    const filters = reactive({
      dateFrom: '',
      dateTo: '',
      actionType: '',
      employeeName: ''
    })

    const filteredLogs = computed(() => {
      let result = logs.value

      if (filters.actionType) {
        result = result.filter(log => log.action_type === filters.actionType)
      }

      if (filters.employeeName) {
        const term = filters.employeeName.toLowerCase()
        result = result.filter(log => 
          (log.employee_name && log.employee_name.toLowerCase().includes(term)) ||
          (log.user_name && log.user_name.toLowerCase().includes(term))
        )
      }

      return result
    })

    const totalPages = computed(() => {
      return Math.ceil(totalLogs.value / pageSize.value)
    })

    const fetchLogs = async () => {
      loading.value = true
      try {
        const params = new URLSearchParams({
          page: currentPage.value,
          limit: pageSize.value
        })

        if (filters.dateFrom) params.append('date_from', filters.dateFrom)
        if (filters.dateTo) params.append('date_to', filters.dateTo)

        const response = await api.get(`/logs/?${params}`)
        logs.value = response.data.items || response.data
        totalLogs.value = response.data.total || logs.value.length
      } catch (error) {
        console.error('Error fetching logs:', error)
        // Datos de ejemplo para desarrollo
        logs.value = [
          {
            id: 1,
            timestamp: new Date().toISOString(),
            employee_name: 'Juan Pérez',
            action_type: 'check_in',
            warehouse_name: 'Warehouse Central',
            ip_address: '192.168.1.100',
            success: true,
            details: 'Check-in exitoso mediante reconocimiento facial'
          },
          {
            id: 2,
            timestamp: new Date(Date.now() - 300000).toISOString(),
            employee_name: 'María García',
            action_type: 'check_out',
            warehouse_name: 'Warehouse Norte',
            ip_address: '192.168.1.101',
            success: true,
            details: 'Check-out exitoso'
          }
        ]
      } finally {
        loading.value = false
      }
    }

    const refreshLogs = () => {
      fetchLogs()
    }

    const exportLogs = async () => {
      try {
        const response = await api.get('/logs/export', { responseType: 'blob' })
        const url = window.URL.createObjectURL(new Blob([response.data]))
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', `logs_${format(new Date(), 'yyyy-MM-dd')}.csv`)
        document.body.appendChild(link)
        link.click()
        link.remove()
      } catch (error) {
        console.error('Error exporting logs:', error)
      }
    }

    const showLogDetails = (log) => {
      selectedLog.value = log
    }

    const prevPage = () => {
      if (currentPage.value > 1) {
        currentPage.value--
        fetchLogs()
      }
    }

    const nextPage = () => {
      if (currentPage.value < totalPages.value) {
        currentPage.value++
        fetchLogs()
      }
    }

    const formatDateTime = (dateString) => {
      return format(new Date(dateString), 'dd/MM/yyyy HH:mm:ss', { locale: es })
    }

    const getActionLabel = (actionType) => {
      const labels = {
        check_in: 'Check-in',
        check_out: 'Check-out',
        login: 'Login',
        logout: 'Logout',
        error: 'Error'
      }
      return labels[actionType] || actionType
    }

    onMounted(() => {
      fetchLogs()
    })

    return {
      logs,
      loading,
      selectedLog,
      currentPage,
      totalPages,
      filters,
      filteredLogs,
      refreshLogs,
      exportLogs,
      showLogDetails,
      prevPage,
      nextPage,
      formatDateTime,
      getActionLabel
    }
  }
}
</script>

<style scoped>
.logs {
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

.header-actions {
  display: flex;
  gap: 12px;
}

.filters {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  background: var(--card-background);
  padding: 20px;
  border-radius: 8px;
  border: 1px solid var(--border-color);
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.table-container {
  background: var(--card-background);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.action-badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.action-badge.check_in {
  background: rgba(16, 185, 129, 0.1);
  color: var(--success-color);
}

.action-badge.check_out {
  background: rgba(239, 68, 68, 0.1);
  color: var(--error-color);
}

.action-badge.login {
  background: rgba(59, 130, 246, 0.1);
  color: var(--primary-color);
}

.status-badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge.success {
  background: rgba(16, 185, 129, 0.1);
  color: var(--success-color);
}

.status-badge.error {
  background: rgba(239, 68, 68, 0.1);
  color: var(--error-color);
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
}

.page-info {
  color: var(--text-secondary);
  font-size: 14px;
}

.log-detail {
  margin-bottom: 12px;
}

.log-detail pre {
  background: var(--background-color);
  padding: 8px;
  border-radius: 4px;
  font-size: 12px;
  margin-top: 4px;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.btn-sm {
  padding: 4px 8px;
  font-size: 12px;
}

@media (max-width: 768px) {
  .filters {
    grid-template-columns: 1fr;
  }
  
  .header-actions {
    flex-direction: column;
  }
}
</style>