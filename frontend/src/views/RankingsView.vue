<script setup>
import {computed, onMounted, ref, watch} from 'vue'
import {useI18n} from 'vue-i18n'
import {closeRound, createRanking, getRankings, startRound} from '../api/routes/rankings.js'
import {addParticipant, getParticipants, removeParticipant} from '../api/routes/participants.js'
import {getPlayers} from '../api/routes/players.js'
import {store} from '../store.js'
import AppSelect from '../components/AppSelect.vue'
import NameForm from '../components/NameForm.vue'
import {useFetch} from '../composables/generic/useFetch.js'
import {OWN_PICK, useRememberedPick} from '../composables/rankings/useRememberedPick.js'
import {useButtonLock} from '../composables/generic/useButtonLock.js'
import {useSubmit} from '../composables/generic/useSubmit.js'

const {t} = useI18n()
const {locked, withLock} = useButtonLock()
const {submit} = useSubmit(withLock)

// own rankings, newest first, ex:
// [{
//     id: 3, name: 'ranking name', ongoing: true, round: 2,
//     created_by_admin_id: 1, created_by_admin_username: 'admin',
// }]
const {data: rankings, load: loadRankings, reload: reloadRankings} = useFetch(getRankings)

// picked ranking's active players, by name, ex: [{player_id: 10, name: 'alice'}]
const {data: participants, load: loadParticipants, reload: reloadParticipants} = useFetch(getParticipants)

// own players, by name, ex: [{id: 10, name: 'alice'}]
const {data: players, load: loadPlayers} = useFetch(getPlayers)

const newRankingName = ref('')

// this view's own pick, not in the url
const picked = ref()
useRememberedPick(OWN_PICK, picked, rankings)

// player picked in the add picker
const pickedPlayerId = ref()

const ranking = computed(() => rankings.value?.find((r) => r.id === picked.value))

const rankingOptions = computed(() => rankings.value?.map((r) => ({value: r.id, label: r.name})))

// non active players in current ranking
const inactivePlayerOptions = computed(() =>
  players.value
    ?.filter((p) => !participants.value?.some((participant) => participant.player_id === p.id))
    .map((p) => ({value: p.id, label: p.name})),
)

onMounted(() => {
  loadRankings(store.user.id)
  loadPlayers()
})

watch(picked, async (id) => {
  pickedPlayerId.value = undefined
  if (!id) return
  const failed = await loadParticipants(id)
  if (failed) picked.value = undefined
})

function handleCreate() {
  return submit(
    () => createRanking(newRankingName.value),
    async () => {
      newRankingName.value = ''
      await reloadRankings()
    },
  )
}

function handleRound() {
  const call = ranking.value.ongoing ? closeRound : startRound
  return submit(() => call(picked.value), reloadRankings)
}

function handleAdd() {
  return submit(
    () => addParticipant(picked.value, pickedPlayerId.value),
    async () => {
      pickedPlayerId.value = undefined
      await reloadParticipants()
    },
  )
}

function handleRemove(participant) {
  return submit(() => removeParticipant(picked.value, participant.player_id), reloadParticipants)
}
</script>

<template>
  <div class="page-column">
    <AppSelect
      v-if="rankings?.length"
      v-model="picked"
      :options="rankingOptions"
      :placeholder="t('rankings.pick')"
    />
    <NameForm
      v-model="newRankingName"
      :label="t('rankings.create')"
      :locked="locked"
      :placeholder="t('rankings.name')"
      class="card tile tile-split"
      @submit="handleCreate"
    />

    <template v-if="ranking">
      <div class="card tile tile-split">
        <span>
          {{ t('rankings.round', {n: ranking.round}) }}
          {{ ranking.ongoing ? t('rankings.ongoing') : t('rankings.paused') }}
        </span>
        <button
          :class="ranking.ongoing ? 'btn-danger' : 'btn-primary'"
          :disabled="locked"
          type="button"
          @click="handleRound"
        >
          {{ ranking.ongoing ? t('rankings.close') : t('rankings.start') }}
        </button>
      </div>

      <div class="card tile tile-split">
        <AppSelect
          v-model="pickedPlayerId"
          :options="inactivePlayerOptions"
          :placeholder="t('rankings.add_player')"
        />
        <button
          :disabled="locked || !pickedPlayerId"
          class="btn-primary"
          type="button"
          @click="handleAdd"
        >
          {{ t('rankings.add') }}
        </button>
      </div>

      <hr />
      <div class="card-wrap">
        <div
          v-for="participant in participants"
          :key="participant.player_id"
          class="card card-row tile"
        >
          <span>{{ participant.name }}</span>
          <button
            :disabled="locked"
            class="btn-danger"
            type="button"
            @click="handleRemove(participant)"
          >
            {{ t('rankings.remove') }}
          </button>
        </div>
      </div>
      <span v-if="participants?.length === 0">{{ t('rankings.empty') }}</span>
    </template>
  </div>
</template>
