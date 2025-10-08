<template>
  <div class="layout">
    <!-- Sidebar -->
    <aside class="sidebar" :class="{ open: sidebarOpen }">
      <div class="sidebar-header">
        <h2>Time Tracker</h2>
        <button @click="toggleSidebar" class="sidebar-toggle">
          <span>☰</span>
        </button>
      </div>

      <nav class="sidebar-nav">
        <router-link
          v-for="navItem in validNavItems"
          :key="navItem.path"
          :to="navItem.path"
          class="nav-item"
        >
          <span class="nav-icon">{{ navItem.icon }}</span>
          <span class="nav-text">{{ navItem.name }}</span>
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
          <div class="user-menu" :class="{ open: userMenuOpen }">
            <div class="user-info" @click="toggleUserMenu">
              <div class="user-avatar">
                <span>{{ getUserInitials() }}</span>
              </div>
              <div class="user-details">
                <div class="user-name">{{ getUserFullName() }}</div>
                <div class="user-role">{{ user?.role || "User" }}</div>
              </div>
              <div class="user-dropdown-icon">
                <span>{{ userMenuOpen ? "▲" : "▼" }}</span>
              </div>
            </div>

            <div class="user-dropdown" v-show="userMenuOpen">
              <div class="user-profile">
                <div class="profile-header">
                  <div class="profile-avatar">
                    <span>{{ getUserInitials() }}</span>
                  </div>
                  <div class="profile-info">
                    <div class="profile-name">{{ getUserFullName() }}</div>
                    <div class="profile-email">
                      {{ user?.email || "No email" }}
                    </div>
                  </div>
                </div>

                <div class="profile-details">
                  <div class="detail-item">
                    <span class="detail-label">Username:</span>
                    <span class="detail-value">{{
                      user?.username || "-"
                    }}</span>
                  </div>
                  <div class="detail-item">
                    <span class="detail-label">Role:</span>
                    <span class="detail-value">{{ user?.role || "-" }}</span>
                  </div>
                  <div class="detail-item">
                    <span class="detail-label">Warehouse:</span>
                    <span class="detail-value">{{
                      user?.warehouse_name || "-"
                    }}</span>
                  </div>
                </div>

                <div class="profile-actions">
                  <button @click="logout" class="btn btn-danger btn-sm">
                    <span>🚪</span>
                    Log Out
                  </button>
                </div>
              </div>
            </div>
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
import { computed, ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { useRoute, useRouter } from "vue-router";
import { useAuthStore } from "@/store/auth";
import { useAppStore } from "@/store/app";
import { usePermissions } from "@/composables/usePermissions";

export default {
  name: "Layout",
  setup() {
    const route = useRoute();
    const router = useRouter();
    const authStore = useAuthStore();
    const appStore = useAppStore();
    const permissions = usePermissions();
    const userMenuOpen = ref(false);

    const pageTitle = computed(() => {
      const titles = {
        Dashboard: "Dashboard",
        Companies: "Companies Management",
        Warehouses: "Warehouses Management",
        Employees: "Employees Management",
        Users: "Users Management",
        Roles: "Roles & Permissions",
        Logs: "Audit & Logs",
        Reports: "Reports & Statistics"
      };
      return titles[route.name] || "Admin Panel";
    });

    // Elementos de navegación filtrados por permisos
    const availableNavItems = computed(() => {
      try {
        const routes = permissions.availableRoutes.value || [];
        return routes;
      } catch (error) {
        // Fallback: rutas básicas sin permisos
        return [{ name: "Dashboard", path: "/admin/dashboard", icon: "📊" }];
      }
    });

    // Validar que los elementos de navegación tengan todas las propiedades requeridas
    const validNavItems = computed(() => {
      try {
        const rawItems = availableNavItems.value || [];
        
        // Asegurar que tenemos un array
        const items = Array.isArray(rawItems) ? rawItems : [];

        const validItems = items.filter((item, index) => {
          const isValid = item && 
            typeof item === "object" && 
            item.path && 
            item.name && 
            item.icon;
          
          
          return isValid;
        });

        return validItems;
      } catch (error) {
        return [{ name: "Dashboard", path: "/admin/dashboard", icon: "📊" }];
      }
    });

    const getUserFullName = () => {
      const user = authStore.user;
      if (user?.first_name && user?.last_name) {
        return `${user.first_name} ${user.last_name}`;
      }
      return user?.username || "User";
    };

    const getUserInitials = () => {
      const user = authStore.user;
      if (user?.first_name && user?.last_name) {
        return `${user.first_name.charAt(0)}${user.last_name.charAt(
          0
        )}`.toUpperCase();
      }
      if (user?.username) {
        return user.username.substring(0, 2).toUpperCase();
      }
      return "U";
    };

    const toggleUserMenu = () => {
      userMenuOpen.value = !userMenuOpen.value;
    };

    const closeUserMenu = (event) => {
      if (!event.target.closest(".user-menu")) {
        userMenuOpen.value = false;
      }
    };

    const logout = () => {
      userMenuOpen.value = false;
      authStore.logout();
      router.push("/admin/login");
    };

    const toggleSidebar = () => {
      appStore.toggleSidebar();
    };

    onMounted(async () => {
      document.addEventListener("click", closeUserMenu);

      // Asegurar que los roles estén cargados ANTES de continuar
      if (authStore.isAuthenticated) {
        try {
          // Esperar a que los roles se carguen completamente
          await permissions.rolesStore.fetchRoles()
        } catch (error) {
          console.warn('Could not load roles in Layout:', error)
        }
      }
      
      
    });

    // Watcher para reaccionar cuando los roles se carguen
    watch(() => permissions.rolesStore.roles.length, async (newLength, oldLength) => {
      if (newLength > 0 && oldLength === 0) {
        console.log('🔄 Roles loaded, refreshing navigation...')
        
        // Forzar reactividad
        await nextTick()
        
        if (import.meta.env.DEV) {
          setTimeout(() => {
            console.log('🧭 Updated available routes:', permissions.availableRoutes.value)
            console.log('🎯 Updated valid nav items:', validNavItems.value)
          }, 50)
        }
      }
    })

    onUnmounted(() => {
      document.removeEventListener("click", closeUserMenu);
    });

    return {
      user: authStore.user,
      sidebarOpen: appStore.sidebarOpen,
      userMenuOpen,
      pageTitle,
      availableNavItems,
      validNavItems,
      getUserFullName,
      getUserInitials,
      toggleUserMenu,
      logout,
      toggleSidebar
    };
  }
};
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
  position: relative;
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.2s;
  border: 1px solid #e2e8f0;
}

