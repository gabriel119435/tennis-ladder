import {describe, expect, it} from 'vitest'
import {useStaleGuard} from './useStaleGuard.js'

describe('useStaleGuard', () => {
    it('keeps a single call latest', () => {
        const {start} = useStaleGuard()
        const isLatest = start()
        expect(isLatest()).toBe(true)
    })

    it('marks an older call stale once a newer one starts', () => {
        const {start} = useStaleGuard()
        const isOlderLatest = start()
        const isNewerLatest = start()
        expect(isOlderLatest()).toBe(false)
        expect(isNewerLatest()).toBe(true)
    })
})
