import {request} from '../request.js'

export async function getRankings(adminId) {
    return request(adminId ? `/api/rankings?admin_id=${adminId}` : '/api/rankings')
}

export async function createRanking(name) {
    return request('/api/rankings', {
        method: 'POST',
        body: JSON.stringify({name}),
    })
}

export async function startRound(rankingId) {
    return request(`/api/rankings/${rankingId}/start`, {method: 'POST'})
}

export async function closeRound(rankingId) {
    return request(`/api/rankings/${rankingId}/close`, {method: 'POST'})
}
