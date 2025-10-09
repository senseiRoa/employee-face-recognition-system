<template>
  <div class="logs">
    <div class="page-header">
      <h2>Audit & Logs</h2>
      <div class="header-actions">
        <button
          v-if="permissions.canExport.value"
          @click="exportLogs"
          class="btn btn-primary"
        >
          📊 Export
        </button>
      </div>
    </div>

    <!-- Filters -->
    <div class="filters">
      <div class="filter-group">
        <label class="form-label">From</label>
        <input v-model="filters.dateFrom" type="date" class="form-control" />
      </div>
      <div class="filter-group">
        <label class="form-label">To</label>
        <input v-model="filters.dateTo" type="date" class="form-control" />
      </div>
      <div class="filter-group">
        <label class="form-label">Type</label>
        <select v-model="filters.actionType" class="form-control">
          <option value="">All</option>
          <option value="clock_in">Clock-in</option>
          <option value="clock_out">Clock-out</option>
          <option value="login">Login</option>
        </select>
      </div>
      <div class="filter-group">
        <label class="form-label">Employee</label>
        <input
          v-model="filters.employeeName"
          type="text"
          placeholder="Search employee..."
          class="form-control"
        />
      </div>
      <div class="filter-group">
        <label class="form-label">Warehouse</label>
        <select v-model="filters.warehouseId" class="form-control">
          <option value="">All Warehouses</option>
          <option
            v-for="warehouse in availableWarehouses"
            :key="warehouse.id"
            :value="warehouse.id"
          >
            {{ warehouse.name }}
          </option>
        </select>
      </div>
      <div class="filter-group">
        <button
          @click="refreshLogs"
          class="btn btn-outline"
          :disabled="loading"
          title="Refresh logs with current filters"
        >
          🔄 Apply Filters
        </button>
      </div>
    </div>

    <!-- Logs table -->
    <div class="table-container">
      <table class="table">
        <thead>
          <tr>
            <th>Date/Time</th>
            <th>Employee</th>
            <th>Action</th>
            <th>Warehouse</th>
            <th>IP</th>
            <th>Status</th>
            <th>Details</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading">
            <td colspan="7" class="text-center">Loading logs...</td>
          </tr>
          <tr v-else-if="filteredLogs.length === 0">
            <td colspan="7" class="text-center">No logs to display</td>
          </tr>
          <tr v-else v-for="log in filteredLogs" :key="log.id">
            <td>{{ formatDateTime(log.timestamp) }}</td>
            <td>{{ log.employee_name || log.user_name || "-" }}</td>
            <td>
              <span class="action-badge" :class="log.action_type">
                {{ getActionLabel(log.action_type) }}
              </span>
            </td>
            <td>{{ log.warehouse_name || "-" }}</td>
            <td>{{ log.ip_address || "-" }}</td>
            <td>
              <span
                class="status-badge"
                :class="log.success ? 'success' : 'error'"
              >
                {{ log.success ? "Success" : "Error" }}
              </span>
            </td>
            <td>
              <button
                v-if="log.details"
                @click="showLogDetails(log)"
                class="btn btn-outline btn-sm"
              >
                View
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Simple pagination -->
    <div class="pagination">
      <button
        @click="prevPage"
        :disabled="currentPage === 1"
        class="btn btn-outline"
      >
        Previous
      </button>
      <span class="page-info">
        Page {{ currentPage }} of {{ totalPages }}
      </span>
      <button
        @click="nextPage"
        :disabled="currentPage === totalPages"
        class="btn btn-outline"
      >
        Next
      </button>
    </div>

    <!-- Details modal -->
    <div
      v-if="selectedLog"
      class="modal-overlay"
      @click.self="selectedLog = null"
    >
      <div class="modal">
        <div class="modal-header">
          <h3>Log Details</h3>
          <button @click="selectedLog = null" class="btn btn-outline">✕</button>
        </div>
        <div class="modal-body">
          <div class="log-detail">
            <strong>Date/Time:</strong>
            {{ formatDateTime(selectedLog.timestamp) }}
          </div>
          <div class="log-detail">
            <strong>Employee:</strong> {{ selectedLog.employee_name || "-" }}
          </div>
          <div class="log-detail">
            <strong>Action:</strong>
            {{ getActionLabel(selectedLog.action_type) }}
          </div>
          <div class="log-detail">
            <strong>Details:</strong>
            <pre>{{ selectedLog.details || "No additional details" }}</pre>
          </div>
        </div>
        <div class="modal-footer">
          <button @click="selectedLog = null" class="btn btn-primary">
            Close
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from "vue";
import { useViewPermissions } from "@/composables/useViewPermissions";
import { useToast } from "vue-toastification";
import api from "@/composables/api";
import { format } from "date-fns";
import { es } from "date-fns/locale";

