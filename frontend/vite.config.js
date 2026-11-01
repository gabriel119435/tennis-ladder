import {defineConfig} from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
    plugins: [vue()],
    // mock calls are cleared before every test so they don't pile up across tests
    test: {clearMocks: true},
    server: {proxy: {'/api': 'http://localhost:5000'}},
})
