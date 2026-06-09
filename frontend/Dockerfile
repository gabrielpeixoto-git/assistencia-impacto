FROM node:20-alpine

WORKDIR /app

# Copiar package.json e package-lock.json
COPY package.json package-lock.json ./

# Instalar dependências
RUN npm install

# Copiar código do aplicativo (exceto api.ts que será criado durante o build)
COPY . .

# Criar script para gerar api.ts
RUN echo "const fs = require('fs');" > /tmp/create_api.js && \
    echo "const content = \`" >> /tmp/create_api.js && \
    echo "import axios from 'axios'" >> /tmp/create_api.js && \
    echo "" >> /tmp/create_api.js && \
    echo "import { API_BASE_URL } from '../config/api.config'" >> /tmp/create_api.js && \
    echo "" >> /tmp/create_api.js && \
    echo "const api = axios.create({" >> /tmp/create_api.js && \
    echo "  baseURL: API_BASE_URL," >> /tmp/create_api.js && \
    echo "  headers: {" >> /tmp/create_api.js && \
    echo "    'Content-Type': 'application/json'," >> /tmp/create_api.js && \
    echo "  }," >> /tmp/create_api.js && \
    echo "})" >> /tmp/create_api.js && \
    echo "" >> /tmp/create_api.js && \
    echo "api.interceptors.request.use(" >> /tmp/create_api.js && \
    echo "  (config) => {" >> /tmp/create_api.js && \
    echo "    const token = localStorage.getItem('access_token')" >> /tmp/create_api.js && \
    echo "    if (token) {" >> /tmp/create_api.js && \
    echo "      config.headers.Authorization = \\\`Bearer \\\${token}\\\`" >> /tmp/create_api.js && \
    echo "    }" >> /tmp/create_api.js && \
    echo "    return config" >> /tmp/create_api.js && \
    echo "  }," >> /tmp/create_api.js && \
    echo "  (error) => {" >> /tmp/create_api.js && \
    echo "    return Promise.reject(error)" >> /tmp/create_api.js && \
    echo "  }" >> /tmp/create_api.js && \
    echo ")" >> /tmp/create_api.js && \
    echo "" >> /tmp/create_api.js && \
    echo "api.interceptors.response.use(" >> /tmp/create_api.js && \
    echo "  (response) => response," >> /tmp/create_api.js && \
    echo "  async (error) => {" >> /tmp/create_api.js && \
    echo "    if (error.response?.status === 401) {" >> /tmp/create_api.js && \
    echo "      localStorage.removeItem('access_token')" >> /tmp/create_api.js && \
    echo "      localStorage.removeItem('refresh_token')" >> /tmp/create_api.js && \
    echo "      window.location.href = '/login'" >> /tmp/create_api.js && \
    echo "    }" >> /tmp/create_api.js && \
    echo "    return Promise.reject(error)" >> /tmp/create_api.js && \
    echo "  }" >> /tmp/create_api.js && \
    echo ")" >> /tmp/create_api.js && \
    echo "" >> /tmp/create_api.js && \
    echo "export default api" >> /tmp/create_api.js && \
    echo "\`;" >> /tmp/create_api.js && \
    echo "fs.writeFileSync('src/lib/api.ts', content, 'utf8');" >> /tmp/create_api.js && \
    node /tmp/create_api.js

# Expor porta
EXPOSE 5173

# Comando padrão (modo dev sem build)
CMD ["npm", "run", "dev", "--", "--host"]
