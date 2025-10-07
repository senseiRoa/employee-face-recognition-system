<template>
  <div class="companies">
    <div class="page-header">
      <h2>Company Management</h2>
      <button @click="showCreateModal = true" class="btn btn-primary">
        <span>➕</span>
        New Company
      </button>
    </div>

    <!-- Filters -->
    <div class="filters">
      <div class="search-box">
        <input
          v-model="searchTerm"
          type="text"
          placeholder="Search companies..."
          class="form-control"
        />
      </div>
    </div>

    <!-- Companies table -->
    <div class="table-container">
      <table class="table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Email</th>
            <th>Phone</th>
            <th>Status</th>
            <th>Created At</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading">
            <td colspan="7" class="text-center">Loading...</td>
          </tr>
          <tr v-else-if="filteredCompanies.length === 0">
            <td colspan="7" class="text-center">No companies registered</td>
          </tr>
          <tr v-else v-for="company in filteredCompanies" :key="company.id">
            <td>{{ company.id }}</td>
            <td>{{ company.name }}</td>
            <td>{{ company.email || '-' }}</td>
            <td>{{ company.phone || '-' }}</td>
            <td>
              <span class="status-badge" :class="company.status ? 'active' : 'inactive'">
                {{ company.status ? 'Active' : 'Inactive' }}
              </span>
            </td>
            <td>{{ formatDate(company.created_at) }}</td>
            <td>
              <div class="action-buttons">
                <button
                  @click="editCompany(company)"
                  class="btn btn-outline btn-sm"
                  title="Edit"
                >
                  ✏️
                </button>
                <button
                  @click="deleteCompanyConfirm(company)"
                  class="btn btn-danger btn-sm"
                  title="Delete"
                >
                  🗑️
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Create/Edit company modal -->
    <div v-if="showCreateModal || showEditModal" class="modal-overlay" @click.self="closeModals">
      <div class="modal">
        <div class="modal-header">
          <h3>{{ editingCompany ? 'Edit Company' : 'New Company' }}</h3>
          <button @click="closeModals" class="btn btn-outline">✕</button>
        </div>
        
        <form @submit.prevent="saveCompany" class="modal-body">
          <div class="form-group">
            <label class="form-label">Name *</label>
            <input
              v-model="companyForm.name"
              type="text"
              class="form-control"
              :class="{ error: errors.name }"
              required
            />
            <div v-if="errors.name" class="form-error">{{ errors.name }}</div>
          </div>

          <div class="form-group">
            <label class="form-label">Email</label>
            <input
              v-model="companyForm.email"
              type="email"
              class="form-control"
              :class="{ error: errors.email }"
            />
            <div v-if="errors.email" class="form-error">{{ errors.email }}</div>
          </div>

          <div class="form-group">
            <label class="form-label">Phone</label>
            <input
              v-model="companyForm.phone"
              type="tel"
              class="form-control"
              :class="{ error: errors.phone }"
            />
            <div v-if="errors.phone" class="form-error">{{ errors.phone }}</div>
          </div>

          <div class="form-group">
            <label class="form-label">Address</label>
            <textarea
              v-model="companyForm.address"
              class="form-control"
              rows="3"
            ></textarea>
          </div>

          <div class="form-group">
            <label class="checkbox-label">
              <input
                v-model="companyForm.status"
                type="checkbox"
              />
              <span>Active company</span>
            </label>
          </div>
        </form>
        
        <div class="modal-footer">
          <button @click="closeModals" type="button" class="btn btn-outline">
            Cancel
          </button>
          <button @click="saveCompany" type="submit" class="btn btn-primary" :disabled="loading">
            {{ loading ? 'Saving...' : 'Save' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Delete confirmation modal -->
    <div v-if="showDeleteModal" class="modal-overlay" @click.self="showDeleteModal = false">
      <div class="modal modal-sm">
        <div class="modal-header">
          <h3>Confirm Deletion</h3>
        </div>
        
        <div class="modal-body">
          <p>Are you sure you want to delete the company <strong>{{ companyToDelete?.name }}</strong>?</p>
          <p class="text-warning">This action cannot be undone.</p>
          <div v-if="deleteError" class="alert alert-error">
            {{ deleteError }}
          </div>
        </div>
        
        <div class="modal-footer">
          <button @click="showDeleteModal = false" class="btn btn-outline">
            Cancel
          </button>
          <button @click="confirmDelete" class="btn btn-danger" :disabled="loading">
            {{ loading ? 'Deleting...' : 'Delete' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted } from 'vue'
import { useCompanies } from '@/composables/useCompanies'
import { format } from 'date-fns'

export default {
  name: 'Companies',
  setup() {
    const {
      companies,
      loading,
      fetchCompanies,
      createCompany,
      updateCompany,
      deleteCompany
    } = useCompanies()

    const searchTerm = ref('')
    const showCreateModal = ref(false)
    const showEditModal = ref(false)
    const showDeleteModal = ref(false)
    const editingCompany = ref(null)
    const companyToDelete = ref(null)
    const deleteError = ref('')

    const companyForm = reactive({
      name: '',
      email: '',
      phone: '',
      address: '',
      status: true
    })

    const errors = reactive({
      name: '',
      email: '',
      phone: ''
    })

    const filteredCompanies = computed(() => {
      if (!searchTerm.value) {
        return companies.value
      }
      
      const term = searchTerm.value.toLowerCase()
      return companies.value.filter(company => 
        company.name.toLowerCase().includes(term) ||
        (company.email && company.email.toLowerCase().includes(term))
      )
    })

    const resetForm = () => {
      Object.assign(companyForm, {
        name: '',
        email: '',
        phone: '',
        address: '',
        status: true
      })
      
      Object.keys(errors).forEach(key => {
        errors[key] = ''
      })
    }

    const validateForm = () => {
      let isValid = true
      
      Object.keys(errors).forEach(key => {
        errors[key] = ''
      })

      if (!companyForm.name.trim()) {
        errors.name = 'Company name is required'
        isValid = false
      }

      if (companyForm.email && !isValidEmail(companyForm.email)) {
        errors.email = 'Invalid email format'
        isValid = false
      }

      return isValid
    }

    const isValidEmail = (email) => {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
      return emailRegex.test(email)
    }

    const editCompany = (company) => {
      editingCompany.value = company
      Object.assign(companyForm, {
        name: company.name,
        email: company.email || '',
        phone: company.phone || '',
        address: company.address || '',
        status: company.status
      })
      showEditModal.value = true
    }

    const deleteCompanyConfirm = (company) => {
      companyToDelete.value = company
      deleteError.value = ''
      showDeleteModal.value = true
    }

    const confirmDelete = async () => {
      if (!companyToDelete.value) return
      
      deleteError.value = ''
      const result = await deleteCompany(companyToDelete.value.id)
      if (result.success) {
        showDeleteModal.value = false
        companyToDelete.value = null
      } else {
        // Show error message from API - composable already extracts detail
        deleteError.value = result.error || 'Error deleting company'
      }
    }

    const saveCompany = async () => {
      if (!validateForm()) {
        return
      }

      const companyData = { ...companyForm }
      let result

      if (editingCompany.value) {
        result = await updateCompany(editingCompany.value.id, companyData)
      } else {
        result = await createCompany(companyData)
      }

      if (result.success) {
        closeModals()
      }
    }

    const closeModals = () => {
      showCreateModal.value = false
      showEditModal.value = false
      editingCompany.value = null
      resetForm()
    }

    const formatDate = (dateString) => {
      if (!dateString) return '-'
      try {
        return format(new Date(dateString), 'MMM dd, yyyy')
      } catch {
        return '-'
      }
    }

    onMounted(() => {
      fetchCompanies()
    })

    return {
      companies,
      loading,
      searchTerm,
      filteredCompanies,
      showCreateModal,
      showEditModal,
      showDeleteModal,
      editingCompany,
      companyToDelete,
      companyForm,
      errors,
      deleteError,
      editCompany,
      deleteCompanyConfirm,
      confirmDelete,
      saveCompany,
      closeModals,
      formatDate
    }
  }
}
</script>

<style scoped>
.companies {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.page-header {
  display: flex;
  justify-content: between;
  align-items: center;
  gap: 16px;
}

.page-header h2 {
  margin: 0;
  color: var(--text-primary);
  font-size: 24px;
  font-weight: 600;
}

.filters {
  display: flex;
  gap: 16px;
  align-items: center;
}

.search-box {
  flex: 1;
  max-width: 400px;
}

.table-container {
  background: var(--card-background);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.action-buttons {
  display: flex;
  gap: 8px;
}

.btn-sm {
  padding: 4px 8px;
  font-size: 12px;
}

.status-badge {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.status-badge.active {
  background: rgba(16, 185, 129, 0.1);
  color: var(--success-color);
}

.status-badge.inactive {
  background: rgba(239, 68, 68, 0.1);
  color: var(--error-color);
}

.modal-sm {
  max-width: 400px;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
  cursor: pointer;
}

.checkbox-label input[type="checkbox"] {
  margin: 0;
}

.alert {
  padding: 12px 16px;
  border-radius: 6px;
  margin-top: 12px;
  font-size: 14px;
}

.alert-error {
  background: rgba(239, 68, 68, 0.1);
  color: var(--error-color);
  border: 1px solid rgba(239, 68, 68, 0.2);
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: stretch;
  }
  
  .filters {
    flex-direction: column;
    align-items: stretch;
  }
  
  .search-box {
    max-width: none;
  }
  
  .table-container {
    overflow-x: auto;
  }
  
  .action-buttons {
    flex-direction: column;
  }
}
</style>