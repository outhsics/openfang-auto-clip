<template>
  <div class="jobs">
    <el-card>
      <template #header>
        <div class="header">
          <h2>📋 Jobs</h2>
          <el-button @click="loadJobs" :loading="loading">
            <el-icon><Refresh /></el-icon> Refresh
          </el-button>
        </div>
      </template>

      <el-table :data="jobs" stripe>
        <el-table-column prop="id" label="Job ID" width="200" />
        <el-table-column prop="status" label="Status" width="120">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="level" label="Level" width="80" />
        <el-table-column prop="progress" label="Progress" width="150">
          <template #default="{ row }">
            <el-progress :percentage="row.progress" />
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="Created" width="180" />
        <el-table-column label="Actions" width="150">
          <template #default="{ row }">
            <el-button
              text
              type="primary"
              @click="viewJob(row.id)"
            >
              View
            </el-button>
            <el-button
              text
              type="danger"
              @click="deleteJob(row.id)"
            >
              Delete
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-empty v-if="jobs.length === 0" description="No jobs found" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import { listJobs, deleteJob as deleteJobApi } from '../api'

const router = useRouter()
const jobs = ref([])
const loading = ref(false)

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

const viewJob = (jobId) => {
  router.push(`/jobs/${jobId}`)
}

const deleteJob = async (jobId) => {
  try {
    await ElMessageBox.confirm('Are you sure you want to delete this job?', 'Warning', {
      type: 'warning'
    })

    await deleteJobApi(jobId)
    ElMessage.success('Job deleted successfully')
    await loadJobs()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(`Failed to delete job: ${error.message}`)
    }
  }
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

onMounted(() => {
  loadJobs()
  // Auto-refresh every 5 seconds
  setInterval(loadJobs, 5000)
})
</script>

<style scoped>
.jobs {
  max-width: 1200px;
  margin: 0 auto;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
