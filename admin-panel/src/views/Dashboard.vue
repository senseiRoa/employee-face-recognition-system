<template>
  <div class="dashboard">
    <!-- Loading overlay -->
    <div v-if="loading" class="loading-overlay">
      <div class="loading-spinner">
        <div class="spinner"></div>
        <p>Loading dashboard data...</p>
      </div>
    </div>

    <!-- Main Metrics -->
    <div class="metrics-grid" :class="{ 'loading': loading }">
      <div class="metric-card">
        <div class="metric-icon">🏢</div>
        <div class="metric-content">
          <h3>{{ metrics.companies || 0 }}</h3>
          <p>Companies</p>
        </div>
      </div>
      
      <div class="metric-card">
        <div class="metric-icon">🏭</div>
        <div class="metric-content">
          <h3>{{ metrics.warehouses || 0 }}</h3>
          <p>Warehouses</p>
        </div>
      </div>
      
      <div class="metric-card">
        <div class="metric-icon">👥</div>
        <div class="metric-content">
          <h3>{{ metrics.employees || 0 }}</h3>
          <p>Employees</p>
        </div>
      </div>
      
      <div class="metric-card">
        <div class="metric-icon">📊</div>
        <div class="metric-content">
          <h3>{{ metrics.todayCheckIns || 0 }}</h3>
          <p>Check-ins Today</p>
        </div>
      </div>
    </div>

    <!-- Charts and Statistics -->
    <div class="charts-grid">
      <div class="chart-card">
        <h3>Weekly Activity</h3>
        <canvas ref="weeklyChart"></canvas>
      </div>
      
      <div class="chart-card">
        <h3>Employee Status</h3>
        <canvas ref="statusChart"></canvas>
      </div>
    </div>

    <!-- Recent Activity -->
    <div class="recent-activity">
      <h3>Recent Activity</h3>
      <div class="activity-list">
        <div
          v-for="activity in recentActivities"
          :key="activity.id"
          class="activity-item"
        >
          <div class="activity-icon" :class="activity.type">
            {{ getActivityIcon(activity.type) }}
          </div>
          <div class="activity-content">
            <p class="activity-description">{{ activity.description }}</p>
            <span class="activity-time">{{ formatTime(activity.timestamp) }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, nextTick } from 'vue'
import { Chart, registerables } from 'chart.js'
import api from '@/composables/api'
import { format } from 'date-fns'
import { es } from 'date-fns/locale'
import { useToast } from 'vue-toastification'

Chart.register(...registerables)

