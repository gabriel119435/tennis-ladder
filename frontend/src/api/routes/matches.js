import {request} from '../request.js'

export async function getMatches(rankingId) {
    return request(`/api/rankings/${rankingId}/matches`)
}

export async function saveResult(matchId, body) {
    return request(`/api/matches/${matchId}/result`, {
        method: 'POST',
        body: JSON.stringify(body),
    })
}

export async function clearResult(matchId) {
    return request(`/api/matches/${matchId}/result`, {method: 'DELETE'})
}
