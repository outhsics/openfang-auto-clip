<template>
  <div class="validate">
    <el-card>
      <template #header>
        <h2>🔍 Validate Level 2 Package</h2>
      </template>

      <el-form :model="form" label-width="140px">
        <el-form-item label="Package Path">
          <el-input
            v-model="form.package_path"
            placeholder="/output/level2_package.json"
            clearable
          />
        </el-form-item>

        <el-form-item label="Original Transcript">
          <el-input
            v-model="form.original_transcript"
            type="textarea"
            :rows="4"
            placeholder="Paste original transcript text for copyright risk assessment..."
          />
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="validate" :loading="validating">
            Validate Package
          </el-button>
          <el-button @click="resetForm">Reset</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- Validation Results -->
    <el-card v-if="result" style="margin-top: 20px;">
      <template #header>
        <h3>Validation Results</h3>
      </template>

      <el-row :gutter="20">
        <el-col :xs="24" :sm="12">
          <el-card class="result-card">
            <template #header>
              <h4>Overall Score</h4>
            </template>
            <div class="score-display">
              <div class="score-number">{{ result.overall_score }}/10</div>
              <el-tag :type="getGradeType(result.grade)" size="large" effect="dark">
                Grade: {{ result.grade }}
              </el-tag>
            </div>
          </el-card>
        </el-col>

        <el-col :xs="24" :sm="12">
          <el-card class="result-card">
            <template #header>
              <h4>Production Ready</h4>
            </template>
            <div class="production-ready">
              <el-tag :type="result.production_ready ? 'success' : 'danger'" size="large">
                {{ result.production_ready ? '✅ Yes' : '❌ No' }}
              </el-tag>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <el-divider />

      <h4>Quality Scores</h4>
      <el-table :data="getScoresTable()" border>
        <el-table-column prop="dimension" label="Dimension" />
        <el-table-column prop="score" label="Score" width="100" />
        <el-table-column label="Rating" width="150">
          <template #default="{ row }">
            <el-rate v-model="row.rating" disabled />
          </template>
        </el-table-column>
      </el-table>

      <el-divider />

      <h4>Copyright Risk</h4>
      <el-alert
        :type="getCopyrightRiskType(result.copyright_risk.risk_level)"
        :title="`Risk Level: ${result.copyright_risk.risk_level}`"
        show-icon
        :closable="false"
      >
        <p>Semantic Similarity: {{ (result.copyright_risk.semantic_similarity * 100).toFixed(1) }}%</p>
        <p>Word Overlap: {{ (result.copyright_risk.word_overlap * 100).toFixed(1) }}%</p>
      </el-alert>

      <el-divider v-if="result.issues.length > 0" />

      <h4 v-if="result.issues.length > 0">Issues ({{ result.issues.length }})</h4>
      <el-alert
        v-for="(issue, index) in result.issues"
        :key="index"
        type="warning"
        :title="issue"
        show-icon
        :closable="false"
        style="margin-bottom: 10px;"
      />

      <el-divider v-if="result.recommendations.length > 0" />

      <h4 v-if="result.recommendations.length > 0">Recommendations</h4>
      <el-alert
        v-for="(rec, index) in result.recommendations"
        :key="index"
        type="info"
        :title="rec"
        show-icon
        :closable="false"
        style="margin-bottom: 10px;"
      />
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { validatePackage } from '../api'

const form = ref({
  package_path: '',
  original_transcript: ''
})

const validating = ref(false)
const result = ref(null)

const validate = async () => {
  try {
    validating.value = true
    const response = await validatePackage(form.value)
    result.value = response.data
    ElMessage.success('Validation completed!')
  } catch (error) {
    ElMessage.error(`Validation failed: ${error.message}`)
  } finally {
    validating.value = false
  }
}

const resetForm = () => {
  form.value = {
    package_path: '',
    original_transcript: ''
  }
  result.value = null
}

const getGradeType = (grade) => {
  const types = { A: 'success', B: 'warning', C: 'info', D: 'warning', F: 'danger' }
  return types[grade] || 'info'
}

const getCopyrightRiskType = (level) => {
  const types = { Safe: 'success', Moderate: 'warning', High: 'danger' }
  return types[level] || 'info'
}

const getScoresTable = () => {
  if (!result.value) return []
  return Object.entries(result.value.scores).map(([dimension, score]) => ({
    dimension,
    score: score.toFixed(1),
    rating: Math.round(score / 2) // Convert 0-10 to 0-5 stars
  }))
}
</script>

<style scoped>
.validate {
  max-width: 1000px;
  margin: 0 auto;
}

.result-card {
  margin-bottom: 20px;
}

.score-display {
  text-align: center;
  padding: 20px 0;
}

.score-number {
  font-size: 48px;
  font-weight: bold;
  color: #409eff;
  margin-bottom: 10px;
}

.production-ready {
  text-align: center;
  padding: 20px 0;
  font-size: 18px;
}
</style>
