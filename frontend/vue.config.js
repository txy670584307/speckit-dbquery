const { defineConfig } = require('@vue/cli-service');
const MonacoWebpackPlugin = require('monaco-editor-webpack-plugin');

module.exports = defineConfig({
  transpileDependencies: [],
  configureWebpack: {
    plugins: [
      new MonacoWebpackPlugin({
        languages: ['sql', 'json'],
      }),
    ],
  },
  devServer: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
});
