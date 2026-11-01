<script setup>
import {computed} from 'vue'
import {useI18n} from 'vue-i18n'
import AppSelect from './AppSelect.vue'
import {useMatchResult} from '../composables/matches/useMatchResult.js'

// one match as a card: the mobile layout for owned and not owned matches
// also on desktop for read only pending matches
const props = defineProps({
  // {
  //   id: 1, player_a_id: 10, player_a_name: 'player name', player_b_id: 20, player_b_name: 'player name',
  //   result_type: 'played', winner_id: 10, sets: [{games_a: 6, games_b: 4}, {games_a: 6, games_b: 3}],
  // }
  match: {type: Object, required: true},
  // ranking owner while its round is open: shows the result form or the clear button
  editable: {type: Boolean, default: false},
  // from the parent's useButtonLock(), disables the buttons while a submit runs
  locked: {type: Boolean, default: false},
})

const emit = defineEmits(['save', 'clear'])

const {t} = useI18n()

const {pending, filled, nameTag, absentOptions, sides, body, absentId, scores} = useMatchResult(props)

// set labels, the header row of the score grid
const labels = computed(() => [t('matches.set_1'), t('matches.set_2'), t('matches.set_3')])

// which of the 3 layouts the card uses, see match-card.css
// games: name and 3 sets, owner's pending or played match
// wo: name and wo text, walkover or no-match
// names: name only, read only pending match
const layout = computed(() => {
  if (pending.value || props.match.result_type === 'played') return 'games'
  return props.match.result_type ? 'wo' : 'names'
})
</script>

<template>
  <div class="card">
    <!-- columns: 4 for games (name + 3 sets), 2 for wo (name + wo state) and 1 for names -->
    <div
      :class="{'match-sets-wo': layout === 'wo', 'match-sets-names': layout === 'names'}"
      class="match-sets"
    >
      <!-- row 1: save or clear button + set labels or empty cell -->
      <template v-if="layout === 'games' || editable">
        <!-- row 1 column 1: save when pending -->
        <button
          v-if="pending"
          :disabled="locked || !filled"
          class="btn-primary"
          type="button"
          @click="emit('save', body())"
        >
          {{ t('matches.save') }}
        </button>
        <!-- row 1 column 1: clear when saved -->
        <button
          v-else-if="editable"
          :disabled="locked"
          class="btn-danger"
          type="button"
          @click="emit('clear')"
        >
          {{ t('matches.clear') }}
        </button>
        <!-- row 1 column 1: empty once played, read only -->
        <span v-else />

        <!-- row 1 columns 2 to 4: set labels -->
        <template v-if="layout === 'games'">
          <span
            v-for="label in labels"
            :key="label"
            >{{ label }}</span
          >
        </template>
        <!-- row 1 column 2: empty for owner's wo -->
        <span v-else />
      </template>

      <!-- rows 2 and 3: player name + set values or wo/no-match state -->
      <template
        v-for="side in sides"
        :key="side.key"
      >
        <!-- rows 2 and 3 column 1: name, bold for the winner -->
        <component :is="nameTag(side.id)">{{ side.name }}</component>
        <!-- rows 2 and 3 columns 2 to 4: inputs while pending, saved games once played -->
        <template v-if="layout === 'games'">
          <template
            v-for="n in 3"
            :key="n"
          >
            <input
              v-if="pending"
              v-model="scores[side.key][n - 1]"
              inputmode="numeric"
              maxlength="2"
              type="text"
            />
            <span v-else>{{ side.cells[n - 1] }}</span>
          </template>
        </template>
        <!-- rows 2 and 3 column 2: present, absent or no_match -->
        <span v-else-if="layout === 'wo'">{{ side.woText }}</span>
      </template>

      <!-- row 4 column 1: wo picker while pending -->
      <AppSelect
        v-if="pending"
        v-model="absentId"
        :clear-label="t('matches.nobody_absent')"
        :options="absentOptions"
        :placeholder="t('matches.wo_pick')"
      />
    </div>
  </div>
</template>
