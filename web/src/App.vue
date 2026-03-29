<template>
  <div id="app">
    <el-container class="app-container">
      <!-- Header -->
      <el-header class="app-header">
        <div class="header-content">
          <h1 class="app-title">
            🎬 OpenFang Auto Clip
          </h1>
          <nav class="app-nav">
            <router-link to="/">Home</router-link>
            <router-link to="/process">Process</router-link>
            <router-link to="/jobs">Jobs</router-link>
            <router-link to="/validate">Validate</router-link>
            <router-link to="/settings">Settings</router-link>
          </nav>
        </div>
      </el-header>

      <!-- Main Content -->
      <el-main class="app-main">
        <router-view />
      </el-main>

      <!-- Footer -->
      <el-footer class="app-footer">
        <p>OpenFang Auto Clip v0.5.0 | <a href="https://github.com/outhsics/openfang-auto-clip" target="_blank">GitHub</a></p>
      </el-footer>
    </el-container>
  </div>
</template>

<script setup>
// App component
</script>

<style scoped>
.app-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 0;
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100%;
  padding: 0 20px;
}

.app-title {
  font-size: 24px;
  font-weight: bold;
  margin: 0;
}

.app-nav {
  display: flex;
  gap: 20px;
}

.app-nav a {
  color: white;
  text-decoration: none;
  font-weight: 500;
  transition: opacity 0.2s;
}

.app-nav a:hover {
  opacity: 0.8;
}

.app-nav a.router-link-active {
  border-bottom: 2px solid white;
}

.app-main {
  flex: 1;
  background: #f5f7fa;
  padding: 20px;
}

.app-footer {
  background: #2c3e50;
  color: white;
  text-align: center;
  border-top: none;
}

.app-footer a {
  color: #667eea;
  text-decoration: none;
}

.app-footer a:hover {
  text-decoration: underline;
}
</style>
