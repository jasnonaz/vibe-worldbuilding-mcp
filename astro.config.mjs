// @ts-check
import { defineConfig } from 'astro/config';
import mdx from '@astrojs/mdx';

// https://astro.build/config
export default defineConfig({
  integrations: [mdx()],
  publicDir: 'public',
  vite: {
    server: {
      fs: {
        // Allow serving files from world directories
        allow: ['..']
      }
    }
  }
});
