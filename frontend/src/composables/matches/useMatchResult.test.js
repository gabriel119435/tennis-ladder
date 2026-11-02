import {describe, expect, it, vi} from 'vitest'
import {useMatchResult} from './useMatchResult.js'

// t returns the key, so no i18n setup is needed
vi.mock('vue-i18n', () => ({useI18n: () => ({t: (key) => key})}))

const match = {player_a_id: 10, player_b_id: 20, result_type: null, winner_id: null, sets: []}

describe('useMatchResult body', () => {
    it('skips empty sets and converts digits', () => {
        const {scores, body} = useMatchResult({match, editable: true})
        scores.value = {a: ['6', '', '7'], b: ['4', '', '5']}
        expect(body()).toEqual({
            sets: [
                [6, 4],
                [7, 5],
            ],
            wo_winner_id: undefined,
        })
    })

    it('keeps non digit text for the backend to reject', () => {
        const {scores, body} = useMatchResult({match, editable: true})
        scores.value = {a: ['6a', '', ''], b: ['4', '', '']}
        expect(body().sets).toEqual([['6a', 4]])
    })

    it('sends the player not picked absent as wo winner', () => {
        const {absentId, body} = useMatchResult({match, editable: true})
        absentId.value = 10
        expect(body()).toEqual({sets: [], wo_winner_id: 20})
    })
})
