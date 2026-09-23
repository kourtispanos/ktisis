import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// Στην ανάπτυξη (npm run dev) τα αιτήματα /api προωθούνται στο FastAPI
export default defineConfig({
  plugins: [react()],
  server: { proxy: { '/api': 'http://127.0.0.1:8000' } },
  test: {
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.js'],
    globals: true,
  },
})
