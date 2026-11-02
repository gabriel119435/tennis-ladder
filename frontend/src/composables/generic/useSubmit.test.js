import {describe, expect, it, vi} from 'vitest'
import {useSubmit} from './useSubmit.js'
import {translateError} from '../../utils/translateError.js'

// vitest runs vi.hoisted first, vi.mock second, imports last, so the mock factory below can use toast
const {toast} = vi.hoisted(() => ({toast: vi.fn()}))
vi.mock('./useToast.js', () => ({useToast: () => ({toast})}))

// runs fn right away, like a free lock
const freeLock = (fn) => fn()
// never runs fn, like a non free lock
const busyLock = async () => {}

describe('useSubmit', () => {
    it('runs onSuccess with the answer and resolves false', async () => {
        const onSuccess = vi.fn()
        const {submit} = useSubmit(freeLock)
        expect(await submit(async () => ({id: 3}), onSuccess)).toBe(false)
        expect(onSuccess).toHaveBeenCalledWith({id: 3})
    })

    it('toasts an error, skips onSuccess and resolves true', async () => {
        const onSuccess = vi.fn()
        const {submit} = useSubmit(freeLock)
        expect(await submit(async () => ({error: 'not_found'}), onSuccess)).toBe(true)
        expect(toast).toHaveBeenCalledWith(translateError('not_found'))
        expect(onSuccess).not.toHaveBeenCalled()
    })

    it('resolves false when the lock is busy', async () => {
        const apiCall = vi.fn()
        const {submit} = useSubmit(busyLock)
        expect(await submit(apiCall, vi.fn())).toBe(false)
        expect(apiCall).not.toHaveBeenCalled()
    })
})
