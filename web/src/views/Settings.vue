<template>
  <div class="settings">
    <el-card>
      <template #header>
        <h2>⚙️ Settings</h2>
      </template>

      <el-tabs v-model="activeTab">
        <!-- General Settings -->
        <el-tab-pane label="General" name="general">
          <el-form :model="settings" label-width="200px">
            <el-form-item label="Default Level">
              <el-radio-group v-model="settings.defaultLevel">
                <el-radio :label="1">Level 1 - Visual Remix</el-radio>
                <el-radio :label="2">Level 2 - Script Generation</el-radio>
                <el-radio :label="3">Level 3 - Complete Recreation</el-radio>
              </el-radio-group>
              <div class="form-tip">
                Default transformation level for new jobs
              </div>
            </el-form-item>

            <el-form-item label="Default Duration">
              <el-slider
                v-model="settings.defaultDuration"
                :min="15"
                :max="300"
                :step="15"
                show-input
                :marks="{15: '15s', 30: '30s', 60: '60s', 120: '2m', 180: '3m'}"
              />
              <div class="form-tip">
                Default target duration for generated videos
              </div>
            </el-form-item>

            <el-form-item label="Auto-validate">
              <el-switch v-model="settings.autoValidate" />
              <div class="form-tip">
                Automatically validate packages after processing
              </div>
            </el-form-item>

            <el-form-item label="Auto-backup">
              <el-switch v-model="settings.autoBackup" />
              <div class="form-tip">
                Automatically create backups before processing
              </div>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <!-- Platform Settings -->
        <el-tab-pane label="Platforms" name="platforms">
          <el-form :model="platforms" label-width="200px">
            <el-form-item label="Default Platform">
              <el-radio-group v-model="platforms.default">
                <el-radio-button label="youtube">YouTube</el-radio-button>
                <el-radio-button label="tiktok">TikTok</el-radio-button>
                <el-radio-button label="instagram">Instagram</el-radio-button>
                <el-radio-button label="generic">Generic</el-radio-button>
              </el-radio-group>
            </el-form-item>

            <el-form-item label="YouTube Settings">
              <el-card shadow="never">
                <el-form-item label="Default Duration">
                  <el-select v-model="platforms.youtube.duration">
                    <el-option label="60 seconds" :value="60" />
                    <el-option label="120 seconds" :value="120" />
                    <el-option label="180 seconds" :value="180" />
                  </el-select>
                </el-form-item>
                <el-form-item label="Aspect Ratio">
                  <el-select v-model="platforms.youtube.aspectRatio">
                    <el-option label="16:9 (Horizontal)" value="16:9" />
                    <el-option label="9:16 (Vertical)" value="9:16" />
                  </el-select>
                </el-form-item>
              </el-card>
            </el-form-item>

            <el-form-item label="TikTok Settings">
              <el-card shadow="never">
                <el-form-item label="Default Duration">
                  <el-select v-model="platforms.tiktok.duration">
                    <el-option label="15 seconds" :value="15" />
                    <el-option label="30 seconds" :value="30" />
                    <el-option label="60 seconds" :value="60" />
                  </el-select>
                </el-form-item>
                <el-form-item label="Aspect Ratio">
                  <el-select v-model="platforms.tiktok.aspectRatio">
                    <el-option label="9:16 (Vertical)" value="9:16" />
                    <el-option label="1:1 (Square)" value="1:1" />
                  </el-select>
                </el-form-item>
              </el-card>
            </el-form-item>

            <el-form-item label="Instagram Settings">
              <el-card shadow="never">
                <el-form-item label="Default Duration">
                  <el-select v-model="platforms.instagram.duration">
                    <el-option label="30 seconds" :value="30" />
                    <el-option label="60 seconds" :value="60" />
                    <el-option label="90 seconds" :value="90" />
                  </el-select>
                </el-form-item>
                <el-form-item label="Format">
                  <el-select v-model="platforms.instagram.format">
                    <el-option label="Reels" value="reels" />
                    <el-option label="Stories" value="stories" />
                  </el-select>
                </el-form-item>
              </el-card>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <!-- Quality Settings -->
        <el-tab-pane label="Quality" name="quality">
          <el-form :model="quality" label-width="200px">
            <el-form-item label="Quality Level">
              <el-radio-group v-model="quality.level">
                <el-radio-button label="fast">Fast</el-radio-button>
                <el-radio-button label="balanced">Balanced</el-radio-button>
                <el-radio-button label="quality">Quality</el-radio-button>
              </el-radio-group>
              <div class="form-tip">
                Trade-off between processing speed and output quality
              </div>
            </el-form-item>

            <el-form-item label="Minimum Quality Score">
              <el-slider
                v-model="quality.minScore"
                :min="0"
                :max="10"
                :step="0.5"
                show-input
                :marks="{5: '5.0', 7: '7.0', 9: '9.0'}"
              />
              <div class="form-tip">
                Packages below this score will trigger a warning
              </div>
            </el-form-item>

            <el-form-item label="Copyright Check">
              <el-switch v-model="quality.copyrightCheck" />
              <div class="form-tip">
                Enable copyright risk assessment
              </div>
            </el-form-item>

            <el-form-item label="Strict Mode">
              <el-switch v-model="quality.strictMode" />
              <div class="form-tip">
                Reject packages that don't meet quality standards
              </div>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <!-- Output Settings -->
        <el-tab-pane label="Output" name="output">
          <el-form :model="output" label-width="200px">
            <el-form-item label="Output Formats">
              <el-checkbox-group v-model="output.formats">
                <el-checkbox label="json">JSON Package</el-checkbox>
                <el-checkbox label="srt">SRT Subtitles</el-checkbox>
                <el-checkbox label="md">Markdown Script</el-checkbox>
                <el-checkbox label="txt">Plain Text</el-checkbox>
              </el-checkbox-group>
            </el-form-item>

            <el-form-item label="Output Directory">
              <el-input v-model="output.directory" placeholder="~/.openfang/clips" clearable />
              <div class="form-tip">
                Directory where generated files will be saved
              </div>
            </el-form-item>

            <el-form-item label="Filename Template">
              <el-input v-model="output.filenameTemplate" placeholder="{title}_{level}_{timestamp}" clearable />
              <div class="form-tip">
                Variables: {title}, {level}, {platform}, {timestamp}, {date}
              </div>
            </el-form-item>

            <el-form-item label="Auto-generate Captions">
              <el-switch v-model="output.autoCaptions" />
              <div class="form-tip">
                Automatically generate captions for videos
              </div>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <!-- Advanced Settings -->
        <el-tab-pane label="Advanced" name="advanced">
          <el-form label-width="200px">
            <el-form-item label="Max Concurrent Jobs">
              <el-input-number v-model="advanced.maxJobs" :min="1" :max="10" />
              <div class="form-tip">
                Maximum number of jobs to process simultaneously
              </div>
            </el-form-item>

            <el-form-item label="Job Timeout">
              <el-input-number v-model="advanced.timeout" :min="60" :max="3600" :step="60" />
              <span style="margin-left: 10px;">seconds</span>
              <div class="form-tip">
                Maximum time to wait for job completion
              </div>
            </el-form-item>

            <el-form-item label="Retry Attempts">
              <el-input-number v-model="advanced.retries" :min="0" :max="5" />
              <div class="form-tip">
                Number of times to retry failed operations
              </div>
            </el-form-item>

            <el-form-item label="Debug Mode">
              <el-switch v-model="advanced.debug" />
              <div class="form-tip">
                Enable detailed logging for troubleshooting
              </div>
            </el-form-item>

            <el-form-item label="Telemetry">
              <el-switch v-model="advanced.telemetry" />
              <div class="form-tip">
                Share anonymous usage data to improve the product
              </div>
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>

      <!-- Actions -->
      <div class="settings-actions">
        <el-space>
          <el-button type="primary" @click="saveSettings">Save Settings</el-button>
          <el-button @click="resetSettings">Reset to Defaults</el-button>
          <el-button @click="exportSettings">Export Settings</el-button>
          <el-button @click="importSettings">Import Settings</el-button>
        </el-space>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'

