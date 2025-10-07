<template>
  <div class="dashboard">
    <!-- Main Metrics -->
    <div class="metrics-grid">
      <div class="metric-card">
        <div class="metric-icon">🏢</div>
        <div class="metric-content">
          <h3>{{ metrics.companies }}</h3>
          <p>Companies</p>
        </div>
      </div>
      
      <div class="metric-card">
        <div class="metric-icon">🏭</div>
        <div class="metric-content">
          <h3>{{ metrics.warehouses }}</h3>
          <p>Warehouses</p>
        </div>
      </div>
      
      <div class="metric-card">
        <div class="metric-icon">👥</div>
        <div class="metric-content">
          <h3>{{ metrics.employees }}</h3>
          <p>Employees</p>
        </div>
      </div>
      
      <div class="metric-card">
        <div class="metric-icon">📊</div>
        <div class="metric-content">
          <h3>{{ metrics.todayCheckIns }}</h3>
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

Chart.register(...registerables)

export default {
  name: 'Dashboard',
  setup() {
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
      try {
        // Cargar métricas del dashboard
        const [companiesRes, warehousesRes, employeesRes] = await Promise.all([
          api.get('/companies/'),
          api.get('/warehouses/'),
          api.get('/employees/')
        ])

        metrics.value = {
          companies: companiesRes.data.total,
          warehouses: warehousesRes.data.length,
          employees: employeesRes.data.length,
          todayCheckIns: 15 //todo:roa- Se puede obtener de los logs
        }
      } catch (error) {
        console.error('Error loading metrics:', error)
      }
    }

    const loadRecentActivities = async () => {
      try {
        const response = await api.get('/logs/?limit=10')
        recentActivities.value = response.data.map(log => ({
          id: log.id,
          type: log.action_type || 'check_in',
          description: `${log.employee_name} - ${log.action_type || 'Check-in'}`,
          timestamp: log.timestamp
        }))
      } catch (error) {
        console.error('Error loading recent activities:', error)
        // Datos de ejemplo si no hay logs
        recentActivities.value = [
            {
            id: 1,
            type: 'check_in',
            description: 'Juan Perez checked in',
            timestamp: new Date().toISOString()
            },
            {
            id: 2,
            type: 'check_out',
            description: 'Maria Garcia checked out',
            timestamp: new Date(Date.now() - 300000).toISOString()
            }
        ]
      }
    }

    const createWeeklyChart = () => {
      if (!weeklyChart.value) return

      const ctx = weeklyChart.value.getContext('2d')
      new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
          datasets: [{
            label: 'Check-ins',
            data: [12, 19, 8, 15, 22, 10, 5],
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

    const createStatusChart = () => {
      if (!statusChart.value) return

      const ctx = statusChart.value.getContext('2d')
      new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Active', 'Inactive', 'On Break'],
          datasets: [{
            data: [65, 25, 10],
            backgroundColor: [
              '#10b981',
              '#ef4444',
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
</style>