.user-info:hover {
  background-color: #f8fafc;
}

.user-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: #2563eb;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 600;
  font-size: 14px;
}

.user-details {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.user-name {
  font-weight: 600;
  color: #1e293b;
  font-size: 14px;
  line-height: 1.2;
}

.user-role {
  font-size: 12px;
  color: #64748b;
  text-transform: capitalize;
}

.user-dropdown-icon {
  color: #64748b;
  font-size: 12px;
  transition: transform 0.2s;
}

.user-menu.open .user-dropdown-icon {
  transform: rotate(180deg);
}

.user-dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 8px;
  width: 280px;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  overflow: hidden;
}

.user-profile {
  padding: 0;
}

.profile-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 20px;
  background: linear-gradient(135deg, #2563eb, #4f46e5);
  color: white;
}

.profile-avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 600;
  font-size: 18px;
}

.profile-info {
  flex: 1;
}

.profile-name {
  font-weight: 600;
  font-size: 16px;
  margin-bottom: 4px;
}

.profile-email {
  font-size: 13px;
  opacity: 0.9;
}

.profile-details {
  padding: 16px 20px;
  border-bottom: 1px solid #e2e8f0;
}

.detail-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.detail-item:last-child {
  margin-bottom: 0;
}

.detail-label {
  font-size: 13px;
  color: #64748b;
  font-weight: 500;
}

.detail-value {
  font-size: 13px;
  color: #1e293b;
  font-weight: 500;
}

.profile-actions {
  padding: 16px 20px;
}

.profile-actions .btn {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 10px 16px;
  border-radius: 8px;
  font-weight: 500;
}

/* Responsive Design */
@media (max-width: 768px) {
  .user-details {
    display: none;
  }

  .user-dropdown {
    width: 260px;
    right: -40px;
  }

  .profile-header {
    padding: 16px;
  }

  .profile-details {
    padding: 12px 16px;
  }

  .profile-actions {
    padding: 12px 16px;
  }
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
