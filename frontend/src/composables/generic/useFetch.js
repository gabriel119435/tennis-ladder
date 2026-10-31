import {ref} from 'vue'
import {useToast} from './useToast.js'
import {useStaleGuard} from './useStaleGuard.js'
import {translateError} from '../../utils/translateError.js'

// fetchFn: api function returning data or {error}
export function useFetch(fetchFn) {
    const {toast} = useToast()
    const {start} = useStaleGuard()

    const data = ref()
    let lastArgs = []

    async function fetchAndStore(args) {
        const isLatest = start()
        const result = await fetchFn(...args)
        if (!isLatest()) return false
        if (result.error) {
            toast(translateError(result.error))
            return true
        }
        data.value = result
        return false
    }

    function load(...args) {
        lastArgs = args
        data.value = undefined
        return fetchAndStore(args)
    }

    function reload() {
        return fetchAndStore(lastArgs)
    }

    // data: undefined until the answer arrives, so a view tells loading from loaded empty
    // load(...args) empties data, calls fetchFn(...args) and stores the answer, an error becomes a toast
    // reload() repeats the last args without emptying, an error keeps the shown data
    // both drop an answer a newer call replaced (useStaleGuard.js), resolve true only when the latest call failed
    return {data, load, reload}
}
