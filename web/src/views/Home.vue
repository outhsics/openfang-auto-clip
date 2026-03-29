<template>
  <div class="home">
    <!-- Hero Section -->
    <el-card class="hero-card">
      <div class="hero-content">
        <h1 class="hero-title">🎬 OpenFang Auto Clip</h1>
        <p class="hero-subtitle">AI-Powered Video Automation Platform</p>
        <p class="hero-description">
          Transform your long-form content into engaging short-form videos.
          Automated script generation with quality validation.
        </p>

        <div class="hero-actions">
          <el-button type="primary" size="large" @click="$router.push('/process')">
            <el-icon><VideoCamera /></el-icon>
            Start Processing
          </el-button>
          <el-button size="large" @click="$router.push('/jobs')">
            <el-icon><List /></el-icon>
            View Jobs
          </el-button>
          <el-button size="large" @click="openLink('https://github.com/outhsics/openfang-auto-clip')">
            <el-icon><Star /></el-icon>
            GitHub
          </el-button>
        </div>
      </div>
    </el-card>

    <!-- Stats Section -->
    <el-row :gutter="20" class="stats-row">
      <el-col :xs="12" :sm="6">
        <el-card class="stat-card">
          <div class="stat-value">9.62/10</div>
          <div class="stat-label">Quality Score</div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="6">
        <el-card class="stat-card">
          <div class="stat-value">4</div>
          <div class="stat-label">Content Types</div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="6">
        <el-card class="stat-card">
          <div class="stat-value">80%+</div>
          <div class="stat-label">Test Coverage</div>
        </el-card>
      </el-col>
      <el-col :xs="12" :sm="6">
        <el-card class="stat-card">
          <div class="stat-value">v0.5.0</div>
          <div class="stat-label">Latest Version</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- Features Section -->
    <el-card class="features-card">
      <template #header>
        <h2>✨ Features</h2>
      </template>

      <el-row :gutter="20">
        <el-col :xs="24" :sm="8">
          <div class="feature-item">
            <div class="feature-icon">🎬</div>
            <h3>Level 1: Visual Remix</h3>
            <p>Style transfer, speed adjustments, and visual effects for copyright-safe transformation</p>
          </div>
        </el-col>

        <el-col :xs="24" :sm="8">
          <div class="feature-item">
            <div class="feature-icon">✍️</div>
            <h3>Level 2: Script Generation</h3>
            <p>AI-powered short-form script generation with visual direction and quality validation</p>
          </div>
        </el-col>

        <el-col :xs="24" :sm="8">
          <div class="feature-item">
            <div class="feature-icon">🚀</div>
            <h3>Production Ready</h3>
            <p>9.62/10 quality score with comprehensive validation and copyright assessment</p>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <!-- Getting Started Section -->
    <el-row :gutter="20" class="getting-started-row">
      <el-col :xs="24" :md="12">
        <el-card>
          <template #header>
            <h3>🚀 Getting Started</h3>
          </template>

          <el-steps direction="vertical" :space="100">
            <el-step title="Upload Transcript" description="Upload your transcript file (SRT, VTT, or TXT)" />
            <el-step title="Choose Level" description="Select Level 1, 2, or 3 transformation" />
            <el-step title="Configure" description="Set duration, content type, and platform" />
            <el-step title="Process" description="Start processing and monitor progress" />
            <el-step title="Download" description="Download your generated package" />
          </el-steps>

          <el-button type="primary" style="margin-top: 20px; width: 100%;" @click="$router.push('/process')">
            Start Now
          </el-button>
        </el-card>
      </el-col>

      <el-col :xs="24" :md="12">
        <el-card>
          <template #header>
            <h3>🎯 Content Types</h3>
          </template>

          <el-space direction="vertical" fill style="width: 100%;" :size="15">
            <el-card shadow="hover" class="content-type-card">
              <div class="content-type-header">
                <span class="content-type-icon">📚</span>
                <span class="content-type-name">Educational</span>
              </div>
              <p class="content-type-desc">In-depth learning content with clear explanations</p>
            </el-card>

            <el-card shadow="hover" class="content-type-card">
              <div class="content-type-header">
                <span class="content-type-icon">🎬</span>
                <span class="content-type-name">Entertainment</span>
              </div>
              <p class="content-type-desc">Engaging entertainment with storytelling</p>
            </el-card>

            <el-card shadow="hover" class="content-type-card">
              <div class="content-type-header">
                <span class="content-type-icon">📖</span>
                <span class="content-type-name">Tutorial</span>
              </div>
              <p class="content-type-desc">Step-by-step instructional content</p>
            </el-card>

            <el-card shadow="hover" class="content-type-card">
              <div class="content-type-header">
                <span class="content-type-icon">📝</span>
                <span class="content-type-name">General</span>
              </div>
              <p class="content-type-desc">Versatile content for any purpose</p>
            </el-card>
          </el-space>
        </el-card>
      </el-col>
    </el-row>

    <!-- New Features Section -->
    <el-card class="new-features-card">
      <template #header>
        <h2>🆕 What's New in v0.5.0</h2>
      </template>

      <el-row :gutter="20">
        <el-col :xs="24" :sm="12" :md="6">
          <div class="new-feature-item">
            <div class="new-feature-icon">🌐</div>
            <h4>Web Dashboard</h4>
            <p>Beautiful, responsive interface</p>
          </div>
        </el-col>

        <el-col :xs="24" :sm="12" :md="6">
          <div class="new-feature-item">
            <div class="new-feature-icon">🔌</div>
            <h4>REST API</h4>
            <p>Full programmatic access</p>
          </div>
        </el-col>

        <el-col :xs="24" :sm="12" :md="6">
          <div class="new-feature-item">
            <div class="new-feature-icon">🐍</div>
            <h4>Python SDK</h4>
            <p>Official Python client</p>
          </div>
        </el-col>

        <el-col :xs="24" :sm="12" :md="6">
          <div class="new-feature-item">
            <div class="new-feature-icon">🗄️</div>
            <h4>Database</h4>
            <p>Persistent job storage</p>
          </div>
        </el-col>
      </el-row>
    </el-card>

    <!-- Quick Links Section -->
    <el-card class="links-card">
      <template #header>
        <h3>🔗 Quick Links</h3>
      </template>

      <el-row :gutter="20">
        <el-col :xs="24" :sm="8">
          <el-space direction="vertical" fill style="width: 100%;">
            <el-button text @click="openLink('https://github.com/outhsics/openfang-auto-clip')">
              📚 Documentation
            </el-button>
            <el-button text @click="openLink('https://github.com/outhsics/openfang-auto-clip/tree/main/docs')">
              📖 API Reference
            </el-button>
            <el-button text @click="openLink('https://github.com/outhsics/openfang-auto-clip/blob/main/CONTRIBUTING.md')">
              🤝 Contributing Guide
            </el-button>
          </el-space>
        </el-col>

        <el-col :xs="24" :sm="8">
          <el-space direction="vertical" fill style="width: 100%;">
            <el-button text @click="openLink('https://github.com/outhsics/openfang-auto-clip/issues')">
              🐛 Report Issues
            </el-button>
            <el-button text @click="openLink('https://github.com/outhsics/openfang-auto-clip/discussions')">
              💬 Community Discussions
            </el-button>
            <el-button text @click="openLink('https://github.com/outhsics/openfang-auto-clip/blob/main/docs/SUCCESS_STORIES.md')">
              📈 Success Stories
            </el-button>
          </el-space>
        </el-col>

        <el-col :xs="24" :sm="8">
          <el-space direction="vertical" fill style="width: 100%;">
            <el-button text @click="$router.push('/validate')">
              ✅ Validate Package
            </el-button>
            <el-button text @click="$router.push('/jobs')">
              📋 View Jobs
            </el-button>
            <el-button text @click="openLink('https://github.com/outhsics/openfang-auto-clip')">
              ⭐ Star on GitHub
            </el-button>
          </el-space>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup>
