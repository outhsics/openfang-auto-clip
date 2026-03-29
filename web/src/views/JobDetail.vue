<template>
  <div class="job-detail">
    <el-card v-if="!loading && job">
      <template #header>
        <div class="header">
          <h2>Job {{ $route.params.id }}</h2>
          <el-button @click="$router.push('/jobs')">Back to Jobs</el-button>
        </div>
      </template>

      <el-descriptions :column="2" border>
        <el-descriptions-item label="Status">
          <el-tag :type="getStatusType(job.status)">
            {{ job.status }}
          </el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="Level">{{ job.level }}</el-descriptions-item>
        <el-descriptions-item label="Progress">
          <el-progress :percentage="job.progress" />
        </el-descriptions-item>
        <el-descriptions-item label="Created">{{ job.created_at }}</el-descriptions-item>
        <el-descriptions-item label="Updated">{{ job.updated_at }}</el-descriptions-item>
      </el-descriptions>

      <el-divider />

      <div v-if="job.status === 'completed' && job.result">
        <h3>Result</h3>
        <el-card>
          <pre>{{ JSON.stringify(job.result, null, 2) }}</pre>
        </el-card>
      </div>

      <div v-if="job.status === 'failed' && job.error">
        <h3>Error</h3>
        <el-alert type="error" :title="job.error" :closable="false" />
      </div>
    </el-card>

    <el-skeleton v-if="loading" :rows="10" animated />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getJob } from '../api'

const route = useRoute()
const job = ref(null)
const loading = ref(false)

const loadJob = async () => {
  try {
    loading.value = true
    const response = await getJob(route.params.id)
    job.value = response.data
  } catch (error) {
    ElMessage.error(`Failed to load job: ${error.message}`)
  } finally {
    loading.value = false
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
  loadJob()
  // Auto-refresh every 3 seconds if job is processing
  const interval = setInterval(() => {
    if (job.value && job.value.status === 'processing') {
      loadJob()
    } else {
      clearInterval(interval)
    }
  }, 3000)
})
</script>

<style scoped>
.job-detail {
  max-width: 1000px;
  margin: 0 auto;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

pre {
  background: #f5f7fa;
  padding: 15px;
  border-radius: 4px;
  overflow-x: auto;
}
</style>
