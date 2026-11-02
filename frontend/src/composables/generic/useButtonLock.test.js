// @vitest-environment happy-dom
import {describe, expect, it, vi} from 'vitest'
import {useButtonLock} from './useButtonLock.js'

// a focused button on the page, like the one the user clicked
function focusedButton() {
    const button = document.createElement('button')
    document.body.append(button)
    button.focus()
    return button
}

describe('useButtonLock', () => {
    it('drops a call made while locked', async () => {
        // later holds a function that ends the 1st click's request
        let outerResolve
        const {locked, withLock} = useButtonLock()

        // js rule: new Promise(arrow) runs arrow right away, passing it 2 functions js creates, by position
        // input 1 ends the promise, input 2 fails it, any names work, resolve and reject are the usual ones
        // this test needs only input 1, named innerResolve

        // the 1st click's request: a promise that ends only on outerResolve(), like a server not answering yet
        // the arrow stores innerResolve in outerResolve, so the test can end the request later
        // first: the 1st click, not awaited, still running while its request waits
        const first = withLock(() => new Promise((innerResolve) => (outerResolve = innerResolve)))
        expect(locked.value).toBe(true)

        // 2nd click while the 1st is running: dropped, second never runs
        const second = vi.fn()
        await withLock(second)
        expect(second).not.toHaveBeenCalled()

        // ends the 1st click's request, the 1st click ends and the lock goes off
        outerResolve()
        await first
        expect(locked.value).toBe(false)
    })

    it('gives focus back to the button', async () => {
        const button = focusedButton()
        const {withLock} = useButtonLock()
        // disabling the button drops focus to <body>, blur does the same here
        await withLock(async () => button.blur())
        expect(document.activeElement).toBe(button)
    })

    it('skips refocus when the button is gone', async () => {
        const button = focusedButton()
        const {withLock} = useButtonLock()
        await withLock(async () => button.remove())
        expect(document.activeElement).toBe(document.body)
    })
})
