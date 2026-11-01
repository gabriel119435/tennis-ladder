import {request} from '../request.js'

export async function login(username, password) {
    return request('/api/login', {
        method: 'POST',
        body: JSON.stringify({username, password}),
    })
}

export async function logout() {
    return request('/api/logout', {method: 'POST'})
}

export async function getMe() {
    return request('/api/me')
}
