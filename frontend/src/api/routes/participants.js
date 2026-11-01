import {request} from '../request.js'

export async function getParticipants(rankingId) {
    return request(`/api/participants/${rankingId}`)
}

export async function addParticipant(rankingId, playerId) {
    return request(`/api/participants/${rankingId}`, {
        method: 'POST',
        body: JSON.stringify({player_id: playerId}),
    })
}

export async function removeParticipant(rankingId, playerId) {
    return request(`/api/participants/${rankingId}/${playerId}`, {method: 'DELETE'})
}
