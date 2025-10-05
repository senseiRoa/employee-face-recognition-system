<template>
  <div class="layout">
    <!-- Sidebar -->
    <aside class="sidebar" :class="{ 'open': sidebarOpen }">
      <div class="sidebar-header">
        <h2>Employee Tracker</h2>
        <button @click="toggleSidebar" class="sidebar-toggle">
          <span>☰</span>
        </button>
      </div>
      
      <nav class="sidebar-nav">
        <router-link to="/admin/dashboard" class="nav-item">
          <span class="nav-icon">📊</span>
          <span class="nav-text">Dashboard</span>
        </router-link>
        
        <router-link to="/admin/companies" class="nav-item">
          <span class="nav-icon">🏢</span>
          <span class="nav-text">Companies</span>
        </router-link>
        
        <router-link to="/admin/warehouses" class="nav-item">
          <span class="nav-icon">🏭</span>
          <span class="nav-text">Warehouses</span>
        </router-link>
        
        <router-link to="/admin/employees" class="nav-item">
          <span class="nav-icon">👥</span>
          <span class="nav-text">Employees</span>
        </router-link>
        
        <router-link to="/admin/users" class="nav-item">
          <span class="nav-icon">👤</span>
          <span class="nav-text">Users</span>
        </router-link>
        
        <router-link to="/admin/roles" class="nav-item">
          <span class="nav-icon">🔑</span>
          <span class="nav-text">Roles</span>
        </router-link>
        
        <router-link to="/admin/logs" class="nav-item">
          <span class="nav-icon">📋</span>
          <span class="nav-text">Logs</span>
        </router-link>
        
        <router-link to="/admin/reports" class="nav-item">
          <span class="nav-icon">📈</span>
          <span class="nav-text">Reports</span>
        </router-link>
      </nav>
    </aside>

    <!-- Main Content -->
    <div class="main-content">
      <!-- Header -->
      <header class="header">
        <div class="header-left">
          <button @click="toggleSidebar" class="menu-toggle">
            <span>☰</span>
          </button>
          <h1>{{ pageTitle }}</h1>
        </div>
        
        <div class="header-right">
          <div class="user-menu">
            <span class="user-name">{{ user?.name || 'User' }}</span>
            <button @click="logout" class="btn btn-outline">
              Log Out
            </button>
          </div>
        </div>
      </header>

      <!-- Content -->
      <main class="content">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import { useAppStore } from '@/store/app'

export default {
  name: 'Layout',
  setup() {
    const route = useRoute()
    const router = useRouter()
    const authStore = useAuthStore()
    const appStore = useAppStore()

    const pageTitle = computed(() => {
      const titles = {
        'Dashboard': 'Panel de Control',
        'Companies': 'Gestión de Empresas',
        'Warehouses': 'Gestión de Warehouses',
        'Employees': 'Gestión de Empleados',
        'Users': 'Gestión de Usuarios',
        'Roles': 'Gestión de Roles',
        'Logs': 'Auditoría y Logs',
        'Reports': 'Reportes'
      }
      return titles[route.name] || 'Panel de Administración'
    })

    const logout = () => {
      authStore.logout()
      router.push('/admin/login')
    }

    const toggleSidebar = () => {
      appStore.toggleSidebar()
    }

    return {
      user: authStore.user,
      sidebarOpen: appStore.sidebarOpen,
      pageTitle,
      logout,
      toggleSidebar
    }
  }
}
</script>

<style scoped>
.sidebar {
  background: var(--card-background);
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
}

.sidebar-header {
  padding: 24px;
  border-bottom: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.sidebar-header h2 {
  color: var(--primary-color);
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.sidebar-toggle {
  display: none;
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: var(--text-secondary);
}

.sidebar-nav {
  padding: 16px 0;
  flex: 1;
}

.nav-item {
  display: flex;
  align-items: center;
  padding: 12px 24px;
  color: var(--text-secondary);
  text-decoration: none;
  transition: all 0.2s;
  border-left: 3px solid transparent;
}

.nav-item:hover {
  background-color: var(--background-color);
  color: var(--text-primary);
}

.nav-item.router-link-active {
  background-color: rgba(59, 130, 246, 0.1);
  color: var(--primary-color);
  border-left-color: var(--primary-color);
}

.nav-icon {
  margin-right: 12px;
  font-size: 16px;
}

.nav-text {
  font-weight: 500;
}

.header {
  background: var(--card-background);
  border-bottom: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  height: var(--header-height);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.header-left h1 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
}

.menu-toggle {
  display: none;
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: var(--text-secondary);
  padding: 8px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}

.user-menu {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-name {
  font-weight: 500;
  color: var(--text-primary);
}

.content {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
  background-color: var(--background-color);
}

@media (max-width: 768px) {
  .sidebar {
    position: fixed;
    z-index: 100;
    height: 100vh;
    transform: translateX(-100%);
    transition: transform 0.3s;
  }
  
  .sidebar.open {
    transform: translateX(0);
  }
  
  .sidebar-toggle {
    display: block;
  }
  
  .menu-toggle {
    display: block;
  }
  
  .main-content {
    margin-left: 0;
  }
  
  .header-left h1 {
    font-size: 16px;
  }
  
  .content {
    padding: 16px;
  }
}
</style>