const activeTab = ref('general')

const settings = ref({
  defaultLevel: 2,
  defaultDuration: 60,
  autoValidate: true,
  autoBackup: true
})

const platforms = ref({
  default: 'youtube',
  youtube: {
    duration: 60,
    aspectRatio: '16:9'
  },
  tiktok: {
    duration: 15,
    aspectRatio: '9:16'
  },
  instagram: {
    duration: 30,
    format: 'reels'
  }
})

const quality = ref({
  level: 'balanced',
  minScore: 7.0,
  copyrightCheck: true,
  strictMode: false
})

const output = ref({
  formats: ['json', 'srt'],
  directory: '~/.openfang/clips',
  filenameTemplate: '{title}_{level}_{timestamp}',
  autoCaptions: true
})

const advanced = ref({
  maxJobs: 3,
  timeout: 300,
  retries: 3,
  debug: false,
  telemetry: false
})

const saveSettings = () => {
  // Save settings to localStorage
  const config = {
    settings: settings.value,
    platforms: platforms.value,
    quality: quality.value,
    output: output.value,
    advanced: advanced.value
  }

  localStorage.setItem('openfang_settings', JSON.stringify(config))
  ElMessage.success('Settings saved successfully!')
}

const resetSettings = () => {
  if (confirm('Are you sure you want to reset all settings to defaults?')) {
    localStorage.removeItem('openfang_settings')
    ElMessage.success('Settings reset to defaults!')
    // Reload to apply defaults
    setTimeout(() => location.reload(), 1000)
  }
}

const exportSettings = () => {
  const config = {
    settings: settings.value,
    platforms: platforms.value,
    quality: quality.value,
    output: output.value,
    advanced: advanced.value
  }

  const blob = new Blob([JSON.stringify(config, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = 'openfang-settings.json'
  link.click()
  URL.revokeObjectURL(url)

  ElMessage.success('Settings exported!')
}

const importSettings = () => {
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = '.json'

  input.onchange = (e) => {
    const file = e.target.files[0]
    const reader = new FileReader()

    reader.onload = (event) => {
      try {
        const config = JSON.parse(event.target.result)

        settings.value = config.settings || settings.value
        platforms.value = config.platforms || platforms.value
        quality.value = config.quality || quality.value
        output.value = config.output || output.value
        advanced.value = config.advanced || advanced.value

        ElMessage.success('Settings imported successfully!')
      } catch (error) {
        ElMessage.error('Failed to import settings: Invalid file format')
      }
    }

    reader.readAsText(file)
  }

  input.click()
}

// Load settings from localStorage on mount
const loadSettings = () => {
  const saved = localStorage.getItem('openfang_settings')
  if (saved) {
    try {
      const config = JSON.parse(saved)
      settings.value = config.settings || settings.value
      platforms.value = config.platforms || platforms.value
      quality.value = config.quality || quality.value
      output.value = config.output || output.value
      advanced.value = config.advanced || advanced.value
    } catch (error) {
      console.error('Failed to load settings:', error)
    }
  }
}

loadSettings()
</script>

<style scoped>
.settings {
  max-width: 1000px;
  margin: 0 auto;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
  line-height: 1.4;
}

.settings-actions {
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #dcdfe6;
  display: flex;
  justify-content: center;
}

.el-card {
  margin-bottom: 10px;
}
</style>
