<template>
  <div class="reports">
    <div class="page-header">
      <h2>Reports & Statistics</h2>
    </div>

    <!-- Report Filters -->
    <div class="report-filters">
      <div class="filter-group">
        <label class="form-label">Report Type</label>
        <select v-model="reportConfig.type" class="form-control">
          <option value="attendance">Attendance</option>
          <option value="employees">Employees</option>
          <option value="warehouses">Warehouses</option>
          <option value="activity">Activity</option>
        </select>
      </div>
      <div class="filter-group">
        <label class="form-label">Start Date</label>
        <input
          v-model="reportConfig.dateFrom"
          type="date"
          class="form-control"
          lang="en"
        />
      </div>
      <div class="filter-group">
        <label class="form-label">End Date</label>
        <input
          v-model="reportConfig.dateTo"
          type="date"
          class="form-control"
          lang="en"
        />
      </div>
      <div class="filter-group">
        <label class="form-label">Format</label>
        <select v-model="reportConfig.format" class="form-control">
          <option value="pdf">PDF</option>
          <option value="csv">CSV</option>
          <option value="excel">Excel</option>
        </select>
      </div>
      <div class="filter-group">
        <label class="form-label">Actions</label>
        <button
          v-if="permissions.canView.value"
          @click="generateReport"
          class="btn btn-primary"
          :disabled="loading"
        >
          📊 Generate Report
        </button>
      </div>
    </div>

    <!-- Quick Stats -->
    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon">👥</div>
        <div class="stat-content">
          <h3>{{ stats.totalEmployees }}</h3>
          <p>Total Employees</p>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon">📍</div>
        <div class="stat-content">
          <h3>{{ stats.totalCheckIns }}</h3>
          <p>Check-ins Today</p>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon">🏭</div>
        <div class="stat-content">
          <h3>{{ stats.activeWarehouses }}</h3>
          <p>Active Warehouses</p>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon">⏰</div>
        <div class="stat-content">
          <h3>{{ stats.avgWorkingHours }}</h3>
          <p>Average Hours/Day</p>
        </div>
      </div>
    </div>

    <!-- Attendance Chart Filters -->
    <div class="chart-filters">
      <h3>Attendance Analysis</h3>
      <div class="filter-row">
        <div class="filter-group">
          <label class="form-label">Time Period</label>
          <select
            v-model="attendanceFilters.groupBy"
            @change="updateAttendanceChart"
            class="form-control"
          >
            <option value="day">Daily</option>
            <option value="week">Weekly</option>
            <option value="month">Monthly</option>
          </select>
        </div>
        <div class="filter-group">
          <label class="form-label">Days to Show</label>
          <select
            v-model="attendanceFilters.days"
            @change="updateAttendanceChart"
            class="form-control"
          >
            <option value="7">Last 7 days</option>
            <option value="14">Last 14 days</option>
            <option value="30">Last 30 days</option>
            <option value="60">Last 60 days</option>
            <option value="90">Last 90 days</option>
          </select>
        </div>
        <div class="filter-group">
          <label class="form-label">Warehouse</label>
          <select
            v-model="attendanceFilters.warehouseId"
            @change="updateAttendanceChart"
            class="form-control"
          >
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
      </div>
    </div>

    <!-- Charts -->
    <div class="charts-section">
      <div class="chart-container">
        <h3>
          Attendance by
          {{
            attendanceFilters.groupBy === "day"
              ? "Day"
              : attendanceFilters.groupBy === "week"
              ? "Week"
              : "Month"
          }}
        </h3>
        <canvas ref="attendanceChart"></canvas>
        
        <!-- Attendance Summary Information -->
        <div v-if="attendanceSummary.total_checkins > 0 || attendanceSummary.total_checkouts > 0" class="chart-summary">
          <h4>Attendance Analysis Summary</h4>
          <div class="summary-grid">
            <div class="summary-item">
              <span class="summary-label">Total Check-ins:</span>
              <span class="summary-value">{{ attendanceSummary.total_checkins }}</span>
            </div>
            <div class="summary-item">
              <span class="summary-label">Total Check-outs:</span>
              <span class="summary-value">{{ attendanceSummary.total_checkouts }}</span>
            </div>
            <div class="summary-item">
              <span class="summary-label">Avg {{ getPeriodLabel() }} Check-ins:</span>
              <span class="summary-value">{{ getAvgCheckins() }}</span>
            </div>
            <div class="summary-item">
              <span class="summary-label">Avg {{ getPeriodLabel() }} Check-outs:</span>
              <span class="summary-value">{{ getAvgCheckouts() }}</span>
            </div>
            <div class="summary-item">
              <span class="summary-label">Analysis Period:</span>
              <span class="summary-value">{{ attendanceSummary.period }}</span>
            </div>
            <div class="summary-item">
              <span class="summary-label">Balance:</span>
              <span class="summary-value" :class="{
                'highlight': attendanceSummary.total_checkins === attendanceSummary.total_checkouts,
                'text-warning': attendanceSummary.total_checkins > attendanceSummary.total_checkouts,
                'text-danger': attendanceSummary.total_checkins < attendanceSummary.total_checkouts
              }">
                {{ attendanceSummary.total_checkins === attendanceSummary.total_checkouts ? 'Balanced' :
                   attendanceSummary.total_checkins > attendanceSummary.total_checkouts ? 'More Check-ins' : 'More Check-outs' }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <div class="chart-container">
        <h3>Employees per Warehouse</h3>
        <canvas ref="warehouseChart"></canvas>

        <!-- Warehouse Summary Information -->
        <div v-if="warehouseSummary.total_warehouses > 0" class="chart-summary">
          <h4>Warehouse Analysis Summary</h4>
          <div class="summary-grid">
            <div class="summary-item">
              <span class="summary-label">Total Warehouses:</span>
              <span class="summary-value">{{
                warehouseSummary.total_warehouses
              }}</span>
            </div>
            <div class="summary-item">
              <span class="summary-label">Total Employees:</span>
              <span class="summary-value">{{
                warehouseSummary.total_employees
              }}</span>
            </div>
            <div class="summary-item">
              <span class="summary-label">Avg per Warehouse:</span>
              <span class="summary-value"
                >{{
                  warehouseSummary.avg_employees_per_warehouse
                }}
                employees</span
              >
            </div>
            <div class="summary-item">
              <span class="summary-label">Access Logs (Period):</span>
              <span class="summary-value">{{
                warehouseSummary.total_access_logs_period
              }}</span>
            </div>
            <div class="summary-item">
              <span class="summary-label">Analysis Period:</span>
              <span class="summary-value">{{ warehouseSummary.period }}</span>
            </div>
            <div class="summary-item">
              <span class="summary-label">Most Active:</span>
              <span class="summary-value highlight">{{
                warehouseSummary.most_active_warehouse
              }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Recent Reports Table -->
    <div class="recent-reports">
      <h3>Recent Reports</h3>
      <div class="reports-list">
        <div
          v-for="report in recentReports"
          :key="report.id"
          class="report-item"
        >
          <div class="report-info">
            <h4>{{ report.name }}</h4>
            <p>{{ report.description }}</p>
            <span class="report-date">{{ formatDate(report.created_at) }}</span>
          </div>
          <div class="report-actions">
            <button
              @click="downloadReport(report)"
              class="btn btn-outline btn-sm"
            >
              📥 Download
            </button>
            <button @click="viewReport(report)" class="btn btn-primary btn-sm">
              👁️ View
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Report Preview Modal -->
    <div
      v-if="previewReport"
      class="modal-overlay"
      @click.self="previewReport = null"
    >
      <div class="modal modal-lg">
        <div class="modal-header">
          <h3>Preview: {{ previewReport.name }}</h3>
          <button @click="previewReport = null" class="btn btn-outline">
            ✕
          </button>
        </div>
        <div class="modal-body">
          <div class="report-preview">
            <iframe
              v-if="previewReport.url"
              :src="previewReport.url"
              width="100%"
              height="500"
            ></iframe>
            <div v-else class="no-preview">
              <p>Preview not available for this file type.</p>
              <button
                @click="downloadReport(previewReport)"
                class="btn btn-primary"
              >
                Download File
              </button>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button
            @click="downloadReport(previewReport)"
            class="btn btn-primary"
          >
            Download
          </button>
          <button @click="previewReport = null" class="btn btn-outline">
            Close
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted, nextTick } from "vue";
import { Chart, registerables } from "chart.js";
import { useViewPermissions } from "@/composables/useViewPermissions";
import api from "@/composables/api";
import { format } from "date-fns";
import { useToast } from "vue-toastification";

Chart.register(...registerables);

export default {
  name: "Reports",
  setup() {
    // Permisos usando el composable reutilizable
    const permissions = useViewPermissions("reports");
    const toast = useToast();

    const loading = ref(false);
    const attendanceChart = ref(null);
    const warehouseChart = ref(null);
    const previewReport = ref(null);

    const reportConfig = reactive({
      type: "attendance",
      dateFrom: format(
        new Date(Date.now() - 30 * 24 * 60 * 60 * 1000),
        "yyyy-MM-dd"
      ),
      dateTo: format(new Date(), "yyyy-MM-dd"),
      format: "pdf"
    });

    const stats = reactive({
      totalEmployees: 0,
      totalCheckIns: 0,
      activeWarehouses: 0,
      avgWorkingHours: 0
    });

    const recentReports = ref([]);
    const availableWarehouses = ref([]);

    // Summary information from warehouse chart
    const warehouseSummary = ref({
      total_warehouses: 0,
      total_employees: 0,
      total_access_logs_period: 0,
      avg_employees_per_warehouse: 0,
      period: "",
      most_active_warehouse: ""
    });

    // Summary information from attendance chart
    const attendanceSummary = ref({
      total_checkins: 0,
      total_checkouts: 0,
      avg_daily_checkins: 0,
      avg_daily_checkouts: 0,
      avg_weekly_checkins: 0,
      avg_weekly_checkouts: 0,
      avg_monthly_checkins: 0,
      avg_monthly_checkouts: 0,
      period: ""
    });

    // Filtros específicos para el chart de attendance
    const attendanceFilters = reactive({
      groupBy: "week",
      days: 30,
      warehouseId: ""
    });

    const loadStats = async () => {
      try {
        // Cargar estadísticas específicas de reportes desde el endpoint real
        const statsResponse = await api.get("/reports/stats");

        Object.assign(stats, {
          totalEmployees: statsResponse.data.total_employees || 0,
          totalCheckIns: statsResponse.data.total_checkins_today || 0,
          activeWarehouses: statsResponse.data.active_warehouses || 0,
          avgWorkingHours: statsResponse.data.avg_working_hours || "8.2h"
        });
      } catch (error) {
        console.error("Error loading reports stats:", error);
        toast.error("Error loading reports statistics. Showing fallback data.");
      }
    };

    const loadRecentReports = async () => {
      try {
        // Cargar reportes recientes desde el endpoint real
        const response = await api.get("/reports/recent?limit=10");
        recentReports.value = response.data.reports.map((report) => ({
          id: report.id,
          name: report.name,
          description: report.description,
          created_at: report.created_at,
          format: report.format,
          url: report.download_url,
          created_by: report.created_by_name,
          file_size: report.file_size
        }));
      } catch (error) {
        console.error("Error loading recent reports:", error);
        // Datos simulados de reportes recientes si el endpoint no existe
        toast.error("Error loading recent reports. Showing fallback data.");
      }
    };

    const createAttendanceChart = async () => {
      if (!attendanceChart.value) return;

      try {
        // Construir URL con parámetros de filtro
        let url = `/reports/charts/attendance?days=${attendanceFilters.days}&group_by=${attendanceFilters.groupBy}`;
        if (attendanceFilters.warehouseId) {
          url += `&warehouse_id=${attendanceFilters.warehouseId}`;
        }

        // Intentar obtener datos reales del endpoint de charts de reports
        const chartResponse = await api.get(url);

        const ctx = attendanceChart.value.getContext("2d");

        // Limpiar chart anterior si existe
        if (window.attendanceChartInstance) {
          window.attendanceChartInstance.destroy();
        }

        window.attendanceChartInstance = new Chart(ctx, {
          type: "bar",
          data: {
            labels: chartResponse.data.labels || [],
            datasets: (chartResponse.data.datasets || []).map((dataset) => ({
              ...dataset,
              borderWidth: 1,
              backgroundColor:
                dataset.backgroundColor || "rgba(59, 130, 246, 0.8)",
              borderColor: dataset.borderColor || "rgba(59, 130, 246, 1)"
            }))
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: {
                display: chartResponse.data.datasets.length > 1
              }
            },
            scales: {
              y: {
                beginAtZero: true,
                grid: {
                  color: "#e2e8f0"
                }
              },
              x: {
                grid: {
                  display: false
                }
              }
            }
          }
        });

        // Mostrar información del summary si está disponible
        if (chartResponse.data.summary) {
          attendanceSummary.value = chartResponse.data.summary;
          console.log('Attendance Chart Summary:', chartResponse.data.summary);
          
          // Mensaje dinámico según el período
          const periodLabel = attendanceFilters.groupBy === 'day' ? 'daily' : 
                             attendanceFilters.groupBy === 'week' ? 'weekly' : 'monthly';
          toast.success(`Loaded ${periodLabel} attendance data: ${chartResponse.data.summary.total_checkins} check-ins, ${chartResponse.data.summary.total_checkouts} check-outs`);
        }

      } catch (error) {
        console.error("Error loading attendance chart data:", error);
        toast.error(
          "Error loading attendance chart data. Showing fallback data."
        );
      }
    };

    // Función para actualizar el chart de attendance cuando cambien los filtros
    const updateAttendanceChart = async () => {
      await createAttendanceChart();
      await createWarehouseChart();
    };

    // Funciones helper para obtener valores dinámicos del summary
    const getAvgCheckins = () => {
      switch (attendanceFilters.groupBy) {
        case 'day':
          return attendanceSummary.value.avg_daily_checkins || 0;
        case 'week':
          return attendanceSummary.value.avg_weekly_checkins || 0;
        case 'month':
          return attendanceSummary.value.avg_monthly_checkins || 0;
        default:
          return 0;
      }
    };

    const getAvgCheckouts = () => {
      switch (attendanceFilters.groupBy) {
        case 'day':
          return attendanceSummary.value.avg_daily_checkouts || 0;
        case 'week':
          return attendanceSummary.value.avg_weekly_checkouts || 0;
        case 'month':
          return attendanceSummary.value.avg_monthly_checkouts || 0;
        default:
          return 0;
      }
    };

    const getPeriodLabel = () => {
      switch (attendanceFilters.groupBy) {
        case 'day':
          return 'Daily';
        case 'week':
          return 'Weekly';
        case 'month':
          return 'Monthly';
        default:
          return 'Weekly';
      }
    };

    // Función para cargar warehouses para el filtro
    const loadWarehouses = async () => {
      try {
        const response = await api.get("/warehouses/");
        availableWarehouses.value = response.data || [];
      } catch (error) {
        console.error("Error loading warehouses:", error);
        availableWarehouses.value = [];
      }
    };

    const createWarehouseChart = async () => {
      if (!attendanceChart.value) return;
      if (!warehouseChart.value) return;

      try {
        // Intentar obtener datos reales del endpoint de charts de warehouses
        const chartResponse = await api.get(`/reports/charts/warehouses?days=${attendanceFilters.days}`);

        // Extraer datos de la respuesta
        const responseData = chartResponse.data;
        const labels = responseData.labels || [];
        const datasets = responseData.datasets || [];

        // Usar el primer dataset que contiene la información de empleados
        const employeeData = datasets.length > 0 ? datasets[0] : {};
        const data = employeeData.data || [];
        const backgroundColor = employeeData.backgroundColor || [
          "#3B82F6",
          "#10B981",
          "#F59E0B",
          "#EF4444",
          "#8B5CF6",
          "#EC4899",
          "#06B6D4",
          "#84CC16",
          "#F97316",
          "#6366F1"
        ];

        const ctx = warehouseChart.value.getContext("2d");

        // Limpiar chart anterior si existe
        if (window.warehouseChartInstance) {
          window.warehouseChartInstance.destroy();
        }

        window.warehouseChartInstance = new Chart(ctx, {
          type: "doughnut",
          data: {
            labels: labels,
            datasets: [
              {
                label: employeeData.label || "Employees",
                data: data,
                backgroundColor: backgroundColor,
                borderWidth: 2,
                borderColor: "#ffffff"
              }
            ]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: {
                position: "bottom",
                labels: {
                  padding: 20,
                  usePointStyle: true,
                  font: {
                    size: 12
                  }
                }
              },
              tooltip: {
                callbacks: {
                  label: function (context) {
                    const label = context.label || "";
                    const value = context.parsed || 0;
                    const total = context.dataset.data.reduce(
                      (a, b) => a + b,
                      0
                    );
                    const percentage =
                      total > 0 ? ((value / total) * 100).toFixed(1) : 0;
                    return `${label}: ${value} employees (${percentage}%)`;
                  }
                }
              }
            }
          }
        });

        // Mostrar información del summary si está disponible
        if (responseData.summary) {
          warehouseSummary.value = responseData.summary;
          console.log("Warehouse Chart Summary:", responseData.summary);
          toast.success(
            `Loaded data for ${responseData.summary.total_warehouses} warehouses with ${responseData.summary.total_employees} total employees`
          );
        }
      } catch (error) {
        console.error("Error loading warehouse chart data:", error);
        toast.error(
          "Error loading warehouse chart data. Showing fallback data."
        );

       
      }
    };

    const generateReport = async () => {
      loading.value = true;
      try {
        // Crear el payload con los datos del formulario
        const payload = {
          type: reportConfig.type,
          date_from: reportConfig.dateFrom,
          date_to: reportConfig.dateTo,
          format: reportConfig.format
        };

        const response = await api.post("/reports/generate", payload, {
          responseType: "blob"
        });

        // Obtener el nombre del archivo desde el header Content-Disposition
        const contentDisposition = response.headers["content-disposition"];
        let filename = `reporte_${reportConfig.type}_${format(
          new Date(),
          "yyyy-MM-dd"
        )}.${reportConfig.format}`;

        if (contentDisposition) {
          const filenameMatch = contentDisposition.match(
            /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/
          );
          if (filenameMatch && filenameMatch[1]) {
            filename = filenameMatch[1].replace(/['"]/g, "");
          }
        }

        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement("a");
        link.href = url;
        link.setAttribute("download", filename);

        document.body.appendChild(link);
        link.click();
        link.remove();

        // Show success message
        toast.success(
          `Report generated and downloaded successfully: ${filename}`
        );

        // Recargar reportes recientes
        await loadRecentReports();
      } catch (error) {
        console.error("Error generating report:", error);
        if (error.response?.status === 403) {
          toast.error("No tienes permisos para generar reportes.");
        } else if (error.response?.status === 422) {
          toast.error(
            "Datos de reporte inválidos. Verifica las fechas y parámetros."
          );
        } else {
          toast.error("Error al generar el reporte. Intenta nuevamente.");
        }
      } finally {
        loading.value = false;
      }
    };

    const downloadReport = async (report) => {
      try {
        const response = await api.get(report.url, { responseType: "blob" });
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement("a");
        link.href = url;
        link.setAttribute("download", `${report.name}.${report.format}`);
        document.body.appendChild(link);
        link.click();
        link.remove();
      } catch (error) {
        console.error("Error downloading report:", error);
      }
    };

    const viewReport = (report) => {
      if (report.format === "pdf") {
        previewReport.value = report;
      } else {
        downloadReport(report);
      }
    };

    const formatDate = (dateString) => {
      return format(new Date(dateString), "MM/dd/yyyy HH:mm");
    };

    onMounted(async () => {
      await loadStats();
      loadRecentReports();
      loadWarehouses(); // Cargar warehouses para el filtro

      await nextTick();
      createAttendanceChart();
      createWarehouseChart();
    });

    return {
      loading,
      attendanceChart,
      warehouseChart,
      previewReport,
      reportConfig,
      stats,
      recentReports,
      availableWarehouses,
      warehouseSummary,
      attendanceSummary,
      attendanceFilters,
      generateReport,
      downloadReport,
      viewReport,
      formatDate,
      updateAttendanceChart,
      getAvgCheckins,
      getAvgCheckouts,
      getPeriodLabel,
      // Permisos
      permissions
    };
  }
};
</script>

<style scoped>
.reports {
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

.report-filters {
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

.chart-filters {
  background: var(--card-background);
  padding: 20px;
  border-radius: 8px;
  border: 1px solid var(--border-color);
  margin-bottom: 20px;
}

.chart-filters h3 {
  margin: 0 0 16px 0;
  color: var(--text-primary);
  font-size: 18px;
  font-weight: 600;
}

.filter-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 20px;
}

.stat-card {
  background: var(--card-background);
  border-radius: 12px;
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  border: 1px solid var(--border-color);
}

.stat-icon {
  font-size: 32px;
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(59, 130, 246, 0.1);
  border-radius: 12px;
}

.stat-content h3 {
  margin: 0;
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
}

.stat-content p {
  margin: 4px 0 0 0;
  color: var(--text-secondary);
  font-size: 14px;
}

.charts-section {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 24px;
}

.chart-container {
  background: var(--card-background);
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  border: 1px solid var(--border-color);
}

.chart-container h3 {
  margin: 0 0 20px 0;
  color: var(--text-primary);
  font-size: 18px;
  font-weight: 600;
}

.chart-container canvas {
  max-height: 300px;
}

.chart-summary {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid var(--border-color);
}

.chart-summary h4 {
  margin: 0 0 16px 0;
  color: var(--text-primary);
  font-size: 16px;
  font-weight: 600;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px;
}

.summary-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: var(--background-secondary, #f8fafc);
  border-radius: 6px;
  border: 1px solid var(--border-color, #e2e8f0);
}

.summary-label {
  font-size: 13px;
  color: var(--text-secondary, #64748b);
  font-weight: 500;
}

.summary-value {
  font-size: 14px;
  color: var(--text-primary, #1e293b);
  font-weight: 600;
}

.summary-value.highlight {
  color: var(--primary-color, #3b82f6);
  background: var(--primary-light, rgba(59, 130, 246, 0.1));
  padding: 2px 8px;
  border-radius: 4px;
  font-weight: 700;
}

.summary-value.text-warning {
  color: #f59e0b;
  background: rgba(245, 158, 11, 0.1);
  padding: 2px 8px;
  border-radius: 4px;
  font-weight: 700;
}

.summary-value.text-danger {
  color: #ef4444;
  background: rgba(239, 68, 68, 0.1);
  padding: 2px 8px;
  border-radius: 4px;
  font-weight: 700;
}

.recent-reports {
  background: var(--card-background);
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  border: 1px solid var(--border-color);
}

.recent-reports h3 {
  margin: 0 0 20px 0;
  color: var(--text-primary);
  font-size: 18px;
  font-weight: 600;
}

.reports-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.report-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: var(--background-color);
  border-radius: 8px;
  border: 1px solid var(--border-color);
}

.report-info h4 {
  margin: 0 0 4px 0;
  color: var(--text-primary);
  font-size: 14px;
  font-weight: 600;
}

.report-info p {
  margin: 0 0 4px 0;
  color: var(--text-secondary);
  font-size: 12px;
}

.report-date {
  color: var(--text-secondary);
  font-size: 11px;
}

.report-actions {
  display: flex;
  gap: 8px;
}

.btn-sm {
  padding: 6px 12px;
  font-size: 12px;
}

.modal-lg {
  max-width: 90vw;
  width: 1000px;
}

.report-preview {
  width: 100%;
}

.no-preview {
  text-align: center;
  padding: 40px;
  color: var(--text-secondary);
}

@media (max-width: 768px) {
  .report-filters {
    grid-template-columns: 1fr;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .charts-section {
    grid-template-columns: 1fr;
  }

  .report-item {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }

  .report-actions {
    justify-content: center;
  }
}
</style>
