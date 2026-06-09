import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  return {
    plugins: [react()],
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src'),
      },
    },
    server: {
      host: '0.0.0.0',
      port: 5173,
      proxy: {
        '/api': {
          target: 'http://backend:8000',
          changeOrigin: true,
          secure: false,
          configure: (proxy, _options) => {
            proxy.on('error', (err, _req, _res) => {
              console.log('[PROXY ERROR]', err.message);
            });
            proxy.on('proxyReq', (proxyReq, req, _res) => {
              console.log('[PROXY →]', req.method, req.url, '→ backend:8000');
            });
            proxy.on('proxyRes', (proxyRes, req, _res) => {
              console.log('[PROXY ←]', proxyRes.statusCode, req.url);
            });
          },
        },
        '/ws': {
          target: 'ws://backend:8000',
          ws: true,
          changeOrigin: true,
        },
      },
    },
    test: {
      environment: 'jsdom',
      globals: true,
      setupFiles: ['./src/tests/setup.ts'],
      exclude: ['node_modules', 'dist', 'e2e']
    }
  }
})
