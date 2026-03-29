<template>
  <div class="home">
    <el-row :gutter="20">
      <el-col :span="24">
        <el-card class="welcome-card">
          <template #header>
            <h2>🎉 Welcome to OpenFang Auto Clip</h2>
          </template>

          <p class="description">
            Automated video short creation with AI-powered script generation.
            Transform your long-form content into engaging vertical clips.
          </p>

          <el-divider />

          <el-row :gutter="20">
            <el-col :xs="24" :sm="8">
              <el-card class="feature-card" shadow="hover">
                <div class="feature-icon">🎬</div>
                <h3>Level 1: Visual Remix</h3>
                <p>Style transfer, speed adjustments, and visual effects</p>
              </el-card>
            </el-col>

            <el-col :xs="24" :sm="8">
              <el-card class="feature-card" shadow="hover">
                <div class="feature-icon">✍️</div>
                <h3>Level 2: Script Generation</h3>
                <p>AI-powered short-form script with visual direction</p>
              </el-card>
            </el-col>

            <el-col :xs="24" :sm="8">
              <el-card class="feature-card" shadow="hover">
                <div class="feature-icon">🚀</div>
                <h3>Production Ready</h3>
                <p>Quality: 9.62/10 with comprehensive validation</p>
              </el-card>
            </el-col>
          </el-row>

          <el-divider />

          <div class="actions">
            <el-button type="primary" size="large" @click="$router.push('/process')">
              Get Started
            </el-button>
            <el-button size="large" @click="$router.push('/validate')">
              Validate Package
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :xs="24" :md="12">
        <el-card>
          <template #header>
            <h3>📊 Quick Stats</h3>
          </template>
          <el-descriptions :column="1" border>
            <el-descriptions-item label="Version">0.5.0</el-descriptions-item>
            <el-descriptions-item label="Quality Score">9.62/10</el-descriptions-item>
            <el-descriptions-item label="Content Types">4 (Educational, Entertainment, Tutorial, General)</el-descriptions-item>
            <el-descriptions-item label="Validation">4-dimensional quality scoring</el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>

      <el-col :xs="24" :md="12">
        <el-card>
          <template #header>
            <h3>🔗 Quick Links</h3>
          </template>
          <el-space direction="vertical" fill style="width: 100%;">
            <el-button text @click="openLink('https://github.com/outhsics/openfang-auto-clip')">
              📚 Documentation
            </el-button>
            <el-button text @click="openLink('https://github.com/outhsics/openfang-auto-clip/issues')">
              🐛 Report Issues
            </el-button>
            <el-button text @click="openLink('https://github.com/outhsics/openfang-auto-clip/discussions')">
              💬 Community Discussions
            </el-button>
            <el-button text @click="openLink('https://github.com/outhsics/openfang-auto-clip')">
              ⭐ Star on GitHub
            </el-button>
          </el-space>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
const openLink = (url) => {
  window.open(url, '_blank')
}
</script>

<style scoped>
.home {
  max-width: 1200px;
  margin: 0 auto;
}

.welcome-card {
  background: white;
}

.description {
  font-size: 16px;
  color: #606266;
  line-height: 1.6;
}

.feature-card {
  text-align: center;
  height: 100%;
  transition: transform 0.2s;
}

.feature-card:hover {
  transform: translateY(-5px);
}

.feature-icon {
  font-size: 48px;
  margin-bottom: 10px;
}

.feature-card h3 {
  color: #303133;
  margin: 10px 0;
}

.feature-card p {
  color: #909399;
  font-size: 14px;
}

.actions {
  display: flex;
  justify-content: center;
  gap: 15px;
  margin-top: 20px;
}
</style>
