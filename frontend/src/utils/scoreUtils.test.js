import {describe, expect, it} from 'vitest'
import {toScore} from './scoreUtils.js'

describe('toScore', () => {
    it.each([
        ['6', 6],
        ['12', 12],
        ['06', 6],
    ])('turns digits only %s into %s', (text, score) => {
        expect(toScore(text)).toBe(score)
    })

    it.each(['6a', 'a6', '6.5', '-6', ' 6', ''])('keeps %s as typed', (text) => {
        expect(toScore(text)).toBe(text)
    })
})
