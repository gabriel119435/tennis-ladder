import {watch} from 'vue'

// rankings tab, only the logged admin's own rankings
export const OWN_PICK = 'own_ranking_pick'
// standings and matches tab, any ranking
export const ANY_PICK = 'any_ranking_pick'

// key: OWN_PICK or ANY_PICK
// picked: ranking id, ex: 3, a ref or a writable computed
// rankings: the loaded list, [{id: 3, ...}]
export function useRememberedPick(key, picked, rankings) {
    // every pick is saved, ex: /standings/3 opened from a link saves 3
    watch(
        picked,
        (id) => {
            if (id) localStorage.setItem(key, id)
        },
        {immediate: true},
    )

    // rankings arrived and nothing picked: restores the saved id or forgets it if unlisted, loading or failed keeps it
    watch(rankings, (list) => {
        if (picked.value || !list) return
        const stored = Number(localStorage.getItem(key))
        if (list.some((r) => r.id === stored)) picked.value = stored
        else localStorage.removeItem(key)
    })
}
