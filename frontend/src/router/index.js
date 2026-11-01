import {createRouter, createWebHistory} from 'vue-router'
import {getMe} from '../api/routes/auth.js'
import {store} from '../store.js'
import {useToast} from '../composables/generic/useToast.js'
import {translateError} from '../utils/translateError.js'
import LoginView from '../views/LoginView.vue'
import StandingsView from '../views/StandingsView.vue'
import MatchesView from '../views/MatchesView.vue'
import PlayersView from '../views/PlayersView.vue'
import RankingsView from '../views/RankingsView.vue'

const routes = [
    {path: '/', redirect: '/standings'},
    {path: '/login', component: LoginView},
    {path: '/standings/:id?', component: StandingsView},
    {path: '/matches/:id?', component: MatchesView},
    {path: '/players', component: PlayersView, meta: {requiresAuth: true}},
    {path: '/rankings', component: RankingsView, meta: {requiresAuth: true}},

    // :wrongUrl is param, (.*) is path regex, catch all
    {path: '/:wrongUrl(.*)', redirect: '/standings'},
]

const {toast} = useToast()

const router = createRouter({history: createWebHistory(), routes})

// runs before every navigation, true lets it through, a url string redirects there
// exported for the tests, named after vue router's navigation guards
export async function navigationGuard(to) {
    // asks who is logged in, a failure toasts and leaves sessionLoaded false so the next navigation retries
    if (!store.sessionLoaded) {
        const data = await getMe()
        if (data.error) {
            toast(translateError(data.error))
        } else {
            store.user = data.user
            store.sessionLoaded = true
        }
    }

    // admin page without a login: error toast then go to /login
    if (to.meta.requiresAuth && !store.user) {
        toast(translateError('unauthorized'))
        return '/login'
    }
    // login page with logged-in user: goes to /rankings
    if (to.path === '/login' && store.user) return '/rankings'
    return true
}

router.beforeEach(navigationGuard)

export default router
