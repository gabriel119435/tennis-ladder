<script setup>
import {computed, onMounted, watch} from 'vue'
import {useRouter} from 'vue-router'
import {useI18n} from 'vue-i18n'
import {getRankings} from '../api/routes/rankings.js'
import {clearResult, getMatches, saveResult} from '../api/routes/matches.js'
import {store} from '../store.js'
import AppSelect from '../components/AppSelect.vue'
import MatchCard from '../components/MatchCard.vue'
import MatchList from '../components/MatchList.vue'
import {useFetch} from '../composables/generic/useFetch.js'
import {useUrlPick} from '../composables/rankings/useUrlPick.js'
import {useButtonLock} from '../composables/generic/useButtonLock.js'
import {useSubmit} from '../composables/generic/useSubmit.js'

const router = useRouter()
const {t} = useI18n()
const {locked, withLock} = useButtonLock()
const {submit} = useSubmit(withLock)

// every ranking, newest first, ex:
// [{
//     id: 3, name: 'ranking name', ongoing: true, round: 2,
//     created_by_admin_id: 1, created_by_admin_username: 'admin',
// }]
const {data: rankings, load: loadRankings, reload: reloadRankings} = useFetch(getRankings)

// picked ranking's current round matches, by id, ex:
// [{
//     id: 1, player_a_id: 10, player_a_name: 'alice', player_b_id: 20, player_b_name: 'bob',
//     result_type: 'played', winner_id: 10, sets: [{games_a: 6, games_b: 4}, {games_a: 6, games_b: 3}],
// }]
const {data: matches, load: loadMatches, reload: reloadMatches} = useFetch(getMatches)

const {picked, options} = useUrlPick('/matches', rankings)

const ranking = computed(() => rankings.value?.find((r) => r.id === picked.value))

// owner while the round is open
const editable = computed(() => ranking.value?.ongoing && ranking.value.created_by_admin_id === store.user?.id)

// pending: no result yet, saved: played, wo or no-match
const pending = computed(() => matches.value?.filter((m) => !m.result_type))
const saved = computed(() => matches.value?.filter((m) => m.result_type))

onMounted(loadRankings)

watch(
  picked,
  async (id) => {
    if (!id) return
    const failed = await loadMatches(id)
    if (failed) router.replace('/matches')
  },
  {immediate: true},
)

// a failed write can mean the round closed elsewhere, so both lists refresh
async function refreshAfterFailure(failed) {
  if (failed) await Promise.all([reloadRankings(), reloadMatches()])
}

async function handleSave(match, body) {
  await refreshAfterFailure(await submit(() => saveResult(match.id, body), reloadMatches))
}

async function handleClear(match) {
  await refreshAfterFailure(await submit(() => clearResult(match.id), reloadMatches))
}
</script>

<template>
  <div class="page-column">
    <AppSelect
      v-if="rankings?.length"
      v-model="picked"
      :options="options"
      :placeholder="t('matches.pick')"
    />
    <template v-if="ranking && matches">
      <h2>{{ t('matches.pending', {n: pending.length}) }}</h2>
      <!-- pending | desktop/mobile | editable -->
      <MatchList
        v-if="pending.length && editable"
        :editable="editable"
        :locked="locked"
        :matches="pending"
        @save="handleSave"
      />
      <!-- pending | desktop/mobile | read-only -->
      <div
        v-else-if="pending.length"
        class="card-wrap"
      >
        <MatchCard
          v-for="match in pending"
          :key="match.id"
          :match="match"
          class="match-names-card"
        />
      </div>

      <h2>{{ t('matches.saved', {n: saved.length}) }}</h2>
      <!-- saved | desktop/mobile | editable/read-only -->
      <MatchList
        v-if="saved.length"
        :editable="editable"
        :locked="locked"
        :matches="saved"
        @clear="handleClear"
      />
    </template>
  </div>
</template>

<style scoped>
/* card width = widest name + 2 card paddings + 2 card borders */
.match-names-card {
  width: calc(var(--width-input-text) + 2 * var(--space-3) + 2 * var(--border-width));
}
</style>
