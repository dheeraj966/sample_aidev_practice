import { defineConfig } from 'vite';
import { resolve } from 'path';

export default defineConfig({
  server: {
    proxy: {
      '/api': 'http://127.0.0.1:5000'
    }
  },
  build: {
    outDir: 'static',
    emptyOutDir: true,
    rollupOptions: {
      input: {
        script: resolve(__dirname, 'static/script.js')
      }
    }
  }
});