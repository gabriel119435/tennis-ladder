import {useToast} from './useToast.js'
import {translateError} from '../../utils/translateError.js'

// withLock: from the caller's useButtonLock(), keeps one submit at a time per page
export function useSubmit(withLock) {
    const {toast} = useToast()

    async function submit(apiCall, onSuccess) {
        let failed = false
        await withLock(async () => {
            const data = await apiCall()
            if (data.error) {
                toast(translateError(data.error))
                failed = true
                return
            }
            await onSuccess(data)
        })
        return failed
    }

    // submit(apiCall, onSuccess) runs apiCall inside withLock, an error becomes a toast, otherwise onSuccess(data) runs
    // resolves true when apiCall failed, false when it succeeded or the lock ignored it
    return {submit}
}
