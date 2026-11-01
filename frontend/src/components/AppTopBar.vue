<script setup>
import {useRoute, useRouter} from 'vue-router'
import {useI18n} from 'vue-i18n'
import {logout} from '../api/routes/auth.js'
import {store} from '../store.js'
import {useButtonLock} from '../composables/generic/useButtonLock.js'
import {useSubmit} from '../composables/generic/useSubmit.js'

const route = useRoute()
const router = useRouter()
const {t} = useI18n()
const {locked, withLock} = useButtonLock()
const {submit} = useSubmit(withLock)

// js can't delete the http only session cookie, only the backend logout call can
// if that call fails, the user stays logged in and the toast shows the error
function handleLogout() {
  return submit(logout, async () => {
    store.user = null
    await router.push('/standings')
  })
}

// an open tab links to the current url, so clicking it keeps its /:id, ex: /standings/3 stays /standings/3
function tabLink(path) {
  return route.path.startsWith(path) ? route.fullPath : path
}
</script>

<template>
  <nav class="top-bar">
    <span
      v-if="store.user"
      class="top-bar-left"
      >{{ store.user.username }}</span
    >
    <RouterLink
      v-else
      class="top-bar-left"
      to="/login"
      >{{ t('nav.login') }}</RouterLink
    >

    <div class="top-bar-links">
      <template v-if="store.user">
        <RouterLink :to="tabLink('/players')">{{ t('nav.players') }}</RouterLink>
        <RouterLink :to="tabLink('/rankings')">{{ t('nav.rankings') }}</RouterLink>
      </template>
      <RouterLink :to="tabLink('/standings')">{{ t('nav.standings') }}</RouterLink>
      <RouterLink :to="tabLink('/matches')">{{ t('nav.matches') }}</RouterLink>
    </div>

    <!-- the grid's third column keeps the links centered, rendered even when empty -->
    <div class="top-bar-right">
      <button
        v-if="store.user"
        :disabled="locked"
        class="btn-danger"
        type="button"
        @click="handleLogout"
      >
        {{ t('nav.logout') }}
      </button>
    </div>
  </nav>
</template>
