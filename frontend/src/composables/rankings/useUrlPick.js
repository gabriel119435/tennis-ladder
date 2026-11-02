import {computed} from 'vue'
import {useRoute, useRouter} from 'vue-router'
import {ANY_PICK, useRememberedPick} from './useRememberedPick.js'

// base: the tab's path, ex: '/standings'
// rankings: the loaded list, [{id: 3, name: 'ranking name', created_by_admin_username: 'admin', ...}]
export function useUrlPick(base, rankings) {
    const route = useRoute()
    const router = useRouter()

    const picked = computed({
        get: () => (route.params.id ? Number(route.params.id) : undefined),
        set: (id) => router.replace(`${base}/${id}`),
    })
    useRememberedPick(ANY_PICK, picked, rankings)

    const options = computed(() =>
        rankings.value?.map((r) => ({value: r.id, label: `${r.name} - ${r.created_by_admin_username}`})),
    )

    // picked: ranking id from the url, ex: /standings/3 -> 3, writing it replaces the url, remembered as ANY_PICK
    // options: picker entries, one per ranking, ex: [{value: 3, label: 'ranking name - admin'}]
    return {picked, options}
}
