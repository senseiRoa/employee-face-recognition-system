<template>
  <div class="login-container">
    <div class="login-card">
      <div class="login-header">
        <h1>Admin Panel</h1>
        <p>Time Tracker System</p>
      </div>
      
      <form @submit.prevent="handleLogin" class="login-form">
        <div class="form-group">
          <label for="username" class="form-label">Username</label>
          <input
            id="username"
            v-model="form.username"
            type="text"
            class="form-control"
            :class="{ error: errors.username }"
            placeholder="Enter your username"
            required
          />
          <div v-if="errors.username" class="form-error">
            {{ errors.username }}
          </div>
        </div>

        <div class="form-group">
          <label for="password" class="form-label">Password</label>
          <input
            id="password"
            v-model="form.password"
            type="password"
            class="form-control"
            :class="{ error: errors.password }"
            placeholder="Enter your password"
            required
          />
          <div v-if="errors.password" class="form-error">
            {{ errors.password }}
          </div>
        </div>

        <div v-if="errors.general" class="alert alert-error">
          {{ errors.general }}
        </div>

        <button
          type="submit"
          class="btn btn-primary login-btn"
          :disabled="loading"
        >
          <span v-if="loading">Signing in...</span>
          <span v-else>Sign In</span>
        </button>
      </form>
    </div>
  </div>
</template>

<script>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'

export default {
  name: 'Login',
  setup() {
    const router = useRouter()
    const authStore = useAuthStore()
    
    const form = reactive({
      username: '',
      password: ''
    })
    
    const errors = reactive({
      username: '',
      password: '',
      general: ''
    })
    
    const loading = ref(false)

    const validateForm = () => {
      let isValid = true
      
      // Reset errors
      Object.keys(errors).forEach(key => {
        errors[key] = ''
      })

      if (!form.username.trim()) {
        errors.username = 'El usuario es requerido'
        isValid = false
      }

      if (!form.password.trim()) {
        errors.password = 'La contraseña es requerida'
        isValid = false
      } else if (form.password.length < 6) {
        errors.password = 'La contraseña debe tener al menos 6 caracteres'
        isValid = false
      }

      return isValid
    }

    const handleLogin = async () => {
      if (!validateForm()) {
        return
      }

      loading.value = true
      
      try {
        const result = await authStore.login({
          username: form.username,
          password: form.password
        })

        if (result.success) {
          router.push('/admin/dashboard')
        } else {
          errors.general = result.error
        }
      } catch (error) {
        errors.general = 'Error de conexión. Intenta nuevamente.'
      } finally {
        loading.value = false
      }
    }

    return {
      form,
      errors,
      loading,
      handleLogin
    }
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.login-card {
  background: var(--card-background);
  border-radius: 12px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  padding: 40px;
  width: 100%;
  max-width: 400px;
}

.login-header {
  text-align: center;
  margin-bottom: 32px;
}

.login-header h1 {
  color: var(--text-primary);
  margin: 0 0 8px 0;
  font-size: 28px;
  font-weight: 700;
}

.login-header p {
  color: var(--text-secondary);
  margin: 0;
  font-size: 16px;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.login-btn {
  padding: 14px;
  font-size: 16px;
  font-weight: 600;
  border-radius: 8px;
}

.alert {
  padding: 12px;
  border-radius: 6px;
  font-size: 14px;
}

.alert-error {
  background-color: rgba(239, 68, 68, 0.1);
  color: var(--error-color);
  border: 1px solid rgba(239, 68, 68, 0.2);
}

@media (max-width: 480px) {
  .login-card {
    padding: 24px;
  }
  
  .login-header h1 {
    font-size: 24px;
  }
}
</style>