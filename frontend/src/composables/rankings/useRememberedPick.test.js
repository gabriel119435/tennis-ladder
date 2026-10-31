import {beforeEach, describe, expect, it, vi} from 'vitest'
import {nextTick, ref} from 'vue'
import {ANY_PICK, useRememberedPick} from './useRememberedPick.js'

// vitest runs in node without browser localStorage, stubbed here with a Map
const saved = new Map()
vi.stubGlobal('localStorage', {
    getItem: (key) => saved.get(key) ?? null,
    setItem: (key, value) => saved.set(key, String(value)),
    removeItem: (key) => saved.delete(key),
})

describe('useRememberedPick', () => {
    beforeEach(() => saved.clear())

    it('saves every pick', async () => {
        const picked = ref()
        useRememberedPick(ANY_PICK, picked, ref([]))
        picked.value = 3
        await nextTick()
        expect(saved.get(ANY_PICK)).toBe('3')
    })

    it('picks the saved id once the list has it', async () => {
        saved.set(ANY_PICK, '3')
        const picked = ref()
        const rankings = ref([])
        useRememberedPick(ANY_PICK, picked, rankings)
        rankings.value = [{id: 1}, {id: 3}]
        await nextTick()
        expect(picked.value).toBe(3)
    })

    it('forgets the saved id when the list lacks it', async () => {
        saved.set(ANY_PICK, '3')
        const picked = ref()
        const rankings = ref([])
        useRememberedPick(ANY_PICK, picked, rankings)
        rankings.value = [{id: 1}]
        await nextTick()
        expect(picked.value).toBeUndefined()
        expect(saved.has(ANY_PICK)).toBe(false)
    })

    it('forgets the saved id on an empty list', async () => {
        saved.set(ANY_PICK, '3')
        const rankings = ref()
        useRememberedPick(ANY_PICK, ref(), rankings)
        rankings.value = []
        await nextTick()
        expect(saved.has(ANY_PICK)).toBe(false)
    })

    it('keeps the saved id while the list is missing', async () => {
        saved.set(ANY_PICK, '3')
        const rankings = ref([{id: 1}])
        useRememberedPick(ANY_PICK, ref(), rankings)
        rankings.value = undefined
        await nextTick()
        expect(saved.get(ANY_PICK)).toBe('3')
    })
})
