// @ts-check
import { defineConfig } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';

// https://astro.build/config
export default defineConfig({
  site: 'https://finelines98.github.io',
  base: '/math-exam-archive',
  vite: {
    plugins: [tailwindcss()]
  }
});
