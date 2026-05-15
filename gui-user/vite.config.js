import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import legacy from '@vitejs/plugin-legacy';
import { viteSingleFile } from "vite-plugin-singlefile";

export default defineConfig({
  plugins: [
    react(),
    // The legacy plugin will create a separate ES5 version safely
    legacy({
      targets: ['safari 9', 'ios 9'],
      additionalLegacyPolyfills: ['regenerator-runtime/runtime'],
      renderLegacyChunks: true, // Required for legacy support
    }),
    viteSingleFile({
      removeViteModuleLoader: true,
      useRecommendedBuildConfig: true,
    }),
  ],
  build: {
    // Set this to es2015 to stop esbuild from throwing "Target Not Supported" errors
    target: 'es2015', 
    cssTarget: 'safari9',
    assetsInlineLimit: 100000000,
    rollupOptions: {
      output: {
        manualChunks: undefined,
      },
    },
  },
});