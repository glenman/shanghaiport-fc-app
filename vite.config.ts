import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { copyFileSync, existsSync, mkdirSync, readdirSync } from 'fs'
import { resolve } from 'path'

// 自定义插件，复制data目录到dist
const copyDataPlugin = {
  name: 'copy-data',
  writeBundle() {
    const dataDir = resolve(__dirname, 'data')
    const distDataDir = resolve(__dirname, 'dist/data')
    
    if (existsSync(dataDir)) {
      // 创建dist/data目录
      if (!existsSync(distDataDir)) {
        mkdirSync(distDataDir, { recursive: true })
      }
      
      // 复制data目录中的所有文件
      const copyFiles = (srcDir: string, destDir: string) => {
        const files = readdirSync(srcDir, { withFileTypes: true })
        files.forEach(file => {
          const srcPath = resolve(srcDir, file.name)
          const destPath = resolve(destDir, file.name)
          if (file.isDirectory()) {
            if (!existsSync(destPath)) {
              mkdirSync(destPath, { recursive: true })
            }
            copyFiles(srcPath, destPath)
          } else {
            copyFileSync(srcPath, destPath)
          }
        })
      }
      
      copyFiles(dataDir, distDataDir)
      console.log('Data directory copied to dist')
    }
  }
}

// https://vitejs.dev/config/
export default defineConfig({
  base: '/shanghaiport-fc-app/',
  plugins: [react(), copyDataPlugin],
  build: {
    rollupOptions: {
      output: {
        manualChunks: undefined
      }
    }
  }
})