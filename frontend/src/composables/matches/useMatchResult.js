import {computed, ref} from 'vue'
import {useI18n} from 'vue-i18n'
import {toScore} from '../../utils/scoreUtils.js'

// props.match: one match from the api, ex:
// {
//     player_a_id: 10, player_b_id: 20, result_type: 'played', winner_id: 10,
//     sets: [{games_a: 6, games_b: 4}, {games_a: 6, games_b: 3}],
// }
// props.editable: true for the ranking owner while its round is open
export function useMatchResult(props) {
    const {t} = useI18n()

    // set by the components' v-model
    const absentId = ref()
    const scores = ref({a: ['', '', ''], b: ['', '', '']})

    const pending = computed(() => props.editable && !props.match.result_type)
    const filled = computed(() => absentId.value || [...scores.value.a, ...scores.value.b].some((v) => v !== ''))

    const nameTag = (playerId) => (props.match.winner_id === playerId ? 'strong' : 'span')

    const absentOptions = computed(() => [
        {value: props.match.player_a_id, label: t('matches.absent_top')},
        {value: props.match.player_b_id, label: t('matches.absent_bottom')},
    ])

    function woText(key, id) {
        const {result_type: type, winner_id: winnerId} = props.match
        if (type === 'walkover') return t(winnerId === id ? 'matches.present' : 'matches.absent')
        if (type === 'no_match' && key === 'b') return t('matches.no_match')
        return ''
    }

    const sides = computed(() =>
        ['a', 'b'].map((key) => {
            const id = props.match[`player_${key}_id`]
            const cells = props.match.sets.map((s) => s[`games_${key}`])
            return {key, id, name: props.match[`player_${key}_name`], cells, woText: woText(key, id)}
        }),
    )

    function body() {
        const {a, b} = scores.value
        const sets = [0, 1, 2]
            .map((i) => [a[i], b[i]])
            .filter((pair) => pair.some((v) => v !== ''))
            .map((pair) => pair.map(toScore))
        const players = [props.match.player_a_id, props.match.player_b_id]
        return {sets, wo_winner_id: absentId.value && players.find((id) => id !== absentId.value)}
    }

    // read:
    //   pending: editable (owner, open round) and no result yet
    //   filled: a score typed or a player picked absent
    //   nameTag(playerId): 'strong' for the winner, 'span' otherwise
    //   absentOptions: [{value: 10, label: absent_top}, {value: 20, label: absent_bottom}]
    //   sides: [{key, id, name, cells, woText}] per player, cells: saved games per set
    //     woText: present or absent on a walkover, no_match only on key 'b'
    //   body(): save payload, ex: {sets: [[6, 4], [6, 3]]} or {sets: [], wo_winner_id: 20}, empty sets skipped
    //     wo_winner_id: the player not picked absent, scores plus a pick are both sent, the backend rejects that
    // write:
    //   absentId: player id picked absent, ex: 10, undefined while none
    //   scores: typed text, {a: [set 1, set 2, set 3], b: [...]}, '' while empty
    return {pending, filled, nameTag, absentOptions, sides, body, absentId, scores}
}
