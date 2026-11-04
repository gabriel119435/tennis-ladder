<script setup>
import {computed} from 'vue'
import {useI18n} from 'vue-i18n'
import MatchCard from './MatchCard.vue'
import MatchRows from './MatchRows.vue'

// matches as a table on desktop and as cards on mobile
defineProps({
  // [{
  //   id: 1, player_a_id: 10, player_a_name: 'player name', player_b_id: 20, player_b_name: 'player name',
  //   result_type: 'played', winner_id: 10, sets: [{games_a: 6, games_b: 4}, {games_a: 6, games_b: 3}],
  // }]
  matches: {type: Array, required: true},
  // ranking owner while its round is open: shows the result form or the clear button
  editable: {type: Boolean, default: false},
  // from the parent's useButtonLock(), disables the buttons while a submit runs
  locked: {type: Boolean, default: false},
})

const emit = defineEmits(['save', 'clear'])

const {t} = useI18n()

// table header, empty over the names and over the buttons
const columns = computed(() => ['', t('matches.set_1'), t('matches.set_2'), t('matches.set_3'), t('matches.wo'), ''])
</script>

<template>
  <!-- desktop: one table, 2 rows per match -->
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
          v-for="match in matches"
          :key="match.id"
          :editable="editable"
          :locked="locked"
          :match="match"
          @clear="emit('clear', match)"
          @save="(body) => emit('save', match, body)"
        />
      </tbody>
    </table>
  </div>
  <!-- mobile: one card per match -->
  <!-- mobile-only hides cards on desktop, card-wrap spaces cards -->
  <div class="mobile-only">
    <div class="card-wrap">
      <MatchCard
        v-for="match in matches"
        :key="match.id"
        :editable="editable"
        :locked="locked"
        :match="match"
        @clear="emit('clear', match)"
        @save="(body) => emit('save', match, body)"
      />
    </div>
  </div>
</template>

<style scoped>
/* :deep: style also reaches child components' non root tags */
.match-table th,
.match-table :deep(td) {
  padding: var(--space-1) var(--space-2);
}

.set-column {
  width: var(--width-set-column);
}
</style>
