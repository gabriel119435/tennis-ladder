import {describe, expect, it, vi} from 'vitest'
import {useFetch} from './useFetch.js'
import {translateError} from '../../utils/translateError.js'

// vitest runs vi.hoisted first, vi.mock second, imports last, so the mock factory below can use toast
const {toast} = vi.hoisted(() => ({toast: vi.fn()}))
vi.mock('./useToast.js', () => ({useToast: () => ({toast})}))

// promise: an empty box the test fills by hand with resolve(value)
function deferred() {
    let resolve
    const promise = new Promise((r) => {
        // r is the function that fills this promise, copied out so the test can call it as resolve
        resolve = r
    })
    return {promise, resolve}
}

describe('useFetch', () => {
    it('empties data while loading, then stores the answer', async () => {
        const answer = deferred()
        const {data, load} = useFetch(() => answer.promise)
        data.value = ['old']
        const pending = load()
        expect(data.value).toBeUndefined()
        answer.resolve(['new'])
        expect(await pending).toBe(false)
        expect(data.value).toEqual(['new'])
    })

    it('toasts an error and leaves data undefined', async () => {
        const {data, load} = useFetch(async () => ({error: 'not_found'}))
        expect(await load()).toBe(true)
        expect(toast).toHaveBeenCalledWith(translateError('not_found'))
        expect(data.value).toBeUndefined()
    })

    it('drops an older answer that arrives last', async () => {
        const answers = {1: deferred(), 2: deferred()}
        const {data, load} = useFetch((id) => answers[id].promise)
        const first = load(1)
        const second = load(2)
        answers[2].resolve(['two'])
        await second
        answers[1].resolve(['one'])
        expect(await first).toBe(false)
        expect(data.value).toEqual(['two'])
    })

    it('reload repeats the last args and keeps data until the answer arrives', async () => {
        const answer = deferred()
        // mockResolvedValueOnce returns a box filled with its value, mockReturnValueOnce returns its value as is
        const fetchFn = vi.fn().mockResolvedValueOnce(['old']).mockReturnValueOnce(answer.promise)
        const {data, load, reload} = useFetch(fetchFn)
        await load(7)
        const pending = reload()
        expect(data.value).toEqual(['old'])
        answer.resolve(['new'])
        await pending
        expect(data.value).toEqual(['new'])
        expect(fetchFn).toHaveBeenLastCalledWith(7)
    })
})
