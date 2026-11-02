import {request} from '../request.js'

export async function getStandings(rankingId) {
    return request(`/api/rankings/${rankingId}/standings`)
}
