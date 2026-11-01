import {request} from '../request.js'

// logged admin's own players only
export async function getPlayers() {
    return request('/api/players')
}

export async function createPlayer(name) {
    return request('/api/players', {
        method: 'POST',
        body: JSON.stringify({name}),
    })
}

export async function renamePlayer(playerId, name) {
    return request(`/api/players/${playerId}`, {
        method: 'PATCH',
        body: JSON.stringify({name}),
    })
}