export default {
  name: 'Dashboard',
  setup() {
    const loading = ref(false)
    const toast = useToast()
    const weeklyChart = ref(null)
    const statusChart = ref(null)
    const metrics = ref({
      companies: 0,
      warehouses: 0,
      employees: 0,
      todayCheckIns: 0
    })
    const recentActivities = ref([])

    const loadMetrics = async () => {
      loading.value = true
      try {
        // Cargar estadísticas del dashboard desde el endpoint real
        const statsResponse = await api.get('/dashboard/stats')
        
        metrics.value = {
          companies: statsResponse.data.total_companies || statsResponse.data.companies || 0,
          warehouses: statsResponse.data.total_warehouses || statsResponse.data.warehouses || 0,
          employees: statsResponse.data.total_employees || statsResponse.data.employees || 0,
          todayCheckIns: statsResponse.data.todays_checkins || statsResponse.data.todayCheckIns || statsResponse.data.today_check_ins || 0
        }
        // Show success message only if all data loaded successfully
        if (statsResponse.data.total_companies !== undefined || statsResponse.data.companies !== undefined) {
          toast.success('Dashboard data loaded successfully')
        }
      } catch (error) {
        console.error('Error loading dashboard stats:', error)
        
        // Handle specific error types
        if (error.response?.status === 403) {
          toast.error('You do not have permission to view dashboard statistics.')
          return
        } else if (error.response?.status === 422) {
          toast.error('Invalid request format for dashboard statistics.')
          return
        }
        
        // Fallback: cargar métricas individuales si el endpoint dashboard no existe
        try {
          const [companiesRes, warehousesRes, employeesRes] = await Promise.all([
            api.get('/companies/'),
            api.get('/warehouses/'),
            api.get('/employees/')
          ])

          metrics.value = {
            companies: companiesRes.data.total || companiesRes.data.length || 0,
            warehouses: warehousesRes.data.total || warehousesRes.data.length || 0,
            employees: employeesRes.data.total || employeesRes.data.length || 0,
            todayCheckIns: 0 // Cannot determine from individual endpoints
          }
          toast.info('Dashboard loaded using basic data (some features may be limited)')
        } catch (fallbackError) {
          console.error('Error loading fallback metrics:', fallbackError)
          // Set zero values as last resort
          metrics.value = {
            companies: 0,
            warehouses: 0,
            employees: 0,
            todayCheckIns: 0
          }
          toast.error('Failed to load dashboard data. Please check your connection and try again.')
        }
      } finally {
        loading.value = false
      }
    }

    const loadRecentActivities = async () => {
      try {
        // Intentar cargar desde el endpoint de dashboard primero
        const response = await api.get('/dashboard/recent-activities?limit=10')
        
        // Handle different response structures
        const activities = response.data.activities || response.data || []
        recentActivities.value = activities.map(activity => ({
          id: activity.id,
          type: activity.action || activity.event || 'check',
          description: `${activity.employee_name || activity.employee?.name || 'Unknown Employee'} - ${activity.action === 'in' ? 'Check-in' : 'Check-out'} at ${activity.warehouse_name || activity.warehouse?.name || 'Unknown Location'}`,
          timestamp: activity.timestamp || activity.created_at
        }))
      } catch (error) {
        console.error('Error loading recent activities from dashboard:', error)
        
        // Handle specific error types
        if (error.response?.status === 403) {
          toast.error('You do not have permission to view recent activities.')
          recentActivities.value = []
          return
        } else if (error.response?.status === 422) {
          toast.error('Invalid request format for recent activities.')
          recentActivities.value = []
          return
        }
        
        // Fallback: intentar cargar desde logs
        try {
          const response = await api.get('/logs/?limit=10')
          const logs = response.data.logs || response.data || []
          recentActivities.value = logs.map(log => ({
            id: log.id,
            type: log.action_type || log.event || 'check',
            description: `${log.employee_name || log.employee?.name || 'Unknown Employee'} - ${log.action_type || 'Activity'}`,
            timestamp: log.timestamp || log.created_at
          }))
        } catch (fallbackError) {
          console.error('Error loading recent activities fallback:', fallbackError)
          // Empty array if no data available
          recentActivities.value = []
          toast.error('Failed to load recent activities. Please check your connection and try again.')
        }
      }
    }

    const createWeeklyChart = async () => {
      if (!weeklyChart.value) return

      try {
        // Intentar obtener datos reales del endpoint de charts
        const chartResponse = await api.get('/dashboard/charts/attendance?days=7')
        
        // Handle different response structures
        const chartData = chartResponse.data
        const labels = chartData.labels || ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        const datasets = chartData.datasets || [{
          label: 'Check-ins',
          data: chartData.data || [0, 0, 0, 0, 0, 0, 0],
          borderColor: '#3b82f6',
          backgroundColor: 'rgba(59, 130, 246, 0.1)'
        }]
        
        const ctx = weeklyChart.value.getContext('2d')
        new Chart(ctx, {
          type: 'line',
          data: {
            labels: labels,
            datasets: datasets.map(dataset => ({
              ...dataset,
              borderColor: dataset.borderColor || dataset.backgroundColor || '#3b82f6',
              backgroundColor: dataset.backgroundColor ? dataset.backgroundColor.replace('0.8', '0.1') : 'rgba(59, 130, 246, 0.1)',
              tension: 0.4,
              fill: true
            }))
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: {
                display: datasets.length > 1
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
      } catch (error) {
        console.error('Error loading chart data:', error)
        
        // Handle specific error types
        if (error.response?.status === 403) {
          console.warn('No permission to view attendance chart')
        } else if (error.response?.status === 422) {
          console.warn('Invalid request format for attendance chart')
        }
        
        // Fallback: datos estáticos
        const ctx = weeklyChart.value.getContext('2d')
        new Chart(ctx, {
          type: 'line',
          data: {
            labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            datasets: [{
              label: 'Check-ins',
              data: [0, 0, 0, 0, 0, 0, 0],
              borderColor: '#3b82f6',
              backgroundColor: 'rgba(59, 130, 246, 0.1)',
              tension: 0.4,
              fill: true
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
    }

    const createStatusChart = async () => {
      if (!statusChart.value) return

      try {
        // Intentar obtener datos reales del endpoint de warehouses
        const chartResponse = await api.get('/dashboard/charts/warehouses')
        
        // Handle different response structures
        const chartData = chartResponse.data
        const labels = chartData.labels || ['No Data']
        const data = chartData.data || chartData.values || [1]
        const colors = chartData.colors || chartData.backgroundColor || ['#e2e8f0']
        
        const ctx = statusChart.value.getContext('2d')
        new Chart(ctx, {
          type: 'doughnut',
          data: {
            labels: labels,
            datasets: [{
              data: data,
              backgroundColor: colors,
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
      } catch (error) {
        console.error('Error loading warehouse chart data:', error)
        
        // Handle specific error types
        if (error.response?.status === 403) {
          console.warn('No permission to view warehouse chart')
        } else if (error.response?.status === 422) {
          console.warn('Invalid request format for warehouse chart')
        }
        
        // Fallback: datos estáticos o vacíos
        const ctx = statusChart.value.getContext('2d')
        new Chart(ctx, {
          type: 'doughnut',
          data: {
            labels: ['No Data Available'],
            datasets: [{
              data: [1],
              backgroundColor: ['#e2e8f0'],
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
    }

    const getActivityIcon = (type) => {
      const icons = {
        check_in: '📍',
        check_out: '🚪',
        login: '🔑',
        error: '⚠️'
      }
      return icons[type] || '📝'
    }

    const formatTime = (timestamp) => {
      return format(new Date(timestamp), 'dd/MM/yyyy HH:mm', { locale: es })
    }

    onMounted(async () => {
      await loadMetrics()
      await loadRecentActivities()
      
      await nextTick()
      createWeeklyChart()
      createStatusChart()
    })

    return {
      loading,
      weeklyChart,
      statusChart,
      metrics,
      recentActivities,
      getActivityIcon,
      formatTime
    }
  }
}
</script>

<style scoped>
.dashboard {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 20px;
}

.metric-card {
  background: var(--card-background);
  border-radius: 12px;
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  border: 1px solid var(--border-color);
}

.metric-icon {
  font-size: 32px;
  width: 60px;
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(59, 130, 246, 0.1);
  border-radius: 12px;
}

.metric-content h3 {
  margin: 0;
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
}

.metric-content p {
  margin: 4px 0 0 0;
  color: var(--text-secondary);
  font-size: 14px;
}

.charts-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 24px;
}

.chart-card {
  background: var(--card-background);
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  border: 1px solid var(--border-color);
}

.chart-card h3 {
  margin: 0 0 20px 0;
  color: var(--text-primary);
  font-size: 18px;
  font-weight: 600;
}

.chart-card canvas {
  max-height: 300px;
}

.recent-activity {
  background: var(--card-background);
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  border: 1px solid var(--border-color);
}

.recent-activity h3 {
  margin: 0 0 20px 0;
  color: var(--text-primary);
  font-size: 18px;
  font-weight: 600;
}

.activity-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.activity-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-radius: 8px;
  background: var(--background-color);
}

.activity-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  background: rgba(59, 130, 246, 0.1);
}

.activity-icon.check_in {
  background: rgba(16, 185, 129, 0.1);
}

.activity-icon.check_out {
  background: rgba(239, 68, 68, 0.1);
}

.activity-content {
  flex: 1;
}

.activity-description {
  margin: 0;
  color: var(--text-primary);
  font-weight: 500;
}

.activity-time {
  color: var(--text-secondary);
  font-size: 12px;
}

@media (max-width: 768px) {
  .metrics-grid {
    grid-template-columns: 1fr;
  }
  
  .charts-grid {
    grid-template-columns: 1fr;
  }
  
  .metric-card {
    padding: 16px;
  }
  
  .chart-card {
    padding: 16px;
  }
}

/* Loading styles */
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.loading-spinner {
  text-align: center;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #e2e8f0;
  border-left-color: #3b82f6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 16px;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.loading-spinner p {
  color: #64748b;
  font-size: 14px;
  margin: 0;
}

.metrics-grid.loading,
.charts-grid.loading {
  opacity: 0.6;
  pointer-events: none;
}
</style>