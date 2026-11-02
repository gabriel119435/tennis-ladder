<script setup>
import {computed, onMounted, watch} from 'vue'
import {useRoute, useRouter} from 'vue-router'
import {useI18n} from 'vue-i18n'
import {getRankings} from '../api/routes/rankings.js'
import {clearResult, getMatches, saveResult} from '../api/routes/matches.js'
import {store} from '../store.js'
import AppSelect from '../components/AppSelect.vue'
import MatchCard from '../components/MatchCard.vue'
import MatchRows from '../components/MatchRows.vue'
import {useFetch} from '../composables/generic/useFetch.js'
import {ANY_PICK, useRememberedPick} from '../composables/rankings/useRememberedPick.js'
import {useButtonLock} from '../composables/generic/useButtonLock.js'
import {useSubmit} from '../composables/generic/useSubmit.js'

const route = useRoute()
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

// picked ranking from the url, ex: /matches/3 -> 3, picking replaces the url
const picked = computed({
  get: () => (route.params.id ? Number(route.params.id) : undefined),
  set: (id) => router.replace(`/matches/${id}`),
})
useRememberedPick(ANY_PICK, picked, rankings)

// picker entries, one per ranking, ex: [{value: 3, label: 'ranking name - admin'}]
const options = computed(() =>
  rankings.value?.map((r) => ({value: r.id, label: `${r.name} - ${r.created_by_admin_username}`})),
)

const ranking = computed(() => rankings.value?.find((r) => r.id === picked.value))

// owner while the round is open
const editable = computed(() => ranking.value?.ongoing && ranking.value.created_by_admin_id === store.user?.id)

// pending: no result yet, saved: played, wo or no-match
const pending = computed(() => matches.value?.filter((m) => !m.result_type))
const saved = computed(() => matches.value?.filter((m) => m.result_type))

// table header, empty over the names and over the buttons
const columns = computed(() => ['', t('matches.set_1'), t('matches.set_2'), t('matches.set_3'), t('matches.wo'), ''])

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
      <template v-if="pending.length && editable">
        <!-- pending | desktop | editable -->
        <div class="card desktop-only">
          <table class="match-table">
            <thead>
              <tr>
                <th
                  v-for="(column, i) in columns"
                  :key="i"
                  :class="{'set-column': i >= 1 && i <= 3}"
                >
                  {{ column }}
                </th>
              </tr>
            </thead>
            <tbody>
              <MatchRows
                v-for="match in pending"
                :key="match.id"
                :editable="editable"
                :locked="locked"
                :match="match"
                @save="(body) => handleSave(match, body)"
              />
            </tbody>
          </table>
        </div>
        <!-- pending | mobile | editable -->
        <!-- mobile-only hides cards on desktop, card-wrap spaces cards -->
        <div class="mobile-only">
          <div class="card-wrap">
            <MatchCard
              v-for="match in pending"
              :key="match.id"
              :editable="editable"
              :locked="locked"
              :match="match"
              @save="(body) => handleSave(match, body)"
            />
          </div>
        </div>
      </template>
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
      <template v-if="saved.length">
        <!-- saved | desktop | editable/read-only -->
        <div class="card desktop-only">
          <table class="match-table">
            <thead>
              <tr>
                <th
                  v-for="(column, i) in columns"
                  :key="i"
                  :class="{'set-column': i >= 1 && i <= 3}"
                >
                  {{ column }}
                </th>
              </tr>
            </thead>
            <tbody>
              <MatchRows
                v-for="match in saved"
                :key="match.id"
                :editable="editable"
                :locked="locked"
                :match="match"
                @clear="handleClear(match)"
              />
            </tbody>
          </table>
        </div>
        <!-- saved | mobile | editable/read-only -->
        <div class="mobile-only">
          <div class="card-wrap">
            <MatchCard
              v-for="match in saved"
              :key="match.id"
              :editable="editable"
              :locked="locked"
              :match="match"
              @clear="handleClear(match)"
            />
          </div>
        </div>
      </template>
    </template>
  </div>
</template>
