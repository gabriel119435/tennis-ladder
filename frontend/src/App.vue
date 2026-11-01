<script setup>
import {watchEffect} from 'vue'
import {useI18n} from 'vue-i18n'
import AppToast from './components/AppToast.vue'
import AppTopBar from './components/AppTopBar.vue'

const {t} = useI18n()
watchEffect(() => {
  document.title = t('app.title')
})
</script>

<template>
  <AppTopBar />
  <main class="page">
    <RouterView />
  </main>
  <AppToast />
</template>
