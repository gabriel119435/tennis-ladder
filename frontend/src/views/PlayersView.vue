<script setup>
import {onMounted, ref} from 'vue'
import {useI18n} from 'vue-i18n'
import {createPlayer, getPlayers, renamePlayer} from '../api/routes/players.js'
import {resetAccount} from '../api/routes/reset.js'
import {store} from '../store.js'
import NameForm from '../components/NameForm.vue'
import {useFetch} from '../composables/generic/useFetch.js'
import {useButtonLock} from '../composables/generic/useButtonLock.js'
import {useSubmit} from '../composables/generic/useSubmit.js'

const {t} = useI18n()
const {locked, withLock} = useButtonLock()
const {submit} = useSubmit(withLock)

// [{id: 1, name: 'player name'}], the admin's own players
const {data: players, load, reload} = useFetch(getPlayers)

const newPlayerName = ref('')

onMounted(() => load())

function handleCreate() {
  return submit(
    () => createPlayer(newPlayerName.value),
    async () => {
      newPlayerName.value = ''
      await reload()
    },
  )
}

async function handleRename(player) {
  const failed = await submit(() => renamePlayer(player.id, player.name), reload)
  if (failed) await reload()
}

function handleReset() {
  return submit(resetAccount, reload)
}
</script>

<template>
  <div class="page-column">
    <button
      v-if="store.user?.is_default"
      :disabled="locked"
      class="btn-danger"
      type="button"
      @click="handleReset"
    >
      {{ t('players.reset') }}
    </button>
    <NameForm
      v-model="newPlayerName"
      :label="t('players.create')"
      :locked="locked"
      :placeholder="t('players.name')"
      class="card tile"
      @submit="handleCreate"
    />
    <hr />
    <div class="card-wrap">
      <NameForm
        v-for="player in players"
        :key="player.id"
        v-model="player.name"
        :label="t('players.rename')"
        :locked="locked"
        :placeholder="t('players.name')"
        class="card tile"
        @submit="handleRename(player)"
      />
    </div>
    <span v-if="players?.length === 0">{{ t('players.empty') }}</span>
  </div>
</template>
