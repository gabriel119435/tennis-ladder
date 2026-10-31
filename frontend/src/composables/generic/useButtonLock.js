import {nextTick, ref} from 'vue'

export function useButtonLock() {
    const locked = ref(false)

    async function withLock(fn) {
        if (locked.value) return
        const focused = document.activeElement
        locked.value = true
        try {
            await fn()
        } finally {
            locked.value = false
            // disabling drops focus to <body>, focus can come back only after nextTick removes the attribute
            await nextTick()
            // refocus, unless the button is gone (deleted row, new page)
            if (document.activeElement === document.body && focused?.isConnected) focused.focus()
        }
    }

    // withLock(fn) runs fn with `locked` true, calls made meanwhile are ignored, so repeated clicks send one action
    // read `locked` to disable buttons, write via `withLock()`
    return {locked, withLock}
}
