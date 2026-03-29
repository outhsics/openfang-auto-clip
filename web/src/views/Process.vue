<template>
  <div class="process">
    <el-card>
      <template #header>
        <h2>🎬 Process Video/Transcript</h2>
      </template>

      <el-form :model="form" label-width="120px">
        <el-form-item label="Level">
          <el-radio-group v-model="form.level">
            <el-radio :label="1">Level 1 - Visual Remix</el-radio>
            <el-radio :label="2">Level 2 - Script Generation</el-radio>
            <el-radio :label="3">Level 3 - Complete Recreation</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="Input Type">
          <el-radio-group v-model="inputType">
            <el-radio label="transcript">Transcript File</el-radio>
            <el-radio label="url">Video URL</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item v-if="inputType === 'transcript'" label="Transcript File">
          <el-upload
            drag
            action="#"
            :auto-upload="false"
            @change="handleFileChange"
            accept=".srt,.vtt,.txt"
          >
            <el-icon class="el-icon--upload"><upload-filled /></el-icon>
            <div class="el-upload__text">
              Drop transcript file here or <em>click to upload</em>
            </div>
            <template #tip>
              <div class="el-upload__tip">
                Supported formats: SRT, VTT, TXT (max 100MB)
              </div>
            </template>
          </el-upload>
        </el-form-item>

        <el-form-item v-if="inputType === 'url'" label="Video URL">
          <el-input
            v-model="form.video_url"
            placeholder="https://www.youtube.com/watch?v=..."
            clearable
          />
        </el-form-item>

        <el-form-item label="Configuration">
          <el-card>
            <el-form-item label="Content Type">
              <el-select v-model="form.config.content_type" placeholder="Auto-detect">
                <el-option label="Auto-detect" value="auto" />
                <el-option label="Educational" value="educational" />
                <el-option label="Entertainment" value="entertainment" />
                <el-option label="Tutorial" value="tutorial" />
                <el-option label="General" value="general" />
              </el-select>
            </el-form-item>

            <el-form-item label="Duration (seconds)">
              <el-input-number v-model="form.config.default_duration" :min="30" :max="300" />
            </el-form-item>
          </el-card>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="submitProcess" :loading="processing">
            Start Processing
          </el-button>
          <el-button @click="resetForm">Reset</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- Job Created Dialog -->
    <el-dialog v-model="showJobDialog" title="Job Created" width="500px">
      <el-result icon="success" title="Processing Started">
        <template #sub-title>
          <p>Your job has been created and is being processed.</p>
          <p><strong>Job ID:</strong> {{ jobId }}</p>
        </template>
        <template #extra>
          <el-button type="primary" @click="goToJob">View Job Status</el-button>
          <el-button @click="showJobDialog = false">Close</el-button>
        </template>
      </el-result>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'
import { processVideo } from '../api'

const router = useRouter()

const form = ref({
  level: 2,
  transcript_path: '',
  video_url: '',
  config: {
    content_type: 'auto',
    default_duration: 60
  }
})

const inputType = ref('transcript')
const processing = ref(false)
const showJobDialog = ref(false)
const jobId = ref('')

const handleFileChange = (file) => {
  form.value.transcript_path = file.name
  ElMessage.success(`File selected: ${file.name}`)
}

const submitProcess = async () => {
  try {
    processing.value = true

    const data = {
      level: form.value.level,
      config: form.value.config
    }

    if (inputType.value === 'transcript') {
      data.transcript_path = form.value.transcript_path
    } else {
      data.video_url = form.value.video_url
    }

    const response = await processVideo(data)
    jobId.value = response.data.job_id
    showJobDialog.value = true

    ElMessage.success('Job created successfully!')
  } catch (error) {
    ElMessage.error(`Failed to create job: ${error.message}`)
  } finally {
    processing.value = false
  }
}

const resetForm = () => {
  form.value = {
    level: 2,
    transcript_path: '',
    video_url: '',
    config: {
      content_type: 'auto',
      default_duration: 60
    }
  }
}

const goToJob = () => {
  router.push(`/jobs/${jobId.value}`)
}
</script>

<style scoped>
.process {
  max-width: 800px;
  margin: 0 auto;
}
</style>
