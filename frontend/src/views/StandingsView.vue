<script setup>
import {onMounted, ref, watch} from 'vue'
import {useRouter} from 'vue-router'
import {useI18n} from 'vue-i18n'
import {getRankings} from '../api/routes/rankings.js'
import {getStandings} from '../api/routes/standings.js'
import AppSelect from '../components/AppSelect.vue'
import {useFetch} from '../composables/generic/useFetch.js'
import {useUrlPick} from '../composables/rankings/useUrlPick.js'

const router = useRouter()
const {t} = useI18n()

// every ranking, newest first, ex:
// [{
//     id: 3, name: 'ranking name', ongoing: true, round: 2,
//     created_by_admin_id: 1, created_by_admin_username: 'admin',
// }]
const {data: rankings, load: loadRankings} = useFetch(getRankings)

// picked ranking's active players, best first, ex:
// [{
//     id: 10, name: 'alice', points: 4, attended_matches: 1,
//     total_matches: 1, won_matches: 1, lost_matches: 0,
//     won_sets: 2, lost_sets: 0, won_games: 12, lost_games: 7,
// }]
const {data: rows, load: loadStandings} = useFetch(getStandings)

const {picked, options} = useUrlPick('/standings', rankings)

// ids of rows showing their details on mobile, ex: Set([10, 12])
const opened = ref(new Set())

function toggle(id) {
  if (opened.value.has(id)) opened.value.delete(id)
  else opened.value.add(id)
}

onMounted(loadRankings)

// runs on open and on every pick
watch(
  picked,
  async (id) => {
    opened.value.clear()
    if (!id) return
    const failed = await loadStandings(id)
    if (failed) router.replace('/standings')
  },
  {immediate: true},
)
</script>

<template>
  <div class="page-column">
    <AppSelect
      v-if="rankings?.length"
      v-model="picked"
      :options="options"
      :placeholder="t('standings.pick')"
    />
    <div
      v-if="rows?.length"
      class="card"
    >
      <table>
        <thead>
          <tr>
            <th>{{ t('standings.position') }}</th>
            <th>{{ t('standings.player') }}</th>
            <th>{{ t('standings.points') }}</th>
            <th class="desktop-only">{{ t('standings.attendance') }}</th>
            <th class="desktop-only">{{ t('standings.matches') }}</th>
            <th class="desktop-only">{{ t('standings.sets') }}</th>
            <th class="desktop-only">{{ t('standings.games') }}</th>
            <th class="mobile-only"></th>
          </tr>
        </thead>
        <tbody>
          <template
            v-for="(row, i) in rows"
            :key="row.id"
          >
            <tr>
              <td>{{ i + 1 }}</td>
              <td>{{ row.name }}</td>
              <td>{{ row.points }}</td>
              <td class="desktop-only">{{ row.attended_matches }}/{{ row.total_matches }}</td>
              <td class="desktop-only">{{ row.won_matches }}-{{ row.lost_matches }}</td>
              <td class="desktop-only">{{ row.won_sets }}-{{ row.lost_sets }}</td>
              <td class="desktop-only">{{ row.won_games }}-{{ row.lost_games }}</td>
              <td class="mobile-only">
                <button
                  class="btn-primary toggle-button"
                  type="button"
                  @click="toggle(row.id)"
                >
                  <span :class="{hidden: opened.has(row.id)}">{{ t('standings.info') }}</span>
                  <span :class="{hidden: !opened.has(row.id)}">{{ t('standings.hide') }}</span>
                </button>
              </td>
            </tr>
            <!-- extra info in mobile: attendance, matches, sets, games -->
            <tr
              v-if="opened.has(row.id)"
              class="mobile-only"
            >
              <td colspan="4">
                <div class="cell-grid">
                  <span>
                    <span>{{ t('standings.attendance') }}</span>
                    <span>{{ row.attended_matches }}/{{ row.total_matches }}</span>
                  </span>
                  <span>
                    <span>{{ t('standings.matches') }}</span>
                    <span>{{ row.won_matches }}-{{ row.lost_matches }}</span>
                  </span>
                  <span>
                    <span>{{ t('standings.sets') }}</span>
                    <span>{{ row.won_sets }}-{{ row.lost_sets }}</span>
                  </span>
                  <span>
                    <span>{{ t('standings.games') }}</span>
                    <span>{{ row.won_games }}-{{ row.lost_games }}</span>
                  </span>
                </div>
              </td>
            </tr>
          </template>
        </tbody>
      </table>
    </div>
    <span v-if="rows?.length === 0">{{ t('standings.empty') }}</span>
  </div>
</template>

<style scoped>
.cell-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-3);
}

/* .c1 > *: every direct c1's child */
.cell-grid > * {
  background: var(--color-bg-2);
  border: var(--border-width) solid var(--color-b-1);
  border-radius: var(--border-radius-0);
  padding: var(--space-1) var(--space-3);
  display: flex;
  justify-content: space-between;
}
</style>
