<template>
  <div class="process">
    <el-card>
      <template #header>
        <h2>🎬 Process Video/Transcript</h2>
      </template>

      <el-form :model="form" label-width="140px">
        <el-form-item label="Level">
          <el-radio-group v-model="form.level">
            <el-radio :label="1">Level 1 - Visual Remix</el-radio>
            <el-radio :label="2">Level 2 - Script Generation</el-radio>
            <el-radio :label="3">Level 3 - Complete Recreation</el-radio>
          </el-radio-group>
          <div class="level-description">
            {{ getLevelDescription(form.level) }}
          </div>
        </el-form-item>

        <el-form-item label="Input Type">
          <el-radio-group v-model="inputType">
            <el-radio label="upload">Upload File</el-radio>
            <el-radio label="local">Local File Path</el-radio>
            <el-radio label="url">Video URL</el-radio>
          </el-radio-group>
        </el-form-item>

        <!-- Upload File -->
        <el-form-item v-if="inputType === 'upload'" label="Transcript File">
          <el-upload
            ref="uploadRef"
            class="upload-demo"
            drag
            action="#"
            :auto-upload="false"
            :on-change="handleFileChange"
            :limit="1"
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

          <!-- Upload progress -->
          <div v-if="uploadProgress > 0 && uploadProgress < 100" class="upload-progress">
            <el-progress :percentage="uploadProgress" :status="uploadStatus" />
          </div>

          <!-- Uploaded file info -->
          <el-alert
            v-if="uploadedFile"
            type="success"
            :closable="false"
            style="margin-top: 10px;"
          >
            <template #title>
              ✅ File uploaded: {{ uploadedFile.filename }} ({{ formatFileSize(uploadedFile.size) }})
            </template>
          </el-alert>
        </el-form-item>

        <!-- Local File Path -->
        <el-form-item v-if="inputType === 'local'" label="File Path">
          <el-input
            v-model="form.transcript_path"
            placeholder="/path/to/transcript.srt"
            clearable
          />
          <div class="form-tip">
            Enter the absolute path to the transcript file on the server
          </div>
        </el-form-item>

        <!-- Video URL -->
        <el-form-item v-if="inputType === 'url'" label="Video URL">
          <el-input
            v-model="form.video_url"
            placeholder="https://www.youtube.com/watch?v=..."
            clearable
          />
          <div class="form-tip">
            Supports: YouTube, TikTok, and other video platforms
          </div>
        </el-form-item>

        <!-- Configuration -->
        <el-form-item label="Configuration">
          <el-card shadow="never">
            <el-form-item label="Content Type">
              <el-select
                v-model="form.config.content_type"
                placeholder="Auto-detect"
                style="width: 100%;"
              >
                <el-option label="🤖 Auto-detect" value="auto" />
                <el-option label="📚 Educational" value="educational" />
                <el-option label="🎬 Entertainment" value="entertainment" />
                <el-option label="📖 Tutorial" value="tutorial" />
                <el-option label="📝 General" value="general" />
              </el-select>
              <div class="form-tip">
                AI will automatically detect content type if set to "Auto-detect"
              </div>
            </el-form-item>

            <el-form-item label="Target Duration">
              <el-slider
                v-model="form.config.default_duration"
                :min="30"
                :max="300"
                :step="10"
                show-input
                :marks="{30: '30s', 60: '60s', 120: '2m', 180: '3m'}"
              />
              <div class="form-tip">
                Target duration for generated short video
              </div>
            </el-form-item>

            <el-form-item label="Output Format">
              <el-checkbox-group v-model="form.config.output_formats">
                <el-checkbox label="json">JSON Package</el-checkbox>
                <el-checkbox label="srt">SRT Subtitles</el-checkbox>
                <el-checkbox label="md">Markdown Script</el-checkbox>
              </el-checkbox-group>
            </el-form-item>
          </el-card>
        </el-form-item>

        <!-- Submit buttons -->
        <el-form-item>
          <el-button
            type="primary"
            size="large"
            @click="submitProcess"
            :loading="processing"
            :disabled="!canSubmit"
          >
            <el-icon v-if="!processing"><VideoCamera /></el-icon>
            {{ processing ? 'Processing...' : 'Start Processing' }}
          </el-button>
          <el-button size="large" @click="resetForm" :disabled="processing">
            Reset
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- Job Created Dialog -->
    <el-dialog v-model="showJobDialog" title="✅ Job Created" width="500px">
      <el-result icon="success" title="Processing Started">
        <template #sub-title>
          <p>Your job has been created and is being processed.</p>
          <el-descriptions :column="1" border style="margin-top: 20px;">
            <el-descriptions-item label="Job ID">
              <el-tag>{{ jobId }}</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="Level">{{ form.level }}</el-descriptions-item>
            <el-descriptions-item label="Status">
              <el-tag type="warning">Pending</el-tag>
            </el-descriptions-item>
          </el-descriptions>
        </template>
        <template #extra>
          <el-space wrap>
            <el-button type="primary" size="large" @click="goToJob">
              View Job Status
            </el-button>
            <el-button size="large" @click="showJobDialog = false">
              Close
            </el-button>
          </el-space>
        </template>
      </el-result>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { UploadFilled, VideoCamera } from '@element-plus/icons-vue'
