import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Health check
export const healthCheck = () => api.get('/api/v1/health')

// Process video/transcript
export const processVideo = (data) => api.post('/api/v1/process', data)

// Jobs
export const listJobs = (params) => api.get('/api/v1/jobs', { params })
export const getJob = (jobId) => api.get(`/api/v1/jobs/${jobId}`)
export const deleteJob = (jobId) => api.delete(`/api/v1/jobs/${jobId}`)

// Validate
export const validatePackage = (data) => api.post('/api/v1/validate', data)

export default api
