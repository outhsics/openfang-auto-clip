<template>
  <div class="jobs">
    <el-card>
      <template #header>
        <div class="header">
          <h2>📋 Jobs</h2>
          <el-space>
            <el-button @click="loadJobs" :loading="loading">
              <el-icon><Refresh /></el-icon> Refresh
            </el-button>
            <el-button @click="clearFilters" v-if="hasFilters">
              Clear Filters
            </el-button>
          </el-space>
        </div>
      </template>

      <!-- Filters -->
      <div class="filters">
        <el-row :gutter="20">
          <el-col :xs="24" :sm="8" :md="6">
            <el-select
              v-model="filters.status"
              placeholder="All Statuses"
              clearable
              @change="applyFilters"
              style="width: 100%;"
            >
              <el-option label="All Statuses" value="" />
              <el-option label="Pending" value="pending" />
              <el-option label="Processing" value="processing" />
              <el-option label="Completed" value="completed" />
              <el-option label="Failed" value="failed" />
            </el-select>
          </el-col>

          <el-col :xs="24" :sm="8" :md="6">
            <el-select
              v-model="filters.level"
              placeholder="All Levels"
              clearable
              @change="applyFilters"
              style="width: 100%;"
            >
              <el-option label="All Levels" value="" />
              <el-option label="Level 1" :value="1" />
              <el-option label="Level 2" :value="2" />
              <el-option label="Level 3" :value="3" />
            </el-select>
          </el-col>

          <el-col :xs="24" :sm="8" :md="6">
            <el-select
              v-model="sortBy"
              placeholder="Sort by"
              @change="applyFilters"
              style="width: 100%;"
            >
              <el-option label="Created (Newest)" value="created_desc" />
              <el-option label="Created (Oldest)" value="created_asc" />
              <el-option label="Progress (High-Low)" value="progress_desc" />
              <el-option label="Progress (Low-High)" value="progress_asc" />
            </el-select>
          </el-col>

          <el-col :xs="24" :sm="24" :md="6">
            <el-input
              v-model="searchQuery"
              placeholder="Search jobs..."
              clearable
              @input="applyFilters"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
          </el-col>
        </el-row>
      </div>

      <!-- Stats -->
      <div class="stats" v-if="jobs.length > 0">
        <el-space :size="20">
          <div class="stat-item">
            <span class="stat-label">Total:</span>
            <span class="stat-value">{{ filteredJobs.length }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">Pending:</span>
            <span class="stat-value">{{ statusCounts.pending }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">Processing:</span>
            <span class="stat-value">{{ statusCounts.processing }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">Completed:</span>
            <span class="stat-value">{{ statusCounts.completed }}</span>
          </div>
          <div class="stat-item">
            <span class="stat-label">Failed:</span>
            <span class="stat-value">{{ statusCounts.failed }}</span>
          </div>
        </el-space>
      </div>

      <!-- Jobs Table -->
      <el-table :data="filteredJobs" stripe v-loading="loading">
        <el-table-column prop="id" label="Job ID" width="200">
          <template #default="{ row }">
            <el-tag size="small">{{ row.id.substring(0, 8) }}...</el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="status" label="Status" width="120">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)" effect="dark">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="level" label="Level" width="100">
          <template #default="{ row }">
            <el-tag type="info">L{{ row.level }}</el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="progress" label="Progress" width="180">
          <template #default="{ row }">
            <el-progress
              :percentage="row.progress"
              :status="row.progress === 100 ? 'success' : ''"
              :stroke-width="8"
            />
          </template>
        </el-table-column>

        <el-table-column prop="created_at" label="Created" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>

        <el-table-column label="Actions" width="200" fixed="right">
          <template #default="{ row }">
            <el-space>
              <el-button
                size="small"
                type="primary"
                @click="viewJob(row.id)"
              >
                <el-icon><View /></el-icon> View
              </el-button>
              <el-button
                size="small"
                type="success"
                v-if="row.status === 'completed'"
                @click="downloadResult(row)"
              >
                <el-icon><Download /></el-icon>
              </el-button>
              <el-button
                size="small"
                type="danger"
                @click="deleteJob(row.id)"
              >
                <el-icon><Delete /></el-icon>
              </el-button>
            </el-space>
          </template>
        </el-table-column>
      </el-table>

      <!-- Empty State -->
      <el-empty
        v-if="jobs.length === 0"
        description="No jobs found"
      >
        <el-button type="primary" @click="$router.push('/process')">
          Create Your First Job
        </el-button>
      </el-empty>

      <el-empty
        v-else-if="filteredJobs.length === 0"
        description="No jobs match your filters"
      >
        <el-button @click="clearFilters">Clear Filters</el-button>
      </el-empty>

      <!-- Batch Actions -->
      <div class="batch-actions" v-if="selectedJobs.length > 0">
        <el-card>
          <div class="batch-content">
            <span>{{ selectedJobs.length }} jobs selected</span>
            <el-space>
              <el-button size="small" @click="batchDelete" type="danger">
                Delete Selected
              </el-button>
              <el-button size="small" @click="clearSelection">
                Clear Selection
              </el-button>
            </el-space>
          </div>
        </el-card>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh, Search, View, Download, Delete } from '@element-plus/icons-vue'
import { listJobs, deleteJob as deleteJobApi } from '../api'

const router = useRouter()

const jobs = ref([])
const loading = ref(false)
const searchQuery = ref('')
const sortBy = ref('created_desc')
const selectedJobs = ref([])

const filters = ref({
  status: '',
  level: ''
})

const hasFilters = computed(() => {
  return filters.value.status || filters.value.level || searchQuery.value
})

const filteredJobs = computed(() => {
  let result = [...jobs.value]

  // Apply status filter
  if (filters.value.status) {
    result = result.filter(job => job.status === filters.value.status)
  }

  // Apply level filter
  if (filters.value.level !== '') {
    result = result.filter(job => job.level === filters.value.level)
  }

  // Apply search filter
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(job =>
      job.id.toLowerCase().includes(query) ||
      job.status.toLowerCase().includes(query)
    )
  }

  // Apply sorting
  result.sort((a, b) => {
    switch (sortBy.value) {
      case 'created_desc':
        return new Date(b.created_at) - new Date(a.created_at)
      case 'created_asc':
        return new Date(a.created_at) - new Date(b.created_at)
      case 'progress_desc':
        return b.progress - a.progress
      case 'progress_asc':
        return a.progress - b.progress
      default:
        return 0
    }
  })

  return result
})