export default {
  name: "Logs",
  setup() {
    // Permisos usando el composable reutilizable
    const permissions = useViewPermissions("logs");
    const { showSuccess, showError } = useToast();

    const logs = ref([]);
    const loading = ref(false);
    const selectedLog = ref(null);
    const currentPage = ref(1);
    const pageSize = ref(50);
    const totalLogs = ref(0);
    const availableWarehouses = ref([]);

    const filters = reactive({
      dateFrom: "",
      dateTo: "",
      actionType: "",
      employeeName: "",
      warehouseId: "",
      employeeId: ""
    });

    const loadWarehouses = async () => {
      try {
        const response = await api.get("/warehouses/");
        availableWarehouses.value = response.data;
      } catch (error) {
        console.error("Error loading warehouses:", error);
        availableWarehouses.value = [];
      }
    };

    const filteredLogs = computed(() => {
      let result = logs.value;

      if (filters.actionType) {
        result = result.filter((log) => log.action_type === filters.actionType);
      }

      if (filters.employeeName) {
        const term = filters.employeeName.toLowerCase();
        result = result.filter(
          (log) =>
            (log.employee_name &&
              log.employee_name.toLowerCase().includes(term)) ||
            (log.user_name && log.user_name.toLowerCase().includes(term))
        );
      }

      return result;
    });

    const totalPages = computed(() => {
      return Math.ceil(totalLogs.value / pageSize.value);
    });

    const fetchLogs = async () => {
      loading.value = true;
      try {
        const params = new URLSearchParams({
          skip: currentPage.value,
          limit: pageSize.value
        });
        if (filters.employeeId)
          params.append("employee_id", filters.employeeId);
        if (filters.warehouseId)
          params.append("warehouse_id", filters.warehouseId);
        if (filters.dateFrom) params.append("start_date", filters.dateFrom);
        if (filters.dateTo) params.append("end_date", filters.dateTo);

        const response = await api.get(`/logs/access?${params}`);
        logs.value = response.data.items || response.data;
        totalLogs.value = response.data.total || logs.value.length;
      } catch (error) {
        console.error("Error fetching logs:", error);
        // Datos de ejemplo para desarrollo
        logs.value = [];
      } finally {
        loading.value = false;
      }
    };

    const refreshLogs = () => {
      fetchLogs();
    };

    const exportLogs = async () => {
      try {
        // Construir parámetros de consulta basados en los filtros
        const params = new URLSearchParams();

        if (filters.employeeId)
          params.append("employee_id", filters.employeeId);
        if (filters.warehouseId)
          params.append("warehouse_id", filters.warehouseId);
        if (filters.dateFrom) params.append("start_date", filters.dateFrom);
        if (filters.dateTo) params.append("end_date", filters.dateTo);

        // Configurar límite alto para exportación
        params.append("limit", "1000");
        params.append("skip", "0");

        const url = `/logs/exports${
          params.toString() ? "?" + params.toString() : ""
        }`;

        const response = await api.get(url, { responseType: "blob" });

        // Obtener el nombre del archivo desde el header Content-Disposition o usar uno por defecto
        const contentDisposition = response.headers["content-disposition"];
        let filename = `access_logs_${format(new Date(), "yyyy-MM-dd")}.xlsx`;

        if (contentDisposition) {
          const filenameMatch = contentDisposition.match(
            /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/
          );
          if (filenameMatch && filenameMatch[1]) {
            filename = filenameMatch[1].replace(/['"]/g, "");
          }
        }

        const url_blob = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement("a");
        link.href = url_blob;
        link.setAttribute("download", filename);
        document.body.appendChild(link);
        link.click();
        link.remove();

        // Mostrar mensaje de éxito
        showSuccess(`Exported logs successfully: ${filename}`);
      } catch (error) {
        console.error("Error exporting logs:", error);
        showError("Error exporting logs. Please try again.");
      }
    };

    const showLogDetails = (log) => {
      selectedLog.value = log;
    };

    const prevPage = () => {
      if (currentPage.value > 1) {
        currentPage.value--;
        fetchLogs();
      }
    };

    const nextPage = () => {
      if (currentPage.value < totalPages.value) {
        currentPage.value++;
        fetchLogs();
      }
    };

    const formatDateTime = (dateString) => {
      return format(new Date(dateString), "dd/MM/yyyy HH:mm:ss", {
        locale: es
      });
    };

    const getActionLabel = (actionType) => {
      const labels = {
        clock_in: "Clock-in",
        clock_out: "Clock-out",
        login: "Login",
        logout: "Logout",
        error: "Error"
      };
      return labels[actionType] || actionType;
    };

    onMounted(() => {
      loadWarehouses();
      fetchLogs();
    });

    return {
      logs,
      loading,
      selectedLog,
      currentPage,
      totalPages,
      filters,
      filteredLogs,
      availableWarehouses,
      refreshLogs,
      exportLogs,
      showLogDetails,
      prevPage,
      nextPage,
      formatDateTime,
      getActionLabel,
      // Permisos
      permissions
    };
  }
};
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

.action-badge.clock_in {
  background: rgba(16, 185, 129, 0.1);
  color: var(--success-color);
}

.action-badge.clock_out {
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
