import { defineConfig } from 'vitest/config';
import react from '@vitejs/plugin-react';
import tailwindcss from '@tailwindcss/vite';
export default defineConfig({plugins:[react(),tailwindcss()],optimizeDeps:{entries:['index.html']},server:{watch:{ignored:['**/sources/**','**/content/**','**/scripts/**','**/tests/**','**/tmp/**']}},test:{include:['tests/**/*.test.ts']}});
