import {request} from '../request.js'

export async function getParticipants(rankingId) {
    return request(`/api/rankings/${rankingId}/participants`)
}

export async function addParticipant(rankingId, playerId) {
    return request(`/api/rankings/${rankingId}/participants`, {
        method: 'POST',
        body: JSON.stringify({player_id: playerId}),
    })
}

export async function removeParticipant(rankingId, playerId) {
    return request(`/api/rankings/${rankingId}/participants/${playerId}`, {method: 'DELETE'})
}
