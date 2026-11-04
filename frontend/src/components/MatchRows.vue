<script setup>
import {useI18n} from 'vue-i18n'
import AppSelect from './AppSelect.vue'
import {useMatchResult} from '../composables/matches/useMatchResult.js'

// one match as 2 table rows: the desktop layout
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
</script>

<template>
  <tr
    v-for="(side, i) in sides"
    :key="side.key"
    :class="{'match-top': i === 0}"
  >
    <td>
      <component :is="nameTag(side.id)">{{ side.name }}</component>
    </td>
    <td
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
      <template v-else>{{ side.cells[n - 1] }}</template>
    </td>
    <!-- single wo picker when pending, wo text for each row when saved -->
    <td
      v-if="pending && i === 0"
      rowspan="2"
    >
      <AppSelect
        v-model="absentId"
        :clear-label="t('matches.nobody_absent')"
        :options="absentOptions"
        :placeholder="t('matches.wo_pick')"
      />
    </td>
    <td v-else-if="!pending">{{ side.woText }}</td>
    <!-- save when pending, clear when saved, owner only -->
    <td
      v-if="i === 0"
      rowspan="2"
    >
      <button
        v-if="pending"
        :disabled="locked || !filled"
        class="btn-primary"
        type="button"
        @click="emit('save', body())"
      >
        {{ t('matches.save') }}
      </button>
      <button
        v-else-if="editable"
        :disabled="locked"
        class="btn-danger"
        type="button"
        @click="emit('clear')"
      >
        {{ t('matches.clear') }}
      </button>
    </td>
  </tr>
</template>

<style scoped>
/* .c1 > .c2:not([foo]): c2 without foo attribute directly inside c1 */
.match-top > td:not([rowspan]) {
  border-bottom: none;
  padding-bottom: 0;
}

/* .c1 + .c2: c2 right after c1, same parent */
.match-top + tr > td {
  padding-top: var(--space-1);
}
</style>
