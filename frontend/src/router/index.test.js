import {beforeEach, describe, expect, it, vi} from 'vitest'
import {getMe} from '../api/routes/auth.js'
import {store} from '../store.js'
import {navigationGuard} from './index.js'

// vitest runs vi.hoisted first, vi.mock second, imports last, so the mock factories below can use toast
const {toast} = vi.hoisted(() => ({toast: vi.fn()}))
vi.mock('../api/routes/auth.js', () => ({getMe: vi.fn()}))
vi.mock('../composables/generic/useToast.js', () => ({useToast: () => ({toast})}))
vi.mock('vue-router', () => ({
    createRouter: vi.fn(() => ({beforeEach: vi.fn()})),
    // the real createWebHistory reads window.location, node has no window
    createWebHistory: vi.fn(),
}))

// meta defaults to {} for public pages
function route(path, meta = {}) {
    return {path, meta}
}

const ADMIN = {id: 1, username: 'admin'}

beforeEach(() => {
    store.user = null
})

describe('session loading', () => {
    beforeEach(() => {
        store.sessionLoaded = false
    })

    it('stores the user and marks the session loaded', async () => {
        getMe.mockResolvedValue({user: ADMIN})
        await navigationGuard(route('/standings'))
        expect(store.user).toEqual(ADMIN)
        expect(store.sessionLoaded).toBe(true)
    })

    it('toasts a failed check, keeps the user and retries on the next navigation', async () => {
        store.user = ADMIN
        getMe.mockResolvedValue({error: 'network_error'})
        await navigationGuard(route('/standings'))
        expect(toast).toHaveBeenCalledOnce()
        expect(store.user).toEqual(ADMIN)
        expect(store.sessionLoaded).toBe(false)
    })

    it('skips getMe when the session is already loaded', async () => {
        store.sessionLoaded = true
        await navigationGuard(route('/standings'))
        expect(getMe).not.toHaveBeenCalled()
    })
})

describe('access', () => {
    // session already checked, so the guard skips getMe
    beforeEach(() => {
        store.sessionLoaded = true
    })

    it.each([
        // logged out
        [null, '/standings', {}, true],
        [null, '/login', {}, true],
        [null, '/players', {requiresAuth: true}, '/login'],
        [null, '/rankings', {requiresAuth: true}, '/login'],
        // logged in
        [ADMIN, '/standings', {}, true],
        [ADMIN, '/rankings', {requiresAuth: true}, true],
        [ADMIN, '/login', {}, '/rankings'],
    ])('user %j on %j %j returns %j', async (user, path, meta, expected) => {
        store.user = user
        expect(await navigationGuard(route(path, meta))).toBe(expected)
    })

    it('toasts when an admin page sends a logged-out user to /login', async () => {
        await navigationGuard(route('/players', {requiresAuth: true}))
        expect(toast).toHaveBeenCalledOnce()
    })
})
