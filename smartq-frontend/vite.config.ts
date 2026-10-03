import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  build: {
    outDir: path.resolve(__dirname, '../smartq_static/react'),
    emptyOutDir: true,
  },
  server: {
    port: 5173,
    host: true,
  },
  base: '/static/react/',
});