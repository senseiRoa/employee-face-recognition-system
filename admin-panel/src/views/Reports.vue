<template>
  <div class="reports">
    <div class="page-header">
      <h2>Reports & Statistics</h2>
      <div class="header-actions">
        <button @click="generateReport" class="btn btn-primary" :disabled="loading">
          📊 Generate Report
        </button>
      </div>
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
        <input v-model="reportConfig.dateFrom" type="date" class="form-control" lang="en" />
      </div>
      <div class="filter-group">
        <label class="form-label">End Date</label>
        <input v-model="reportConfig.dateTo" type="date" class="form-control" lang="en" />
      </div>
      <div class="filter-group">
        <label class="form-label">Format</label>
        <select v-model="reportConfig.format" class="form-control">
          <option value="pdf">PDF</option>
          <option value="csv">CSV</option>
          <option value="excel">Excel</option>
        </select>
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

    <!-- Charts -->
    <div class="charts-section">
      <div class="chart-container">
        <h3>Attendance by Day</h3>
        <canvas ref="attendanceChart"></canvas>
      </div>
      
      <div class="chart-container">
        <h3>Employees per Warehouse</h3>
        <canvas ref="warehouseChart"></canvas>
      </div>
    </div>

    <!-- Recent Reports Table -->
    <div class="recent-reports">
      <h3>Recent Reports</h3>
      <div class="reports-list">
        <div v-for="report in recentReports" :key="report.id" class="report-item">
          <div class="report-info">
            <h4>{{ report.name }}</h4>
            <p>{{ report.description }}</p>
            <span class="report-date">{{ formatDate(report.created_at) }}</span>
          </div>
          <div class="report-actions">
            <button @click="downloadReport(report)" class="btn btn-outline btn-sm">
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
    <div v-if="previewReport" class="modal-overlay" @click.self="previewReport = null">
      <div class="modal modal-lg">
        <div class="modal-header">
          <h3>Preview: {{ previewReport.name }}</h3>
          <button @click="previewReport = null" class="btn btn-outline">✕</button>
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
              <button @click="downloadReport(previewReport)" class="btn btn-primary">
                Download File
              </button>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button @click="downloadReport(previewReport)" class="btn btn-primary">
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
import { ref, reactive, onMounted, nextTick } from 'vue'
import { Chart, registerables } from 'chart.js'
import api from '@/composables/api'
import { format } from 'date-fns'

Chart.register(...registerables)

export default {
  name: 'Reports',
  setup() {
    const loading = ref(false)
    const attendanceChart = ref(null)
    const warehouseChart = ref(null)
    const previewReport = ref(null)

    const reportConfig = reactive({
      type: 'attendance',
      dateFrom: format(new Date(Date.now() - 30 * 24 * 60 * 60 * 1000), 'yyyy-MM-dd'),
      dateTo: format(new Date(), 'yyyy-MM-dd'),
      format: 'pdf'
    })

    const stats = reactive({
      totalEmployees: 0,
      totalCheckIns: 0,
      activeWarehouses: 0,
      avgWorkingHours: 0
    })

    const recentReports = ref([])

    const loadStats = async () => {
      try {
        // Cargar estadísticas básicas
        const [employeesRes, warehousesRes] = await Promise.all([
          api.get('/employees/'),
          api.get('/warehouses/')
        ])

        stats.totalEmployees = employeesRes.data.length
        stats.activeWarehouses = warehousesRes.data.filter(w => w.is_active).length
        stats.totalCheckIns = Math.floor(Math.random() * 50) + 10 // Simulado
        stats.avgWorkingHours = '8.2h' // Simulado
      } catch (error) {
        console.error('Error loading stats:', error)
        // Valores por defecto
        Object.assign(stats, {
          totalEmployees: 25,
          totalCheckIns: 18,
          activeWarehouses: 3,
          avgWorkingHours: '8.2h'
        })
      }
    }

    const loadRecentReports = () => {
      // Datos simulados de reportes recientes
      recentReports.value = [
        {
          id: 1,
          name: 'Weekly Attendance Report',
          description: 'Employee attendance from October 1-7',
          created_at: new Date().toISOString(),
          format: 'pdf',
          url: '/api/reports/1/download'
        },
        {
          id: 2,
          name: 'Warehouse Statistics',
          description: 'Activity summary by warehouse',
          created_at: new Date(Date.now() - 86400000).toISOString(),
          format: 'excel',
          url: '/api/reports/2/download'
        }
      ]
    }

    const createAttendanceChart = () => {
      if (!attendanceChart.value) return

      const ctx = attendanceChart.value.getContext('2d')
      new Chart(ctx, {
        type: 'bar',
        data: {
          labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
          datasets: [{
            label: 'Check-ins',
            data: [22, 25, 18, 28, 24, 12, 8],
            backgroundColor: 'rgba(59, 130, 246, 0.8)',
            borderColor: '#3b82f6',
            borderWidth: 1
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              display: false
            }
          },
          scales: {
            y: {
              beginAtZero: true,
              grid: {
                color: '#e2e8f0'
              }
            },
            x: {
              grid: {
                display: false
              }
            }
          }
        }
      })
    }

    const createWarehouseChart = () => {
      if (!warehouseChart.value) return

      const ctx = warehouseChart.value.getContext('2d')
      new Chart(ctx, {
        type: 'doughnut',
        data: {
          labels: ['Warehouse Central', 'Warehouse Norte', 'Warehouse Sur'],
          datasets: [{
            data: [45, 30, 25],
            backgroundColor: [
              '#10b981',
              '#3b82f6',
              '#f59e0b'
            ],
            borderWidth: 0
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: 'bottom'
            }
          }
        }
      })
    }

    const generateReport = async () => {
      loading.value = true
      try {
        const response = await api.post('/reports/generate', reportConfig, {
          responseType: 'blob'
        })
        
        const url = window.URL.createObjectURL(new Blob([response.data]))
        const link = document.createElement('a')
        link.href = url
        
        const filename = `reporte_${reportConfig.type}_${format(new Date(), 'yyyy-MM-dd')}.${reportConfig.format}`
        link.setAttribute('download', filename)
        
        document.body.appendChild(link)
        link.click()
        link.remove()
        
        // Recargar reportes recientes
        loadRecentReports()
      } catch (error) {
        console.error('Error generating report:', error)
        alert('Error al generar el reporte. Intenta nuevamente.')
      } finally {
        loading.value = false
      }
    }

    const downloadReport = async (report) => {
      try {
        const response = await api.get(report.url, { responseType: 'blob' })
        const url = window.URL.createObjectURL(new Blob([response.data]))
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', `${report.name}.${report.format}`)
        document.body.appendChild(link)
        link.click()
        link.remove()
      } catch (error) {
        console.error('Error downloading report:', error)
      }
    }

    const viewReport = (report) => {
      if (report.format === 'pdf') {
        previewReport.value = report
      } else {
        downloadReport(report)
      }
    }

    const formatDate = (dateString) => {
      return format(new Date(dateString), 'MM/dd/yyyy HH:mm')
    }

    onMounted(async () => {
      await loadStats()
      loadRecentReports()
      
      await nextTick()
      createAttendanceChart()
      createWarehouseChart()
    })

    return {
      loading,
      attendanceChart,
      warehouseChart,
      previewReport,
      reportConfig,
      stats,
      recentReports,
      generateReport,
      downloadReport,
      viewReport,
      formatDate
    }
  }
}
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