const statusCounts = computed(() => {
  const counts = {
    pending: 0,
    processing: 0,
    completed: 0,
    failed: 0
  }

  filteredJobs.value.forEach(job => {
    if (counts.hasOwnProperty(job.status)) {
      counts[job.status]++
    }
  })

  return counts
})

let refreshInterval = null

const loadJobs = async () => {
  try {
    loading.value = true
    const response = await listJobs()
    jobs.value = response.data
  } catch (error) {
    ElMessage.error(`Failed to load jobs: ${error.message}`)
  } finally {
    loading.value = false
  }
}

const applyFilters = () => {
  // Filters are applied via computed property
}

const clearFilters = () => {
  filters.value.status = ''
  filters.value.level = ''
  searchQuery.value = ''
  sortBy.value = 'created_desc'
}

const viewJob = (jobId) => {
  router.push(`/jobs/${jobId}`)
}

const downloadResult = (job) => {
  // TODO: Implement result download
  ElMessage.info('Download feature coming soon!')
}

const deleteJob = async (jobId) => {
  try {
    await ElMessageBox.confirm(
      'Are you sure you want to delete this job? This action cannot be undone.',
      'Warning',
      {
        type: 'warning',
        confirmButtonText: 'Delete',
        cancelButtonText: 'Cancel'
      }
    )

    await deleteJobApi(jobId)
    ElMessage.success('Job deleted successfully')
    await loadJobs()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(`Failed to delete job: ${error.message}`)
    }
  }
}

const batchDelete = async () => {
  try {
    await ElMessageBox.confirm(
      `Are you sure you want to delete ${selectedJobs.value.length} jobs? This action cannot be undone.`,
      'Warning',
      {
        type: 'warning',
        confirmButtonText: 'Delete All',
        cancelButtonText: 'Cancel'
      }
    )

    for (const jobId of selectedJobs.value) {
      await deleteJobApi(jobId)
    }

    ElMessage.success(`${selectedJobs.value.length} jobs deleted successfully`)
    selectedJobs.value = []
    await loadJobs()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(`Failed to delete jobs: ${error.message}`)
    }
  }
}

const clearSelection = () => {
  selectedJobs.value = []
}

const getStatusType = (status) => {
  const types = {
    pending: 'info',
    processing: 'warning',
    completed: 'success',
    failed: 'danger'
  }
  return types[status] || 'info'
}

const formatDate = (dateString) => {
  const date = new Date(dateString)
  const now = new Date()
  const diff = now - date

  // Less than 1 minute
  if (diff < 60000) {
    return 'Just now'
  }

  // Less than 1 hour
  if (diff < 3600000) {
    const minutes = Math.floor(diff / 60000)
    return `${minutes}m ago`
  }

  // Less than 1 day
  if (diff < 86400000) {
    const hours = Math.floor(diff / 3600000)
    return `${hours}h ago`
  }

  // Less than 1 week
  if (diff < 604800000) {
    const days = Math.floor(diff / 86400000)
    return `${days}d ago`
  }

  // Format date
  return date.toLocaleDateString()
}

onMounted(() => {
  loadJobs()
  // Auto-refresh every 5 seconds
  refreshInterval = setInterval(loadJobs, 5000)
})

onUnmounted(() => {
  if (refreshInterval) {
    clearInterval(refreshInterval)
  }
})
</script>

<style scoped>
.jobs {
  max-width: 1400px;
  margin: 0 auto;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.filters {
  margin-bottom: 20px;
  padding: 15px;
  background: #f5f7fa;
  border-radius: 4px;
}

.stats {
  margin-bottom: 20px;
  padding: 15px;
  background: #ecf5ff;
  border-radius: 4px;
  border: 1px solid #d9ecff;
}

.stat-item {
  display: inline-flex;
  align-items: center;
  gap: 5px;
}

.stat-label {
  font-size: 14px;
  color: #606266;
  font-weight: 500;
}

.stat-value {
  font-size: 16px;
  color: #409eff;
  font-weight: bold;
}

.batch-actions {
  position: fixed;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 1000;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.15);
}

.batch-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

@media (max-width: 768px) {
  .filters .el-col {
    margin-bottom: 10px;
  }

  .stats {
    font-size: 12px;
  }

  .batch-actions {
    width: 90%;
  }
}
</style>
