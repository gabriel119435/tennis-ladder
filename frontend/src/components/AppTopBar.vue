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

// if logout fails, the user stays logged in and the toast shows the error
function handleLogout() {
  return submit(logout, async () => {
    store.user = null
    await router.push('/standings')
  })
}

// keep path params when clicked tab is current one
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

<style scoped>
.top-bar {
  display: grid;
  /* tabs keep their content width (auto), sides split the leftover in half (1fr each) */
  grid-template-columns: 1fr auto 1fr;
  align-items: center;
  background: var(--color-bg-1);
  border-bottom: var(--border-width) solid var(--color-b-0);
  padding: var(--space-3) var(--space-5);
  margin-bottom: var(--space-5);
}

.top-bar-left {
  justify-self: start;
  color: var(--color-fg-1);
}

.top-bar-right {
  justify-self: end;
}

.top-bar-links {
  display: flex;
  gap: var(--space-1);
}

/* a (html link tag) rendered by vue's RouterLink */
.top-bar a {
  text-decoration: none;
  color: var(--color-fg-1);
  padding: var(--space-1) var(--space-3);
  border: var(--border-width) solid var(--color-b-1);
  border-radius: var(--border-radius-0);
}

/* router-link-active: vue router's class for the current page's link */
.top-bar a:hover,
.top-bar a.router-link-active {
  background: var(--color-bg-2);
  border-color: var(--color-b-2);
  color: var(--color-fg-0);
}

@media (max-width: 800px) {
  /* row 1: user logout
     row 2: tabs */
  .top-bar {
    grid-template-columns: 1fr 1fr;
    row-gap: var(--space-3);
  }

  /* row 2, full width: tabs in 2 columns, each tab fills its half */
  .top-bar-links {
    grid-column: 1 / -1;
    grid-row: 2;
    display: grid;
    grid-template-columns: 1fr 1fr;
  }
}
</style>
