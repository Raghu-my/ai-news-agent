import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Vite configuration targeting port 3000
export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    host: true
  }
})
