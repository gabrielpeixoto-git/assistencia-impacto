const fs = require('fs');
const path = require('path');
const content = "import axios from 'axios'\n\nimport { API_BASE_URL } from '../config/api.config'\n\nconst api = axios.create({\n  baseURL: API_BASE_URL,\n  headers: {\n    'Content-Type': 'application/json',\n  },\n})\n\napi.interceptors.request.use(\n  (config) => {\n    const token = localStorage.getItem('access_token')\n    if (token) {\n      config.headers.Authorization = `Bearer ${token}`\n    }\n    return config\n  },\n  (error) => {\n    return Promise.reject(error)\n  }\n)\n\napi.interceptors.response.use(\n  (response) => response,\n  async (error) => {\n    if (error.response?.status === 401) {\n      localStorage.removeItem('access_token')\n      localStorage.removeItem('refresh_token')\n      window.location.href = '/login'\n    }\n    return Promise.reject(error)\n  }\n)\n\nexport default api";
const filePath = path.join(__dirname, 'frontend', 'src', 'lib', 'api.ts');
fs.writeFileSync(filePath, content, 'utf8');
console.log('Arquivo criado com sucesso em:', filePath);