import { VideoCamera, List, Star } from '@element-plus/icons-vue'

const openLink = (url) => {
  window.open(url, '_blank')
}
</script>

<style scoped>
.home {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
}

.hero-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  margin-bottom: 30px;
}

.hero-card :deep(.el-card__header) {
  border: none;
  padding: 40px 20px;
}

.hero-card :deep(.el-card__body) {
  padding: 0;
}

.hero-content {
  text-align: center;
  color: white;
  padding: 40px 20px;
}

.hero-title {
  font-size: 48px;
  font-weight: bold;
  margin: 0 0 10px 0;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
}

.hero-subtitle {
  font-size: 24px;
  margin: 0 0 20px 0;
  opacity: 0.95;
}

.hero-description {
  font-size: 18px;
  max-width: 600px;
  margin: 0 auto 30px;
  line-height: 1.6;
  opacity: 0.9;
}

.hero-actions {
  display: flex;
  justify-content: center;
  gap: 15px;
  flex-wrap: wrap;
}

.hero-actions .el-button {
  min-width: 150px;
}

.stats-row {
  margin-bottom: 30px;
}

.stat-card {
  text-align: center;
  transition: transform 0.2s;
}

.stat-card:hover {
  transform: translateY(-5px);
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #409eff;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

.features-card {
  margin-bottom: 30px;
}

.features-card h2 {
  margin: 0;
  color: #303133;
}

.feature-item {
  padding: 20px;
  text-align: center;
  height: 100%;
}

.feature-icon {
  font-size: 64px;
  margin-bottom: 15px;
}

.feature-item h3 {
  font-size: 20px;
  color: #303133;
  margin: 10px 0;
}

.feature-item p {
  font-size: 14px;
  color: #606266;
  line-height: 1.6;
}

.getting-started-row {
  margin-bottom: 30px;
}

.content-type-card {
  cursor: pointer;
  transition: all 0.2s;
}

.content-type-card:hover {
  transform: translateX(5px);
}

.content-type-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 10px;
}

.content-type-icon {
  font-size: 32px;
}

.content-type-name {
  font-size: 18px;
  font-weight: bold;
  color: #303133;
}

.content-type-desc {
  font-size: 14px;
  color: #606266;
  margin: 0;
}

.new-features-card {
  margin-bottom: 30px;
}

.new-features-card h2 {
  margin: 0;
  color: #303133;
}

.new-feature-item {
  text-align: center;
  padding: 20px;
}

.new-feature-icon {
  font-size: 48px;
  margin-bottom: 10px;
}

.new-feature-item h4 {
  font-size: 18px;
  color: #303133;
  margin: 10px 0 5px;
}

.new-feature-item p {
  font-size: 14px;
  color: #606266;
  margin: 0;
}

.links-card {
  margin-bottom: 30px;
}

.links-card h3 {
  margin: 0;
  color: #303133;
}

@media (max-width: 768px) {
  .hero-title {
    font-size: 32px;
  }

  .hero-subtitle {
    font-size: 18px;
  }

  .hero-description {
    font-size: 16px;
  }

  .hero-actions {
    flex-direction: column;
    align-items: stretch;
  }

  .hero-actions .el-button {
    width: 100%;
  }
}
</style>
