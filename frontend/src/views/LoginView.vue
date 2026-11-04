<script setup>
import {ref, useTemplateRef} from 'vue'
import {useRouter} from 'vue-router'
import {useI18n} from 'vue-i18n'
import {login} from '../api/routes/auth.js'
import {store} from '../store.js'
import {useButtonLock} from '../composables/generic/useButtonLock.js'
import {useSubmit} from '../composables/generic/useSubmit.js'
import {NAME_MAX_LENGTH, PASSWORD_MAX_LENGTH} from '../constants.js'

const router = useRouter()
const {t} = useI18n()
const username = ref('')
const password = ref('')
const passwordInput = useTemplateRef('passwordInput')
const {locked, withLock} = useButtonLock()
const {submit} = useSubmit(withLock)

async function handleSubmit() {
  const failed = await submit(
    () => login(username.value, password.value),
    async (data) => {
      store.user = data.user
      await router.push('/rankings')
    },
  )
  if (failed) passwordInput.value.select()
}
</script>

<template>
  <div class="login-page">
    <div class="card login-card">
      <h1>{{ t('login.title') }}</h1>
      <form @submit.prevent="handleSubmit">
        <input
          v-model="username"
          :maxlength="NAME_MAX_LENGTH"
          :placeholder="t('login.username')"
          required
          type="text"
        />
        <input
          ref="passwordInput"
          v-model="password"
          :maxlength="PASSWORD_MAX_LENGTH"
          :placeholder="t('login.password')"
          required
          type="password"
        />
        <button
          :disabled="locked"
          class="btn-primary"
          type="submit"
        >
          {{ t('login.submit') }}
        </button>
      </form>
    </div>
  </div>
</template>

<style scoped>
.login-page {
  flex: 1;
  display: flex;
}

.login-card {
  margin: auto;
  gap: var(--space-5);
  width: auto;
}

.login-card h1 {
  font-size: var(--font-scale-1);
}

.login-card form {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-3);
}

.login-card button {
  width: var(--width-input-text);
  margin-top: var(--space-1);
}
</style>
