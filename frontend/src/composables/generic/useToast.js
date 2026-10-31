import {ref} from 'vue'

const TOAST_DURATION_MS = 4000

const message = ref(null)
let timer = null

export function useToast() {
    function toast(msg) {
        clearTimeout(timer)

        message.value = msg

        timer = setTimeout(() => {
            message.value = null
        }, TOAST_DURATION_MS)
    }

    // single error message for the whole app, rendered by AppToast.vue
    // toast(msg) shows msg for 4s, a new call replaces the current one
    // read `message`, write via `toast()`
    return {message, toast}
}