import { processVideo, uploadFile } from '../api'

const router = useRouter()

const form = ref({
  level: 2,
  transcript_path: '',
  video_url: '',
  uploaded_file_id: '',
  config: {
    content_type: 'auto',
    default_duration: 60,
    output_formats: ['json']
  }
})

const inputType = ref('upload')
const processing = ref(false)
const showJobDialog = ref(false)
const jobId = ref('')
const uploadedFile = ref(null)
const uploadProgress = ref(0)
const uploadStatus = ref('success')
const uploadRef = ref(null)

const canSubmit = computed(() => {
  if (inputType.value === 'upload') {
    return uploadedFile.value !== null
  } else if (inputType.value === 'local') {
    return form.value.transcript_path.length > 0
  } else if (inputType.value === 'url') {
    return form.value.video_url.length > 0
  }
  return false
})

const getLevelDescription = (level) => {
  const descriptions = {
    1: '🎨 Visual remix with style transfer, speed adjustments, and effects',
    2: '✍️ AI-powered short-form script generation with visual direction',
    3: '🚀 Complete recreation with new narration and visuals'
  }
  return descriptions[level]
}

const handleFileChange = async (file) => {
  try {
    uploadProgress.value = 0
    uploadStatus.value = 'success'

    // Create FormData
    const formData = new FormData()
    formData.append('file', file.raw)

    // Upload file
    uploadProgress.value = 10
    const response = await uploadFile(formData)
    uploadProgress.value = 100

    uploadedFile.value = response.data
    form.value.uploaded_file_id = response.data.file_id

    ElMessage.success(`File uploaded: ${file.name}`)
  } catch (error) {
    uploadStatus.value = 'exception'
    ElMessage.error(`Upload failed: ${error.message}`)
    uploadedFile.value = null
  }
}

const submitProcess = async () => {
  try {
    processing.value = true

    const data = {
      level: form.value.level,
      config: form.value.config
    }

    if (inputType.value === 'upload') {
      data.uploaded_file_id = form.value.uploaded_file_id
    } else if (inputType.value === 'local') {
      data.transcript_path = form.value.transcript_path
    } else if (inputType.value === 'url') {
      data.video_url = form.value.video_url
    }

    const response = await processVideo(data)
    jobId.value = response.data.job_id
    showJobDialog.value = true

    ElMessage.success('Job created successfully!')
  } catch (error) {
    ElMessage.error(`Failed to create job: {error.message}`)
  } finally {
    processing.value = false
  }
}

const resetForm = () => {
  form.value = {
    level: 2,
    transcript_path: '',
    video_url: '',
    uploaded_file_id: '',
    config: {
      content_type: 'auto',
      default_duration: 60,
      output_formats: ['json']
    }
  }
  uploadedFile.value = null
  uploadProgress.value = 0

  if (uploadRef.value) {
    uploadRef.value.clearFiles()
  }
}

const goToJob = () => {
  router.push(`/jobs/{jobId.value}`)
  showJobDialog.value = false
}

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}
</script>

<style scoped>
.process {
  max-width: 900px;
  margin: 0 auto;
}

.level-description {
  margin-top: 8px;
  font-size: 14px;
  color: #606266;
  line-height: 1.5;
}

.upload-demo {
  width: 100%;
}

.el-icon--upload {
  font-size: 67px;
  color: #409eff;
  margin: 20px 0;
}

.el-upload__text {
  font-size: 16px;
  color: #606266;
}

.el-upload__text em {
  color: #409eff;
  font-style: normal;
}

.el-upload__tip {
  font-size: 12px;
  color: #909399;
  margin-top: 7px;
}

.upload-progress {
  margin-top: 15px;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
  line-height: 1.4;
}
</style>
