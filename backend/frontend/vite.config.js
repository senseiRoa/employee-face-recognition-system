import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig(({ command, mode }) => {
  const isDev = command === 'serve'
  
  return {
    plugins: [vue()],
    build: {
      outDir: 'dist',
      assetsDir: 'assets',
      rollupOptions: {
        input: resolve(__dirname, 'index.html'),
      },
    },
    // En desarrollo usa '/', en producción usa '/admin/'
    base: isDev ? '/' : '/admin/',
    server: {
      port: 3030,
      host: '127.0.0.1',
      proxy: {
        '/auth': {
          target: 'http://127.0.0.1:8081',
          changeOrigin: true,
        },
        '/companies': {
          target: 'http://127.0.0.1:8081',
          changeOrigin: true,
        },
        '/warehouses': {
          target: 'http://127.0.0.1:8081',
          changeOrigin: true,
        },
        '/employees': {
          target: 'http://127.0.0.1:8081',
          changeOrigin: true,
        },
        '/users': {
          target: 'http://127.0.0.1:8081',
          changeOrigin: true,
        },
        '/roles': {
          target: 'http://127.0.0.1:8081',
          changeOrigin: true,
        },
        '/logs': {
          target: 'http://127.0.0.1:8081',
          changeOrigin: true,
        },
        '/reports': {
          target: 'http://127.0.0.1:8081',
          changeOrigin: true,
        }
      }
    },
    resolve: {
      alias: {
        '@': resolve(__dirname, 'src'),
      },
    },
  }
})